# ============================================================
# IMPORTACIONES
# ============================================================

from reportlab.lib import colors
from reportlab.lib.enums import (
    TA_LEFT,
    TA_CENTER,
    TA_JUSTIFY,
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.units import cm
from reportlab.platypus import TableStyle


# ============================================================
# CONFIGURACIÓN GENERAL DEL DOCUMENTO
# ============================================================

PAGE_SIZE = A4

MARGIN = 2 * cm

MARGIN_TOP = 2 * cm
MARGIN_BOTTOM = 2 * cm
MARGIN_LEFT = 2 * cm
MARGIN_RIGHT = 2 * cm


# ============================================================
# COLORES
# ============================================================

PRIMARY = colors.HexColor("#10B981")
PRIMARY_DARK = colors.HexColor("#047857")

DARK = colors.HexColor("#111827")
GRAY = colors.HexColor("#6B7280")

LIGHT = colors.HexColor("#E5E7EB")
LIGHT_BG = colors.HexColor("#F3F4F6")

WHITE = colors.white
BLACK = colors.black

# ============================================================
# TIPOGRAFÍA
# ============================================================

FONT_NAME = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_ITALIC = "Helvetica-Oblique"


# ============================================================
# TAMAÑOS DE FUENTE
# ============================================================

FONT_SIZE_BODY = 11
FONT_SIZE_SMALL = 9

FONT_SIZE_TITLE = 20

FONT_SIZE_H1 = 16
FONT_SIZE_H2 = 13
FONT_SIZE_H3 = 11


# ============================================================
# ESPACIADO
# ============================================================

LINE_SPACING = 1.35

SPACE_BEFORE_TITLE = 0
SPACE_AFTER_TITLE = 14

SPACE_BEFORE_H1 = 16
SPACE_AFTER_H1 = 8

SPACE_BEFORE_H2 = 12
SPACE_AFTER_H2 = 6

SPACE_BEFORE_H3 = 10
SPACE_AFTER_H3 = 4

SPACE_AFTER_PARAGRAPH = 8


# ============================================================
# CONFIGURACIÓN DE VIÑETAS
# ============================================================

BULLET_INDENT = 18
BULLET_LEFT_INDENT = 22

NUMBER_LEFT_INDENT = 22


# ============================================================
# CONFIGURACIÓN DE COMPONENTES DE DIBUJO
# ============================================================

# Texto simple utilizado por draw_text()
DRAW_TEXT_FONT = FONT_NAME
DRAW_TEXT_FONT_SIZE = 10
DRAW_TEXT_LEADING = 14


# Títulos utilizados por draw_title()
DRAW_TITLE_FONT = FONT_BOLD
DRAW_TITLE_FONT_SIZE = 18
DRAW_TITLE_LEADING = 25


# Subtítulos utilizados por draw_subtitle()
DRAW_SUBTITLE_FONT = FONT_BOLD
DRAW_SUBTITLE_FONT_SIZE = 12
DRAW_SUBTITLE_LEADING = 18


# ============================================================
# CONFIGURACIÓN DE IMÁGENES
# ============================================================

IMAGE_MAX_WIDTH = 800
IMAGE_MAX_HEIGHT = 800

IMAGE_JPEG_QUALITY = 50


# ============================================================
# ESTILOS BASE DE REPORTLAB
# ============================================================

styles = getSampleStyleSheet()


# ============================================================
# TEXTO NORMAL
# ============================================================

BODY = ParagraphStyle(
    "Body",
    parent=styles["Normal"],
    fontName=FONT_NAME,
    fontSize=FONT_SIZE_BODY,
    leading=FONT_SIZE_BODY * LINE_SPACING,
    textColor=DARK,
    alignment=TA_JUSTIFY,
    spaceBefore=0,
    spaceAfter=SPACE_AFTER_PARAGRAPH,
)


# ============================================================
# TEXTO ALINEADO A LA IZQUIERDA
# ============================================================

BODY_LEFT = ParagraphStyle(
    "BodyLeft",
    parent=BODY,
    alignment=TA_LEFT,
)


# ============================================================
# TEXTO PEQUEÑO
# ============================================================

SMALL = ParagraphStyle(
    "Small",
    parent=BODY,
    fontName=FONT_NAME,
    fontSize=FONT_SIZE_SMALL,
    leading=FONT_SIZE_SMALL * 1.3,
    textColor=GRAY,
    alignment=TA_LEFT,
)


# ============================================================
# TÍTULO PRINCIPAL
# ============================================================

TITLE = ParagraphStyle(
    "TitleCustom",
    parent=styles["Title"],
    fontName=FONT_BOLD,
    fontSize=FONT_SIZE_TITLE,
    leading=FONT_SIZE_TITLE * 1.2,
    textColor=DARK,
    alignment=TA_CENTER,
    spaceBefore=SPACE_BEFORE_TITLE,
    spaceAfter=SPACE_AFTER_TITLE,
)


# ============================================================
# TÍTULO NIVEL 1
# ============================================================

H1 = ParagraphStyle(
    "Heading1Custom",
    parent=styles["Heading1"],
    fontName=FONT_BOLD,
    fontSize=FONT_SIZE_H1,
    leading=FONT_SIZE_H1 * 1.25,
    textColor=PRIMARY_DARK,
    alignment=TA_LEFT,
    spaceBefore=SPACE_BEFORE_H1,
    spaceAfter=SPACE_AFTER_H1,
    keepWithNext=True,
)


# ============================================================
# TÍTULO NIVEL 2
# ============================================================

H2 = ParagraphStyle(
    "Heading2Custom",
    parent=styles["Heading2"],
    fontName=FONT_BOLD,
    fontSize=FONT_SIZE_H2,
    leading=FONT_SIZE_H2 * 1.25,
    textColor=DARK,
    alignment=TA_LEFT,
    spaceBefore=SPACE_BEFORE_H2,
    spaceAfter=SPACE_AFTER_H2,
    keepWithNext=True,
)


# ============================================================
# TÍTULO NIVEL 3
# ============================================================

H3 = ParagraphStyle(
    "Heading3Custom",
    parent=styles["Heading3"],
    fontName=FONT_BOLD,
    fontSize=FONT_SIZE_H3,
    leading=FONT_SIZE_H3 * 1.25,
    textColor=DARK,
    alignment=TA_LEFT,
    spaceBefore=SPACE_BEFORE_H3,
    spaceAfter=SPACE_AFTER_H3,
    keepWithNext=True,
)


# ============================================================
# VIÑETAS
# ============================================================

BULLET = ParagraphStyle(
    "BulletCustom",
    parent=BODY,
    leftIndent=BULLET_LEFT_INDENT,
    firstLineIndent=-BULLET_INDENT,
    bulletIndent=0,
    spaceAfter=5,
    alignment=TA_LEFT,
)


# ============================================================
# NUMERACIÓN
# ============================================================

NUMBERED = ParagraphStyle(
    "NumberedCustom",
    parent=BODY,
    leftIndent=NUMBER_LEFT_INDENT,
    firstLineIndent=-NUMBER_LEFT_INDENT,
    spaceAfter=5,
    alignment=TA_LEFT,
)


# ============================================================
# TEXTO DESTACADO
# ============================================================

QUOTE = ParagraphStyle(
    "Quote",
    parent=BODY,
    leftIndent=20,
    rightIndent=20,
    fontName=FONT_ITALIC,
    textColor=GRAY,
    borderColor=LIGHT,
    borderWidth=1,
    borderPadding=8,
    backColor=LIGHT_BG,
    alignment=TA_LEFT,
)


# ============================================================
# ESTILO GENERAL DE TABLAS
# ============================================================

TABLE_HEADER = TableStyle([

    # --------------------------------------------------------
    # CABECERA
    # --------------------------------------------------------

    (
        "BACKGROUND",
        (0, 0),
        (-1, 0),
        PRIMARY,
    ),

    (
        "TEXTCOLOR",
        (0, 0),
        (-1, 0),
        WHITE,
    ),

    (
        "FONTNAME",
        (0, 0),
        (-1, 0),
        FONT_BOLD,
    ),

    (
        "FONTSIZE",
        (0, 0),
        (-1, 0),
        FONT_SIZE_SMALL,
    ),

    # --------------------------------------------------------
    # CUERPO
    # --------------------------------------------------------

    (
        "FONTNAME",
        (0, 1),
        (-1, -1),
        FONT_NAME,
    ),

    (
        "FONTSIZE",
        (0, 1),
        (-1, -1),
        FONT_SIZE_SMALL,
    ),

    (
        "TEXTCOLOR",
        (0, 1),
        (-1, -1),
        DARK,
    ),

    # --------------------------------------------------------
    # BORDES
    # --------------------------------------------------------

    (
        "GRID",
        (0, 0),
        (-1, -1),
        0.5,
        LIGHT,
    ),

    (
        "BOX",
        (0, 0),
        (-1, -1),
        0.8,
        LIGHT,
    ),

    # --------------------------------------------------------
    # ALINEACIÓN
    # --------------------------------------------------------

    (
        "VALIGN",
        (0, 0),
        (-1, -1),
        "TOP",
    ),

    # --------------------------------------------------------
    # PADDING
    # --------------------------------------------------------

    (
        "LEFTPADDING",
        (0, 0),
        (-1, -1),
        6,
    ),

    (
        "RIGHTPADDING",
        (0, 0),
        (-1, -1),
        6,
    ),

    (
        "TOPPADDING",
        (0, 0),
        (-1, -1),
        6,
    ),

    (
        "BOTTOMPADDING",
        (0, 0),
        (-1, -1),
        6,
    ),

    # --------------------------------------------------------
    # FILAS ALTERNADAS
    # --------------------------------------------------------

    (
        "ROWBACKGROUNDS",
        (0, 1),
        (-1, -1),
        [
            WHITE,
            LIGHT_BG,
        ],
    ),
])


# ============================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================

PAGE_CONFIG = {
    "pagesize": PAGE_SIZE,
    "leftMargin": MARGIN_LEFT,
    "rightMargin": MARGIN_RIGHT,
    "topMargin": MARGIN_TOP,
    "bottomMargin": MARGIN_BOTTOM,
}




# ============================================================
# COLORES DE ESTADO DE SALUD
# ============================================================

# 0 - 20% | CRÍTICO
HEALTH_CRITICAL = colors.HexColor("#EF4444")
HEALTH_CRITICAL_LIGHT = colors.HexColor("#FEE2E2")


# 21 - 40% | MUY BAJO
HEALTH_VERY_LOW = colors.HexColor("#F97316")
HEALTH_VERY_LOW_LIGHT = colors.HexColor("#FFEDD5")


# 41 - 60% | BAJO
HEALTH_LOW = colors.HexColor("#D946EF")
HEALTH_LOW_LIGHT = colors.HexColor("#FAE8FF")


# 61 - 80% | MODERADO
HEALTH_MODERATE = colors.HexColor("#22C55E")
HEALTH_MODERATE_LIGHT = colors.HexColor("#DCFCE7")


# 81 - 100% | SALUDABLE
HEALTH_HEALTHY = colors.HexColor("#10B981")
HEALTH_HEALTHY_LIGHT = colors.HexColor("#D1FAE5")


# ============================================================
# NOTA INFORMATIVA
# ============================================================

NOTE_BLUE = colors.HexColor("#3B82F6")
NOTE_BLUE_DARK = colors.HexColor("#1E40AF")
NOTE_BLUE_LIGHT = colors.HexColor("#EFF6FF")


# ============================================================
# TABLA COLOR TEXTO
# ============================================================
TABLE_TEXT_WHITE = ParagraphStyle(
    "TableTextWhite",
    parent=SMALL,
    fontName=FONT_BOLD,
    textColor=WHITE,
)