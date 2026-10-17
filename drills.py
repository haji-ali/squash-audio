import random

RATE = "+10%"

# Tone markers usable in place of cue text.
ARRIVE = "<arrive>"  # ghosting: you should be at the position and swinging now
TICK = "<tick>"      # countdown tick before a ghosting round restarts

ALL = ("Front left", "Front right", "Middle left", "Middle right", "Back left", "Back right")
FRONT = ALL[0:2]
MIDDLE = ALL[2:4]
BACK = ALL[4:6]
STANCE_MIDDLE = tuple(f"{s}, {p.lower()}." for p in MIDDLE for s in ("Open", "Closed"))

# Time allowed for each position call when fitting calls into a round.
CALL_SECS = {**{p: 0.8 for p in ALL}, **{p: 1.45 for p in STANCE_MIDDLE}}

# Seconds from the end of a call to the arrival beep, then from the beep to the next call.
# Front is the longest run; back is shorter but needs a turn; middle is one or two steps.
PACES = {
    "easy":   {"front": (1.0, 2.2), "middle": (1.0, 2.2), "back": (1.0, 2.2)},
    "slow":   {"front": (2.6, 3.0), "middle": (1.6, 2.2), "back": (2.4, 2.8)},
    "medium": {"front": (2.1, 2.4), "middle": (1.3, 1.7), "back": (1.9, 2.2)},
    "fast":   {"front": (1.7, 2.0), "middle": (1.0, 1.4), "back": (1.5, 1.8)},
}
# An open-stance call is a rushed ball: seconds taken off the time to the pip.
OPEN_HURRY = 0.5
# rounds, work seconds, rest seconds; each fits a three-minute block.
ROUNDS = {"slow": (3, 49, 15), "medium": (3, 46, 15), "fast": (4, 32, 15)}
GHOST_SECS = 180


def d(name, secs, intro, *cues, ten=True, say_secs=True):
    return dict(name=name, secs=secs, intro=intro, cues=list(cues), ten=ten, say_secs=say_secs)


def calls(positions, pace, start, end, rng):
    """Position calls with arrival beeps between start and end. Returns (cues, time back at the T)."""
    cues, t, prev = [], start, []
    while True:
        if len(positions) > 2:
            options = [p for p in positions if prev[-1:] != [p]]
        else:
            options = [p for p in positions if prev[-2:] != [p, p]]
        pos = rng.choice(options)
        to, back = PACES[pace][pos.split()[-2].lower()]
        if pos.startswith("Open"):
            to -= OPEN_HURRY
        arrive = CALL_SECS[pos] + to
        if t + arrive + back > end:
            return cues, t
        cues += [(t, pos), (t + arrive, ARRIVE)]
        prev.append(pos)
        t += arrive + back


def warmup(seed):
    cues, _ = calls(ALL, "easy", 124, 236, random.Random(seed))
    return d("Movement warm-up", 240,
             # The voice reduces "four" in "four minutes" to "for", so the intro gives the two halves instead.
             "Two minutes of moves as I call them, then two minutes of split steps at the T, taking two steps "
             "toward each call.",
             (1, "Jog round the court."),
             (20, "Side-steps."),
             (40, "Lunges, alternating legs."),
             (60, "Open and close the hips."),
             (80, "High knees."),
             (100, "Arm circles, both directions."),
             (120, "Back to the T. Split steps now."),
             *cues, ten=False, say_secs=False)


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


FIGURE_OF_EIGHT = d(
    "Figure of eight warm-up", 180,
    "In the middle, a step in front of the short line, facing the front wall. Front wall only: aim around "
    "the service line, just across from centre, so the ball comes back to your other side: forehand, "
    "backhand, forehand, letting each ball bounce once in front of you.",
    (15, "Easy. This warms the ball."),
    (75, "Racket up between every shot."),
    (140, "Follow through forward, not across your body."))

COOL_DOWN = d(
    "Cool-down", 180,
    "Easy figure of eight, then the stretches as I call them.",
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
    intro="Fast pace, all six positions. Phase two target: every rep at the beep with a full swish, "
          "and form that holds to the last round. Split step on every call, swing on the beep, "
          "and sprint back to the T for the next call.",
    tips=("Stay engaged. Low and wide at the T.",
          "Feet pointing forward. Knees bent.",
          "Last round. Stay engaged."))


