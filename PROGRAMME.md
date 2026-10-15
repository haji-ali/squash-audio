# Solo squash programme

A progressive solo programme built from the coaching notes in `SQUASH_NOTES.md`. Each session is a guided audio file of about 50 minutes. `drills.py` holds the exact wording and timings. This document holds the design, the mastery tests, and the plan for later phases.

## The player and the goal

Right-handed club amateur, about 500 SportyHQ. Sustains rallies, but technique breaks down under pace and fatigue.

What the programme drills, in priority order:
1. **Early, high preparation:** racket up as the ball leaves the front wall.
2. **High, straight follow-through** to the front wall.
3. **Get behind the ball and step in:** feet parallel to the side wall, stomp the front foot, weight forward.
4. **Firm, cocked wrist:** no breaking, twisting or drooping.
5. **Stay engaged at the T:** fast recovery, low and wide stance, split step on the opponent's hit.

Longer-term goals:
- Turn easy balls into forcing shots, and play safe straight drives under pressure.
- Separate your own speed from the ball's.
- Current anchoring thoughts: **step into easy shots** and **volley off the serve**.

## Design principles

- **Progress between phases, not inside a drill.** Each phase has fixed drills and a mastery test. Move up when you pass the test, not by the calendar. Audio never announces "level two" partway through a drill.
- **One drill, one target.** Every announcement says where to stand, where to aim, and gives one focus. Control drills never also ask for T recovery. Recovery is its own drill, and most T work happens in ghosting.
- **Ghosting between hitting blocks.** It rests the arm, gets the heart rate up, and trains the T under fatigue. The audio calls the positions.
- **Order:** warm up, then technique while fresh, then movement under fatigue, then cool down.
- **Two alternating sessions per phase.** Session A covers drives and movement. Session B covers volleys and the front court. Alternate them each solo session.
- **Mantra cues reused from coaching:** *Grip, prep, rotate, swish, follow, T* and *Stay engaged*.

## Terms used in the audio

- **Forehand side** is the right half of the court. **Left and right** in ghosting calls are as you face the front wall.
- **Short line** is the line across the court at the front of the service boxes. **Service line** is the middle line on the front wall.
- **The T** is where the short line meets the half-court line.
- **Length:** a drive whose second bounce is near the back wall.
- **"No T" in control drills:** the ball comes straight back to you, so stay behind it. A softer drive landing in the service box is a *control* target, not a match target.
- **Drive and recover:** hit higher and softer to buy time, push two steps toward the T, then come back in behind the ball.
- **Feed shot and reset:** in a continuous solo drill you are also the opponent, so a really good shot leaves you a hard ball. Loops give one shot the work and play the other as a feed, softer so the ball sits up. In drive drills, a higher, softer drive after a good one gets the rally back. Losing the rhythm after a good shot is expected; scored drills count successes per set of ten, not streaks.

## Ghosting system

- **Positions:** front left, front right, middle left, middle right, back left, back right.
- **How a rep works:**
  1. A voice calls a position.
  2. A short high **pip** marks when you should be there and swinging.
  3. The next call comes when you should be back at the T, so split step on every call.
- **Rounds:** each ghosting block is three minutes, in rounds with spoken rest and one technique tip. Three countdown ticks restart each round.

Times are in seconds from the **end** of the call, which takes about 0.8 s to say (1.45 s with a stance). Each cell is end of call → pip, then pip → next call.

| Pace | Front | Back | Middle | Rounds |
|---|---|---|---|---|
| easy (warm-up, two steps only) | 1.0, 2.2 | 1.0, 2.2 | 1.0, 2.2 | continuous |
| slow | 2.6, 3.0 | 2.4, 2.8 | 1.6, 2.2 | 3 × 49 s, 15 s rest |
| medium | 2.1, 2.4 | 1.9, 2.2 | 1.3, 1.7 | 3 × 46 s, 15 s rest |
| fast | 1.7, 2.0 | 1.5, 1.8 | 1.0, 1.4 | 4 × 32 s, 15 s rest |

- **Front** is the longest run, about 3.5–4 m after the lunge and reach. It also has the hardest push back to the T.
- **Back** is shorter, about 2.5–3 m, but you have to turn and get beside the ball via the box corner.
- **Middle** is one or two steps.
- The return includes the swing, the push-off and the split step, so it's longer than the outbound move.
- Full rep, call to next call:

