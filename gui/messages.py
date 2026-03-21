import tkinter as tk

def show_temporary_message(app, text, duration=2000):
    if hasattr(app, "message_label") and app.message_label.winfo_exists():
        app.message_label.destroy()

    canvas_widget = app.canvas.get_tk_widget()
    app.message_label = tk.Label(
        canvas_widget,
        text=text,
        font=("Segoe UI", 15),
        foreground="white",
        background="#333333",
        padx=10,
        pady=4,
        relief="solid",
        borderwidth=1
    )
    app.message_label.place(relx=0.5, y=10, anchor="n")
    canvas_widget.after(duration, app.message_label.destroy)