def drives(side, wall_tip, mid_tip):
    return d(
        f"{side.capitalize()} straight drives", 180,
        "A racket length off the side wall, at the back of the service box. Medium pace, just above the "
        "service line, with the first bounce in the service box, so it comes up to you. This one is control, "
        "so stay behind the ball, no T.",
        (20, wall_tip),
        (75, mid_tip),
        (105, "Lost the rhythm? Higher and softer to reset."),
        (130, "Grip. Prep. Rotate. Swish. Follow."))


def feed_and_step(side, mid_tip):
    return d(
        f"{side.capitalize()} feed and step in", 180,
        "From behind the short line, tap a soft, high feed so it lands near the short line. Get behind it, "
        "feet facing the side wall, stomp your front foot, and drive deep: a racket head above the service line, "
        "first bounce behind the service box. Score each set of ten. Phase two target: seven out of ten with the "
        "second bounce at the back wall, misses in between allowed.",
        (20, "Get behind the ball."),
        (75, mid_tip),
        (130, "Target: seven out of ten to the back wall."))


def drive_and_recover(side):
    return d(
        f"{side.capitalize()} drive and recover", 120,
        "Behind the short line, higher, softer straight drives to buy time: a racket length above the service "
        "line, first bounce at the back of the service box. After each one, push two steps toward the T and "
        "back in behind the ball. The recovery is the drill.",
        (20, "Shot. Two steps. Back in."),
        (70, "Rushed? Hit higher and softer."))


def front_court_drives(side, mid_tip):
    return d(
        f"{side.capitalize()} front-court drives", 120,
        "A step in front of the short line, a racket length off the side wall. Straight drives to length, "
        "a racket head above the service line with the first bounce behind the service box, turning your "
        "shoulders more than feels natural.",
        (15, "Go around the ball, not at it."),
        (70, mid_tip))


def three_shot(side):
    return d(
        f"{side.capitalize()} three-shot sequence", 120,
        "Straight drives in turn. Soft, on the service line, bouncing in the service box. Medium, a racket "
        "head above it, bouncing behind the box. Then hard, just under the service line, so it comes off "
        "the back wall.",
        (20, "Soft. Medium. Hard."),
        (70, "Same preparation every time. Only the swing speed changes."))


def short_volleys(side, first, second):
    return d(
        f"{side.capitalize()} short volleys", 120,
        "A step in front of the short line, close to the side wall, volleying straight just above "
        "the service line, so it comes back to you at shoulder height without bouncing. "
        "Let it bounce if you lose it.",
        (15, first),
        (60, second))


def box_volleys(side, first, second):
    return d(
        f"{side.capitalize()} box volleys", 120,
        "From the back of the service box, medium pace, a racket head above the service line, so it comes "
        "back at shoulder height without bouncing. Let it bounce if you lose it. "
        "Phase two target: ten volleys in one rally, without a break.",
        (15, first),
        (60, second))


def volley_heights(side, last_tip):
    return d(
        f"{side.capitalize()} volley heights", 120,
        "A step in front of the short line, close to the side wall. Three straight volleys in turn: "
        "just above the service line, on it, then just above the tin. After the low one, let it bounce and "
        "start again.",
        (15, "Above the line. On the line. Above the tin."),
        (55, "Same punch every time. Only the target changes."),
        (90, last_tip))


def drops(side):
    return d(
        f"{side.capitalize()} drops", 120,
        "Two halves. First, counter-drops: two metres from the front wall, close to the side wall, soft drops "
        "just above the tin, kept going. Then feed from just behind the short line, play one drop, and let it "
        "go. Phase two target: six out of ten with the second bounce before the short line, misses in between "
        "allowed.",
        (15, "Open face. Soft hands."),
        (60, "Now feed, drop, and let it go. Score ten."),
        (90, "Step in with your front foot. Stay low."))


def length_check(side):
    return d(
        f"{side.capitalize()} length check", 120,
        "Straight drives to length from behind the short line: a racket head above the service line, first "
        "bounce behind the service box. Score each set of ten by how many bounce first behind the short line. "
        "Reset with a softer one whenever you need to. Resets don't count. Phase two target: eight out of ten, "
        "misses in between allowed.",
        (20, "Racket up early. Finish high."),
        (70, "Count them. Target: eight out of ten."))


