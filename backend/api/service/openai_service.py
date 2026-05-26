import base64
import json

from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def analizar_planta_con_openai(image_file):

    image_bytes = image_file.read()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:image/jpeg;base64,{base64_image}"

    system_prompt = """
Eres un fitopatólogo experto en análisis de plantas.

REGLAS ESTRICTAS:
- Devuelve SOLO JSON válido.
- NO texto adicional.
- NO markdown.
- NO explicaciones.

- NO inventes información fuera de la imagen.
- Si no estás seguro, usa valores conservadores.

FORMATO OBLIGATORIO:

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

REGLAS DE TEXTO:
- en "nombre_planta" me devuelves "Hoja de papa" porque ya tengo otro filtro que valida la hoja.
- "enfermedad_detectada" DEBE ser SOLO el nombre común exacto.
- PROHIBIDO incluir nombres científicos.
- PROHIBIDO usar paréntesis, comas o explicaciones.
- los campos "tratamiento_natural", "tratamiento_quimico" y "prevencion" deben ser STRINGS
- cada punto debe estar separado por el carácter literal "\n" (backslash + n)
- NO uses saltos de línea reales dentro del texto
- NO uses líneas nuevas reales en la respuesta
- NO agregues espacios después de "\n"
- NO termines con "\n"
- el último punto debe terminar con "."
- ejemplo exacto de formato:
  "Aplicar ajo.\nRetirar hojas.\nEvitar humedad."
- Para "tratamiento_natural", "tratamiento_quimico" y "prevencion" 
- tienes que darme 4 frases.
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
                        "text": "Analiza la planta en la imagen y devuelve el JSON solicitado."
                    },
                    {
                        "type": "input_image",
                        "image_url": data_url,
                        "detail": "high"
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



def generar_respuesta_chat(
    pregunta_usuario,
    diagnostico
):
    system_prompt = """
Eres un fitopatólogo experto en enfermedades de plantas.

REGLAS ESTRICTAS:
- Solo usas la información del DIAGNOSTICO.
- NO inventes dosis, tiempos, cantidades ni productos.
- Si algo no está en el diagnóstico, di:
  "El diagnóstico no contiene esa información."

- Si la pregunta no está relacionada con enfermedades de plantas, responde EXACTO:
"Esa pregunta no está relacionada con el diagnóstico de la planta."

- Si el usuario pregunta por:
  dosis, frecuencia, duración, aplicación o tiempos:
  solo responde si está explícitamente en el diagnóstico.

ESTILO:
- Máximo 35 palabras
- Respuesta muy corta
- Lenguaje simple, sin tecnicismos
- Sin listas largas
"""

    user_prompt = f"""
DIAGNOSTICO:
Enfermedad: {diagnostico.enfermedad_detectada}
Severidad: {diagnostico.severidad}
Salud: {diagnostico.porcentaje_salud}%
Tratamiento natural: {diagnostico.tratamiento_natural}
Tratamiento químico: {diagnostico.tratamiento_quimico}
Prevención: {diagnostico.prevencion}

PREGUNTA:
{pregunta_usuario}
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
                "content": user_prompt
            }
        ]
    )

    return response.output_text