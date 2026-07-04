import tkinter as tk

from runtime_bootstrap import configure_bundled_vlc
from core.app_controller import FloorballShotPlotter


def main() -> None:
    configure_bundled_vlc()
    root = tk.Tk()
    FloorballShotPlotter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
