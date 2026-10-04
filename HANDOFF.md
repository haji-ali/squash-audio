# Squash solo audio: project handoff

## Goal

Generate guided audio files for solo squash practice. Each file announces a drill, counts down to its start, gives short focus cues, calls positions during ghosting, and signals the transition to the next drill.

- **Programme design, phases, mastery tests and the plan for unbuilt phases:** `PROGRAMME.md`. Read it first.
- **The player's organised coaching notes:** `SQUASH_NOTES.md`. The drill cues come from these.
- **Listening setup:** the user plays their own music from another app while this audio plays. So: no music bed, few words, silence is fine.
- **App use:** the MP3s also feed an app the user is developing, which jumps to drills using ID3 chapters.

## Current state

Phase 1 is built:
- `out/phase1-a.mp3`: Drive & Move, 14 drills, about 43 min.
- `out/phase1-b.mp3`: Volley & Front Court, 16 drills, about 45 min.

Both are CBR 64k with chapters and cover art. Next to each MP3 in `out/`:
- `<id>.txt`: the announce and start time of each drill.
- `<id>.ffmeta`: the chapter definitions.
- `<id>.jpg`: the cover.
- `<id>.srt`: subtitles of everything spoken, one cue per sentence. Every session build must produce one.

Phases 2 and 3 are designed in `PROGRAMME.md` but not built. The user moves on once they pass the Phase 1 mastery test.

`out/fastfocus-00.mp3` is the earlier FastFocus-based routine. The user rejected it as a training plan. It's kept until the user says to delete it.

## Speech engine

- edge-tts, voice `en-GB-RyanNeural`.
- Kokoro was tried and rejected (sounded worse). Perplexity has no TTS endpoint.
- A music-bed version was dropped at the user's request. Don't bring it back.

## Layout

- **`drills.py`:** all content.
  - `SESSIONS` is a list of session dicts: `id`, `title`, `subtitle`, `intro`, `outro`, `drills`.
  - Each drill is `d(name, secs, intro, *cues, ten=True)`. Cues are `(offset_seconds_from_start, item)`, where `item` is spoken text or a tone marker (`ARRIVE`, `TICK`).
  - `ten=True` adds a "Ten seconds." cue automatically.
  - Helpers: `warmup`, `ghost`, `drives`, `feed_and_step` and others build repeated drill shapes.
  - `ghost()` generates position calls with a fixed random seed from `PACES` (time after each call to the pip and back, per front, middle and back) and `ROUNDS` (work and rest).
- **`build.py`:** synthesises speech, builds the timeline, mixes, and encodes. `build.py [session-id ...]` builds the named sessions, or all of them with no arguments.
- **`cover.py`:** `make(subtitle, footer, path)` draws a 1400×1400 cover. The build calls it for every session. It uses macOS Arial, falling back to DejaVu on Linux.
- **`cache/`:** edge-tts clips as `.mp3`, keyed by SHA1 of `voice|rate|text`, each with a `.json` of edge-tts sentence timings (start, end, text) used for the subtitles. A clip missing its `.json` is resynthesised. Changing the voice, rate or text resynthesises only what changed.
- **Environment:** `.venv` (`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`; `uv` isn't installed). Also needs system `ffmpeg` with libmp3lame.
- Git repo. `.gitignore` excludes `.venv`, `cache`, `out` and `__pycache__`.

Build:

```
.venv/bin/python build.py              # all sessions
.venv/bin/python build.py phase1-a     # one session
```

## How the build works

- The timeline is in seconds, mixed with numpy at 24 kHz mono float32, then piped to ffmpeg as f32le.
- edge-tts clips are trimmed on load. edge-tts pads about 0.25 s before the speech and 0.9 s after, which would make short calls late and longer than they sound. Sentence timings are shifted by the trimmed lead.
- Subtitles: each spoken event's sentence timings are offset to its place on the timeline. Each cue ends no later than the next one starts, because edge-tts sentence durations can overlap the next sentence by about 50 ms.
- Per drill:
  - Stop tone at the previous block's end.
  - Announcement 1.5 s later: name, duration, intro.
  - Start time = announcement end + 4 s, with a minimum transition of 12 s (8 s for the first drill).
  - Three tick beeps at -3, -2 and -1 s, then the start tone.
  - Cues at their offsets.
- Tones:
  - Tick: 880 Hz.
  - Start: rising 988 → 1318 Hz.
  - Stop: double 440 Hz.
  - Ghosting arrival pip: 1568 Hz, 90 ms.
- The build aborts with a list if cues overlap: 0.8 s between spoken cues, 0.3 s between a cue and a tone. It also aborts if a cue runs past the end of a drill.
- Speech is scaled to a fixed RMS (`SPEECH_RMS = 0.12`). Final limiter: `alimiter=limit=0.9:level=0`.

### Gotchas already solved (don't undo)

- `alimiter` needs `level=0`, otherwise it auto-levels back to 0 dBFS.
- Feed ffmpeg float32, not int16. Clipping before the limiter was a bug.
- Keep MP3 output CBR. VBR made chapter seeking imprecise, because players estimate the byte offset from the time.
- ffmpeg writes ID3v2.3 CHAP/CTOC frames from `-map_metadata 2 -map_chapters 2`. The cover is embedded with `-map 1:v -c:v copy -id3v2_version 3`.

## Chapters

- Chapter list: `Intro` at 0, then `N. <drill name> (<mins> min)` for each drill, then `Finish`.
- Each drill chapter starts 0.5 s (`LEAD_IN`) before the spoken announcement, so a slightly late seek doesn't clip the first word.
- Not yet tested in the user's app.

## Open items

- The user should try Phase 1 on court. Ghosting pace (`PACES`) and announcement length are the likeliest things to tune. Transitions are 18 to 28 s because the announcements describe the setup in full.
- Build Phase 2 once the user reports passing the Phase 1 mastery test. Use their log of what broke down to adjust the Phase 2 drills.