| Pace | Front | Back | Middle |
|---|---|---|---|
| slow | 6.4 s | 6.0 s | 4.6 s |
| medium | 5.3 s | 4.9 s | 3.8 s |
| fast | 4.5 s | 4.1 s | 3.2 s |

These are estimates. To calibrate, time five comfortable match-pace reps to each of front, back and middle. Set `medium` to the average, `slow` about 25% slower, and `fast` about 15% faster.

To tune these, edit `PACES`, `CALL_SECS` and `ROUNDS` in `drills.py`. Later phases may add a faster `"match"` pace.

**Ghosting footwork (from coaching):**
- Back corners: go via the service-box corner. Plant at 45°: left then right foot in the right corner, right then left foot in the left corner.
- Front corners: finish closed, with the left foot forward on the right and the right foot forward on the left.
- Middle: open or closed stance. An open-stance backhand needs more rotation. In Session B's volley ghosting each call names the stance ("Open, middle left"). Open is a rushed ball, so its pip comes 0.5 s sooner (`OPEN_HURRY`).
- Every rep: full swish from high prep to high follow-through, then fast back to the T.

## Phase 1: Foundation (built)

**Files:**
- `out/phase1-a.mp3`: Drive & Move, about 52 min.
- `out/phase1-b.mp3`: Volley & Front Court, about 51 min.

### Session A: Drive & Move

| # | Drill | Min | What |
|---|---|---|---|
| 1 | Movement warm-up | 4 | 2 min of called moves (jog, side-steps, lunges, hips, high knees, arm circles), then called split steps (easy pace, two steps) |
| 2 | Side-to-side warm-up | 3 | In the middle, a step in front of the short line, facing the front wall. Around the service line, just off centre, so the ball comes back to the other side: FH, BH, FH, one bounce each |
| 3–4 | FH / BH straight drives | 3 + 3 | A racket length off the wall, at the back of the service box. Medium pace, just above the service line, first bounce in the box so it comes up to you. Prep and finish cues |
| 5 | Ghosting: back corners | 3 | slow |
| 6–7 | FH / BH feed and step in | 3 + 3 | Soft high feed lands near the short line. Get behind it, stomp, deep drive: a racket head above the service line, first bounce behind the box. Collect and repeat |
| 8–9 | FH / BH front-court drives | 2 + 2 | Step in front of the short line: straight drives to length (a racket head above the service line, first bounce behind the box) with exaggerated rotation, going around the ball |
| 10 | Ghosting: front corners | 3 | medium, closed lunge |
| 11–12 | FH / BH drive and recover | 2 + 2 | Higher, softer drives, two steps toward the T and back |
| 13 | Ghosting: middle and back | 3 | medium |
| 14–15 | FH / BH three-shot sequence | 2 + 2 | Soft (on the service line, bouncing in the box), medium (a racket head above, bouncing behind the box), hard (just under the service line, off the back wall). Same prep for all |
| 16 | Ghosting: six points | 3 | fast |
| 17 | Cool-down | 3 | Easy side-to-side, then called stretches: calves, hips, shoulders, each side |

### Session B: Volley & Front Court

| # | Drill | Min | What |
|---|---|---|---|
| 1 | Movement warm-up | 4 | As in A |
| 2 | Side-to-side warm-up | 3 | As in A |
| 3–4 | FH / BH short volleys | 2 + 2 | One step in front of the short line, near the wall, aiming just above the service line so it returns at shoulder height |
| 5 | Ghosting: volley positions | 3 | slow, middle left and right, each called open or closed. Open comes 0.5 s quicker |
| 6 | Forehand to backhand volleys | 3 | Middle, about 2 m from the front wall, around the service line just off centre. First half with a bounce, second half on the volley |
| 7–8 | FH / BH box volleys | 2 + 2 | Back of the service box, medium pace, a racket head above the service line, ball returns at shoulder height. Racket above the ball |
| 9–10 | FH / BH volley heights | 2 + 2 | Step in front of the short line, near the wall: straight volleys just above the service line, on it, just above the tin, then let it bounce and restart |
| 11 | Ghosting: front corners with drops | 3 | medium, shadow drops |
| 12–13 | FH / BH drops | 2 + 2 | In front of the short line: drop, bounce, drop, just above the tin |
| 14 | Serve then T | 3 | Serve, move to the T and split step as if volleying the return. Switch boxes halfway |
| 15–16 | FH / BH length check | 2 + 2 | A racket head above the service line, first bounce behind the box. Score sets of ten by how many bounce first behind the short line; softer reset shots allowed and not counted |
| 17 | Ghosting: six points | 3 | fast |
| 18 | Cool-down | 3 | As in A |

