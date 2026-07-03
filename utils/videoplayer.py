# utils/videoplayer.py
"""
Modern embedded VLC overlay player for Floorball Shot Plotter.

Features:
- Uses bundled VLC runtime
- Fills the center canvas panel
- Minimal bottom controls
- Clickable / draggable timeline
- Start / Stop segment fields
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

        self.instance = None
        self.player = None

        self._build_ui()
        self._init_vlc()

        self.bind_all("<Escape>", self._on_escape)

        if autoplay:
            self.after(350, self.play)

        self.after(250, self._update_loop)

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
            height=86,
            y=-12,
        )

        self.controls.grid_columnconfigure(1, weight=1)

        self.time_label = tk.Label(
            self.controls,
            text="00:00 / --:--",
            bg=self.PANEL_BG,
            fg=self.TEXT,
            font=("Segoe UI", 9, "bold"),
            width=13,
        )
        self.time_label.grid(row=0, column=0, padx=(10, 6), pady=(8, 0), sticky="w")

        self.timeline = tk.Scale(
            self.controls,
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
        self.timeline.grid(
            row=0,
            column=1,
            columnspan=8,
            padx=(0, 10),
            pady=(5, 0),
            sticky="ew",
        )
        self.timeline.bind("<ButtonPress-1>", self._on_timeline_press)
        self.timeline.bind("<B1-Motion>", self._on_timeline_motion)
        self.timeline.bind("<ButtonRelease-1>", self._on_timeline_release)

        tk.Label(
            self.controls,
            text="Start",
            bg=self.PANEL_BG,
            fg=self.MUTED,
            font=("Segoe UI", 9),
        ).grid(row=1, column=0, padx=(10, 4), pady=(6, 8), sticky="e")

        self.start_entry = tk.Entry(
            self.controls,
            bg=self.PANEL_BG_SOFT,
            fg=self.TEXT,
            insertbackground=self.TEXT,
            relief="flat",
            justify="center",
            font=("Segoe UI", 9),
            width=7,
        )
        self.start_entry.insert(0, f"{self.start_time:g}")
        self.start_entry.grid(row=1, column=1, padx=(0, 8), pady=(6, 8), sticky="w")

        tk.Label(
            self.controls,
            text="Stop",
            bg=self.PANEL_BG,
            fg=self.MUTED,
            font=("Segoe UI", 9),
        ).grid(row=1, column=2, padx=(0, 4), pady=(6, 8), sticky="e")

        self.stop_entry = tk.Entry(
            self.controls,
            bg=self.PANEL_BG_SOFT,
            fg=self.TEXT,
            insertbackground=self.TEXT,
            relief="flat",
            justify="center",
            font=("Segoe UI", 9),
            width=7,
        )
        self.stop_entry.insert(0, "" if self.stop_time is None else f"{self.stop_time:g}")
        self.stop_entry.grid(row=1, column=3, padx=(0, 12), pady=(6, 8), sticky="w")

        self.play_btn = create_control_button(self.controls, "▶ / ⏸", self.toggle_play)
        self.play_btn.grid(row=1, column=4, padx=3, pady=(6, 8), sticky="ew")

        self.stop_btn = create_control_button(self.controls, "■", self.stop)
        self.stop_btn.grid(row=1, column=5, padx=3, pady=(6, 8), sticky="ew")

        self.loop_btn = create_control_button(self.controls, "Loop: ON", self.toggle_loop)
        self.loop_btn.grid(row=1, column=6, padx=3, pady=(6, 8), sticky="ew")

        self.save_btn = create_control_button(self.controls, "💾 Save", self.save_segment)
        self.save_btn.grid(row=1, column=7, padx=3, pady=(6, 8), sticky="ew")

        self.close_small_btn = create_control_button(self.controls, "Close", self.close)
        self.close_small_btn.grid(row=1, column=8, padx=(3, 10), pady=(6, 8), sticky="ew")

        self.start_entry.bind("<Return>", lambda _e: self.apply_segment_fields())
        self.stop_entry.bind("<Return>", lambda _e: self.apply_segment_fields())
        self.start_entry.bind("<FocusOut>", lambda _e: self.apply_segment_fields())
        self.stop_entry.bind("<FocusOut>", lambda _e: self.apply_segment_fields())

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
    def play(self) -> None:
        if self.player is None:
            return

        self.apply_segment_fields()

        try:
            self.player.play()
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
                return

            self.apply_segment_fields()
            self.player.play()

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
            self.seek_to(self.start_time)
            self.timeline.set(self.start_time)

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
        self.loop_segment.set(not self.loop_segment.get())
        self.loop_btn.config(text=f"Loop: {'ON' if self.loop_segment.get() else 'OFF'}")

    # --------------------------------------------------------
    # Segment
    # --------------------------------------------------------
    def apply_segment_fields(self) -> None:
        start = parse_float(self.start_entry.get(), self.start_time)
        stop = parse_float(self.stop_entry.get(), self.stop_time)

        if start is None:
            start = 0.0

        if stop is not None and stop <= start:
            stop = None
            self.stop_entry.delete(0, "end")

        self.start_time = max(0.0, float(start))
        self.stop_time = None if stop is None else max(0.0, float(stop))

    def save_segment(self) -> None:
        self.apply_segment_fields()

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

        except Exception as e:
            print("⚠️ timeline release failed:", e)

    def _restart_loop(self) -> None:
        if self.player is None:
            return

        self.seek_to(self.start_time)
        self.timeline.set(self.start_time)

        try:
            self.player.play()
        except Exception as e:
            print("⚠️ loop restart failed:", e)

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

                if self.loop_segment.get():
                    loop_end = self.stop_time if self.stop_time is not None else self.duration_seconds
                    near_loop_end = bool(loop_end and current >= loop_end - 0.25)
                    at_video_end = bool(duration and current >= duration - 0.25)

                    if near_loop_end or at_video_end:
                        self._restart_loop()

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
