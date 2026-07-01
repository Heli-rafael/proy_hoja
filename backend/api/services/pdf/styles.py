from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors

header_style = ParagraphStyle(
    "header_style",
    fontSize=10,
    textColor=colors.white,
    fontName="Helvetica-Bold",
    alignment=1
)

body_style = ParagraphStyle(
    "body_style",
    fontSize=9,
    textColor=colors.black,
    fontName="Helvetica"
)