import os
import sys

def get_project_root():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        # Gå upp tills vi hittar main.py eller Floorball Shot Plotter-roten
        path = os.path.abspath(__file__)
        while True:
            path = os.path.dirname(path)
            if os.path.exists(os.path.join(path, "main.py")) or path == os.path.dirname(path):
                break
        return path