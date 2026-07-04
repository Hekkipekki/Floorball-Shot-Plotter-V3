import tkinter as tk

MESSAGE_DURATION_MS = 2000
MESSAGE_FONT = ("Segoe UI", 15)
MESSAGE_FOREGROUND = "white"
MESSAGE_BACKGROUND = "#333333"
MESSAGE_PAD_X = 10
MESSAGE_PAD_Y = 4
MESSAGE_RELIEF = "solid"
MESSAGE_BORDER_WIDTH = 1
MESSAGE_REL_X = 0.5
MESSAGE_Y = 10
MESSAGE_ANCHOR = "n"


def _destroy_existing_message(app) -> None:
    if hasattr(app, "message_label") and app.message_label.winfo_exists():
        app.message_label.destroy()


def _create_message_label(parent, text) -> tk.Label:
    return tk.Label(
        parent,
        text=text,
        font=MESSAGE_FONT,
        foreground=MESSAGE_FOREGROUND,
        background=MESSAGE_BACKGROUND,
        padx=MESSAGE_PAD_X,
        pady=MESSAGE_PAD_Y,
        relief=MESSAGE_RELIEF,
        borderwidth=MESSAGE_BORDER_WIDTH,
    )


def show_temporary_message(app, text, duration=MESSAGE_DURATION_MS):
    _destroy_existing_message(app)

    canvas_widget = app.canvas.get_tk_widget()
    app.message_label = _create_message_label(canvas_widget, text)
    app.message_label.place(relx=MESSAGE_REL_X, y=MESSAGE_Y, anchor=MESSAGE_ANCHOR)
    canvas_widget.after(duration, app.message_label.destroy)
