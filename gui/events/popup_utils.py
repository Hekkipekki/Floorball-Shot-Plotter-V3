DEFAULT_POPUP_WIDTH = 260
DEFAULT_POPUP_HEIGHT = 220


def _canvas_bounds(app):
    canvas_widget = app.canvas.get_tk_widget()
    canvas_widget.update_idletasks()
    return (
        canvas_widget.winfo_rootx(),
        canvas_widget.winfo_rooty(),
        canvas_widget.winfo_width(),
        canvas_widget.winfo_height(),
    )


def center_popup_in_canvas(app, width=DEFAULT_POPUP_WIDTH, height=DEFAULT_POPUP_HEIGHT):
    x_canvas, y_canvas, canvas_width, canvas_height = _canvas_bounds(app)
    x = x_canvas + max(0, (canvas_width - width) // 2)
    y = y_canvas + max(0, (canvas_height - height) // 2)
    return x, y


def format_geometry_string(width, height, x, y):
    return f"{width}x{height}+{x}+{y}"


def prepare_popup(popup, app, width=DEFAULT_POPUP_WIDTH, height=DEFAULT_POPUP_HEIGHT):
    popup.withdraw()
    popup.update_idletasks()
    x, y = center_popup_in_canvas(app, width, height)
    popup.geometry(format_geometry_string(width, height, x, y))
    popup.deiconify()
