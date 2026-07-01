import os
from django.conf import settings

from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

from .config import MARGIN, DARK, GRAY, PRIMARY, LIGHT
from .styles import header_style, body_style
from .components import draw_text, draw_title, draw_subtitle, draw_image


class DiagnosticosPDFReport:

    def __init__(self, user, diagnosticos, response):
        self.user = user
        self.diagnosticos = diagnosticos
        self.response = response

        self.p = canvas.Canvas(response, pagesize=letter)
        self.WIDTH, self.HEIGHT = letter

    # =========================
    # PORTADA
    # =========================
    def draw_cover(self):

        p = self.p
        y = self.HEIGHT / 2 + 120

        # AVATAR
        if self.user.picture:
            try:
                path = os.path.join(settings.MEDIA_ROOT, str(self.user.picture))
                from reportlab.lib.utils import ImageReader

                img = ImageReader(path)

                p.drawImage(
                    img,
                    (self.WIDTH - 110) / 2,
                    y,
                    width=110,
                    height=110,
                    mask='auto'
                )
            except:
                pass

        y -= 140

        # NOMBRE
        full_name = (
            f"{self.user.first_name} {self.user.last_name}"
            .strip() or self.user.username
        )

        p.setFillColor(DARK)
        p.setFont("Helvetica-Bold", 20)
        p.drawCentredString(self.WIDTH / 2, y, full_name)

        y -= 22

        # USERNAME
        p.setFillColor(GRAY)
        p.setFont("Helvetica", 11)
        p.drawCentredString(self.WIDTH / 2, y, f"@{self.user.username}")

        y -= 16

        # EMAIL
        p.drawCentredString(self.WIDTH / 2, y, self.user.email)

        y -= 30

        # PLAN
        if self.user.plan:
            p.setFillColor(PRIMARY)
            p.setFont("Helvetica-Bold", 13)
            p.drawCentredString(
                self.WIDTH / 2,
                y,
                f"PLAN - {self.user.plan.nombre}"
            )
            y -= 18

            p.setFillColor(GRAY)
            p.setFont("Helvetica", 9)

            for b in (self.user.plan.beneficios[:5] if self.user.plan.beneficios else []):
                p.drawCentredString(self.WIDTH / 2, y, f"• {b}")
                y -= 12

        y -= 25

        # TÍTULO
        p.setFillColor(DARK)
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(
            self.WIDTH / 2,
            y,
            "REPORTE DE DIAGNÓSTICOS IA"
        )

        y -= 18

        p.setFillColor(GRAY)
        p.setFont("Helvetica", 10)
        p.drawCentredString(
            self.WIDTH / 2,
            y,
            "Análisis inteligente de salud vegetal"
        )

        p.showPage()

    # =========================
    # DIAGNÓSTICO
    # =========================
    def draw_diagnostico(self, d):

        p = self.p
        y = self.HEIGHT - MARGIN

        # HEADER
        draw_title(p, d.planta.nombre.upper(), y, MARGIN, DARK)
        y -= 20

        draw_subtitle(
            p,
            f"{d.enfermedad_detectada} | {d.severidad}",
            y,
            MARGIN,
            PRIMARY
        )
        y -= 35

        # IMÁGENES
        img_planta = (
            os.path.join(settings.MEDIA_ROOT, str(d.planta.imagen))
            if d.planta and d.planta.imagen else None
        )

        img_diag = (
            os.path.join(settings.MEDIA_ROOT, str(d.imagen))
            if d.imagen else None
        )

        usable_width = self.WIDTH - (2 * MARGIN)
        gap = 10

        img_width = (usable_width - gap) / 2
        img_height = 170

        img_y = y - 150

        draw_image(p, img_planta, MARGIN, img_y, img_width, img_height)
        draw_image(
            p,
            img_diag,
            MARGIN + img_width + gap,
            img_y,
            img_width,
            img_height
        )

        y = img_y - 20

        # RESUMEN
        draw_subtitle(p, "Resumen diagnostico", y, MARGIN, PRIMARY)
        y -= 18

        y = draw_text(p, f"Salud: {d.porcentaje_salud}%", y, MARGIN, GRAY)
        y = draw_text(p, f"Confianza IA: {d.confianza_ia}%", y, MARGIN, GRAY)
        y = draw_text(p, f"Urgencia: {d.urgencia}", y, MARGIN, GRAY)

        y -= 10

        # SÍNTOMAS
        draw_subtitle(p, "Síntomas detectados", y, MARGIN, PRIMARY)
        y -= 16

        for s in d.sintomas_detectados:
            y = draw_text(p, f"• {s}", y, MARGIN + 10, GRAY)

        y -= 10

        # TABLA TRATAMIENTO
        draw_subtitle(p, "Tratamiento recomendado", y, MARGIN, PRIMARY)
        y -= 10

        max_rows = max(
            len(d.tratamiento_natural),
            len(d.tratamiento_quimico)
        )

        data = [[
            Paragraph("Natural", header_style),
            Paragraph("Químico", header_style)
        ]]

        for i in range(max_rows):
            nat = (
                d.tratamiento_natural[i]
                if i < len(d.tratamiento_natural) else ""
            )

            qui = (
                d.tratamiento_quimico[i]
                if i < len(d.tratamiento_quimico) else ""
            )

            data.append([
                Paragraph(nat, body_style),
                Paragraph(qui, body_style)
            ])

        table_width = self.WIDTH - (2 * MARGIN)

        table = Table(
            data,
            colWidths=[table_width / 2, table_width / 2]
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),

            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))

        table.wrapOn(p, self.WIDTH, self.HEIGHT)
        w, h = table.wrap(table_width, self.HEIGHT)

        table.drawOn(p, MARGIN, y - h)

        y = y - h - 20

        # PLAN DE ACCIÓN
        draw_subtitle(p, "Plan de acción", y, MARGIN, PRIMARY)
        y -= 10

        data = [[
            Paragraph("Semana", header_style),
            Paragraph("Actividad", header_style)
        ]]

        for a in d.actividades.all():
            data.append([
                Paragraph(f"Semana {a.semana}", body_style),
                Paragraph(a.actividad, body_style)
            ])

        table = Table(
            data,
            colWidths=[120, table_width - 120]
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),

            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))

        table.wrapOn(p, self.WIDTH, self.HEIGHT)
        w, h = table.wrap(table_width, self.HEIGHT)

        table.drawOn(p, MARGIN, y - h)

        y = y - h - 20

        # DIVISOR
        p.setStrokeColor(LIGHT)
        p.line(MARGIN, 60, self.WIDTH - MARGIN, 60)

        p.showPage()

    # =========================
    # BUILD
    # =========================
    def build(self):
        self.draw_cover()

        for d in self.diagnosticos:
            self.draw_diagnostico(d)

        self.p.save()