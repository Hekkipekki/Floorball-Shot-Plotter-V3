import tkinter as tk
import ttkbootstrap as tb
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from gui.events import onclick, on_space_key_pressed
from utils.tooltips import BetterToolTip


def setup_plot_canvas(self):
    self.figure = Figure(figsize=(14.5, 10.5))
    self.figure.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
    self.ax = self.figure.add_subplot(111)
    self.selector_dot, = self.ax.plot([], [], 'o', markersize=15, alpha=0.5)

    self.plot_frame = tb.Labelframe(self.center_panel, text="Shot Plot", bootstyle="primary")
    self.plot_frame.pack(fill="both", expand=True, padx=0, pady=0)

    # Ny container Frame för canvas – detta är den riktiga canvas_frame
    self.canvas_frame = tk.Frame(self.plot_frame)
    self.canvas_frame.pack(fill="both", expand=True, padx=0, pady=0)

    self.canvas = FigureCanvasTkAgg(self.figure, master=self.canvas_frame)
    canvas_widget = self.canvas.get_tk_widget()
    canvas_widget.pack(fill="both", expand=True, padx=0, pady=0)

    self.trash_btn = tb.Button(
        self.plot_frame,
        image=self.trash_icon,
        command=self.clear_all_data,
        bootstyle="danger-link",
        cursor="hand2"
    )
    self.trash_btn.place(in_=self.plot_frame, relx=1.0, rely=0.0, anchor="ne", x=-5, y=-6)
    BetterToolTip(self.trash_btn, "Clear all shots/goals from the list.")

    canvas_widget.focus_set()
    canvas_widget.bind("<space>", lambda e: on_space_key_pressed(self, e))
    self.canvas.mpl_connect("button_press_event", lambda e: onclick(self, e))

    self.instructions_label = tk.Label(
        canvas_widget,
        text="ⓘ Hotkeys Info",
        bg="lightyellow",
        font=("Arial", 9, "bold"),
        relief="ridge",
        borderwidth=1
    )
    self.instructions_label.place(x=5, y=5)

    BetterToolTip(
        self.instructions_label,
        "🎯 Hotkeys:\n\n"
        "👡 Left Click  = Add Shot\n"
        "👡 Right Click = Add Goal\n"
        "⎵ Space       = Remove Nearest Dot\n"
        "👡 Double Click (Shot Log) = Delete Entry\n"
        "👡 Right Click (Shot Log) = Link / Play Video"
    )

    self.highlight_artist = None
