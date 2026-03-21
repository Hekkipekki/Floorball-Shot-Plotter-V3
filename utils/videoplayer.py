# utils/videoplayer.py
"""
Embedded VLC overlay player for Floorball Shot Plotter.

Features:
- Portable-friendly: configure bundled VLC runtime BEFORE importing python-vlc
- Force bundled VLC plugins (avoid Program Files VLC)
- Stable overlay stacking: never lower canvas_frame, just raise overlay
- Repeat + segment loop
- Start/Stop fields apply (Enter / FocusOut)
- Auto-play toggle
- Save Segment button (writes back to caller via callback)
- Clean close(): stop -> detach hwnd -> release -> destroy only overlay we created

Dev/Ship:
- Use env var FSP_VLC_RESET_CACHE=1 to enable '--reset-plugins-cache'
  (Useful while debugging bundled plugins; disable for best performance)
"""

from __future__ import annotations

import os
import time
from pathlib import Path
import tkinter as tk

from paths import get_project_root


# ------------------------------------------------------------
# VLC runtime bootstrap (MUST run before import vlc)
# ------------------------------------------------------------
def _configure_vlc_runtime() -> tuple[Path | None, Path | None]:
    base = Path(get_project_root())
    vlc_dir = base / "vlc"
    plugins_dir = vlc_dir / "plugins"

    if not (vlc_dir / "libvlc.dll").exists():
        return None, None

    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(str(vlc_dir))
    else:
        os.environ["PATH"] = f"{vlc_dir};{os.environ.get('PATH','')}"

    os.environ["VLC_PLUGIN_PATH"] = str(plugins_dir)
    return vlc_dir, plugins_dir


_VLC_DIR, _PLUGINS_DIR = _configure_vlc_runtime()

import vlc  # noqa: E402


