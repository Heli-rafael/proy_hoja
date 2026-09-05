# ============================================================
# IMPORTACIONES
# ============================================================

import io
import os

from PIL import Image

from reportlab.lib.utils import ImageReader

from . import styles


# ============================================================
# OPTIMIZACIÓN DE IMÁGENES
# ============================================================

def optimize_image(
    path,
    max_size=(
        styles.IMAGE_MAX_WIDTH,
        styles.IMAGE_MAX_HEIGHT,
    ),
):
    """
    Abre una imagen, reduce su tamaño y la convierte
    en un ImageReader compatible con ReportLab.
    """

    try:

        if not path:
            return None

        if not os.path.exists(path):
            return None

        img = Image.open(path)

        # ----------------------------------------------------
        # Convertir imágenes con transparencia
        # ----------------------------------------------------

        if img.mode in (
            "RGBA",
            "LA",
            "P",
        ):
            background = Image.new(
                "RGB",
                img.size,
                "white",
            )

            if img.mode == "P":
                img = img.convert("RGBA")

            if img.mode in (
                "RGBA",
                "LA",
            ):
                background.paste(
                    img,
                    mask=img.getchannel("A"),
                )

            img = background

        else:
            img = img.convert("RGB")

        # ----------------------------------------------------
        # Reducir tamaño
        # ----------------------------------------------------

        img.thumbnail(
            max_size,
            Image.Resampling.LANCZOS,
        )

        # ----------------------------------------------------
        # Guardar temporalmente en memoria
        # ----------------------------------------------------

        buffer = io.BytesIO()

        img.save(
            buffer,
            format="JPEG",
            quality=styles.IMAGE_JPEG_QUALITY,
            optimize=True,
        )

        buffer.seek(0)

        return ImageReader(buffer)

    except Exception:
        return None


# ============================================================
# DIBUJAR TEXTO
# ============================================================

def draw_text(
    p,
    text,
    y,
    margin,
    color=None,
    indent=0,
):
    """
    Dibuja una línea de texto y devuelve la nueva posición Y.
    """

    if color is None:
        color = styles.DARK

    p.setFillColor(color)

    p.setFont(
        styles.DRAW_TEXT_FONT,
        styles.DRAW_TEXT_FONT_SIZE,
    )

    p.drawString(
        margin + indent,
        y,
        str(text),
    )

    return y - styles.DRAW_TEXT_LEADING

def draw_text_center(p, text, y, color):
    center_x = p._pagesize[0] / 2

    p.setFillColor(color)
    p.setFont(
        styles.FONT_NAME,
        styles.FONT_SIZE_SMALL,
    )

    p.drawCentredString(
        center_x,
        y,
        text,
    )

# ============================================================
# DIBUJAR TÍTULO
# ============================================================

def draw_title(
    p,
    text,
    y,
    margin,
    color=None,
):
    """
    Dibuja un título principal.
    """

    if color is None:
        color = styles.DARK

    p.setFillColor(color)

    p.setFont(
        styles.DRAW_TITLE_FONT,
        styles.DRAW_TITLE_FONT_SIZE,
    )

    p.drawString(
        margin,
        y,
        str(text),
    )

    return y - styles.DRAW_TITLE_LEADING

def draw_title_center(p, text, y, color):
    center_x = p._pagesize[0] / 2

    p.setFillColor(color)
    p.setFont(
        styles.FONT_BOLD,
        styles.FONT_SIZE_TITLE,
    )

    p.drawCentredString(
        center_x,
        y,
        text,
    )


# ============================================================
# DIBUJAR SUBTÍTULO
# ============================================================

def draw_subtitle(
    p,
    text,
    y,
    margin,
    color=None,
):
    """
    Dibuja un subtítulo/sección.
    """

    if color is None:
        color = styles.PRIMARY

    p.setFillColor(color)

    p.setFont(
        styles.DRAW_SUBTITLE_FONT,
        styles.DRAW_SUBTITLE_FONT_SIZE,
    )

    p.drawString(
        margin,
        y,
        str(text),
    )

    return y - styles.DRAW_SUBTITLE_LEADING


def draw_subtitle_center(p, text, y, color):
    center_x = p._pagesize[0] / 2

    p.setFillColor(color)
    p.setFont(
        styles.FONT_BOLD,
        styles.FONT_SIZE_H2,
    )

    p.drawCentredString(
        center_x,
        y,
        text,
    )

# ============================================================
# DIBUJAR IMAGEN
# ============================================================

def draw_image(
    p,
    path,
    x,
    y,
    w=240,
    h=160,
):
    """
    Optimiza y dibuja una imagen en el PDF.

    Si la imagen no existe o no puede procesarse,
    simplemente no se dibuja.
    """

    try:

        if not path:
            return False

        if not os.path.exists(path):
            return False

        img = optimize_image(path)

        if not img:
            return False

        p.drawImage(
            img,
            x,
            y,
            width=w,
            height=h,
            mask="auto",
            preserveAspectRatio=True,
            anchor="c",
        )

        return True

    except Exception:
        return False


# ============================================================
# DIBUJAR LÍNEA DIVISORIA
# ============================================================

def draw_divider(
    p,
    y,
    margin_left=None,
    margin_right=None,
    color=None,
    width=0.8,
):
    """
    Dibuja una línea horizontal para separar secciones.
    """

    if margin_left is None:
        margin_left = styles.MARGIN_LEFT

    if margin_right is None:
        margin_right = styles.MARGIN_RIGHT

    if color is None:
        color = styles.LIGHT

    p.setStrokeColor(color)

    p.setLineWidth(width)

    p.line(
        margin_left,
        y,
        p._pagesize[0] - margin_right,
        y,
    )


# ============================================================
# DIBUJAR PIE DE PÁGINA
# ============================================================

def draw_footer(
    p,
    text,
    y=42,
    color=None,
    font_size=8,
):
    """
    Dibuja un texto centrado como pie de página.
    """

    if color is None:
        color = styles.GRAY

    p.setFillColor(color)

    p.setFont(
        styles.FONT_NAME,
        font_size,
    )

    width = p._pagesize[0]

    p.drawCentredString(
        width / 2,
        y,
        str(text),
    )


# ============================================================
# DIBUJAR TEXTO CENTRADO
# ============================================================

def draw_centered_text(
    p,
    text,
    y,
    color=None,
    font=None,
    font_size=None,
):
    """
    Dibuja texto centrado horizontalmente.
    """

    if color is None:
        color = styles.DARK

    if font is None:
        font = styles.FONT_NAME

    if font_size is None:
        font_size = styles.FONT_SIZE_BODY

    p.setFillColor(color)

    p.setFont(
        font,
        font_size,
    )

    width = p._pagesize[0]

    p.drawCentredString(
        width / 2,
        y,
        str(text),
    )


# ============================================================
# DIBUJAR LISTA CON VIÑETAS
# ============================================================

def draw_bullet_list(
    p,
    items,
    y,
    margin,
    color=None,
    indent=10,
):
    """
    Dibuja una lista simple de elementos.
    """

    if color is None:
        color = styles.GRAY

    if not items:
        return y

    for item in items:

        y = draw_text(
            p,
            f"• {item}",
            y,
            margin,
            color,
            indent=indent,
        )

    return y
