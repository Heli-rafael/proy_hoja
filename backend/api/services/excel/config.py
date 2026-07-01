from openpyxl import Workbook


EXCEL_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


def create_workbook(title: str):
    wb = Workbook()
    ws = wb.active
    ws.title = title
    return wb, ws