class VLCOverlayWithControls(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        video_path: str,
        *,
        start: float = 0.0,
        stop: float | None = None,
        autoplay: bool = True,
        app=None,
        on_save_segment=None,   # callable(start: float, stop: float|None) -> None
        **kwargs,
    ):
        super().__init__(master, bg="#1e1e1e", **kwargs)

        self.app = app
        self.video_path = video_path
        self.on_save_segment = on_save_segment

        self.start_time: float = float(start or 0.0)
        self.stop_time: float | None = float(stop) if stop not in (None, "") else None

        self.running = True

        # Toggle modes
        self.autoplay = bool(autoplay)
        self.repeat_mode = False         # repeats full media end OR segment end
        self.segment_loop = False        # if True: loop only between start/stop (requires stop)

        self.seeking = False
        self.last_seek_time = 0.0

        # VLC
        self.instance: vlc.Instance | None = None
        self.player: vlc.MediaPlayer | None = None

        # ---------------- UI ----------------
        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.controls = tk.Frame(self, bg="#2c2c2c")
        self.controls.pack(fill="x", padx=5, pady=4)

        tk.Label(self.controls, text="Start:", bg="#2c2c2c", fg="white").pack(side="left", padx=(5, 2))
        self.start_entry = tk.Entry(self.controls, width=7)
        self.start_entry.insert(0, str(int(self.start_time)))
        self.start_entry.pack(side="left")

        tk.Label(self.controls, text="Stop:", bg="#2c2c2c", fg="white").pack(side="left", padx=(10, 2))
        self.stop_entry = tk.Entry(self.controls, width=7)
        self.stop_entry.insert(0, "" if self.stop_time is None else str(int(self.stop_time)))
        self.stop_entry.pack(side="left")

        self.slider = tk.Scale(
            self.controls,
            from_=0,
            to=1000,
            orient="horizontal",
            length=320,
            showvalue=False,
        )
        self.slider.pack(side="left", padx=(20, 10))
        self.slider.bind("<ButtonPress-1>", self.on_slider_press)
        self.slider.bind("<ButtonRelease-1>", self.on_slider_release)

        self.time_label = tk.Label(
            self.controls,
            text="00:00 / 00:00",
            bg="#2c2c2c",
            fg="white",
            font=("Segoe UI", 9),
        )
        self.time_label.pack(side="left", padx=(10, 0))

        self.play_btn = tk.Button(self.controls, text="▶", command=self.play)
        self.play_btn.pack(side="left", padx=2)
        self.pause_btn = tk.Button(self.controls, text="⏸", command=self.pause)
        self.pause_btn.pack(side="left", padx=2)
        self.stop_btn = tk.Button(self.controls, text="⏹", command=self.stop)
        self.stop_btn.pack(side="left", padx=2)

        # Right-side toggles / actions
        self.save_btn = tk.Button(self.controls, text="💾 Save Segment", command=self.save_segment)
        self.save_btn.pack(side="right", padx=(6, 10))

        self.autoplay_btn = tk.Button(self.controls, text="▶ Auto", command=self.toggle_autoplay)
        self.autoplay_btn.pack(side="right", padx=(6, 0))

        self.segment_btn = tk.Button(self.controls, text="🎯 Segment", command=self.toggle_segment_loop)
        self.segment_btn.pack(side="right", padx=(6, 0))

        self.repeat_btn = tk.Button(self.controls, text="🔁 Repeat", command=self.toggle_repeat)
        self.repeat_btn.pack(side="right", padx=(6, 0))

        self._sync_toggle_buttons()

        self.close_btn = tk.Button(self, text="❌", command=self.close, bg="#1e1e1e", fg="white", borderwidth=0)
        self.close_btn.place(relx=0.0, rely=0.0, anchor="nw", x=10, y=10)

        # Entry apply bindings
        self.start_entry.bind("<Return>", self._on_start_apply)
        self.start_entry.bind("<FocusOut>", self._on_bounds_apply)
        self.stop_entry.bind("<Return>", self._on_bounds_apply)
        self.stop_entry.bind("<FocusOut>", self._on_bounds_apply)

        # ESC
        self.bind_all("<Escape>", self._on_escape)

        # Init VLC + tick
        self.after(0, self._init_player_safe)
        self.after(200, self.update_slider)

    # ---------------------------
    # UI state
    # ---------------------------
    def _sync_toggle_buttons(self) -> None:
        self.repeat_btn.config(
            text=("🔁 Repeating" if self.repeat_mode else "🔁 Repeat"),
            relief=("sunken" if self.repeat_mode else "raised"),
        )
        self.segment_btn.config(
            text=("🎯 Segment ON" if self.segment_loop else "🎯 Segment"),
            relief=("sunken" if self.segment_loop else "raised"),
        )
        self.autoplay_btn.config(
            text=("▶ Auto ON" if self.autoplay else "▶ Auto"),
            relief=("sunken" if self.autoplay else "raised"),
        )

    # ---------------------------
    # Bounds / seek helpers
    # ---------------------------
    def _apply_time_bounds(self) -> None:
        try:
            s = self.start_entry.get().strip()
            self.start_time = float(s) if s else 0.0
        except Exception:
            self.start_time = 0.0

        try:
            raw = self.stop_entry.get().strip()
            self.stop_time = float(raw) if raw else None
        except Exception:
            self.stop_time = None

    def _seek_seconds(self, seconds: float) -> None:
        if not self.player:
            return
        try:
            self.player.set_time(int(max(0.0, seconds) * 1000))
        except Exception:
            pass

    def _restart_from(self, seconds: float, *, pause_after: bool = False) -> None:
        if not self.player or not self.instance:
            return

        try:
            self.player.stop()
        except Exception:
            pass

        try:
            media = self.instance.media_new(self.video_path)
            self.player.set_media(media)
            self.player.play()
        except Exception as e:
            print("⚠️ restart failed:", e)
            return

        def _after_start():
            self._seek_seconds(seconds)
            if pause_after:
                try:
                    self.player.set_pause(1)
                except Exception:
                    pass

        self.after(250, _after_start)

    def _on_bounds_apply(self, _event=None):
        self._apply_time_bounds()

    def _on_start_apply(self, _event=None):
        self._apply_time_bounds()
        self._restart_from(self.start_time, pause_after=not self.autoplay)

    # ---------------------------
    # VLC init / playback
    # ---------------------------
    def _init_player_safe(self) -> None:
        if not self.running:
            return

        try:
            plugin_path = str(_PLUGINS_DIR.resolve()) if _PLUGINS_DIR else None

            args = [
                "--no-video-title-show",
                "--quiet",
                "--no-osd",
                "--no-stats",
                "--no-media-library",
            ]
            if plugin_path:
                args.append(f"--plugin-path={plugin_path}")

            # Dev switch: set env var FSP_VLC_RESET_CACHE=1 while you debug bundling
            if os.environ.get("FSP_VLC_RESET_CACHE", "0") == "1":
                args.append("--reset-plugins-cache")

            self.instance = vlc.Instance(*args)
            self.player = self.instance.media_player_new()

        except Exception as e:
            print("❌ VLC instance/player init failed:", e)
            self.running = False
            return

        self.init_player()

    def init_player(self) -> None:
        if not self.running or self.player is None or self.instance is None:
            return

        self.update_idletasks()
        window_id = self.canvas.winfo_id()

        try:
            self.player.set_hwnd(window_id)  # Windows
        except Exception:
            try:
                self.player.set_xwindow(window_id)  # X11
            except Exception:
                try:
                    self.player.set_nsobject(window_id)  # macOS
                except Exception as e:
                    print("❌ Could not bind VLC video output:", e)

        # Start playback then seek start; optionally pause immediately
        self._apply_time_bounds()
        self._restart_from(self.start_time, pause_after=not self.autoplay)

    def play(self) -> None:
        if not self.player or not self.instance:
            return

        self._apply_time_bounds()

        try:
            state = self.player.get_state()
        except Exception:
            state = None

        if state in (vlc.State.Ended, vlc.State.Stopped):
            self._restart_from(self.start_time, pause_after=False)
            return

        try:
            self.player.play()
        except Exception as e:
            print("⚠️ Play failed:", e)

    def pause(self) -> None:
        if not self.player:
            return
        try:
            self.player.set_pause(1)
        except Exception as e:
            print("⚠️ Pause failed:", e)

    def stop(self) -> None:
        if not self.player:
            return
        try:
            self.player.stop()
        except Exception:
            pass

    # ---------------------------
    # Slider / loop logic
    # ---------------------------
    def on_slider_press(self, _event) -> None:
        self.seeking = True
        self.pause()

    def on_slider_release(self, _event) -> None:
        self.seeking = False
        self.seek()
        self.play()

    def seek(self, _event=None) -> None:
        if not self.player:
            return
        now = time.time()
        if now - self.last_seek_time < 0.1:
            return
        self.last_seek_time = now
        try:
            value = int(self.slider.get())
            self.player.set_time(value * 1000)
        except Exception:
            pass

    def update_slider(self) -> None:
        if not self.running or self.player is None:
            return

        try:
            state = self.player.get_state()
            current = max(0, int(self.player.get_time() // 1000))

            self._apply_time_bounds()

            length = max(0, int(self.player.get_length() // 1000))

            if not self.seeking and length > 0:
                self.slider.config(to=length)
                self.slider.set(current)

                mins = lambda x: str(x // 60).zfill(2)
                secs = lambda x: str(x % 60).zfill(2)
                self.time_label.config(text=f"{mins(current)}:{secs(current)} / {mins(length)}:{secs(length)}")

            # ---- Segment loop boundary ----
            if self.stop_time is not None and current >= int(self.stop_time):
                if self.segment_loop:
                    self._restart_from(self.start_time, pause_after=False)
                elif self.repeat_mode:
                    # repeat mode but not segment-loop => still loop if stop exists (common expectation)
                    self._restart_from(self.start_time, pause_after=False)
                else:
                    try:
                        self.player.set_pause(1)
                    except Exception:
                        pass

            # ---- Ended handling ----
            if state == vlc.State.Ended:
                if self.repeat_mode:
                    self._restart_from(self.start_time, pause_after=False)
                else:
                    try:
                        self.player.set_pause(1)
                    except Exception:
                        pass

        except Exception as e:
            print("⚠️ update_slider error:", e)

        self.after(200, self.update_slider)

    def toggle_repeat(self) -> None:
        self.repeat_mode = not self.repeat_mode
        self._sync_toggle_buttons()

    def toggle_segment_loop(self) -> None:
        self.segment_loop = not self.segment_loop
        # Segment loop requires a stop; if user enables without stop, we just keep it ON
        # but it won't trigger until stop_time exists.
        self._sync_toggle_buttons()

    def toggle_autoplay(self) -> None:
        self.autoplay = not self.autoplay
        self._sync_toggle_buttons()

    # ---------------------------
    # Save segment back to caller
    # ---------------------------
    def save_segment(self) -> None:
        self._apply_time_bounds()
        if callable(self.on_save_segment):
            try:
                self.on_save_segment(self.start_time, self.stop_time)
            except Exception as e:
                print("⚠️ on_save_segment failed:", e)

    # ---------------------------
    # Close / cleanup
    # ---------------------------
    def _on_escape(self, _event=None):
        try:
            self.close()
        except Exception as e:
            print("⚠️ close() error on ESC:", e)
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
                    self.player.audio_set_volume(0)
                except Exception:
                    pass

                try:
                    self.player.stop()
                except Exception:
                    pass

                # Detach surface (prevents ghost/white surfaces)
                try:
                    self.player.set_hwnd(0)
                except Exception:
                    pass

                try:
                    self.player.set_media(None)
                except Exception:
                    pass

                self.after(80, self._safe_release)
        except Exception as e:
            print("⚠️ close stop/detach error:", e)

        try:
            if self.instance is not None:
                self.instance.release()
                self.instance = None
        except Exception:
            pass

        try:
            if app is not None and getattr(app, "video_overlay", None) is not None:
                try:
                    app.video_overlay.destroy()
                except Exception:
                    pass
                app.video_overlay = None
        except Exception as e:
            print("⚠️ overlay destroy error:", e)

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

    def _safe_release(self) -> None:
        try:
            if self.player is not None:
                self.player.release()
                self.player = None
        except Exception as e:
            print("⚠️ player.release error:", e)


# ------------------------------------------------------------
# Public API used by shotlog
# ------------------------------------------------------------
def show_video_overlay(
    app,
    video_path: str,
    start: float = 0.0,
    stop: float | None = None,
    *,
    autoplay: bool = True,
    on_save_segment=None,
) -> None:
    app.popup_open = True

    existing = getattr(app, "video_overlay", None)
    if existing is not None:
        try:
            existing.destroy()
        except Exception:
            pass
        app.video_overlay = None

    try:
        app.canvas_frame.update_idletasks()
    except Exception:
        pass

    app.video_overlay = tk.Frame(app.canvas_frame, bg="#1e1e1e", bd=2, relief="ridge")
    app.video_overlay.place(x=0, y=0, relwidth=1.0, relheight=1.0)
    app.video_overlay.tkraise()

    player = VLCOverlayWithControls(
        app.video_overlay,
        video_path=video_path,
        start=start,
        stop=stop,
        autoplay=autoplay,
        app=app,
        on_save_segment=on_save_segment,
    )
    player.pack(fill="both", expand=True)

    # Keep a reference to avoid GC
    app._vlc_player = player