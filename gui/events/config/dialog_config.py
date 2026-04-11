# --- Dialog content (WHAT) ---

PHASE_OPTIONS = {
    "Full Court press": "Trying to activate from the normal entry defense, up to a full court press.",
    "Zone entry defense": "The team is playing the normal defense system, trying to prevent the opponent from playing a zone entry with quality.",
    "Zone Defense": "You are trying to defend after the opponent has settled in playing zone offense.",
    "Zone Exit": "The opponent activates counter-press after you have won the ball in your own zone.",
    "Counter on counter": "When a team counters after having won the ball from the opponent's counter-attack.",
    "Uncontrolled": "When a situation cannot be placed under any other game situation.",
}
PHASE_DIALOG_SIZE = (265, 350)


SITUATION_OPTIONS = {
    "Breakaway": "Attacker breaks through alone on the goalkeeper.",
    "2v0": "Two attackers against the goalkeeper without defenders.",
    "2v1": "Two attackers versus one defender.",
    "3v1": "Three attackers versus one defender.",
    "3v2": "Three attackers versus two defenders.",
    "Rebound": "Shot opportunity following a saved or blocked shot.",
    "Penalty Shot": "Awarded direct shot from penalty mark.",
    "Free shot": "No pressure or game system affects this situation.",
}
SITUATION_DIALOG_SIZE = (265, 370)


SHOT_TYPE_OPTIONS = {
    "One-timer": "A direct shot taken immediately after receiving the ball.",
    "Controlled shot": "A composed, aimed shot with time and balance.",
    "Own Goal": "Shot directed by defending team into their own net.",
    "Deke": "A deceptive move to fake out the goalie before shooting.",
    "Deflection": "A shot redirected by a player’s stick or body after an initial shot or pass.",
    "Penalty Shot": "Awarded direct shot from penalty mark.",
    "Free shot": "Direct Shot, no passes.",
}
SHOT_TYPE_DIALOG_SIZE = (265, 320)


HAND_OPTIONS = {
    "Left": "Stick on left side.",
    "Right": "Stick on right side.",
}
HAND_DIALOG_SIZE = (265, 150)


PASS_ORIGIN_DIALOG_SIZE = (300, 120)