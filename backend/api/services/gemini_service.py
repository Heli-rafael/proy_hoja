import base64
import json
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile

from PIL import Image, ImageDraw, ImageFont

from openai import OpenAI

from .promt_service import construir_prompt


# ============================================================
# CONFIGURACIÓN OPENAI
# ============================================================

client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


# ============================================================
# UTILIDADES
# ============================================================

def imagen_a_data_url(image: Image.Image) -> str:
    """
    Convierte la imagen PIL normalizada a JPEG Base64
    y la devuelve como Data URL.
    """

    buffer = BytesIO()

    image.save(
        buffer,
        format="JPEG",
        quality=95
    )

    image_bytes = buffer.getvalue()

    return (
        "data:image/jpeg;base64,"
        + base64.b64encode(image_bytes).decode("utf-8")
    )

# ============================================================
# GENERAR IMAGEN
# ============================================================

def generar_imagen_anotada(image_file, diagnostico=None):

    # CARGAR IMAGEN
    image_file.seek(0)
    image = Image.open(image_file).convert("RGB")
    width, height = image.size

    # CONSTRUIR PROMPT
    prompt = construir_prompt(width, height)

    # OPENAI
    try:
        response = client.responses.create(
            # model="gpt-5.6-luna",
            # model="gpt-5.4-mini",
            model="gpt-5.6-luna",

            reasoning={
                "effort": "medium"
            },
            
            input=[
                {
                    "role": "system",
                    "content": """
                        Eres un sistema experto en visión computacional
                        agrícola y análisis visual fitopatológico.

                        Tu prioridad es localizar correctamente las
                        alteraciones visibles en la imagen.

                        La ubicación espacial debe ser precisa.

                        No inventes lesiones.

                        No confundas fondo, sombras o reflejos
                        con lesiones.

                        Devuelve únicamente el JSON solicitado.
                        """
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt
                        },
                        {
                            "type": "input_image",
                            "image_url": imagen_a_data_url(image),
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

    # ERRORES DE API
    except Exception as e:
        print("ERROR OPENAI:", e)
        raise

    # TOKENS USADOS
    if hasattr(response, "usage") and response.usage:
        print("TOKENS USADOS IMAGEN:", response.usage.total_tokens)
        print("TOKENS INPUT IMAGEN:", response.usage.input_tokens)
        print("TOKENS OUTPUT IMAGEN:", response.usage.output_tokens)

    # PROCESAR JSON
    try:
        data = json.loads(response.output_text)
    except json.JSONDecodeError as e:
        print("ERROR JSON OPENAI:", e)
        print("RESPUESTA OPENAI:", response.output_text)
        data = {
            "damages": []
        }

    damages = data.get("damages", [])

    if not isinstance(damages, list):
        damages = []

    # VALIDAR LESIONES
    lesiones = []

    for i, d in enumerate(damages):
        if not isinstance(d, dict):
            continue

        # DATOS
        title = str(d.get("title", "Lesión")).strip()
        description = str(d.get("description", "")).strip()
        damage_type = str(d.get("type", "Área Sospechosa")).strip()

        # CONFIDENCE
        try:
            confidence = float(d.get("confidence", 0.5))
        except (TypeError, ValueError):
            confidence = 0.5

        confidence = max(0.0, min(confidence, 1.0))

        # BBOX
        bbox = d.get("bbox", {})

        if not isinstance(bbox, dict):
            continue

        try:
            x1 = float(bbox.get("x1", 0))
            y1 = float(bbox.get("y1", 0))
            x2 = float(bbox.get("x2", 0))
            y2 = float(bbox.get("y2", 0))
        except (TypeError, ValueError):
            continue

        # NORMALIZAR COORDENADAS
        x1 = max(0.0, min(x1, 1.0))
        y1 = max(0.0, min(y1, 1.0))
        x2 = max(0.0, min(x2, 1.0))
        y2 = max(0.0, min(y2, 1.0))

        # VALIDAR GEOMETRÍA
        if x2 <= x1:
            continue

        if y2 <= y1:
            continue

        # EVITAR CAJAS DEMASIADO PEQUEÑAS
        box_width = x2 - x1
        box_height = y2 - y1

        if box_width < 0.005:
            continue

        if box_height < 0.005:
            continue

        # GUARDAR
        lesiones.append({
            "id": i + 1,
            "title": title,
            "description": description,
            "type": damage_type,
            "confidence": confidence,
            "bbox": {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2
            }
        })

    # ELIMINAR DUPLICADOS
    lesiones = eliminar_cajas_duplicadas(lesiones)

    # DIBUJAR
    scale = min(width, height) / 800
    draw = ImageDraw.Draw(image)

    # FUENTE
    base_font_size = max(12, int(16 * scale))

    try:
        font = ImageFont.truetype("arial.ttf", base_font_size)
    except Exception:
        font = ImageFont.load_default()

    # DIBUJAR CADA LESIÓN
    for d in lesiones:
        try:
            dibujar_lesion(
                draw=draw,
                lesion=d,
                width=width,
                height=height,
                scale=scale,
                base_font_size=base_font_size,
                font=font
            )
        except Exception as e:
            print("ERROR DIBUJANDO LESION:", e)
            continue

    # EXPORTAR
    output = BytesIO()

    image.save(output, format="PNG")
    output.seek(0)

    imagen = ContentFile(
        output.read(),
        name="diagnostico_openai.png"
    )

    return {
        "imagen": imagen,
        "lesiones": lesiones
    }


def calcular_iou(box_a, box_b):
    ax1 = box_a["x1"]
    ay1 = box_a["y1"]
    ax2 = box_a["x2"]
    ay2 = box_a["y2"]

    bx1 = box_b["x1"]
    by1 = box_b["y1"]
    bx2 = box_b["x2"]
    by2 = box_b["y2"]

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    if inter_x2 <= inter_x1 or inter_y2 <= inter_y1:
        return 0.0

    intersection = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)

    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)

    union = area_a + area_b - intersection

    if union <= 0:
        return 0.0

    return intersection / union


def eliminar_cajas_duplicadas(lesiones, threshold=0.90):
    resultado = []

    for lesion in lesiones:
        duplicada = False

        for existente in resultado:
            iou = calcular_iou(
                lesion["bbox"],
                existente["bbox"]
            )

            if iou >= threshold:
                # Conservamos la lesión
                # con mayor confianza.

                if lesion["confidence"] > existente["confidence"]:
                    resultado.remove(existente)
                    resultado.append(lesion)

                duplicada = True
                break

        if not duplicada:
            resultado.append(lesion)

    # Reasignar IDs

    for index, lesion in enumerate(resultado, start=1):
        lesion["id"] = index

    return resultado


def dibujar_lesion(
    draw,
    lesion,
    width,
    height,
    scale,
    base_font_size,
    font
):
    bbox = lesion["bbox"]

    # CONVERTIR COORDENADAS NORMALIZADAS → PIXELES
    x1 = bbox["x1"] * width
    y1 = bbox["y1"] * height
    x2 = bbox["x2"] * width
    y2 = bbox["y2"] * height

    # CLAMP
    x1 = max(0, min(x1, width))
    y1 = max(0, min(y1, height))
    x2 = max(0, min(x2, width))
    y2 = max(0, min(y2, height))

    if x2 <= x1 or y2 <= y1:
        return

    # COLORES
    RED = (220, 0, 0)
    WHITE = (255, 255, 255)

    # GROSOR DEL BOUNDING BOX
    line_width = max(2, int(3 * scale))

    # DIBUJAR BOUNDING BOX
    draw.rectangle(
        (x1, y1, x2, y2),
        outline=RED,
        width=line_width
    )

    # TEXTO DEL LABEL
    label = lesion.get("type", "Daño")
    confidence = lesion.get("confidence", 0)

    text = f"{label} {confidence:.2f}"

    # TAMAÑO DEL BOX
    box_width = x2 - x1
    box_height = y2 - y1

    # CONFIGURACIÓN DEL TEXTO
    current_font_size = max(9, int(base_font_size))

    try:
        current_font = ImageFont.truetype(
            "arial.ttf",
            current_font_size
        )
    except Exception:
        current_font = font

    padding_x = max(4, int(5 * scale))
    padding_y = max(3, int(4 * scale))

    # AJUSTAR FUENTE
    while current_font_size > 8:

        text_bbox = draw.textbbox(
            (0, 0),
            text,
            font=current_font
        )

        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        label_width = text_width + padding_x * 2
        label_height = text_height + padding_y * 2

        # Si cabe dentro del bounding box, dejamos este tamaño
        if label_width <= box_width:
            break

        current_font_size -= 1

        try:
            current_font = ImageFont.truetype(
                "arial.ttf",
                current_font_size
            )
        except Exception:
            current_font = font
            break

    # CALCULAR TAMAÑO FINAL DEL TEXTO
    text_bbox = draw.textbbox(
        (0, 0),
        text,
        font=current_font
    )

    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    label_width = text_width + padding_x * 2
    label_height = text_height + padding_y * 2

    # POSICIÓN DEL LABEL
    label_x1 = x1
    label_y1 = y1

    label_x2 = label_x1 + label_width
    label_y2 = label_y1 + label_height

    # EVITAR QUE EL LABEL SALGA DE LA IMAGEN
    if label_x2 > width:
        label_x2 = width
        label_x1 = max(0, label_x2 - label_width)

    if label_y2 > height:
        label_y2 = height
        label_y1 = max(0, label_y2 - label_height)

    # DIBUJAR CONTENEDOR ROJO
    draw.rectangle(
        (label_x1, label_y1, label_x2, label_y2),
        fill=RED
    )

    # POSICIÓN DEL TEXTO
    text_x = label_x1 + padding_x
    text_y = label_y1 + padding_y - text_bbox[1]

    # DIBUJAR TEXTO BLANCO
    draw.text(
        (text_x, text_y),
        text,
        fill=WHITE,
        font=current_font
    )
