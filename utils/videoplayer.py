# utils/videoplayer.py
"""
Modern embedded VLC overlay player for Floorball Shot Plotter.

Features:
- Uses bundled VLC runtime
- Fills the center canvas panel
- Clean bottom controls
- Clickable / draggable timeline
- Start / Stop segment fields
- Sync current video position to Start / Stop
- Play / Pause / Stop
- Loop Segment ON/OFF
- Save Segment callback
- ESC / X close
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from utils.video_player_style import (
    CONTROL_ACTIVE_BG,
    CONTROL_BORDER,
    MUTED,
    PANEL_BG,
    PANEL_BG_SOFT,
    TEXT,
    TIMELINE_TROUGH,
    VIDEO_BG,
    create_control_button,
)
from utils.video_runtime import (
    VLC_IMPORT_ERROR,
    format_time,
    parse_float,
    vlc,
)

CONTROL_PANEL_HEIGHT = 116
CONTROL_PANEL_PAD_X = 12
CONTROL_PANEL_PAD_Y = 8
ENTRY_WIDTH = 7
PLAY_TEXT = "▶"
PAUSE_TEXT = "||"
STOP_TEXT = "⏹"


# ------------------------------------------------------------
# Player
# ------------------------------------------------------------
class VLCOverlayWithControls(tk.Frame):
    BG = VIDEO_BG
    PANEL_BG = PANEL_BG
    PANEL_BG_SOFT = PANEL_BG_SOFT
    TEXT = TEXT
    MUTED = MUTED

    def __init__(
        self,
        master: tk.Misc,
        video_path: str,
        *,
        start: float = 0.0,
        stop: float | None = None,
        autoplay: bool = True,
        app=None,
        on_save_segment=None,
        **kwargs,
    ):
        super().__init__(master, bg=self.BG, **kwargs)

        self.app = app
        self.video_path = video_path
        self.on_save_segment = on_save_segment

        self.start_time = float(start or 0.0)
        self.stop_time = None if stop in ("", None) else float(stop)

        self.loop_segment = tk.BooleanVar(value=True)
        self.user_dragging = False
        self.running = True
        self.duration_seconds = 0.0
        self._was_playing_before_drag = False
        self._segment_end_paused = False

        self.instance = None
        self.player = None

        self._build_ui()
        self._init_vlc()

        self.bind_all("<Escape>", self._on_escape)

        if autoplay:
            self.after(350, self.play)

        self.after(250, self._update_loop)

    # --------------------------------------------------------
    # UI helpers
    # --------------------------------------------------------
    def _create_entry(self, parent: tk.Misc, value: str) -> tk.Entry:
        entry = tk.Entry(
            parent,
            bg=self.PANEL_BG_SOFT,
            fg=self.TEXT,
            insertbackground=self.TEXT,
            relief="flat",
            justify="center",
            font=("Segoe UI", 9),
            width=ENTRY_WIDTH,
        )
        entry.insert(0, value)
        entry.bind("<Return>", lambda _e: self.apply_segment_fields(normalize=True))
        entry.bind("<FocusOut>", lambda _e: self.apply_segment_fields(normalize=True))
        return entry

    def _create_field_label(self, parent: tk.Misc, text: str) -> tk.Label:
        return tk.Label(
            parent,
            text=text,
            bg=self.PANEL_BG,
            fg=self.MUTED,
            font=("Segoe UI", 9, "bold"),
        )

    def _build_timeline_row(self) -> None:
        timeline_row = tk.Frame(self.controls, bg=self.PANEL_BG)
        timeline_row.pack(fill="x", padx=CONTROL_PANEL_PAD_X, pady=(CONTROL_PANEL_PAD_Y, 2))

        self.time_label = tk.Label(
            timeline_row,
            text="00:00 / --:--",
            bg=self.PANEL_BG,
            fg=self.TEXT,
            font=("Segoe UI", 10, "bold"),
            width=14,
            anchor="w",
        )
        self.time_label.pack(side="left", padx=(0, 10))

        self.timeline = tk.Scale(
            timeline_row,
            from_=0,
            to=100,
            orient="horizontal",
            showvalue=False,
            resolution=0.1,
            bg=self.PANEL_BG,
            fg=self.TEXT,
            troughcolor=TIMELINE_TROUGH,
            highlightthickness=0,
            bd=0,
            command=self._on_timeline_drag,
        )
        self.timeline.pack(side="left", fill="x", expand=True)
        self.timeline.bind("<ButtonPress-1>", self._on_timeline_press)
        self.timeline.bind("<B1-Motion>", self._on_timeline_motion)
        self.timeline.bind("<ButtonRelease-1>", self._on_timeline_release)

    def _build_segment_group(self, parent: tk.Misc) -> None:
        segment_group = tk.Frame(parent, bg=self.PANEL_BG)
        segment_group.pack(side="left", padx=(0, 14))

        self._create_field_label(segment_group, "Start").pack(side="left", padx=(0, 5))
        self.start_entry = self._create_entry(segment_group, format_time(self.start_time))
        self.start_entry.pack(side="left")

        self.sync_start_btn = create_control_button(segment_group, "Set", self.sync_start_to_current)
        self.sync_start_btn.pack(side="left", padx=(4, 12))

        self._create_field_label(segment_group, "Stop").pack(side="left", padx=(0, 5))
        self.stop_entry = self._create_entry(segment_group, "" if self.stop_time is None else format_time(self.stop_time))
        self.stop_entry.pack(side="left")

        self.sync_stop_btn = create_control_button(segment_group, "Set", self.sync_stop_to_current)
        self.sync_stop_btn.pack(side="left", padx=(4, 0))

    def _build_transport_group(self, parent: tk.Misc) -> None:
        transport_group = tk.Frame(parent, bg=self.PANEL_BG)
        transport_group.pack(side="left", padx=(0, 12))

        self.play_btn = create_control_button(transport_group, PLAY_TEXT, self.toggle_play)
        self.play_btn.pack(side="left", padx=(0, 5))

        self.stop_btn = create_control_button(transport_group, STOP_TEXT, self.stop)
        self.stop_btn.pack(side="left", padx=(0, 5))

        self.loop_btn = create_control_button(transport_group, "Loop: ON", self.toggle_loop)
        self.loop_btn.pack(side="left")

    def _build_action_row(self) -> None:
        action_row = tk.Frame(self.controls, bg=self.PANEL_BG)
        action_row.pack(fill="x", padx=CONTROL_PANEL_PAD_X, pady=(2, CONTROL_PANEL_PAD_Y))

        self._build_segment_group(action_row)
        self._build_transport_group(action_row)

        self.video_tools_frame = tk.Frame(action_row, bg=self.PANEL_BG)
        self.video_tools_frame.pack(side="left", padx=(0, 12))

        spacer = tk.Frame(action_row, bg=self.PANEL_BG)
        spacer.pack(side="left", fill="x", expand=True)

        self.action_group = tk.Frame(action_row, bg=self.PANEL_BG)
        self.action_group.pack(side="right")

        self.save_btn = create_control_button(self.action_group, "💾 Save", self.save_segment)
        self.save_btn.pack(side="left", padx=(0, 5))

        self.close_small_btn = create_control_button(self.action_group, "Close", self.close)
        self.close_small_btn.pack(side="left")

    # --------------------------------------------------------
    # UI
    # --------------------------------------------------------
    def _build_ui(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.video_area = tk.Frame(self, bg="black", highlightthickness=0)
        self.video_area.grid(row=0, column=0, sticky="nsew")

        self.close_btn = tk.Button(
            self,
            text="×",
            command=self.close,
            bg=self.PANEL_BG,
            fg=self.TEXT,
            activebackground=CONTROL_ACTIVE_BG,
            activeforeground=self.TEXT,
            bd=0,
            font=("Segoe UI", 16, "bold"),
            cursor="hand2",
        )
        self.close_btn.place(x=10, y=10, width=36, height=36)

        self.controls = tk.Frame(
            self,
            bg=self.PANEL_BG,
            highlightthickness=1,
            highlightbackground=CONTROL_BORDER,
        )
        self.controls.place(
            relx=0.5,
            rely=1.0,
            anchor="s",
            relwidth=0.96,
            height=CONTROL_PANEL_HEIGHT,
            y=-12,
        )

        self._build_timeline_row()
        self._build_action_row()

    # --------------------------------------------------------
    # VLC
    # --------------------------------------------------------
    def _init_vlc(self) -> None:
        if vlc is None:
            raise RuntimeError(VLC_IMPORT_ERROR or "python-vlc unavailable")

        try:
            self.instance = vlc.Instance(
                "--no-video-title-show",
                "--quiet",
            )
            self.player = self.instance.media_player_new()
            media = self.instance.media_new(self.video_path)
            self.player.set_media(media)

            self.video_area.update_idletasks()
            hwnd = self.video_area.winfo_id()
            self.player.set_hwnd(hwnd)

        except Exception as e:
            messagebox.showerror("Playback Failed", f"Could not initialize video player:\n{e}")
            self.close()

    # --------------------------------------------------------
    # Playback controls
    # --------------------------------------------------------
    def _set_play_button_state(self) -> None:
        if not hasattr(self, "play_btn"):
            return
        try:
            is_playing = bool(self.player is not None and self.player.is_playing())
        except Exception:
            is_playing = False
        self.play_btn.config(text=PAUSE_TEXT if is_playing else PLAY_TEXT)

    def play(self) -> None:
        if self.player is None:
            return

        self.apply_segment_fields()
        self._segment_end_paused = False

        try:
            self.player.play()
            self.after(100, self._set_play_button_state)
            self.after(250, lambda: self.seek_to(self.start_time))
        except Exception as e:
            print("⚠️ play failed:", e)

    def toggle_play(self) -> None:
        if self.player is None:
            return

        try:
            current_ms = self.player.get_time()
            length_ms = self.player.get_length()

            if length_ms > 0 and current_ms >= length_ms - 300:
                self.play()
                return
            if self.player.is_playing():
                self.player.pause()
                self._set_play_button_state()
                return

            self._segment_end_paused = False
            self.apply_segment_fields()
            self.player.play()
            self.after(100, self._set_play_button_state)

            if current_ms <= 0:
                self.after(150, lambda: self.seek_to(self.start_time))

        except Exception as e:
            print("⚠️ toggle_play failed:", e)

    def stop(self) -> None:
        if self.player is None:
            return

        try:
            if self.player.is_playing():
                self.player.pause()

            self.apply_segment_fields()
            self._segment_end_paused = False
            self.seek_to(self.start_time)
            self.timeline.set(self.start_time)
            self._set_play_button_state()

        except Exception as e:
            print("⚠️ stop failed:", e)

    def seek_to(self, seconds: float) -> None:
        if self.player is None:
            return

        try:
            self.player.set_time(int(max(0.0, float(seconds)) * 1000))
        except Exception as e:
            print("⚠️ seek failed:", e)

    def toggle_loop(self) -> None:
        self._segment_end_paused = False
        self.loop_segment.set(not self.loop_segment.get())
        self.loop_btn.config(text=f"Loop: {'ON' if self.loop_segment.get() else 'OFF'}")

    # --------------------------------------------------------
    # Segment
    # --------------------------------------------------------
    def _current_video_time(self) -> float:
        if self.player is None:
            return 0.0
        try:
            current_ms = self.player.get_time()
            return max(0.0, current_ms / 1000) if current_ms and current_ms > 0 else 0.0
        except Exception:
            return 0.0

    def _set_entry_time(self, entry: tk.Entry, seconds: float | None) -> None:
        entry.delete(0, "end")
        if seconds is not None:
            entry.insert(0, format_time(seconds))

    def sync_start_to_current(self) -> None:
        self.start_time = self._current_video_time()
        if self.stop_time is not None and self.stop_time <= self.start_time:
            self.stop_time = None
            self._set_entry_time(self.stop_entry, None)
        self._set_entry_time(self.start_entry, self.start_time)
        self._segment_end_paused = False

    def sync_stop_to_current(self) -> None:
        current = self._current_video_time()
        self.apply_segment_fields()
        if current <= self.start_time:
            current = self.start_time + 0.1
        self.stop_time = current
        self._set_entry_time(self.stop_entry, self.stop_time)
        self._segment_end_paused = False

    def apply_segment_fields(self, normalize: bool = False) -> None:
        start = parse_float(self.start_entry.get(), self.start_time)
        stop = parse_float(self.stop_entry.get(), self.stop_time)

        if start is None:
            start = 0.0

        if stop is not None and stop <= start:
            stop = None
            self.stop_entry.delete(0, "end")

        self.start_time = max(0.0, float(start))
        self.stop_time = None if stop is None else max(0.0, float(stop))

        if normalize:
            self._set_entry_time(self.start_entry, self.start_time)
            self._set_entry_time(self.stop_entry, self.stop_time)

    def save_segment(self) -> None:
        self.apply_segment_fields(normalize=True)

        if callable(self.on_save_segment):
            try:
                self.on_save_segment(self.start_time, self.stop_time)
            except Exception as e:
                print("⚠️ on_save_segment failed:", e)

        self.save_btn.config(text="✓ Saved")
        self.after(1200, lambda: self.save_btn.config(text="💾 Save"))

    # --------------------------------------------------------
    # Timeline
    # --------------------------------------------------------
    def _seek_timeline_from_mouse(self, event) -> None:
        if self.player is None:
            return

        try:
            self.apply_segment_fields()
            self._segment_end_paused = False

            width = max(1, self.timeline.winfo_width())
            fraction = min(max(event.x / width, 0.0), 1.0)

            duration = self.duration_seconds
            if duration <= 0:
                length_ms = self.player.get_length()
                duration = max(0.0, length_ms / 1000) if length_ms and length_ms > 0 else 0.0

            if duration <= 0:
                return

            target_time = duration * fraction

            self.timeline.set(target_time)
            self.seek_to(target_time)

        except Exception as e:
            print("⚠️ timeline click seek failed:", e)

    def _on_timeline_press(self, event=None) -> None:
        self.user_dragging = True

        if self.player is not None:
            try:
                self._was_playing_before_drag = bool(self.player.is_playing())
            except Exception:
                self._was_playing_before_drag = False

        if event is not None:
            self._seek_timeline_from_mouse(event)

    def _on_timeline_motion(self, event=None) -> None:
        if event is not None:
            self._seek_timeline_from_mouse(event)

    def _on_timeline_drag(self, _value) -> None:
        pass

    def _on_timeline_release(self, event=None) -> None:
        self.user_dragging = False

        if self.player is None:
            return

        try:
            if event is not None:
                self._seek_timeline_from_mouse(event)

            if self._was_playing_before_drag and not self.player.is_playing():
                self.player.play()
                self.after(100, self._set_play_button_state)

        except Exception as e:
            print("⚠️ timeline release failed:", e)

    def _restart_loop(self) -> None:
        if self.player is None:
            return

        self._segment_end_paused = False
        self.seek_to(self.start_time)
        self.timeline.set(self.start_time)

        try:
            self.player.play()
            self.after(100, self._set_play_button_state)
        except Exception as e:
            print("⚠️ loop restart failed:", e)

    def _pause_at_segment_end(self, loop_end: float) -> None:
        if self.player is None or self._segment_end_paused:
            return

        self._segment_end_paused = True

        try:
            self.player.pause()
        except Exception as e:
            print("⚠️ segment pause failed:", e)

        self.seek_to(loop_end)
        self.timeline.set(loop_end)
        self._set_play_button_state()

    def _update_loop(self) -> None:
        if not self.running:
            return

        try:
            if self.player is not None:
                current_ms = self.player.get_time()
                length_ms = self.player.get_length()

                current = max(0.0, current_ms / 1000) if current_ms and current_ms > 0 else 0.0
                duration = max(0.0, length_ms / 1000) if length_ms and length_ms > 0 else 0.0

                if duration > 0:
                    self.duration_seconds = duration
                    self.timeline.config(to=duration)

                if not self.user_dragging:
                    self.timeline.set(current)

                end_label = self.stop_time if self.stop_time is not None else self.duration_seconds
                self.time_label.config(text=f"{format_time(current)} / {format_time(end_label)}")
                self._set_play_button_state()

                loop_end = self.stop_time if self.stop_time is not None else self.duration_seconds
                near_loop_end = bool(loop_end and current >= loop_end - 0.25)
                at_video_end = bool(duration and current >= duration - 0.25)

                if loop_end and current < loop_end - 0.5:
                    self._segment_end_paused = False

                if self.loop_segment.get():
                    if near_loop_end or at_video_end:
                        self._restart_loop()
                elif self.stop_time is not None and near_loop_end:
                    self._pause_at_segment_end(loop_end)

        except Exception as e:
            print("⚠️ video update loop error:", e)

        self.after(150, self._update_loop)

    # --------------------------------------------------------
    # Close
    # --------------------------------------------------------
    def _on_escape(self, _event=None):
        self.close()
        return "break"

    def close(self) -> None:
        if not self.running:
            return

        self.running = False
        app = self.app

        try:
            self.unbind_all("<Escape>")
        except Exception:
            pass

        try:
            if self.player is not None:
                try:
                    self.player.stop()
                except Exception:
                    pass

                try:
                    self.player.set_hwnd(0)
                except Exception:
                    pass

                try:
                    self.player.set_media(None)
                except Exception:
                    pass

                try:
                    self.player.release()
                except Exception:
                    pass

                self.player = None
        except Exception as e:
            print("⚠️ player cleanup failed:", e)

        try:
            if self.instance is not None:
                self.instance.release()
                self.instance = None
        except Exception:
            pass

        try:
            if app is not None and getattr(app, "video_overlay", None) is not None:
                app.video_overlay.destroy()
                app.video_overlay = None
        except Exception as e:
            print("⚠️ overlay destroy failed:", e)

        try:
            if app is not None and hasattr(app, "canvas"):
                app.canvas.draw_idle()
        except Exception:
            pass

        try:
            if app is not None:
                app.popup_open = False
        except Exception:
            pass


# ------------------------------------------------------------
# Backwards-compatible public API used by shotlog code
# ------------------------------------------------------------
def show_video_overlay(*args, **kwargs) -> None:
    from utils.video_overlay import show_video_overlay as _show_video_overlay

    _show_video_overlay(*args, **kwargs)
