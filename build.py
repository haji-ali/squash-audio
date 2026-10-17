"""Writes each session as an Overtone script, out/<id>.overtone.json, which the Overtone repo's
scripts/render_script.swift renders to an MP3.

Each script has an intro chapter, then per drill an announcement, a 3.5 s countdown, the drill and its
stop tone, then a finish chapter. Ghosting calls and arrival pips are chained with `after`, so each
pip is timed from the end of its call as the voice actually says it.
"""
import base64
import json
import sys
import tempfile
from pathlib import Path

import cover
from drills import ARRIVE, CALL_SECS, RATE, SESSIONS, TICK

OUT = Path(__file__).parent / "out"

# Tone levels relative to the speech's peaks.
SOUNDS = {
    "tick": {"tones": [{"hz": 880, "seconds": 0.12}], "volume": 0.5},
    "start": {"tones": [{"hz": 988, "seconds": 0.15}, {"seconds": 0.05}, {"hz": 1318, "seconds": 0.45}],
              "volume": 0.5},
    "stop": {"tones": [{"hz": 440, "seconds": 0.25}, {"seconds": 0.15}, {"hz": 440, "seconds": 0.25}],
             "volume": 0.5},
    "arrive": {"tones": [{"hz": 1568, "seconds": 0.09}], "volume": 0.6},
}
MARKERS = {TICK: "tick", ARRIVE: "arrive"}
STOP_SECS = sum(t["seconds"] for t in SOUNDS["stop"]["tones"])
ARRIVE_SECS = sum(t["seconds"] for t in SOUNDS["arrive"]["tones"])
COUNTDOWN = 3.5
WORDS_PER_SEC = 2.5 * (1 + int(RATE.strip("%+")) / 100)
NUMBERS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five"}


def r(t):
    return round(t, 3)


def say(text, **timing):
    return {**timing, "text": text}


def sound(name, **timing):
    return {**timing, "sound": name}


def duration_words(secs):
    m, s = divmod(secs, 60)
    if s == 0:
        return f"{NUMBERS[m]} minute{'s' if m > 1 else ''}"
    if s == 30:
        return f"{NUMBERS[m]} and a half minutes"
    raise ValueError(f"unsupported drill length {secs}s")


def announcement(drill):
    name = drill['name'].replace(':', ',')
    if not drill["say_secs"]:
        return f"{name}. {drill['intro']}"
    return f"{name}, {duration_words(drill['secs']).lower()}. {drill['intro']}"


def drill_cues(drill):
    cues = list(drill["cues"])
    if drill["ten"]:
        cues.append((drill["secs"] - 10, "Ten seconds."))
    return sorted(cues, key=lambda c: c[0])


def work_lines(drill):
    """The drill's cues, from the start tone. A pip follows its call, and a call or rest follows a pip,
    with `after`; everything else stays at its offset."""
    lines = [sound("start", at=0)]
    prev = None
    for off, item in drill_cues(drill):
        if drill["ten"] and item == "Ten seconds." and off == drill["secs"] - 10:
            line = say(item, beforeEnd=10)
        elif item == ARRIVE and prev and prev[1] in CALL_SECS:
            line = sound("arrive", after=r(off - prev[0] - CALL_SECS[prev[1]]))
        elif prev and prev[1] == ARRIVE and item not in MARKERS:
            line = say(item, after=r(off - prev[0] - ARRIVE_SECS))
        elif item in MARKERS:
            line = sound(MARKERS[item], at=r(off))
        else:
            line = say(item, at=r(off))
        lines.append(line)
        prev = (off, item)
    return lines


def drill_chapter(i, drill):
    # The announcement comes 1 s after the previous stop tone starts (1 s after the intro for the first
    # drill), and the start tone 3.5 s after the announcement, but no sooner than 8 s after that stop
    # tone starts (6 s after the intro). The stop tone ends the chapter before, so this chapter starts
    # as it finishes.
    gap = 1.0 if i == 0 else 1.0 - STOP_SECS
    least = 6 - COUNTDOWN if i == 0 else 8 - COUNTDOWN - STOP_SECS
    return {
        "title": f"{i + 1}. {drill['name']} ({drill['secs'] // 60} min)",
        "parts": [
            {"minDuration": r(least), "lines": [say(announcement(drill), after=r(gap))]},
            {"duration": COUNTDOWN, "lines": [sound("tick", beforeEnd=k) for k in (3, 2, 1)]},
            {"duration": drill["secs"], "lines": work_lines(drill)},
            {"lines": [sound("stop", after=0)]},
        ],
    }


def estimated_minutes(session):
    speech = lambda text: len(text.split()) / WORDS_PER_SEC
    total = 0.5 + speech(session["intro"]) + 1
    for i, drill in enumerate(session["drills"]):
        total += max(1 + speech(announcement(drill)) + COUNTDOWN, 8 if i else 6) + drill["secs"]
    return round((total + 2 + speech(session["outro"]) + 1) / 60)


def artwork(session):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "cover.jpg"
        cover.make(session["subtitle"], f"{estimated_minutes(session)} min", path)
        return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode()


def script(session):
    chapters = [{"title": "Intro", "lines": [say(session["intro"], at=0.5)]}]
    chapters += [drill_chapter(i, drill) for i, drill in enumerate(session["drills"])]
    chapters.append({"title": "Finish", "parts": [
        # The outro comes 2 s after the last stop tone starts, and the file ends 1 s after it.
        {"lines": [say(session["outro"], after=r(2.0 - STOP_SECS))]},
        {"duration": 1},
    ]})
    return {
        "format": "overtone-script",
        "version": 1,
        "title": session["title"],
        "artwork": artwork(session),
        "voice": {"language": "en-GB", "gender": "male"},
        "speechRate": 1 + int(RATE.strip("%+")) / 100,
        "sounds": SOUNDS,
        # Spoken cues stay 0.8 s apart.
        "minimumGap": 0.8,
        "chapters": chapters,
    }


def main():
    wanted = sys.argv[1:]
    sessions = [s for s in SESSIONS if not wanted or s["id"] in wanted]
    if not sessions:
        sys.exit(f"unknown session; choose from: {', '.join(s['id'] for s in SESSIONS)}")
    OUT.mkdir(exist_ok=True)
    for session in sessions:
        path = OUT / f"{session['id']}.overtone.json"
        path.write_text(json.dumps(script(session), indent=1, ensure_ascii=False) + "\n")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
