import base64
import json
import re
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from google import genai
import math


# =========================
# CONFIG GEMINI (NUEVO SDK)
# =========================

client = genai.Client(api_key=settings.GEMINI_API_KEY)

# =========================
# UTILIDADES
# =========================

def to_data_url(image_bytes: bytes) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(image_bytes).decode("utf-8")


def safe_json_extract(text: str):
    """
    Extrae JSON aunque Gemini agregue texto extra.
    """
    try:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            return None
        return json.loads(match.group())
    except Exception:
        return None


# =========================
# FUNCION PRINCIPAL
# =========================

def generar_imagen_anotada(image_file, diagnostico=None):

    image_file.seek(0)
    image_bytes = image_file.read()

    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    width, height = image.size

    # =========================
    # 1. GEMINI DETECTION
    # =========================

    prompt = f"""
Eres un sistema experto en análisis agrícola de hojas de papa (Solanum tuberosum).

OBJETIVO:
Detectar SOLO zonas dañadas visibles en la hoja.

REGLAS CRÍTICAS:
- Ignora fondo, mesa, sombras.
- Ignora venas normales.
- Solo detecta daño real y visible.
- Si no estás seguro, NO detectes nada.

TIPOS:
- necrosis
- mancha
- clorosis
- hongo
- otro

FORMATO OBLIGATORIO (SOLO JSON):
{{
  "damages": [
    {{
      "type": "string",
      "confidence": number,
      "bbox": {{
        "x1": number,
        "y1": number,
        "x2": number,
        "y2": number
      }}
    }}
  ]
}}

REGLAS IMPORTANTES:
- Coordenadas NORMALIZADAS (0 a 1)
- Relativas SOLO a la hoja
- x1 < x2, y1 < y2
- Si no hay daño: {{"damages": []}}

Imagen tamaño: {width}x{height}
"""

    try:

        response = client.models.generate_content(
            # gemini-2.5-flash
            # gemini-flash-latest
            model="gemini-flash-latest",
            contents=[
                prompt,
                image
            ]
        )
    
    except Exception as e:
        print("ERROR GEMINI:", e)
        raise

    data = safe_json_extract(response.text)
    damages = data.get("damages", []) if data else []

    # =========================
    # 2. DIBUJO
    # =========================
    scale = min(width, height) / 800
    draw = ImageDraw.Draw(image)

    try:
        font_size = max(10, int(14 * scale))
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    for d in damages:
        try:
            bbox = d.get("bbox", {})

            x1 = float(bbox.get("x1", 0)) * width
            y1 = float(bbox.get("y1", 0)) * height
            x2 = float(bbox.get("x2", 0)) * width
            y2 = float(bbox.get("y2", 0)) * height

            if x2 <= x1 or y2 <= y1:
                continue

            # clamp
            x1 = max(0, min(x1, width))
            x2 = max(0, min(x2, width))
            y1 = max(0, min(y1, height))
            y2 = max(0, min(y2, height))

            # =========================
            # BOX PRINCIPAL (DAÑO)
            # =========================
            draw.rectangle(
                (x1, y1, x2, y2),
                outline=(255, 0, 0),
                width=max(2, int(2 * scale))
            )

            # =========================
            # TEXTO
            # =========================
            label = d.get("type", "damage")
            conf = float(d.get("confidence", 0))
            text = f"{label} {conf:.2f}"

            # tamaño del texto
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_w = text_bbox[2] - text_bbox[0]
            text_h = text_bbox[3] - text_bbox[1]

            # padding del label (INTERNO del fondo blanco)
            pad_x = max(3, int(4 * scale))
            pad_y = max(2, int(3 * scale))

            # separación entre bbox rojo y label
            offset = max(4, int(6 * scale))

            # posición base (arriba del bbox)
            text_x = x1 + int(5 * scale)
            text_y = y1 - text_h - offset

            # si no cabe arriba, lo ponemos abajo
            if text_y < 0:
                text_y = y2 + offset

            # =========================
            # FONDO BLANCO (CON PADDING REAL)
            # =========================
            bg_x1 = text_x - pad_x
            bg_y1 = text_y - pad_y
            bg_x2 = text_x + text_w + pad_x
            bg_y2 = text_y + text_h + pad_y

            draw.rectangle(
                (bg_x1, bg_y1, bg_x2, bg_y2),
                fill=(255, 255, 255)
            )

            # =========================
            # TEXTO (CENTRADO VISUAL)
            # =========================
            vertical_lift = max(1, int(2 * scale))
            text_y_centered = bg_y1 + pad_y - vertical_lift

            draw.text(
                (text_x, text_y_centered),
                text,
                fill=(255, 0, 0),
                font=font
            )

        except Exception:
            continue

    # =========================
    # 4. EXPORT
    # =========================

    output = BytesIO()
    image.save(output, format="PNG")
    output.seek(0)

    return ContentFile(output.read(), name="diagnostico_gemini.png")