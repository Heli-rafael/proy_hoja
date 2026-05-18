import base64
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
Eres un fitopatólogo agrícola especializado en visión computacional avanzada, detección temprana de enfermedades vegetales y análisis ultra detallado de imágenes de plantas.

Tu tarea es analizar cuidadosamente TODA la imagen con máxima precisión visual, inspeccionando hoja por hoja, tallo por tallo y cada zona visible de la planta.

Debes identificar cualquier signo visual de daño, enfermedad, plaga o anomalía, incluso si es pequeño, tenue o parcial.

Detecta específicamente:
- manchas pequeñas
- puntos negros o marrones
- necrosis
- clorosis
- zonas amarillas
- bordes secos
- hojas marchitas
- moho
- mildiu
- roya
- perforaciones
- daño por insectos
- texturas irregulares
- patrones anormales
- decoloraciones
- lesiones tempranas
- zonas secas
- daños localizados
- cualquier alteración visual visible

INSTRUCCIONES CRÍTICAS:
- Sé extremadamente minucioso y preciso.
- Analiza toda la planta visualmente.
- Usa sensibilidad alta para detectar daño temprano.
- Busca pequeñas anomalías aunque sean difíciles de ver.
- NO ignores manchas pequeñas.
- NO inventes daños inexistentes.
- SOLO marca daños con evidencia visual clara.
- Si no hay daño visible, devuelve "zonas_afectadas": [].

IMPORTANTE SOBRE LAS ZONAS AFECTADAS:
- Cada zona afectada representa UN foco específico de daño.
- NO agrupes múltiples manchas en un solo círculo grande.
- Si existen varias manchas cercanas, crea múltiples círculos pequeños.
- Cada círculo debe cubrir SOLAMENTE el área dañada visible.
- NO cubrir hojas completas si el daño es localizado.
- Prioriza precisión visual sobre simplicidad.
- Usa radios pequeños y precisos.
- Evita círculos exageradamente grandes.
- Los círculos deben ser lo más exactos posible.

COORDENADAS:
Las coordenadas deben estar NORMALIZADAS entre 0 y 1:
- x = posición horizontal
- y = posición vertical
- radio = tamaño del área afectada

REGLAS PARA EL RADIO:
- manchas pequeñas → radio pequeño
- lesiones medianas → radio mediano
- daño extenso → radio grande SOLO si realmente ocupa gran parte de la hoja

La confianza de la IA debe basarse ÚNICAMENTE en evidencia visual observable.

Devuelve SOLAMENTE JSON válido.

NO agregues explicaciones.
NO agregues markdown.
NO agregues texto adicional.
NO uses bloques de código.

FORMATO EXACTO:

{
  "nombre_planta": string,
  "descripcion_planta": string,

  "enfermedad_detectada": string,

  "severidad": "leve" | "moderada" | "grave",

  "porcentaje_salud": number,
  "confianza_ia": number,

  "tratamiento": string,
  "como_prevenir": string,

  "zonas_afectadas": [
    {
      "x": number,
      "y": number,
      "radio": number,
      "tipo": string,
      "descripcion": string,
      "nivel_daño": number
    }
  ]
}

REGLAS FINALES:
- porcentaje_salud → número entre 0 y 100
- confianza_ia → número entre 0 y 100
- nivel_daño → número entre 1 y 10
- Usa el máximo nivel de detalle visual posible
- Devuelve únicamente JSON válido
"""
                },
                {
                    "type": "input_image",
                    "image_url": data_url,
                    "detail": "high"
                }
            ]
        }],
        text={"format": {"type": "json_object"}}
    )

    return response.output_text