### Phase 1 mastery test

Pass every line in two consecutive sessions, then move to Phase 2. Expect roughly 4 to 8 weeks.

The audio states each target in the drill that tests it ("Phase two target: ..."), and both session intros say to hit every target in two sessions in a row.

| Test | Target |
|---|---|
| Length check: drives bouncing first behind the short line, per set of ten, resets allowed | 8 of 10 each side, misses in between allowed |
| Feed and step in, second bounce at the back wall | 7 of 10 each side, misses in between allowed |
| Forehand to backhand volleys, no bounce | 20 in one unbroken rally |
| Box volleys | 10 in one unbroken rally, each side |
| Drops, bouncing twice before the short line | 5 in one unbroken rally, each side |
| Ghosting | Every rep at the pip, full swish, split step on each call, form holds in the fast block |

Keep a short log: date, session, the numbers above, and one line on what broke down. That line decides the Phase 2 details.

## Focus session: Drops, Lobs & Length (built)

**File:** `out/focus-front.mp3`, about 49 min. A one-off session added after a match lost mainly on unreached drops, alongside Phase 1 rather than part of the progression. Three aims:
- **Reach the drop** by starting earlier: recover just behind the T (not deep), split step on the hit, racket up before arriving.
- **Lob from the front** to buy time: low, under the ball, open face, lift high above the service line. Cross-court lobs clip the side wall high behind the service box. From the front court, a cross-court's front-wall target is on the hitter's own half, not past the middle.
- **Length by height, not force:** aim about a racket head above the service line, so the first bounce lands behind the service box and the second near the back wall.

Announcements in this session are longer than in Phase 1: each one explains what the drill is for and what a good rep looks like, at the user's request.

| # | Drill | Min | What |
|---|---|---|---|
| 1 | Movement warm-up | 4 | As in Phase 1 |
| 2 | Side-to-side warm-up | 3 | As in Phase 1 |
| 3 | Ghosting: split step and go | 3 | slow, front corners. Early start, closed lunge, racket up |
| 4–5 | FH / BH length by height | 3 + 3 | Behind the short line, aim a racket head above the service line |
| 6–7 | FH / BH drop and lob | 3 + 3 | From the short line, drop, move in and lob before the second bounce. Straight, then cross-court halfway |
| 8 | Ghosting: front corners with lobs | 3 | medium, shadow lob, low to high |
| 9 | Boast and straight lob | 3 | Alternating loop: boast from the back right, straight lob down the left, boast from the back left, straight lob down the right. First half the lob is the real shot and the boast a feed; second half the reverse |
| 10 | Ghosting: back to front | 3 | medium, back and front corners. Full recovery to the T after every back corner |
| 11 | Boast and cross-court | 3 | Boast from the back right, firm cross-court drive with width (side wall behind the box) back to the back right. The boast is a feed. Switch sides halfway |
| 12–13 | FH / BH length when tired | 2 + 2 | Same aim as 4–5. Score sets of ten by how many bounce first behind the short line, with resets allowed |
| 14 | Ghosting: drop retrieval | 3 | fast, all six with the front corners called twice as often |
| 15 | Cool-down | 3 | As in Phase 1 |

Suggested use: once a week in place of one Phase 1 session until drops stop costing points. Log the length-when-tired counts against the Phase 1 length check.

## Phase 2: Build (designed, not yet built)

**Aim:** the same technique at higher pace and with tighter targets, plus the first movement-and-shot combinations. Ghosting gets faster with less rest.

### Session A: Drive & Move

