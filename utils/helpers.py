import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from paths import get_project_root

def get_resource_path(*parts):
    base_path = get_project_root()
    return os.path.join(base_path, *parts)

def get_resource_path(*parts):
    base_path = get_project_root()
    return os.path.join(base_path, *parts)

def export_figure_as_image(app, figure):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png")]
    )
    if file_path:
        figure.savefig(file_path, bbox_inches="tight", dpi=300)
        messagebox.showinfo("Image Saved", f"Exported plot to:\n{os.path.basename(file_path)}")

def prompt_link_video(app, iid, online=True):
    try:
        values = app.shotlog_tree.item(iid, "values")
        index = int(values[0]) - 1
    except Exception as e:
        print("⚠️ Failed to parse index from treeview:", e)
        return

    if index >= len(app.log_entries):
        print("⚠️ Invalid log entry index.")
        return

    if online:
        url = tk.simpledialog.askstring("Link Video", "Paste video URL:")
        if url:
            app.log_entries[index] = tuple(list(app.log_entries[index][:-1]) + [url])
            app.update_shot_log_treeview()
            app.auto_update_current_match()
    else:
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")]
        )
        if not file_path:
            print("🚫 No file selected.")
            return

        def on_confirm(path, start, stop):
            final_path = f"{path}|{int(start)}|{int(stop)}"
            app.log_entries[index] = tuple(list(app.log_entries[index][:-1]) + [final_path])
            app.update_shot_log_treeview()
            app.auto_update_current_match()
            app.video_overlay.destroy()
            app.video_overlay = None
            app.popup_open = False
            app.update_plot()
            print(f"✅ Linked video: {final_path}")

        app.popup_open = True
        app.video_overlay = tk.Frame(app.canvas_frame, bg="#1e1e1e", bd=2, relief="ridge")
        app.video_overlay.place(
            x=0, y=0,
            width=app.canvas_frame.winfo_width(),
            height=app.canvas_frame.winfo_height()
        )
        app.video_overlay.lift()

        player = VLCOverlayWithControls(
            app.video_overlay,
            video_path=file_path,
            mode="preview",
            on_confirm=on_confirm,
            start=0
        )
        player.pack(fill="both", expand=True)
        print("✅ Video preview overlay active.")

def open_video_from_entry(app, entry, playback_duration=None):
    data = entry[-1]
    if not data:
        return

    if "|" in data:
        parts = data.split("|")
        filepath = parts[0]
        start_time = int(parts[1]) if len(parts) > 1 else 0
        stop_time = int(parts[2]) if len(parts) > 2 else None
    else:
        filepath = data
        start_time = 0
        stop_time = None

    if not os.path.exists(filepath):
        print("⚠️ File does not exist:", filepath)
        return

    show_video_overlay(app, filepath, start=start_time, stop=stop_time)

def handle_open_linked_video(app, iid):
    values = app.shotlog_tree.item(iid, "values")
    index = int(values[0]) - 1
    if index < len(app.log_entries):
        entry = app.log_entries[index]
        open_video_from_entry(app, entry)

def save_video_link(app, index, path, start_seconds, stop_seconds):
    final_path = f"{path}|{int(start_seconds)}|{int(stop_seconds)}"
    app.log_entries[index] = tuple(list(app.log_entries[index][:-1]) + [final_path])
    app.update_shot_log_treeview()
    app.auto_update_current_match()

def remove_video_link(app, index):
    entry = list(app.log_entries[index])
    entry[9] = ""
    app.log_entries[index] = tuple(entry)
    app.update_shot_log_treeview()
    app.auto_update_current_match()