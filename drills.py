import random

VOICE = "en-GB-RyanNeural"
RATE = "+10%"

# Tone markers usable in place of cue text.
ARRIVE = "<arrive>"  # ghosting: you should be at the position and swinging now
TICK = "<tick>"      # countdown tick before a ghosting round restarts

ALL = ("Front left", "Front right", "Middle left", "Middle right", "Back left", "Back right")
FRONT = ALL[0:2]
MIDDLE = ALL[2:4]
BACK = ALL[4:6]

# Spoken length of a position call; build.py aborts if a call clip runs longer.
CALL_SECS = 0.8

# Seconds from the end of a call to the arrival beep, then from the beep to the next call.
# Front is the longest run; back is shorter but needs a turn; middle is one or two steps.
PACES = {
    "easy":   {"front": (1.0, 2.2), "middle": (1.0, 2.2), "back": (1.0, 2.2)},
    "slow":   {"front": (2.6, 3.0), "middle": (1.6, 2.2), "back": (2.4, 2.8)},
    "medium": {"front": (2.1, 2.4), "middle": (1.3, 1.7), "back": (1.9, 2.2)},
    "fast":   {"front": (1.7, 2.0), "middle": (1.0, 1.4), "back": (1.5, 1.8)},
}
# rounds, work seconds, rest seconds; each fits a three-minute block.
ROUNDS = {"slow": (3, 49, 15), "medium": (3, 46, 15), "fast": (4, 32, 15)}
GHOST_SECS = 180


def d(name, secs, intro, *cues, ten=True):
    return dict(name=name, secs=secs, intro=intro, cues=list(cues), ten=ten)


def calls(positions, pace, start, end, rng):
    """Position calls with arrival beeps between start and end. Returns (cues, time back at the T)."""
    cues, t, prev = [], start, []
    while True:
        if len(positions) > 2:
            options = [p for p in positions if prev[-1:] != [p]]
        else:
            options = [p for p in positions if prev[-2:] != [p, p]]
        pos = rng.choice(options)
        to, back = PACES[pace][pos.split()[0].lower()]
        arrive = CALL_SECS + to
        if t + arrive + back > end:
            return cues, t
        cues += [(t, pos), (t + arrive, ARRIVE)]
        prev.append(pos)
        t += arrive + back


def warmup(seed):
    cues, _ = calls(ALL, "easy", 124, 236, random.Random(seed))
    return d("Movement warm-up", 240,
             "Two minutes of moves as I call them, then split step at the T and take two steps toward each call.",
             (1, "Jog round the court."),
             (20, "Side-steps."),
             (40, "Lunges, alternating legs."),
             (60, "Open and close the hips."),
             (80, "High knees."),
             (100, "Arm circles, both directions."),
             (120, "Back to the T. Split steps now."),
             *cues, ten=False)


def ghost(name, pace, positions, intro, tips, seed):
    rounds, work, rest = ROUNDS[pace]
    rng = random.Random(seed)
    cues = []
    for r in range(rounds):
        s = 1.0 + r * (work + rest)
        if r:
            cues += [(s - k, TICK) for k in (3, 2, 1)]
        round_cues, back = calls(positions, pace, s, s + work, rng)
        cues += round_cues
        if r < rounds - 1:
            cues.append((back, f"Rest. {tips[r]}"))
    assert 1.0 + rounds * work + (rounds - 1) * rest <= GHOST_SECS
    return d(name, GHOST_SECS, intro, *cues, ten=False)


SIDE_TO_SIDE = d(
    "Side-to-side warm-up", 180,
    "From the middle, a step in front of the short line, gentle cross-courts from forehand to backhand, "
    "letting each ball bounce.",
    (15, "Easy. This warms the ball."),
    (75, "Racket up between every shot."),
    (140, "Finish each swing toward the front wall."))

