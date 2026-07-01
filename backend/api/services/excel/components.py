from .styles import apply_header_style


def add_header(ws, headers):
    ws.append(headers)
    apply_header_style(ws)


def add_row(ws, values):
    ws.append(values)