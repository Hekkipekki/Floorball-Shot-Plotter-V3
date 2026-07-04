"""Shared styling helpers for the embedded video player."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

VIDEO_BG = "#0b0f14"
PANEL_BG = "#111820"
PANEL_BG_SOFT = "#17212b"
TEXT = "#f4f7fa"
MUTED = "#aab4bf"
CONTROL_ACTIVE_BG = "#263646"
CONTROL_BORDER = "#253445"
TIMELINE_TROUGH = "#2a3542"

CONTROL_BUTTON_PAD_X = 10
CONTROL_BUTTON_PAD_Y = 4
CONTROL_BUTTON_FONT = ("Segoe UI", 9, "bold")
CONTROL_BUTTON_CURSOR = "hand2"


def create_control_button(parent: tk.Misc, text: str, command: Callable[[], None]) -> tk.Button:
    """Create a standard video-player control button."""
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=PANEL_BG_SOFT,
        fg=TEXT,
        activebackground=CONTROL_ACTIVE_BG,
        activeforeground=TEXT,
        bd=0,
        padx=CONTROL_BUTTON_PAD_X,
        pady=CONTROL_BUTTON_PAD_Y,
        font=CONTROL_BUTTON_FONT,
        cursor=CONTROL_BUTTON_CURSOR,
    )