COOL_DOWN = d(
    "Cool-down", 180,
    "Easy side-to-side, then the stretches as I call them.",
    (5, "Nice and easy. Breathe out."),
    (45, "Ball down. Calf stretch, left leg back."),
    (67, "Switch legs."),
    (90, "Hip stretch. Long lunge, left leg back."),
    (112, "Switch legs."),
    (135, "Shoulder stretch. Left arm across."),
    (157, "Switch arms."),
    ten=False)

FAST_SIX = dict(
    pace="fast", positions=ALL,
    intro="Fast pace, all six positions. Split step on every call, swing on the beep, "
          "and sprint back to the T for the next call.",
    tips=("Stay engaged. Low and wide at the T.",
          "Feet pointing forward. Knees bent.",
          "Last round. Stay engaged."))


def drives(side, wall_tip, mid_tip):
    return d(
        f"{side.capitalize()} straight drives", 180,
        "A racket length off the side wall, just behind the short line. Medium pace, bouncing at the back "
        "of the service box and coming back to you. This one is control, so stay behind the ball, no T.",
        (20, wall_tip),
        (75, mid_tip),
        (130, "Grip. Prep. Rotate. Swish. Follow."))


def feed_and_step(side, mid_tip):
    return d(
        f"{side.capitalize()} feed and step in", 180,
        "From behind the short line, tap a soft, high feed so it lands near the short line. Get behind it, "
        "feet facing the side wall, stomp your front foot, and drive deep into the back corner.",
        (20, "Get behind the ball."),
        (75, mid_tip),
        (130, "Second bounce near the back wall."))


def drive_and_recover(side):
    return d(
        f"{side.capitalize()} drive and recover", 120,
        "Behind the short line, higher, softer straight drives to buy time. After each one, push two steps "
        "toward the T and back in behind the ball. The recovery is the drill.",
        (20, "Shot. Two steps. Back in."),
        (70, "Rushed? Hit higher and softer."))


def three_shot(side):
    return d(
        f"{side.capitalize()} three-shot sequence", 120,
        "Straight drives in turn: soft into the service box, medium behind it, then hard and low, "
        "under the service line, so it comes off the back wall.",
        (20, "Soft. Medium. Hard."),
        (70, "Same preparation every time. Only the swing speed changes."))


def short_volleys(side, first, second):
    return d(
        f"{side.capitalize()} short volleys", 120,
        "A step in front of the short line, close to the side wall, volleying straight just above "
        "the service line. Let it bounce if you lose it.",
        (15, first),
        (60, second))


def box_volleys(side, first, second):
    return d(
        f"{side.capitalize()} box volleys", 120,
        "From the back of the service box, medium pace, above the service line, so it comes back "
        "at shoulder height. Let it bounce if you lose it.",
        (15, first),
        (60, second))


def drops(side):
    return d(
        f"{side.capitalize()} drops", 120,
        "In front of the short line, close to the side wall. Feed softly, then drop, let it bounce, "
        "and drop again, just above the tin.",
        (15, "Open face. Soft hands."),
        (60, "Step in with your front foot. Stay low."))


def length_check(side):
    return d(
        f"{side.capitalize()} length check", 120,
        "Straight drives to length from behind the short line. Count how many in a row land behind it.",
        (20, "Racket up early. Finish high."),
        (70, "Count them. Beat your best."))


