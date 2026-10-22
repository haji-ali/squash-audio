# Squash solo audio: project handoff

## Goal

Generate guided audio files for solo squash practice. Each file announces a drill, counts down to its start, gives short focus cues, calls positions during ghosting, and signals the transition to the next drill.

- **Programme design, phases, mastery tests and the plan for unbuilt phases:** `PROGRAMME.md`. Read it first.
- **The player's organised coaching notes:** `SQUASH_NOTES.md`. The drill cues come from these.
- **Listening setup:** the user plays their own music from another app while this audio plays. So: no music bed, few words, silence is fine.
- **App use:** the MP3s feed Overtone, the user's app, which jumps to drills using ID3 chapters.

## Current state

Phase 1 is built:
- `out/phase1-a.mp3`: Drive & Move, 17 drills, about 52 min.
- `out/phase1-b.mp3`: Volley & Front Court, 18 drills, about 51 min.

Also built: `out/focus-front.mp3`, a one-off Drops, Lobs & Length session (15 drills, about 50 min). See `PROGRAMME.md`. Its announcements are deliberately longer than Phase 1's, explaining each drill's purpose.

Three ladders are built, `out/ladder-figure-eight.mp3`, `out/ladder-side-to-side.mp3` and `out/ladder-volley.mp3`: single-skill progressions with one short chapter per level, played one level at a time (see "Ladders" in `PROGRAMME.md`, which also plans four more). Session B's ladder volleys are played from the line of the player's current volley ladder level.

Each MP3 is rendered from `out/<id>.overtone.json`, the session as an Overtone script.

Phases 2 and 3 are designed in `PROGRAMME.md` but not built. The user moves on once they pass the Phase 1 mastery test.

## Pipeline

1. `drills.py` holds all the content.
2. `build.py` writes each session as an Overtone script, `out/<id>.overtone.json`. The format is `docs/SCRIPT-FORMAT.md` in the Overtone repo (`../overtone`).
3. The Overtone repo's `scripts/render_script.swift` renders a script to an MP3: it speaks each line, lays the lines out by their timing, mixes in the tones and encodes CBR 64k with chapters and the cover.

```
.venv/bin/python build.py                 # all sessions
.venv/bin/python build.py phase1-a        # one session
swift ../overtone/scripts/render_script.swift out/phase1-a.overtone.json out/phase1-a.mp3 --edge-tts .venv/bin/edge-tts
```

The renderer reports every fixed line it had to move by more than 0.5 s, and every timed part a line ran past. Fix the text or offsets in `drills.py` until it reports no warnings. It caches spoken lines in `~/Library/Caches/OvertoneRender`, so only changed lines are spoken again.

## Speech engine

- edge-tts, Ryan (`en-GB-RyanNeural`) at `+10%`. The script asks for an `en-GB` male voice at `speechRate` 1.1, which the renderer maps to Ryan at `+10%`. `--engine apple --voice <name>` renders with a Mac voice instead.
- Kokoro was tried and rejected (sounded worse). Perplexity has no TTS endpoint.
- A music-bed version was dropped at the user's request. Don't bring it back.

## Layout

- **`drills.py`:** all content.
  - `SESSIONS` is a list of session dicts: `id`, `title`, `subtitle`, `intro`, `outro`, `drills`. A ladder has `levels` instead of `drills`, and no `outro`. Optional: `description` (the script's description, written as the MP3's comment) and `footer` (the cover footer, instead of the estimated minutes).
  - Each drill is `d(name, secs, intro, *cues, ten=True)`. Cues are `(offset_seconds_from_start, item)`, where `item` is spoken text or a tone marker (`ARRIVE`, `TICK`).
  - `ten=True` adds a "Ten seconds." cue automatically.
  - Helpers: `warmup`, `ghost`, `drives`, `feed_and_step` and others build repeated drill shapes. `level(num, title, setup, target, *tips)` is a ladder level.
  - `ghost()` generates position calls with a fixed random seed from `PACES` (time after each call to the pip and back, per front, middle and back) and `ROUNDS` (work and rest).
  - `CALL_SECS` is the time allowed for each call when fitting calls into a round. `STANCE_MIDDLE` calls name the stance ("Open, middle left."), and an open call's pip comes `OPEN_HURRY` seconds sooner.
- **`build.py`:** writes the Overtone scripts. `build.py [session-id ...]` writes the named sessions, or all of them with no arguments.
- **`cover.py`:** `make(subtitle, footer, path)` draws a 1400×1400 cover, embedded in each script as its artwork. The footer's minutes are estimated from word counts. It uses macOS Arial, falling back to DejaVu on Linux.
- **Environment:** `.venv` (`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`; `uv` isn't installed). The renderer also needs system `ffmpeg` with libmp3lame, and the `.venv`'s edge-tts.
- Git repo. `.gitignore` excludes `.venv`, `out` and `__pycache__`.

## Timeline

- Intro chapter: the session intro at 0.5 s.
- Per drill, one chapter of four parts:
  - The announcement, 1 s after the previous stop tone starts (1 s after the intro for the first drill): one flowing line, "<name>, <duration>. <where to stand and what to hit>". Keep them flowing, without filler, round counts or anything the audio already signals. Always keep the setup details (where to stand, where the ball should land, foot position): they tell the user what a good rep looks like. Ghosting announcements end with "swing on the beep, and get back to the T for the next call". The user can add rest between chapters in their app.
  - A 3.5 s countdown, three ticks at -3, -2 and -1 s. The drill starts at least 8 s after the previous stop tone starts (6 s after the intro).
  - The drill: the start tone, then the cues at their offsets. "Ten seconds." uses `beforeEnd`. Each arrival pip follows its call (`after`) by the pace, timed from the end of the call as spoken, and the next call or rest follows the pip the same way.
  - The stop tone.
- Finish chapter: the outro 2 s after the last stop tone starts, then 1 s of silence.
- A ladder instead has the intro chapter, then one chapter per level, titled "Level <num>: <title>": the title and setup, the target and the tips, each 0.5–0.7 s after the line before, then 0.5 s of silence. Playback stops at the end of a chapter, so there's no countdown or timed block. The level number isn't spoken, because the voice says "four" as "for".
- `minimumGap` is 0.8 s: a fixed line that would overlap the one before it starts 0.8 s after it ends.
- Tones (`SOUNDS` in `build.py`, volumes relative to the speech's peaks):
  - Tick: 880 Hz.
  - Start: rising 988 → 1318 Hz.
  - Stop: double 440 Hz.
  - Ghosting arrival pip: 1568 Hz, 90 ms.

### Gotchas already solved (don't undo)

- The voice mispronounces "row" (as in a fight) and reduces "four" to "for" mid-sentence. Keep both out of spoken text: "without a break" or "back to back" instead of "in a row", and `say_secs=False` on the four-minute warm-up so its length isn't announced.
- edge-tts failing with `403, message='Invalid response status'` means the installed edge-tts is out of date: `.venv/bin/pip install --upgrade edge-tts`.

## Chapters

- Chapter list: `Intro` at 0, then `N. <drill name> (<mins> min)` for each drill, then `Finish`.
- A drill chapter starts as the previous stop tone ends, 0.35 s before the announcement, so a slightly late seek doesn't clip the first word.

## Open items

- The user should try Phase 1 on court. Ghosting pace (`PACES`) is the likeliest thing to tune. Transitions are 9 to 25 s.
- Build Phase 2 once the user reports passing the Phase 1 mastery test. Use their log of what broke down to adjust the Phase 2 drills.
