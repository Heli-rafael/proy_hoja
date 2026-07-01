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

    "urgencia": "Baja" | "Media" | "Alta",
    "contagio": "Bajo" | "Medio" | "Alto",

    "recuperacion": "1-2 semanas" | "1-4 semanas" | "2-6 semanas",

    "etapa": "Inicial" | "Intermedia" | "Avanzada" | "Crítica",
  
    "sintomas_detectados": [
        string
    ],

    "prediccion_evolucion": [
        {
        "periodo": number,
        "descripcion": string (máximo 10 palabras + porcentaje(solo number))
        }
    ],

    "plagas_relacionadas": [
        {
        "plaga": string,
        "riesgo": string
        }
    ],

    "factores_climaticos_favorables": {
        "temperatura": "string con formato 'min - max'",
        "humedad": numer,
        "viento": "Bajo" | "Moderado" | "Alto",
    },

    "calendario_tratamiento": [
        {
        "actividad": string,
        "tipo": string,
        "semana": number
        }
    ],

    "tratamiento_natural": [
        string (4 frases)
    ],

    "tratamiento_quimico": [
        string (4 frases)
    ],

    "prevencion": [
        string (4 frases)
    ],
}

REGLAS DE TEXTO:
- Siempre la primera letra de cada oracion, frase en MAYUSCULA
- En el campo "nombre_planta" devuelve únicamente el nombre común de la planta en español.
- En el campo "nombre_planta" No incluyas nombre científico, sinónimos, ni nombres en otro idioma.
- "enfermedad_detectada" DEBE ser SOLO el nombre común exacto.
- PROHIBIDO incluir nombres científicos.
- PROHIBIDO usar paréntesis, comas o explicaciones.
- los campos "sintomas_detectados", "plagas_relacionadas", "tratamiento_natural", "tratamiento_quimico" y "prevencion"
deben contener exactamente 4 frases cortas.
- cada frase debe terminar en punto.
- NO uses listas numeradas.
- "calendario_tratamiento" debe contener acciones orgánicas y/o químicas según necesidad del cultivo.
- En "actividad" de "calendario_tratamiento" debes incluir actividad, producto, dosis (g/L o mL/L), forma de aplicación e intervalo.
- Todas las actividades deben ser ecológicas, preventivas o culturales.
"""
    try:

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
        
    except Exception as e:
        print("ERROR OPENAI:", e)
        raise

    resultado = json.loads(
        response.output_text
    )

    resultado.setdefault("tratamiento_natural", [])

    resultado.setdefault("tratamiento_quimico", [])

    resultado.setdefault("prevencion", [])

    resultado.setdefault("sintomas_detectados", [])

    resultado.setdefault("prediccion_evolucion", [])

    resultado.setdefault("plagas_relacionadas", [])

    resultado.setdefault("factores_climaticos_favorables",{})

    resultado.setdefault("calendario_tratamiento",[])

    return resultado

    return json.loads(response.output_text)



def generar_respuesta_chat(
    pregunta_usuario,
    diagnostico
):
    system_prompt = """
Eres un asistente experto en fitopatología enfocado en enfermedades de plantas (especialmente papa).

## FUENTES DE INFORMACIÓN
1. DIAGNÓSTICO (fuente principal)
2. CONOCIMIENTO AGRONÓMICO GENERAL (solo cuando el diagnóstico no tenga la información)

## REGLA DE PRIORIDAD
- Primero usa siempre el diagnóstico.
- Si el diagnóstico NO incluye la información solicitada (especialmente tratamiento, dosis, frecuencia o aplicación), entonces DEBES usar conocimiento agronómico general confiable sobre esa enfermedad.

## PROHIBICIÓN IMPORTANTE
- No digas “El diagnóstico no contiene esa información” si existe conocimiento agronómico general aplicable.
- Solo usa esa frase si la pregunta es imposible de responder incluso con conocimiento general.

## TRATAMIENTOS (CRÍTICO)
Si el usuario pregunta por tratamiento:
- Responde SIEMPRE con una recomendación agronómica general adecuada a la enfermedad detectada.
- Incluye dosis, frecuencia y aplicación si es estándar agrícola conocido.

## FUERA DE CONTEXTO
Si la pregunta no está relacionada con enfermedades de plantas o hojas:
"Esa consulta no está relacionada con diagnósticos de enfermedades de hojas."

## ESTILO
- Máximo 30 palabras (excepto tratamientos)
- Respuestas directas
- Sin explicaciones largas
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