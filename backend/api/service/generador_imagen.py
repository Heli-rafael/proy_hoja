import base64

from openai import OpenAI
from django.conf import settings
from django.core.files.base import ContentFile


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generar_imagen_anotada(
    image_file,
    diagnostico
):

    image_file.seek(0)

    result = client.images.edit(

        model="gpt-image-1",

        image=image_file,

        size="auto",

        prompt=f"""

CRÍTICO: NO RECONSTRUIR NI MEJORAR LA IMAGEN.
USA LA IMAGEN ORIGINAL SIN MODIFICAR PIXELES.
SOLO ANOTACIÓN VISUAL (círculos rojos).

TAREA:
Detecta SOLO daño vegetal REAL visible con alta certeza.

SÍNTOMAS VÁLIDOS:
- necrosis (tejido negro/marrón seco)
- manchas marrones definidas
- clorosis evidente (amarilleo localizado)
- hongos o mildiu visibles
- agujeros en hoja
- bordes secos o quemados
- lesiones claramente diferenciadas del tejido sano

REGLAS DE DETECCIÓN (MUY IMPORTANTE):
- Ignora variaciones leves de color o textura.
- Ignora sombras, luz, reflejos o ruido de cámara.
- NO marcar zonas dudosas.
- Si no estás seguro, NO marques.

REGLAS DE ANOTACIÓN:
- Solo dibuja círculos rojos.
- Tamaño del círculo proporcional al área dañada (pequeño/medio/grande).
- Máximo 1 círculo por lesión continua.
- No solapar círculos innecesariamente.
- Solo marcar daño confirmado.

PROHIBIDO:
- NO mejorar calidad de imagen
- NO enfocar ni suavizar
- NO cambiar colores
- NO reinterpretar la imagen
- NO agregar texto, flechas o etiquetas
- NO modificar fondo ni estructura

RESULTADO:
Imagen idéntica + círculos rojos únicamente en daño confirmado.

"""
    )

    image_base64 = result.data[0].b64_json

    image_bytes = base64.b64decode(image_base64)

    return ContentFile(
        image_bytes,
        name="diagnostico_ai.png"
    )