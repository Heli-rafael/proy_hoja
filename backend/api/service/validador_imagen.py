import base64
import json

from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def validar_imagen_planta(image_file):

    image_bytes = image_file.read()

    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    data_url = f"data:image/jpeg;base64,{base64_image}"

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": """
Analiza la imagen.

Responde SOLO JSON válido.

{
  "es_planta": true,
  "es_apta_para_analisis": true,
  "motivo": ""
}

REGLAS:
- es_planta = true SOLO si hay planta real.
- es_apta_para_analisis = true SOLO si hay hojas visibles.
- Si la imagen no contiene plantas o no permite analizar hojas:
  devuelve false.
- NO expliques.
- SOLO JSON.
"""
                },
                {
                    "type": "input_image",
                    "image_url": data_url,
                    "detail": "low"
                }
            ]
        }],
        text={
            "format": {
                "type": "json_object"
            }
        }
    )

    return json.loads(response.output_text)