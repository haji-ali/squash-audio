import asyncio
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import edge_tts
import numpy as np

import cover
from drills import ARRIVE, RATE, SESSIONS, TICK, VOICE

SR = 24000
ROOT = Path(__file__).parent
CACHE = ROOT / "cache"
OUT = ROOT / "out"
MIN_GAP = 0.8   # between two spoken cues
TONE_GAP = 0.3  # between a cue and a tone
SPEECH_RMS = 0.12
LEAD_IN = 0.5


def clip_path(text):
    h = hashlib.sha1(f"{VOICE}|{RATE}|{text}".encode()).hexdigest()[:16]
    return CACHE / f"{h}.mp3"


def timing_path(text):
    return clip_path(text).with_suffix(".json")


async def synth_all(texts):
    CACHE.mkdir(exist_ok=True)
    sem = asyncio.Semaphore(4)

    async def one(text):
        path, timing = clip_path(text), timing_path(text)
        if path.exists() and timing.exists():
            return
        async with sem:
            audio, sentences = bytearray(), []
            async for chunk in edge_tts.Communicate(text, VOICE, rate=RATE).stream():
                if chunk["type"] == "audio":
                    audio += chunk["data"]
                elif chunk["type"] == "SentenceBoundary":
                    start = chunk["offset"] / 1e7  # 100 ns ticks
                    sentences.append([start, start + chunk["duration"] / 1e7, chunk["text"]])
            path.write_bytes(audio)
            timing.write_text(json.dumps(sentences))

    await asyncio.gather(*(one(t) for t in dict.fromkeys(texts)))


def load(text):
    """Trimmed samples, plus (start, end, sentence) timings relative to the trimmed clip."""
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(clip_path(text)),
         "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
        check=True, capture_output=True).stdout
    y = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    # edge-tts pads clips with ~0.25 s of leading and ~0.9 s of trailing silence.
    loud = np.nonzero(np.abs(y) > 0.01)[0]
    lo, hi = max(loud[0] - int(SR * 0.02), 0), loud[-1] + int(SR * 0.1)
    dur, lead = (hi - lo) / SR, lo / SR
    sentences = [(max(a - lead, 0), min(b - lead, dur), t) for a, b, t in json.loads(timing_path(text).read_text())]
    return y[lo:hi], sentences or [(0, dur, text)]


def tone(freq, dur, amp=0.3):
    t = np.arange(int(SR * dur)) / SR
    y = np.sin(2 * np.pi * freq * t) * amp
    fade = int(SR * 0.01)
    y[:fade] *= np.linspace(0, 1, fade)
    y[-fade:] *= np.linspace(1, 0, fade)
    return y.astype(np.float32)


def silence(dur):
    return np.zeros(int(SR * dur), dtype=np.float32)


TICK_TONE = tone(880, 0.12)
START = np.concatenate([tone(988, 0.15), silence(0.05), tone(1318, 0.45)])
STOP = np.concatenate([tone(440, 0.25), silence(0.15), tone(440, 0.25)])
ARRIVE_TONE = tone(1568, 0.09, amp=0.35)
TONES = {TICK: TICK_TONE, ARRIVE: ARRIVE_TONE}


def ffmetadata(starts, total):
    esc = lambda x: x.replace("\\", "\\\\").replace("=", "\\=").replace(";", "\\;").replace("#", "\\#")
    lines = [";FFMETADATA1"]
    ends = [t for t, _ in starts[1:]] + [total]
    for (start, title), end in zip(starts, ends):
        lines += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={int(start * 1000)}",
                  f"END={int(end * 1000) - 1}", f"title={esc(title)}"]
    return "\n".join(lines) + "\n"


def srt(lines):
    stamp = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(t % 1 * 1000):03d}"
    lines = sorted(lines)
    ends = [min(b, nxt[0]) for (_, b, _), nxt in zip(lines, lines[1:] + [(float("inf"),)])]
    return "\n".join(f"{i}\n{stamp(a)} --> {stamp(b)}\n{text}\n"
                     for i, ((a, _, text), b) in enumerate(zip(lines, ends), 1))


def fmt(t):
    return f"{int(t // 60):02d}:{t % 60:06.3f}"


NUMBERS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five"}


def duration_words(secs):
    m, s = divmod(secs, 60)
    if s == 0:
        return f"{NUMBERS[m]} minute{'s' if m > 1 else ''}"
    if s == 30:
        return f"{NUMBERS[m]} and a half minutes"
    raise ValueError(f"unsupported drill length {secs}s")


def announcement(drill):
    return f"{drill['name']}. {duration_words(drill['secs'])}. {drill['intro']}"


def drill_cues(drill):
    cues = list(drill["cues"])
    if drill["ten"]:
        cues.append((drill["secs"] - 10, "Ten seconds."))
    return sorted(cues, key=lambda c: c[0])


