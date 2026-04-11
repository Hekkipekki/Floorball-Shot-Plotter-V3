def center_popup_in_canvas(app, width=260, height=220, top_offset=150):
    canvas_widget = app.canvas.get_tk_widget()
    canvas_widget.update_idletasks()
    x_canvas = canvas_widget.winfo_rootx()
    y_canvas = canvas_widget.winfo_rooty()
    canvas_width = canvas_widget.winfo_width()
    x = x_canvas + (canvas_width - width) // 2
    y = y_canvas + top_offset
    return x, y


def format_geometry_string(width, height, x, y):
    return f"{width}x{height}+{x}+{y}"


def prepare_popup(popup, app, width=260, height=220, top_offset=400):
    popup.withdraw()
    popup.update_idletasks()
    x, y = center_popup_in_canvas(app, width, height, top_offset)
    popup.geometry(format_geometry_string(width, height, x, y))
    popup.deiconify()