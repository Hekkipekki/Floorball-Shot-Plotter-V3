from __future__ import annotations

XG_CONTEXT_DEFAULTS = {
    "strength_state": "5v5",
    "chance_type": "Possession",
    "screen": "Clear sight",
    "pressure": "Low pressure",
    "goalie_state": "Set",
    "period_time": "",
}

STRENGTH_OPTIONS = ("5v5", "Power play against", "Shorthanded chance against", "6v5 against", "Empty net against", "Penalty shot")
CHANCE_TYPE_OPTIONS = ("Possession", "Rush", "Turnover", "Breakaway", "Set play", "Rebound", "Scramble")
SCREEN_OPTIONS = ("Clear sight", "Partial screen", "Full screen")
PRESSURE_OPTIONS = ("No pressure", "Low pressure", "High pressure")
GOALIE_STATE_OPTIONS = ("Set", "Moving", "Out of position")


def normalize_xg_context(context: dict | None) -> dict:
    normalized = dict(XG_CONTEXT_DEFAULTS)
    if isinstance(context, dict):
        for key in normalized:
            value = context.get(key)
            if value not in (None, ""):
                normalized[key] = str(value)
    return normalized


def infer_xg_context_defaults(phase: str = "", situation: str = "", shot_type: str = "") -> dict:
    text = f"{phase} {situation} {shot_type}".lower()
    context = dict(XG_CONTEXT_DEFAULTS)

    if "power play" in text:
        context["strength_state"] = "Power play against"
    elif "shorthanded" in text or "box play" in text:
        context["strength_state"] = "Shorthanded chance against"
    elif "6v5" in text or "goalie pulled" in text:
        context["strength_state"] = "6v5 against"
    elif "empty net" in text:
        context["strength_state"] = "Empty net against"
    elif "penalty" in text:
        context["strength_state"] = "Penalty shot"

    if "breakaway" in text:
        context["chance_type"] = "Breakaway"
    elif "rush" in text or "transition" in text or "counter" in text or "entry" in text:
        context["chance_type"] = "Rush"
    elif "turnover" in text or "intercept" in text or "failed zone exit" in text:
        context["chance_type"] = "Turnover"
    elif "free hit" in text or "faceoff" in text or "set play" in text or "free shot" in text:
        context["chance_type"] = "Set play"
    elif "rebound" in text:
        context["chance_type"] = "Rebound"
    elif "scramble" in text or "loose ball" in text or "broken" in text:
        context["chance_type"] = "Scramble"

    if "screen" in text or "traffic" in text:
        context["screen"] = "Partial screen"
    if "full screen" in text or "goalkeeper screened" in text:
        context["screen"] = "Full screen"

    if "breakaway" in text or "cross-pass" in text or "cross pass" in text or "deke" in text:
        context["goalie_state"] = "Moving"
    if "empty net" in text:
        context["goalie_state"] = "Out of position"

    if "pressure" in text:
        context["pressure"] = "High pressure"

    return context