def session_texts(session):
    texts = [session["intro"], session["outro"]]
    for drill in session["drills"]:
        texts.append(announcement(drill))
        texts += [c for _, c in drill_cues(drill) if c not in TONES]
    return texts


def build(session):
    drills = session["drills"]
    texts = session_texts(session)
    loaded = {t: load(t) for t in dict.fromkeys(texts)}
    clips = {t: samples for t, (samples, _) in loaded.items()}
    clip = lambda item: TONES.get(item, clips.get(item))
    dur_of = lambda item: len(clip(item)) / SR

    events = []  # (start, samples, text or None for tones)
    schedule = []
    chapter_starts = [(0.0, "Intro")]
    problems = []

    t = 0.5
    events.append((t, clips[session["intro"]], session["intro"]))
    t += dur_of(session["intro"]) + 1.0

    for i, drill in enumerate(drills):
        ann = announcement(drill)
        if i > 0:
            events.append((t, STOP, None))
            ann_start = t + 1.5
            min_end = t + 12
        else:
            ann_start = t
            min_end = t + 8
        events.append((ann_start, clips[ann], ann))
        chapter_starts.append((ann_start - LEAD_IN, f"{i + 1}. {drill['name']} ({drill['secs'] // 60} min)"))
        start = max(ann_start + dur_of(ann) + 4.0, min_end)
        for k in (3, 2, 1):
            events.append((start - k, TICK_TONE, None))
        events.append((start, START, None))

        timed = [(start + off, item) for off, item in drill_cues(drill)]
        for (a, ia), (b, ib) in zip(timed, timed[1:]):
            gap = MIN_GAP if ia not in TONES and ib not in TONES else TONE_GAP
            if a + dur_of(ia) + gap > b:
                problems.append(f"drill {i + 1} '{drill['name']}': cue at {fmt(a - start)} overlaps next ({ia!r})")
        end = start + drill["secs"]
        if timed and timed[-1][0] + dur_of(timed[-1][1]) > end:
            problems.append(f"drill {i + 1} '{drill['name']}': last cue runs past the end")
        events += [(a, clip(item), None if item in TONES else item) for a, item in timed]
        schedule.append(f"{fmt(ann_start)}  announce  {i + 1:2d}. {drill['name']} ({drill['secs'] // 60} min)\n"
                        f"{fmt(start)}  start     (transition {start - t:.0f}s)")
        t = end

    if problems:
        sys.exit(f"{session['id']}:\n" + "\n".join(problems))

    events.append((t, STOP, None))
    chapter_starts.append((t + 2.0 - LEAD_IN, "Finish"))
    events.append((t + 2.0, clips[session["outro"]], session["outro"]))
    total = t + 2.0 + dur_of(session["outro"]) + 1.0
    schedule.append(f"{fmt(t)}  finished  total {fmt(total)}")

    buf = np.zeros(int(total * SR) + SR, dtype=np.float32)
    for at, samples, _ in events:
        s = int(at * SR)
        buf[s:s + len(samples)] += samples
    speech = np.concatenate([samples for _, samples, text in events if text])
    buf *= SPEECH_RMS / np.sqrt(np.mean(speech ** 2))

    OUT.mkdir(exist_ok=True)
    name = session["id"]
    cover_file = OUT / f"{name}.jpg"
    cover.make(session["subtitle"], f"{round(total / 60)} min", cover_file)
    chapters_file = OUT / f"{name}.ffmeta"
    chapters_file.write_text(ffmetadata(chapter_starts, total))
    path = OUT / f"{name}.mp3"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
         "-i", str(cover_file), "-i", str(chapters_file),
         "-map", "0:a", "-map", "1:v", "-map_metadata", "2", "-map_chapters", "2",
         "-af", "alimiter=limit=0.9:level=0", "-ar", "44100",
         "-c:a", "libmp3lame", "-b:a", "64k", "-c:v", "copy", "-id3v2_version", "3",
         "-metadata", f"title={session['title']}",
         "-metadata:s:v", "title=Album cover", "-metadata:s:v", "comment=Cover (front)",
         str(path)],
        input=buf.astype(np.float32).tobytes(), check=True)
    (OUT / f"{name}.txt").write_text("\n".join(schedule) + "\n")
    subtitles = [(at + a, at + b, sentence) for at, _, text in events if text for a, b, sentence in loaded[text][1]]
    (OUT / f"{name}.srt").write_text(srt(subtitles))
    print(f"== {name}\n" + "\n".join(schedule) + f"\nwrote {path}\n")


def main():
    wanted = sys.argv[1:]
    sessions = [s for s in SESSIONS if not wanted or s["id"] in wanted]
    if not sessions:
        sys.exit(f"unknown session; choose from: {', '.join(s['id'] for s in SESSIONS)}")
    asyncio.run(synth_all([t for s in sessions for t in session_texts(s)]))
    for session in sessions:
        build(session)


if __name__ == "__main__":
    main()
