from openpyxl.styles import Font


HEADER_FONT = Font(bold=True)


def apply_header_style(ws):
    for cell in ws[1]:
        cell.font = HEADER_FONT