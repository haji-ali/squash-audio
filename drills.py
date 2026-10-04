import random

VOICE = "en-GB-RyanNeural"
RATE = "+0%"

# Tone markers usable in place of cue text.
ARRIVE = "<arrive>"  # ghosting: you should be at the position and swinging now
TICK = "<tick>"      # countdown tick before a ghosting round restarts

ALL = ("Front left", "Front right", "Middle left", "Middle right", "Back left", "Back right")
FRONT = ALL[0:2]
MIDDLE = ALL[2:4]
BACK = ALL[4:6]

# Spoken length of a position call; build.py aborts if a call clip runs longer.
CALL_SECS = 0.85

# Seconds from the end of a call to the arrival beep, then from the beep to the next call.
# Front is the longest run; back is shorter but needs a turn; middle is one or two steps.
PACES = {
    "easy":   {"front": (1.0, 2.2), "middle": (1.0, 2.2), "back": (1.0, 2.2)},
    "slow":   {"front": (2.6, 3.0), "middle": (1.6, 2.2), "back": (2.4, 2.8)},
    "medium": {"front": (2.1, 2.4), "middle": (1.3, 1.7), "back": (1.9, 2.2)},
    "fast":   {"front": (1.7, 2.0), "middle": (1.0, 1.4), "back": (1.5, 1.8)},
}
# rounds, work seconds, rest seconds; each fits a three-minute block.
ROUNDS = {"slow": (3, 45, 20), "medium": (3, 40, 25), "fast": (4, 25, 25)}
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
    cues, _ = calls(ALL, "easy", 64, 176, random.Random(seed))
    return d("Movement warm-up", 180,
             "One minute of easy movement: jog, side-step and lunge around the court. "
             "Then I'll call positions. Split step at the T, take two steps toward the call, and come back.",
             (40, "Open and close the hips."),
             (60, "Back to the T. Split steps now."),
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
    "Stand in the middle, a step in front of the short line. Gentle forehand across to your backhand, "
    "backhand back across. Let each ball bounce once.",
    (15, "Easy. This warms the ball."),
    (75, "Racket up between every shot."),
    (140, "Finish each swing toward the front wall."))

COOL_DOWN = d(
    "Cool-down", 120,
    "Easy side-to-side, let it bounce. Then stretch.",
    (15, "Nice and easy. Breathe out."),
    (60, "Put the ball down. Stretch calves, hips and shoulders."),
    ten=False)

FAST_SIX = dict(
    pace="fast", positions=ALL,
    intro="Fast pace. Four rounds of twenty-five seconds, all six positions. "
          "Split step on every call, swing on the beep, and sprint back to the T.",
    tips=("Stay engaged. Low and wide at the T.",
          "Feet pointing forward. Knees bent.",
          "Last round. Stay engaged."))


def drives(side, wall_tip, mid_tip):
    return d(
        f"{side.capitalize()} straight drives", 180,
        f"{side.capitalize()} side, a racket length off the side wall, just behind the short line. "
        "Medium-pace drives that bounce at the back of the service box and come back to you. "
        "This one is about control, so stay behind the ball. No T.",
        (20, wall_tip),
        (75, mid_tip),
        (130, "Grip. Prep. Rotate. Swish. Follow."))


def feed_and_step(side, mid_tip):
    return d(
        f"{side.capitalize()} feed and step in", 180,
        f"{side.capitalize()} side. From behind the short line, tap a soft, high feed to the front wall "
        "so it lands around the short line. Move behind it, feet facing the side wall, stomp your front foot, "
        "and drive it deep into the back corner. Let it go, collect it, and feed again.",
        (20, "Get behind the ball."),
        (75, mid_tip),
        (130, "Second bounce near the back wall."))


def drive_and_recover(side):
    return d(
        f"{side.capitalize()} drive and recover", 120,
        f"{side.capitalize()} side, behind the short line. Hit higher, softer straight drives to buy time. "
        "After each one, push two steps toward the T, then move back in behind the ball. The recovery is the drill.",
        (20, "Shot. Two steps. Back in."),
        (70, "Rushed? Hit higher and softer."))


def three_shot(side):
    return d(
        f"{side.capitalize()} three-shot sequence", 120,
        f"{side.capitalize()} side. Three straight drives in order. One, soft: it lands in the service box. "
        "Two, medium: it lands behind the service box. Three, hard and low, under the service line, "
        "so it comes off the back wall. Then start again.",
        (20, "Soft. Medium. Hard."),
        (70, "Same preparation every time. Only the swing speed changes."))


def short_volleys(side, first, second):
    return d(
        f"{side.capitalize()} short volleys", 120,
        f"{side.capitalize()} side, one step in front of the short line, close to the side wall. "
        "Volley straight, aiming just above the service line. Lose it? Let it bounce once and carry on.",
        (15, first),
        (60, second))


