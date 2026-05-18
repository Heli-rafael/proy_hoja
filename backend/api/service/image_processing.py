from PIL import Image, ImageDraw
from django.core.files.base import ContentFile
import io


def dibujar_zonas_afectadas(image_file, zonas):

    # Abrir imagen
    image = Image.open(image_file).convert("RGBA")

    width, height = image.size

    # Overlay transparente
    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    for zona in zonas:

        # Coordenadas normalizadas
        x = zona.get("x", 0) * width
        y = zona.get("y", 0) * height
        r = zona.get("radio", 0.03) * min(width, height)

        daño = zona.get("nivel_daño", 5)

        # =========================
        # COLOR SEGÚN DAÑO
        # =========================
        if daño <= 3:
            outline = (255, 255, 0, 255)   # amarillo
            fill = (255, 255, 0, 60)

        elif daño <= 7:
            outline = (255, 165, 0, 255)   # naranja
            fill = (255, 165, 0, 80)

        else:
            outline = (255, 0, 0, 255)     # rojo
            fill = (255, 0, 0, 90)

        # =========================
        # CÍRCULO DAÑADO
        # =========================
        draw.ellipse(
            (
                x - r,
                y - r,
                x + r,
                y + r
            ),
            outline=outline,
            fill=fill,
            width=4
        )

    # Combinar imagen + overlay
    final_image = Image.alpha_composite(image, overlay)

    # Convertir a RGB para JPG
    final_image = final_image.convert("RGB")

    # Guardar
    buffer = io.BytesIO()

    final_image.save(
        buffer,
        format="JPEG",
        quality=95
    )

    return ContentFile(
        buffer.getvalue(),
        name="diagnostico_ai.jpg"
    )