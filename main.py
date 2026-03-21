import tkinter as tk
from core.app_controller import FloorballShotPlotter

if __name__ == "__main__":
    root = tk.Tk()
    app = FloorballShotPlotter(root)
    root.mainloop()
