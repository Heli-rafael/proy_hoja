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
  "es_planta_papa": true,
  "es_apta_para_analisis": true,
  "motivo": ""
}

REGLAS ESTRICTAS:
- es_planta_papa = true SOLO si la imagen contiene hojas de planta de PAPA (Solanum tuberosum).
- Si es cualquier otra planta (maíz, tomate, maleza, ornamentales, etc.), es_planta_papa = false.
- es_apta_para_analisis = true SOLO si:
  - Se observan claramente hojas de papa.
  - Las hojas permiten un análisis visual (no borrosas, no ocultas, no demasiado pequeñas).
- Si NO es planta de papa o no hay hojas visibles de papa:
  - es_planta_papa = false
  - es_apta_para_analisis = false
- NO inventes.
- NO asumas.
- Si tienes duda, responde false.
- NO expliques nada fuera del JSON.
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