def box_volleys(side, first, second):
    return d(
        f"{side.capitalize()} box volleys", 120,
        f"{side.capitalize()} side, at the back of the service box. Volley straight at medium pace, "
        "above the service line, so it comes back at shoulder height. Lose it? Let it bounce and carry on.",
        (15, first),
        (60, second))


def drops(side):
    return d(
        f"{side.capitalize()} drops", 120,
        f"{side.capitalize()} side, in front of the short line, close to the side wall. "
        "Feed a soft ball, let it bounce, and play a straight drop just above the tin. "
        "Keep it going: drop, bounce, drop.",
        (15, "Open face. Soft hands."),
        (60, "Step in with your front foot. Stay low."))


def length_check(side):
    return d(
        f"{side.capitalize()} length check", 120,
        f"{side.capitalize()} side, behind the short line. Straight drives to length. "
        "Count how many in a row land behind the short line.",
        (20, "Racket up early. Finish high."),
        (70, "Count them. Beat your best."))


PHASE1_A = dict(
    id="phase1-a",
    title="Squash solo - Phase 1 A: Drive & Move",
    subtitle="Phase 1  ·  A  ·  Drive & Move",
    intro="Phase one, session A. Drive and move. "
          "In ghosting, I call a position. Swing on the beep, then back to the T. First drill coming up.",
    outro="That's session A. Well done.",
    drills=[
        warmup(seed=11),
        SIDE_TO_SIDE,
        drives("forehand", "Racket up as the ball leaves the front wall.", "Finish high, pointing at the front wall."),
        drives("backhand", "Racket up early. No wrist twist.", "Use the space. Don't crowd the ball."),
        ghost("Ghosting: back corners", "slow", BACK,
              "Slow pace. Three rounds of forty-five seconds. Back left or back right. "
              "Go via the corner of the service box, swing on the beep, then back to the T.",
              ("Plant at forty-five degrees. Full swish.", "Fast back to the T. Split step."), seed=12),
        feed_and_step("forehand", "Stomp, and let your weight go forward."),
        feed_and_step("backhand", "Racket away from your body. Rotate."),
        ghost("Ghosting: front corners", "medium", FRONT,
              "Medium pace. Three rounds of forty seconds. Front left or front right. "
              "Lunge closed: left foot forward on the right, right foot forward on the left. Swing on the beep.",
              ("Racket up before you leave the T.", "Push back hard from the lunge."), seed=13),
        drive_and_recover("forehand"),
        drive_and_recover("backhand"),
        three_shot("forehand"),
        three_shot("backhand"),
        ghost("Ghosting: six points", seed=14, **FAST_SIX),
        COOL_DOWN,
    ])

PHASE1_B = dict(
    id="phase1-b",
    title="Squash solo - Phase 1 B: Volley & Front Court",
    subtitle="Phase 1  ·  B  ·  Volley & Front Court",
    intro="Phase one, session B. Volleys and the front court. "
          "In ghosting, I call a position. Swing on the beep, then back to the T. First drill coming up.",
    outro="That's session B. Well done.",
    drills=[
        warmup(seed=21),
        SIDE_TO_SIDE,
        short_volleys("forehand", "Racket high. Punch, don't swing.", "Shoulders to the side wall."),
        short_volleys("backhand", "Racket high. Punch, then extend up.", "Firm wrist."),
        ghost("Ghosting: volley positions", "slow", MIDDLE,
              "Slow pace. Three rounds of forty-five seconds. Middle left or middle right. "
              "Take the volley on the beep, open or closed stance, then back to the T.",
              ("Racket up, ready for the volley.", "Backhand in an open stance? Rotate more."), seed=22),
        d("Forehand to backhand volleys", 180,
          "Stand in the middle, about two metres from the front wall. Forehand across to your backhand, "
          "backhand back across. For the first half, let it bounce.",
          (15, "Short swings. Racket up early."),
          (90, "Now on the volley. Lose it? Restart with a bounce."),
          (140, "Keep the rhythm. Watch the ball.")),
        box_volleys("forehand", "Racket above the ball. Come down on it.", "Follow through to the front wall."),
        box_volleys("backhand", "Racket high. Punch.", "Shoulders to the side wall."),
        ghost("Ghosting: front corners with drops", "medium", FRONT,
              "Medium pace. Three rounds of forty seconds. Front left or front right. "
              "On the beep, lunge closed and play a short, soft shadow drop. Then back to the T.",
              ("Racket up early. Open face.", "Stay low through the lunge."), seed=23),
        drops("forehand"),
        drops("backhand"),
        d("Serve then T", 180,
          "Serve from the right box. As you hit, move to the T and split step, ready to volley the return. "
          "Collect the ball and serve again. Switch boxes halfway.",
          (15, "Aim just left of centre, so it touches the side wall."),
          (90, "Switch to the left box. Aim just right of centre."),
          (130, "Split step. Ready to volley.")),
        length_check("forehand"),
        length_check("backhand"),
        ghost("Ghosting: six points", seed=24, **FAST_SIX),
        COOL_DOWN,
    ])

SESSIONS = [PHASE1_A, PHASE1_B]
