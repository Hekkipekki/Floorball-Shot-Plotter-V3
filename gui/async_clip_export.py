from __future__ import annotations

from pathlib import Path
from tkinter import filedialog, messagebox

from gui.shotlog_video import CLIP_FILETYPES
from paths import VIDEOS_DIR, ensure_data_dirs
from utils.render_progress import close_render_progress, show_render_progress, update_render_progress
from utils.video_clip_exporter import export_local_segment_async


def default_clip_name(source_path: str, start: float, stop: float | None) -> str:
    source_stem = Path(source_path).stem or "video_clip"
    start_label = int(max(0.0, float(start or 0.0)))
    stop_label = "end" if stop is None else int(max(0.0, float(stop)))
    return f"{source_stem}_{start_label}s-{stop_label}s.mp4"


def run_on_ui(app, callback, *args) -> None:
    root = getattr(app, "root", None)
    if root is not None:
        try:
            root.after(0, lambda: callback(*args))
            return
        except Exception:
            pass
    callback(*args)


def export_standalone_local_clip_async(app, path: str, start: float, stop: float | None) -> None:
    ensure_data_dirs()
    output_path = filedialog.asksaveasfilename(
        title="Export Short Clip",
        initialdir=str(VIDEOS_DIR),
        initialfile=default_clip_name(path, start, stop),
        defaultextension=".mp4",
        filetypes=CLIP_FILETYPES,
    )
    if not output_path:
        return

    progress = show_render_progress(app, message="Exporting 1080p analysis clip...")

    def progress_callback(fraction, rendered, total) -> None:
        run_on_ui(app, update_render_progress, progress, fraction, rendered, total)

    def done_callback(result_path, error) -> None:
        def finish() -> None:
            close_render_progress(progress)
            if error is not None:
                messagebox.showerror("Clip Export Failed", str(error))
                return
            messagebox.showinfo("Clip Exported", "The shorter 1080p clip was exported successfully.")

        run_on_ui(app, finish)

    export_local_segment_async(
        path,
        output_path,
        start=start,
        stop=stop,
        progress_callback=progress_callback,
        done_callback=done_callback,
    )
