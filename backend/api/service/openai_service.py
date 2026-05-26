import base64
import json

from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def analizar_planta_con_openai(image_file):

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
Eres un fitopatólogo experto.

Analiza la planta y detecta enfermedades visibles.

Devuelve SOLO JSON válido:

{
  "nombre_planta": string,
  "descripcion_planta": string,
  "enfermedad_detectada": string,
  "severidad": "Leve" | "Moderada" | "Grave",
  "porcentaje_salud": number,
  "confianza_ia": number,
  "tratamiento_natural": string,
  "tratamiento_quimico": string,
  "prevencion": string
}

REGLAS:
- no agregues markdown
- no agregues texto extra
- devuelve solo JSON
- los campos "tratamiento_natural", "tratamiento_quimico" y "prevencion" deben ser STRINGS
- cada punto debe estar separado por el carácter literal "\n" (backslash + n)
- NO uses saltos de línea reales dentro del texto
- NO uses líneas nuevas reales en la respuesta
- NO agregues espacios después de "\n"
- NO termines con "\n"
- el último punto debe terminar con "."
- ejemplo exacto de formato:
  "Aplicar ajo.\nRetirar hojas.\nEvitar humedad."
"""
                },
                {
                    "type": "input_image",
                    "image_url": data_url,
                    "detail": "high"
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



def generar_respuesta_chat(
    pregunta_usuario,
    diagnostico
):
    """
    Genera respuesta inteligente basada en:
    - enfermedad detectada
    - tratamiento
    - severidad
    - salud planta
    - pregunta del usuario
    """

    prompt = f"""
Eres fitopatólogo experto en diagnóstico de enfermedades de plantas.

Solo puedes usar la información del DIAGNOSTICO. Puedes conocimiento externo si esta referenciado del diagnostico.

DIAGNOSTICO:
Enfermedad: {diagnostico.enfermedad_detectada}
Severidad: {diagnostico.severidad}
Salud: {diagnostico.porcentaje_salud}%
Tratamiento natural: {diagnostico.tratamiento_natural}
Tratamiento quimico: {diagnostico.tratamiento_quimico}
Prevención: {diagnostico.prevencion}

PREGUNTA: {pregunta_usuario}

REGLAS:
- Responde SOLO si la pregunta se relaciona directamente con el DIAGNOSTICO.
- Si no está relacionada, responde EXACTO:
"Esa pregunta no está relacionada con el diagnóstico de la planta."
- Si es relevante, responde usando SOLO el DIAGNOSTICO (no inventes nada).
- Respuesta máxima: 80 palabras.
- Sé claro, directo y técnico pero simple.

IMPORTANTE:
- Es una plataforma sobre detección de enfermedades de hojas.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text