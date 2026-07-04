DEFAULT_POPUP_WIDTH = 260
DEFAULT_POPUP_HEIGHT = 220
DEFAULT_CENTER_TOP_OFFSET = 150
DEFAULT_PREPARE_TOP_OFFSET = 400


def _canvas_bounds(app):
    canvas_widget = app.canvas.get_tk_widget()
    canvas_widget.update_idletasks()
    return (
        canvas_widget.winfo_rootx(),
        canvas_widget.winfo_rooty(),
        canvas_widget.winfo_width(),
    )


def center_popup_in_canvas(
    app,
    width=DEFAULT_POPUP_WIDTH,
    height=DEFAULT_POPUP_HEIGHT,
    top_offset=DEFAULT_CENTER_TOP_OFFSET,
):
    x_canvas, y_canvas, canvas_width = _canvas_bounds(app)
    x = x_canvas + (canvas_width - width) // 2
    y = y_canvas + top_offset
    return x, y


def format_geometry_string(width, height, x, y):
    return f"{width}x{height}+{x}+{y}"


def prepare_popup(
    popup,
    app,
    width=DEFAULT_POPUP_WIDTH,
    height=DEFAULT_POPUP_HEIGHT,
    top_offset=DEFAULT_PREPARE_TOP_OFFSET,
):
    popup.withdraw()
    popup.update_idletasks()
    x, y = center_popup_in_canvas(app, width, height, top_offset)
    popup.geometry(format_geometry_string(width, height, x, y))
    popup.deiconify()
