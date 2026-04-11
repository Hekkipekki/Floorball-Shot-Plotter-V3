import os
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import ttkbootstrap as tb
import webbrowser
from ttkbootstrap.constants import *
from PIL import Image, ImageTk

from utils.tooltips import BetterToolTip
from gui.plotting import plot_points
from utils.helpers import get_resource_path


def setup_shotlog_frame(self, parent, app):
    self.app = app

    style = tb.Style()
    style.configure("Treeview", font=("Segoe UI Emoji", 8))

    frame = tb.Labelframe(parent, text="Shot Log", bootstyle="primary")
    frame.pack(fill="both", expand=True, padx=5, pady=5)
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    columns = ("#", "S/G", "Phase", "Situation", "Type", "Passer", "Shooter", "P", "xG", "Video")
    col_widths = {
        "#": 22, "S/G": 33, "Phase": 52, "Situation": 76, "Type": 70,
        "Passer": 50, "Shooter": 55, "P": 28, "xG": 36, "Video": 30
    }

    tree = tb.Treeview(frame, columns=columns, show="headings", bootstyle="primary")

    try:
        icon_path = get_resource_path("Resources", "Icons", "VideoIcon.png")
        video_img = Image.open(icon_path).convert("RGBA").resize((16, 16))
        bg_color = (44, 62, 80, 255)
        background = Image.new("RGBA", video_img.size, bg_color)
        combined = Image.alpha_composite(background, video_img)
        self.video_icon_tk = ImageTk.PhotoImage(combined.convert("RGB"))
    except Exception as e:
        print("⚠️ Failed to load video icon:", e)
        self.video_icon_tk = None

    for col in columns:
        if col == "Video" and self.video_icon_tk:
            tree.heading(col, image=self.video_icon_tk)
        else:
            tree.heading(col, text=col)
        tree.column(col, anchor="center", width=col_widths.get(col, 60))

    tree.grid(row=0, column=0, sticky="nsew")

    scrollbar = tb.Scrollbar(frame, orient="vertical", command=tree.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    tree.configure(yscrollcommand=scrollbar.set)

    tree.bind("<Motion>", lambda e: on_hover_shot(e, tree, app))
    tree.bind("<Leave>", lambda e: on_leave_shotlog(e, tree, app))
    tree.bind("<Double-1>", lambda e: on_row_double_click(e, tree, app))
    tree.bind("<Button-3>", lambda e: on_right_click_shotlog(e, tree, app))

    tree._last_hovered_row_id = None
    app.shotlog_tree = tree


def reset_shot_log(app):
    if not messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all data?"):
        return
    app.log_entries.clear()
    app.update_shot_log_treeview()
    app.update_plot()
    app.update_stats()


def on_row_double_click(event, tree, app):
    iid = tree.identify_row(event.y)
    if not iid:
        return
    try:
        index = int(iid)
        if 0 <= index < len(app.log_entries):
            del app.log_entries[index]
            app.update_shot_log_treeview()
            app.update_plot()
            app.update_stats()
    except Exception as e:
        print("Double-click error:", e)


def on_hover_shot(event, tree, app):
    iid = tree.identify_row(event.y)
    if not iid:
        if tree._last_hovered_row_id is not None:
            tree._last_hovered_row_id = None
            app.clear_highlight()
        return
    if iid == tree._last_hovered_row_id:
        return

    try:
        index = int(iid)
        if 0 <= index < len(app.log_entries):
            tree._last_hovered_row_id = iid
            app.highlight_point(index)
    except Exception as e:
        print("Hover error:", e)
        app.clear_highlight()
        tree._last_hovered_row_id = None


def on_leave_shotlog(event, tree, app):
    if tree._last_hovered_row_id is not None:
        tree._last_hovered_row_id = None
        app.clear_highlight()


# -----------------------------
# Video helpers
# -----------------------------
def _video_to_dict(video):
    """Normalize entry[13] into dict or None."""
    if not video:
        return None
    if isinstance(video, dict):
        return video
    # legacy string
    return {"path": str(video), "start": 0.0, "stop": None}


def _video_display_symbol(video):
    v = _video_to_dict(video)
    return "🔗" if v and v.get("path") else ""


# -----------------------------
# Right click menu
# -----------------------------
def on_right_click_shotlog(event, tree, app):
    iid = tree.identify_row(event.y)
    if not iid:
        return

    tree.selection_set(iid)
    index = int(iid)

    if not (0 <= index < len(app.log_entries)):
        return  # safety

    def ensure_video_field():
        entry = list(app.log_entries[index])
        if len(entry) < 14:
            entry += [None] * (14 - len(entry))
            app.log_entries[index] = tuple(entry)

    def set_video_dict(path_or_url: str):
        ensure_video_field()
        entry = list(app.log_entries[index])
        entry[13] = {"path": path_or_url, "start": 0.0, "stop": None}
        app.log_entries[index] = tuple(entry)
        app.update_shot_log_treeview()

    def link_offline():
        path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.mov *.avi *.mkv")]
        )
        if path:
            set_video_dict(path)

    def link_online():
        url = simpledialog.askstring("Link Online Video", "Enter video URL:")
        if url:
            set_video_dict(url)

    def relink_offline():
        link_offline()

    def relink_online():
        link_online()

    def remove_video():
        ensure_video_field()
        entry = list(app.log_entries[index])
        entry[13] = None
        app.log_entries[index] = tuple(entry)
        app.update_shot_log_treeview()

    def play_or_edit_video():
        ensure_video_field()
        video = _video_to_dict(app.log_entries[index][13])
        if not video or not video.get("path"):
            return

        path = video["path"]
        start = float(video.get("start") or 0.0)
        stop = video.get("stop", None)

        def save_segment_cb(new_start, new_stop):
            ensure_video_field()
            entry = list(app.log_entries[index])
            v = _video_to_dict(entry[13]) or {"path": path, "start": 0.0, "stop": None}
            v["start"] = float(new_start or 0.0)
            v["stop"] = None if new_stop in ("", None) else float(new_stop)
            entry[13] = v
            app.log_entries[index] = tuple(entry)
            app.update_shot_log_treeview()

        try:
            if str(path).startswith("http"):
                webbrowser.open(path)
            else:
                if os.path.exists(path):
                    from utils.videoplayer import show_video_overlay

                    show_video_overlay(
                        app,
                        path,
                        start=start,
                        stop=stop,
                        autoplay=True,
                        on_save_segment=save_segment_cb,
                    )
                else:
                    messagebox.showwarning("Video Missing", "Video file could not be found.")
        except Exception as e:
            messagebox.showerror("Playback Failed", f"Could not play video:\n{e}")

    # Build menu
    ensure_video_field()
    current_video = _video_to_dict(app.log_entries[index][13])
    has_video = bool(current_video and current_video.get("path"))

    menu = tk.Menu(tree, tearoff=0)

    if has_video:
        menu.add_command(label="🎬 Play / Edit Segment", command=play_or_edit_video)
        menu.add_separator()
        menu.add_command(label="🎞️ Relink Offline Video", command=relink_offline)
        menu.add_command(label="🌐 Relink Online Video", command=relink_online)
        menu.add_separator()
        menu.add_command(label="❌ Remove Video Link", command=remove_video)
    else:
        menu.add_command(label="🎞️ Link Offline Video", command=link_offline)
        menu.add_command(label="🌐 Link Online Video", command=link_online)

    menu.post(event.x_root, event.y_root)


# -----------------------------
# Tree update
# -----------------------------
def update_treeview(tree, entries):
    tree.delete(*tree.get_children())

    for i, entry in enumerate(entries):
        entry = list(entry)
        if len(entry) < 14:
            entry += [None] * (14 - len(entry))

        video_symbol = _video_display_symbol(entry[13])

        values = [
            entry[0], entry[1], entry[2], entry[3], entry[4],
            entry[5], entry[6], entry[7], f"{entry[8]:.2f}", video_symbol
        ]

        tree.insert("", "end", iid=str(i), values=values)