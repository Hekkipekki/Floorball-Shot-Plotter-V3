import tkinter as tk

from core.app_controller import FloorballShotPlotter


def main() -> None:
    root = tk.Tk()
    FloorballShotPlotter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