| # | Drill | Min | Notes |
|---|---|---|---|
| 1 | Movement warm-up | 3 | Called split steps at slow pace (full distance) |
| 2 | Side-to-side volleys | 3 | First minute with a bounce, then on the volley |
| 3–4 | FH / BH channel drives | 3 + 3 | Harder. Land inside the door width (or a racket width of the wall) and keep it there |
| 5 | Ghosting: back corners with a boast | 3 | medium. Shadow boast on the pip |
| 6–7 | FH / BH feed and attack | 3 + 3 | Self-feed to mid court. Alternate a deep drive and a hard drive under the service line. Same set-up for both |
| 8 | Solo boast and drive | 3 | Boast from the back right, ball goes to the front left. Run, straight drive down the left wall, it comes back to the back left. Boast, drive down the right wall, and repeat. Start slow |
| 10 | Ghosting: front corners | 3 | fast |
| 10–11 | FH / BH drive then volley | 2 + 2 | Drive straight, volley the return straight, and alternate. Racket up for the volley |
| 12–13 | FH / BH three-shot sequence with recovery | 2 + 2 | Phase 1 sequence plus two steps toward the T after each shot |
| 14 | Ghosting: six points | 3 | fast, 5 × 20 s, 20 s rest |
| 15 | Cool-down | 2 | |

### Session B: Volley & Front Court

| # | Drill | Min | Notes |
|---|---|---|---|
| 1 | Movement warm-up | 3 | |
| 2 | Side-to-side volleys | 3 | |
| 3 | Figure of eight with a bounce | 3 | Ball hits the front wall high, then the side wall, then bounces. Alternate sides |
| 4 | Forehand to backhand volleys, stepping back | 3 | Start about 2 m from the front wall and drift back toward the short line |
| 5 | Ghosting: volley positions | 3 | medium, plus a "middle" T-volley call if added |
| 6–7 | FH / BH high volley to length | 2 + 2 | Hit a high straight ball to yourself, then volley it deep from the back of the box. This rehearses volleying off the serve |
| 8 | Ghosting: front corners with drops | 3 | fast |
| 9 | Cross-court drop rally | 3 | Front court: FH drop across to the BH side, move, BH drop back |
| 10–11 | FH / BH boast then counter-drop | 2 + 2 | Feed to mid court. Boast low and early on the side wall so it lands mid front wall. Run in and drop it |
| 12 | Serve then volley | 3 | Lob serve from one box, then cross to the receiving side and volley the serve straight to length before it reaches the back. This is volleying off the serve from the receiver's side |
| 13 | Ghosting: six points | 3 | fast |
| 14 | Cool-down | 2 | |

### Phase 2 mastery test

| Test | Target |
|---|---|
| Channel drives inside the door width | 10 in a row each side |
| Figure of eight with a bounce | 30 in a row |
| Solo boast and drive | 6 cycles without a break |
| Cross-court drop rally | 10 drops |
| Ghosting | Fast block with 20 s rest, form holding |

## Phase 3: Apply (outline)

**Aim:** decisions and match transfer.
- **Decision feeds.** New audio feature: the voice calls *"Easy"* or *"Pressure"* at random before each feed.
  - Easy: soft feed, step back, step in, and play a forcing shot (drive under the service line, drop, or cross court).
  - Pressure: deep or hard feed, then a safe straight drive to length.
- **Figure of eight volleys.** Progress from a bounce, to volleys near the front wall, to stepping back.
- **Boast, drive and drop circuit.** Solo continuous movement around the court.
- **Match-intensity ghosting.** A new `match` pace, 6 to 8 rounds of 20 s, with shot-type calls ("Volley", "Boast", "Drop").
- **Anchoring thoughts.** The session intro states the two current anchors. A short "match block" asks the player to say them aloud before each round.

## Building a new phase

1. In `drills.py`, write `PHASE2_A` and `PHASE2_B` dicts like `PHASE1_A`, reusing the helper functions (`drives`, `ghost`, `warmup` and the rest) where they fit, and append them to `SESSIONS`.
2. Run `.venv/bin/python build.py phase2-a phase2-b`. With no arguments, it builds every session.
   Each session produces `out/<id>.mp3` with its `.srt` subtitles, `.txt` schedule, `.ffmeta` chapters and `.jpg` cover.
3. The build aborts if cues overlap. Shorten the text or move the offsets.

`HANDOFF.md` covers the technical details of the audio pipeline.
