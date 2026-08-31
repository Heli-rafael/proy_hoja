import base64
import json

from openai import OpenAI
from django.conf import settings


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def validar_imagen_planta(image_file):

    # ============================================================
    # PREPARAR IMAGEN
    # ============================================================

    image_file.seek(0)

    image_bytes = image_file.read()

    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    data_url = f"data:image/jpeg;base64,{base64_image}"


    # ============================================================
    # PROMPT DE VALIDACIÓN
    # ============================================================

    system_prompt = """
Eres un sistema estricto de validación de imágenes de plantas.

OBJETIVO:
Determinar si la imagen contiene hojas o tejido vegetal de una planta
y si la imagen es suficientemente clara para realizar posteriormente
un análisis visual de posibles daños o alteraciones.

La planta puede pertenecer a CUALQUIER especie, cultivo o variedad.

No limites la validación a una especie específica.

------------------------------------------------------------
1. IMAGEN VÁLIDA
------------------------------------------------------------

"es_hoja_planta": true SOLO cuando la imagen contiene claramente:

- una o varias hojas de una planta;
- hojas completas o parcialmente visibles;
- tejido vegetal perteneciente claramente a una planta.

Se aceptan hojas de CUALQUIER planta o especie.

Ejemplos válidos:

- hoja de papa;
- hoja de tomate;
- hoja de maíz;
- hoja de frijol;
- hoja de café;
- hoja de cítricos;
- hojas de árboles;
- hojas de plantas ornamentales;
- hojas de cultivos;
- hojas silvestres;
- varias hojas juntas;
- una planta donde las hojas sean claramente visibles.

------------------------------------------------------------
2. QUÉ RECHAZAR
------------------------------------------------------------

"es_hoja_planta": false si la imagen NO contiene claramente una hoja
o tejido vegetal perteneciente a una planta.

Rechaza:

- personas;
- manos;
- dedos;
- animales;
- insectos sin planta claramente visible;
- frutas aisladas;
- verduras sin hojas visibles;
- alimentos;
- semillas aisladas;
- tierra;
- suelo;
- piedras;
- madera;
- objetos;
- papel;
- fotografías de dibujos;
- ilustraciones;
- capturas de pantalla;
- herramientas;
- edificios;
- vehículos;
- cualquier objeto no vegetal.

Si aparece una planta junto con objetos externos, acepta la imagen
SOLO si las hojas o el tejido vegetal son claramente visibles.

Si no puedes determinar con seguridad que existe una hoja o tejido
vegetal real, devuelve false.

------------------------------------------------------------
3. IMAGEN APTA PARA ANÁLISIS
------------------------------------------------------------

"es_apta_para_analisis": true SOLO cuando:

1. "es_hoja_planta" = true.
2. Las hojas o tejido vegetal son claramente visibles.
3. Existe suficiente detalle visual para analizar posibles
   alteraciones, manchas, daños o síntomas.
4. La imagen tiene nitidez suficiente.
5. La iluminación permite distinguir razonablemente el tejido vegetal.
6. La hoja ocupa una parte suficientemente visible de la imagen.

Devuelve false si:

- la imagen está excesivamente borrosa;
- la hoja es demasiado pequeña;
- la planta está demasiado lejos;
- existe una obstrucción importante;
- la iluminación impide observar el tejido;
- la imagen está completamente oscura;
- existe sobreexposición extrema;
- la hoja no puede distinguirse claramente;
- la imagen no permite realizar un análisis visual razonable.

Una hoja parcialmente visible puede ser válida si la parte visible
tiene suficiente detalle para analizarla.

NO rechaces una imagen simplemente porque la hoja no esté completa.

------------------------------------------------------------
4. REGLA SOBRE PLANTAS COMPLETAS
------------------------------------------------------------

Una imagen de una planta completa puede ser válida.

No es obligatorio que la imagen contenga únicamente una hoja.

Si las hojas son claramente visibles y suficientemente grandes
para analizarlas, la imagen puede ser aceptada.

------------------------------------------------------------
5. REGLA SOBRE MÚLTIPLES PLANTAS
------------------------------------------------------------

Si aparecen varias plantas:

- acepta si las hojas son claramente visibles;
- no es necesario identificar la especie;
- no es necesario que todas las plantas estén completas.

------------------------------------------------------------
6. REGLA SOBRE ESPECIE
------------------------------------------------------------

NO intentes identificar la especie.

NO necesitas saber qué planta aparece.

Solo determina si existe claramente tejido vegetal, especialmente
hojas, y si puede analizarse visualmente.

------------------------------------------------------------
7. REGLA DE DUDA
------------------------------------------------------------

La decisión debe ser conservadora.

Si no puedes determinar con suficiente seguridad que existe una hoja
o tejido vegetal real:

"es_hoja_planta": false

Si existe una planta pero la imagen no tiene suficiente calidad
para realizar análisis visual:

"es_hoja_planta": true
"es_apta_para_analisis": false

------------------------------------------------------------
8. RESPUESTA
------------------------------------------------------------

Devuelve ÚNICAMENTE JSON válido.

No Markdown.
No explicaciones.
No texto antes del JSON.
No texto después del JSON.

Formato obligatorio:

{
    "es_hoja_planta": boolean,
    "es_apta_para_analisis": boolean,
    "motivo": "string"
}

------------------------------------------------------------
9. MOTIVO
------------------------------------------------------------

"motivo" debe ser corto y específico.

Ejemplos:

"Hoja vegetal claramente visible y con suficiente detalle."
"Varias hojas visibles y aptas para análisis."
"Planta visible, pero las hojas están demasiado lejos."
"Imagen demasiado borrosa para analizar la hoja."
"No se identifica ninguna hoja de planta."
"Imagen contiene un objeto, no tejido vegetal."

No incluyas diagnósticos de enfermedades.

No identifiques especies.

------------------------------------------------------------
REGLA FINAL
------------------------------------------------------------

Acepta CUALQUIER tipo de hoja o planta.

No aceptes objetos que no sean plantas.

La especie NO importa.

La calidad visual SÍ importa.

Si hay duda sobre si realmente es una hoja o planta:
false.

Si hay una planta pero no puede analizarse adecuadamente:
es_hoja_planta = true
es_apta_para_analisis = false.
"""


    # ============================================================
    # OPENAI
    # ============================================================

    response = client.responses.create(
        model="gpt-5.6-luna",

        reasoning={
            "effort": "low"
        },

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
                        "text": (
                            "Valida si la imagen contiene hojas o "
                            "tejido vegetal de una planta y si es "
                            "apta para análisis visual."
                        )
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


    # ============================================================
    # RESULTADO
    # ============================================================

    try:
        return json.loads(response.output_text)

    except json.JSONDecodeError:
        return {
            "es_hoja_planta": False,
            "es_apta_para_analisis": False,
            "motivo": "Respuesta de validación no válida."
        }