PHASE1_A = dict(
    id="phase1-a",
    title="Squash solo - Phase 1 A: Drive & Move",
    subtitle="Phase 1  ·  A  ·  Drive & Move",
    intro="Phase one, session A: drive and move.",
    outro="That's session A. Well done.",
    drills=[
        warmup(seed=11),
        SIDE_TO_SIDE,
        drives("forehand", "Racket up as the ball leaves the front wall.", "Finish high, pointing at the front wall."),
        drives("backhand", "Racket up early. No wrist twist.", "Use the space. Don't crowd the ball."),
        ghost("Ghosting: back corners", "slow", BACK,
              "Slow pace. Go via the corner of the service box, swing on the beep, and get back to the T for the next call.",
              ("Plant at forty-five degrees. Full swish.", "Fast back to the T. Split step."), seed=12),
        feed_and_step("forehand", "Stomp, and let your weight go forward."),
        feed_and_step("backhand", "Racket away from your body. Rotate."),
        d("Front-court drives", 180,
          "A step in front of the short line, a racket length off the forehand wall. Straight drives to length, "
          "turning your shoulders more than feels natural. Switch to the backhand halfway.",
          (15, "Go around the ball, not at it."),
          (60, "Rotate. Finish high, to the front wall."),
          (90, "Switch to the backhand wall."),
          (140, "Racket away from your body. Use the space.")),
        ghost("Ghosting: front corners", "medium", FRONT,
              "Medium pace. Lunge closed, left foot forward on the right and right foot forward on the left. "
              "Swing on the beep, and get back to the T for the next call.",
              ("Racket up before you leave the T.", "Push back hard from the lunge."), seed=13),
        drive_and_recover("forehand"),
        drive_and_recover("backhand"),
        ghost("Ghosting: middle and back", "medium", MIDDLE + BACK,
              "Medium pace. Back corners via the box corner, middle open or closed. "
              "Swing on the beep, and get back to the T for the next call.",
              ("Plant at forty-five degrees at the back.", "Split step on every call."), seed=15),
        three_shot("forehand"),
        three_shot("backhand"),
        ghost("Ghosting: six points", seed=14, **FAST_SIX),
        COOL_DOWN,
    ])

PHASE1_B = dict(
    id="phase1-b",
    title="Squash solo - Phase 1 B: Volley & Front Court",
    subtitle="Phase 1  ·  B  ·  Volley & Front Court",
    intro="Phase one, session B: volleys and the front court.",
    outro="That's session B. Well done.",
    drills=[
        warmup(seed=21),
        SIDE_TO_SIDE,
        short_volleys("forehand", "Racket high. Punch, don't swing.", "Shoulders to the side wall."),
        short_volleys("backhand", "Racket high. Punch, then extend up.", "Firm wrist."),
        ghost("Ghosting: volley positions", "slow", MIDDLE,
              "Slow pace. Volley on the beep, open or closed stance, and get back to the T for the next call.",
              ("Racket up, ready for the volley.", "Backhand in an open stance? Rotate more."), seed=22),
        d("Forehand to backhand volleys", 180,
          "In the middle, two metres from the front wall: forehand across to your backhand, backhand back across. "
          "Let it bounce for the first half.",
          (15, "Short swings. Racket up early."),
          (90, "Now on the volley. Lose it? Restart with a bounce."),
          (140, "Keep the rhythm. Watch the ball.")),
        box_volleys("forehand", "Racket above the ball. Come down on it.", "Follow through to the front wall."),
        box_volleys("backhand", "Racket high. Punch.", "Shoulders to the side wall."),
        d("Volley heights", 180,
          "A step in front of the short line, close to the forehand wall. Three straight volleys in turn: "
          "just above the service line, on it, then just above the tin. Switch to the backhand halfway.",
          (15, "Above the line. On the line. Above the tin."),
          (60, "Same punch every time. Only the target changes."),
          (90, "Switch to the backhand wall."),
          (140, "Racket high. Firm wrist.")),
        ghost("Ghosting: front corners with drops", "medium", FRONT,
              "Medium pace. Lunge closed and play a soft shadow drop on the beep, then get back to the T "
              "for the next call.",
              ("Racket up early. Open face.", "Stay low through the lunge."), seed=23),
        drops("forehand"),
        drops("backhand"),
        d("Serve then T", 180,
          "Start in the right box. After each serve, move to the T and split step, ready to volley the return. "
          "Switch boxes halfway.",
          (15, "Aim just left of centre, so it touches the side wall."),
          (90, "Switch to the left box. Aim just right of centre."),
          (130, "Split step. Ready to volley.")),
        length_check("forehand"),
        length_check("backhand"),
        ghost("Ghosting: six points", seed=24, **FAST_SIX),
        COOL_DOWN,
    ])

SESSIONS = [PHASE1_A, PHASE1_B]
