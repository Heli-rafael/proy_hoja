import base64
import json
import re
from io import BytesIO

from openai import OpenAI
from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def to_data_url(image_bytes: bytes) -> str:
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


def generar_imagen_anotada(image_file, diagnostico=None):
    image_file.seek(0)
    image_bytes = image_file.read()

    # abrir imagen
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    width, height = image.size

    image_url = to_data_url(image_bytes)

    # ----------------------------
    # 1. VISIÓN IA (SIN response_format para compatibilidad)
    # ----------------------------
    response = client.responses.create(
        model="gpt-4o",
        temperature=0,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"""
Eres un sistema experto en visión agrícola de alta precisión.

La imagen tiene dimensiones exactas:
width = {width}
height = {height}

OBJETIVO:
Detectar TODAS las lesiones visibles en hojas.

RESPONDE SOLO JSON VÁLIDO:

{{
  "damages": [
    {{
      "type": "necrosis|mancha|clorosis|hongo|otro",
      "confidence": 0.0,
      "bbox": {{
        "x1": 0.0,
        "y1": 0.0,
        "x2": 0.0,
        "y2": 0.0
      }}
    }}
  ]
}}

REGLAS CRÍTICAS:
- Coordenadas NORMALIZADAS (0 a 1)
- bbox debe ajustarse EXACTAMENTE al daño visible
- NO incluir sombras, fondo o ruido
- cada daño es independiente
- máxima precisión espacial
- NO texto adicional
"""
                    },
                    {
                        "type": "input_image",
                        "image_url": image_url
                    }
                ]
            }
        ]
    )

    # ----------------------------
    # 2. PARSEO ROBUSTO (ANTI-ERRORES)
    # ----------------------------
    try:
        raw = response.output_text.strip()

        match = re.search(r"\{.*\}", raw, re.S)
        if match:
            data = json.loads(match.group())
            damages = data.get("damages", [])
        else:
            damages = []

    except Exception:
        damages = []

    # ----------------------------
    # 3. DIBUJO EN IMAGEN (CORRECTO Y ESTABLE)
    # ----------------------------
    draw = ImageDraw.Draw(image)

    for d in damages:
        try:
            bbox = d.get("bbox", {})

            x1 = float(bbox["x1"]) * width
            y1 = float(bbox["y1"]) * height
            x2 = float(bbox["x2"]) * width
            y2 = float(bbox["y2"]) * height

            # validación básica anti-errores del modelo
            if x2 <= x1 or y2 <= y1:
                continue

            draw.rectangle(
                (x1, y1, x2, y2),
                outline=(255, 0, 0),
                width=3
            )

            label = d.get("type", "damage")
            confidence = d.get("confidence", 0)

            draw.text(
                (x1, max(0, y1 - 12)),
                f"{label} {confidence:.2f}",
                fill=(255, 0, 0)
            )

        except Exception:
            continue

    # ----------------------------
    # 4. EXPORTAR IMAGEN FINAL
    # ----------------------------
    output = BytesIO()
    image.save(output, format="PNG")
    output.seek(0)

    return ContentFile(output.read(), name="diagnostico_ai.png")