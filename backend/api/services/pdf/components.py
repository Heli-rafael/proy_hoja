import io, os
from PIL import Image
from reportlab.lib.utils import ImageReader


def optimize_image(path, max_size=(800, 800)):
    try:
        img = Image.open(path)
        img.thumbnail(max_size)

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=50, optimize=True)
        buffer.seek(0)

        return ImageReader(buffer)
    except:
        return None


def draw_text(p, text, y, margin, color, indent=0):
    p.setFillColor(color)
    p.setFont("Helvetica", 10)
    p.drawString(margin + indent, y, text)
    return y - 14


def draw_title(p, text, y, margin, dark):
    p.setFillColor(dark)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(margin, y, text)
    return y - 25


def draw_subtitle(p, text, y, margin, primary):
    p.setFillColor(primary)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(margin, y, text)
    return y - 18


def draw_image(p, path, x, y, w=240, h=160):
    try:
        if path and os.path.exists(path):
            img = optimize_image(path)
            if img:
                p.drawImage(img, x, y, width=w, height=h, mask="auto")
    except:
        pass