PHASE1_A = dict(
    id="phase1-a",
    title="Squash solo - Phase 1 A: Drive & Move",
    subtitle="Phase 1  ·  A  ·  Drive & Move",
    intro="Phase one, session A: drive and move. Drills with a phase two target say so. "
          "Hit every target in two sessions back to back to move up.",
    outro="That's session A. Well done.",
    drills=[
        warmup(seed=11),
        FIGURE_OF_EIGHT,
        drives("forehand", "Racket up as the ball leaves the front wall.", "Finish high, pointing at the front wall."),
        drives("backhand", "Racket up early. No wrist twist.", "Use the space. Don't crowd the ball."),
        ghost("Ghosting: back corners", "slow", BACK,
              "Slow pace. Go via the corner of the service box, swing on the beep, and get back to the T for the next call.",
              ("Plant at forty-five degrees. Full swish.", "Fast back to the T. Split step."), seed=12),
        feed_and_step("forehand", "Stomp, and let your weight go forward."),
        feed_and_step("backhand", "Racket away from your body. Rotate."),
        front_court_drives("forehand", "Rotate. Finish high, to the front wall."),
        front_court_drives("backhand", "Racket away from your body. Use the space."),
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
    intro="Phase one, session B: volleys and the front court. Drills with a phase two target say so. "
          "Hit every target in two sessions back to back to move up.",
    outro="That's session B. Well done.",
    drills=[
        warmup(seed=21),
        FIGURE_OF_EIGHT,
        short_volleys("forehand", "Racket high. Punch, don't swing.", "Shoulders to the side wall."),
        short_volleys("backhand", "Racket high. Punch, then extend up.", "Firm wrist."),
        ghost("Ghosting: volley positions", "slow", STANCE_MIDDLE,
              "Slow pace, with the stance in each call. Closed is a step across with your far foot. "
              "Open is one step with your near foot, and comes quicker, like a rushed ball. "
              "Volley on the beep, and get back to the T for the next call.",
              ("Racket up, ready for the volley.", "Backhand in an open stance? Rotate more."), seed=22),
        d("Forehand to backhand volleys", 180,
          "In the middle, two metres from the front wall: forehand across to your backhand, backhand back across, "
          "hitting around the service line just off centre. Let it bounce for the first half. "
          "Phase two target: twenty volleys in one rally, without a break.",
          (15, "Short swings. Racket up early."),
          (90, "Now on the volley. Target: twenty without a break. Lose it? Restart with a bounce, and count from zero."),
          (140, "Keep the rhythm. Watch the ball.")),
        box_volleys("forehand", "Racket above the ball. Come down on it.", "Follow through to the front wall."),
        box_volleys("backhand", "Racket high. Punch.", "Shoulders to the side wall."),
        volley_heights("forehand", "Racket above the ball. Come down on it."),
        volley_heights("backhand", "Racket high. Firm wrist."),
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

def length_by_height(side, mid_tip):
    return d(
        f"{side.capitalize()} length by height", 180,
        "Behind the short line, a racket length off the side wall. Straight drives at medium pace, aimed "
        "about a racket head above the service line. Height gives you length without forcing it: first bounce "
        "behind the service box, second bounce near the back wall. When a good one dies in the back, play the "
        "next one higher and softer to get the rally back.",
        (15, "Aim higher, not harder."),
        (60, mid_tip),
        (105, "Hit it level with your front foot. Weight goes forward."),
        (140, "Finish high, to the front wall. Keep the grip relaxed."))


def drop_and_lob(side):
    return d(
        f"{side.capitalize()} drop and lob", 180,
        "On the short line near the side wall, play a soft drop, then move in and lob it before its second "
        "bounce. Get low and under the ball, open the face, and lift it high above the service line so it "
        "lands in the back corner. Collect it and repeat. Straight for the first half, then cross-court.",
        (15, "Get under the ball. Low to high."),
        (55, "Open face. Lift it, don't hit it."),
        (90, "Now cross-court. Aim high, on your half of the front wall."),
        (130, "Clip the side wall high, behind the service box."))


BOAST_AND_LOB = d(
    "Boast and straight lob", 180,
    "Start in the back right corner. Boast to the front left, run in, and lob straight down the left wall. "
    "Then boast from the back left to the front right, and lob straight down the right wall, so every loop "
    "plays both boasts and both lobs. For the first half the lob is the real shot, high and tight so it dies "
    "in the back corner, and the boast is a feed, softer and higher so it sits up at the front. "
    "A lob too good to boast is a win: hand feed and restart.",
    (15, "Racket up as you run. Lob from low to high."),
    (50, "Lob high and tight to the wall. The height is your time to recover."),
    (90, "Swap. The boast is the real shot now, hard and low. The lob is a feed that sits up off the back wall."),
    (130, "Boast angled at the far front corner. Hand feed whenever it breaks."))

BOAST_AND_CROSS = d(
    "Boast and cross-court", 180,
    "Start in the back right corner. Boast so the ball reaches the front left, run after it, and drive it "
    "firmly cross-court, just above the service line on the left half of the front wall, into the back right "
    "corner. Then boast again and keep the loop going. The boast is a feed, soft enough to reach; the "
    "cross-court is the shot. Switch sides halfway. Restart with a hand feed whenever it breaks down.",
    (15, "Width: hit the side wall behind the service box."),
    (50, "Get in front of the ball. Rotate through it."),
    (90, "Switch. Boast from the back left, cross-court from the front right, aiming right of centre."),
    (130, "Wide enough to pass someone standing on the T."))


def length_tired(side):
    return d(
        f"{side.capitalize()} length when tired", 120,
        "Behind the short line, straight drives aimed a racket head above the service line, as earlier. "
        "Tired is when length drops short in a match, so hold the same shot. Score each set of ten by how "
        "many bounce first behind the short line, resetting with a softer one whenever you need to.",
        (20, "Aim higher, not harder."),
        (70, "Racket up early. Count them."))


FOCUS_FRONT = dict(
    id="focus-front",
    title="Squash solo - Focus: Drops, Lobs & Length",
    subtitle="Focus  ·  Drops, Lobs & Length",
    intro="Focus session: drops, lobs and length. Start early to reach the drop, lob to buy time, "
          "and aim higher for length.",
    outro="That's the focus session. Well done.",
    drills=[
        warmup(seed=31),
        FIGURE_OF_EIGHT,
        ghost("Ghosting: split step and go", "slow", FRONT,
              "Slow pace, front corners. Reaching drops is about starting early, not running faster. "
              "Split step as each call starts, push off hard, and lunge closed with the racket already up. "
              "Swing on the beep, and get back to the T for the next call.",
              ("Wait just behind the T, not deep.", "Racket up before you arrive. Stay low in the lunge."),
              seed=32),
        length_by_height("forehand", "Racket up early. Step in and stomp."),
        length_by_height("backhand", "Racket away from your body. Rotate."),
        drop_and_lob("forehand"),
        drop_and_lob("backhand"),
        ghost("Ghosting: front corners with lobs", "medium", FRONT,
              "Medium pace. Lunge closed and play a shadow lob on the beep, face open, swinging low to high "
              "and finishing high. Then get back to the T for the next call.",
              ("Get lower than the ball. Lift through it.", "Push back hard from the lunge."), seed=33),
        BOAST_AND_LOB,
        ghost("Ghosting: back to front", "medium", BACK + FRONT,
              "Medium pace, back and front corners. This is the rally that beats you: pushed deep, then a drop. "
              "Get fully back to the T after every back corner, so the front is in reach. "
              "Swing on the beep, and get back to the T for the next call.",
              ("Don't hang deep. Back to the T every time.", "Split step, then attack the front."), seed=34),
        BOAST_AND_CROSS,
        length_tired("forehand"),
        length_tired("backhand"),
        ghost("Ghosting: drop retrieval", "fast", FRONT + FRONT + MIDDLE + BACK,
              "Fast pace, all six positions, with the front corners called twice as often. Split step on every "
              "call, swing on the beep, and sprint back to the T for the next call.",
              ("Split step as the call starts. Push off early.",
               "Racket up before you arrive.",
               "Last round. Stay engaged."), seed=41),
        COOL_DOWN,
    ])

SESSIONS = [PHASE1_A, PHASE1_B, FOCUS_FRONT]
