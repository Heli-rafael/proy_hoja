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
Eres un sistema de validación de imágenes botánicas.

TAREA:
Determinar si la imagen contiene HOJAS DE PLANTAS (cualquier especie) y si es útil para análisis.

REGLAS ESTRICTAS:
- Responde SOLO JSON válido.
- NO texto adicional.
- NO explicaciones fuera del JSON.
- NO markdown.

DEFINICIONES:

es_hoja_planta:
- true SOLO si la imagen contiene hojas reales de una planta (cualquier especie).
- false si es cualquier otro objeto (papel, mano, animal, comida, tierra sin hojas, etc.).
- false si no estás seguro.

es_apta_para_analisis:
- true SOLO si:
  - es hoja de planta = true
  - las hojas son claramente visibles
  - la imagen tiene buena nitidez y permite análisis visual
- false en cualquier otro caso (borroso, lejos, parcial, duda, mala iluminación)

PRINCIPIO CLAVE:
- Si hay duda → SIEMPRE false

FORMATO OBLIGATORIO:

{
  "es_hoja_planta": boolean,
  "es_apta_para_analisis": boolean,
  "motivo": string
}

MOTIVO:
- corto
- claro
- explica rechazo o aceptación de forma simple
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