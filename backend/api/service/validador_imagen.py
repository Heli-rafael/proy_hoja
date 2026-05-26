import base64
import json

from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def validar_imagen_planta(image_file):

    image_bytes = image_file.read()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:image/jpeg;base64,{base64_image}"

    system_prompt = """
Eres un sistema de validación de imágenes agrícolas.

TAREA:
Determinar si la imagen contiene hojas de planta de papa (Solanum tuberosum) y si es útil para análisis.

REGLAS ESTRICTAS:
- Responde SOLO JSON válido.
- NO texto adicional.
- NO explicaciones.
- NO markdown.

DEFINICIONES:

es_planta_papa:
- true SOLO si estás seguro de que son hojas de papa.
- false si es cualquier otra planta o no estás seguro.

es_apta_para_analisis:
- true SOLO si:
  - es planta de papa
  - las hojas son claramente visibles y evaluables
- false en cualquier otro caso (borroso, lejos, parcial, duda)

PRINCIPIO CLAVE:
- Si hay duda → SIEMPRE false

FORMATO OBLIGATORIO:

{
  "es_planta_papa": boolean,
  "es_apta_para_analisis": boolean,
  "motivo": string
}

MOTIVO:
- corto
- simple
- explica por qué se aceptó o rechazó la imagen
"""
    
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Valida si la imagen es adecuada para análisis de enfermedad en hoja de papa."
                    },
                    {
                        "type": "input_image",
                        "image_url": data_url,
                        "detail": "low"
                    }
                ]
            }
        ],
        text={
            "format": {
                "type": "json_object"
            }
        }
    )

    return json.loads(response.output_text)