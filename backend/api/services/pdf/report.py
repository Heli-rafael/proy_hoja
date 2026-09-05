import json
import os

from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

from . import styles
from .components import draw_image, draw_subtitle, draw_text, draw_title
from . import components

import locale

from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle

class DiagnosticosPDFReport:
    def __init__(self, user, diagnosticos, response):
        self.user = user
        self.diagnosticos = diagnosticos
        self.response = response

        self.p = canvas.Canvas(response, pagesize=styles.PAGE_SIZE)
        self.WIDTH, self.HEIGHT = styles.PAGE_SIZE

    def parse_json_field(self, value, default=None):
        """Convierte valores JSON o estructuras Python a datos utilizables."""
        if default is None:
            default = []

        if value is None:
            return default

        if isinstance(value, (list, dict)):
            return value

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return default

            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return default

        return default

    def get_actividades(self, diagnostico):
        """Obtiene las actividades desde una relación Django o un JSON."""
        actividades = getattr(diagnostico, "actividades", [])

        if hasattr(actividades, "all"):
            try:
                return actividades.all()
            except Exception:
                return []

        actividades = self.parse_json_field(actividades, [])

        return actividades if isinstance(actividades, list) else []

    def get_list_field(self, diagnostico, field_name):
        """Obtiene de forma segura un campo que debería contener una lista."""
        value = getattr(diagnostico, field_name, [])
        value = self.parse_json_field(value, [])

        return value if isinstance(value, list) else []

    def treatment_to_text(self, treatment):
        """Convierte un tratamiento a HTML compatible con ReportLab."""
        if treatment is None:
            return ""

        if isinstance(treatment, dict):
            return (
                f"<b>Producto:</b> {treatment.get('producto', '')}<br/>"
                f"<b>Dosis:</b> {treatment.get('dosis', '')}<br/>"
                f"<b>Aplicación:</b> {treatment.get('aplicacion', '')}<br/>"
                f"<b>Frecuencia:</b> {treatment.get('frecuencia', '')}"
            )

        if isinstance(treatment, str):
            return treatment

        return str(treatment)

    def get_media_path(self, value):
        """Obtiene la ruta física de un archivo almacenado en MEDIA_ROOT."""
        if not value:
            return None

        try:
            return os.path.join(settings.MEDIA_ROOT, str(value))
        except Exception:
            return None

    def get_health_status(self, porcentaje):
        porcentaje = max(0, min(100, float(porcentaje or 0)))

        if porcentaje <= 20:
            return {
                "label": "Estado crítico",
                "accent": styles.HEALTH_CRITICAL,
                "light": styles.HEALTH_CRITICAL_LIGHT,
            }

        if porcentaje <= 40:
            return {
                "label": "Estado muy bajo",
                "accent": styles.HEALTH_VERY_LOW,
                "light": styles.HEALTH_VERY_LOW_LIGHT,
            }

        if porcentaje <= 60:
            return {
                "label": "Estado bajo",
                "accent": styles.HEALTH_LOW,
                "light": styles.HEALTH_LOW_LIGHT,
            }

        if porcentaje <= 80:
            return {
                "label": "Estado moderado",
                "accent": styles.HEALTH_MODERATE,
                "light": styles.HEALTH_MODERATE_LIGHT,
            }

        return {
            "label": "Estado saludable",
            "accent": styles.HEALTH_HEALTHY,
            "light": styles.HEALTH_HEALTHY_LIGHT,
        }

    def draw_footer(self):
        p = self.p

        p.setStrokeColor(styles.LIGHT)
        p.setLineWidth(0.8)

        p.line(
            styles.MARGIN_LEFT,
            60,
            self.WIDTH - styles.MARGIN_RIGHT,
            60,
        )

        p.setFillColor(styles.GRAY)
        p.setFont(
            styles.FONT_NAME,
            styles.FONT_SIZE_SMALL,
        )

        p.drawCentredString(
            self.WIDTH / 2,
            42,
            "AgroVision AI | Inteligencia artificial aplicada al análisis de plantas",
        )
        
    # ============================================================
    # DOCUMENTO PORTADA
    # ============================================================

    def draw_cover(self):
        p = self.p
        center_x = self.WIDTH / 2

        # POSICIÓN INICIAL
        y = self.HEIGHT - 120

        # AVATAR DEL USUARIO
        avatar_path = self.get_media_path(getattr(self.user, "picture", None))
        avatar_size = 110
        avatar_x = center_x - (avatar_size / 2)
        avatar_y = y - avatar_size

        if avatar_path:
            try:
                p.saveState()
                path = p.beginPath()
                path.circle(center_x, avatar_y + (avatar_size / 2), avatar_size / 2)
                p.clipPath(path, stroke=0, fill=0)

                draw_image(p, avatar_path, avatar_x, avatar_y, avatar_size, avatar_size)

                p.restoreState()

                # Borde del avatar
                p.setStrokeColor(styles.LIGHT_BG)
                p.setLineWidth(2)
                p.circle(center_x, avatar_y + (avatar_size / 2), avatar_size / 2, fill=0, stroke=1)

            except Exception:
                avatar_path = None

        if not avatar_path:
            # AVATAR GENÉRICO
            p.setFillColor(styles.LIGHT_BG)
            p.circle(center_x, avatar_y + (avatar_size / 2), avatar_size / 2, fill=1, stroke=0)

            # AVATAR — CABEZA
            head_radius = avatar_size * 0.16
            head_center_y = avatar_y + avatar_size * 0.68
            p.setFillColor(styles.DARK)
            p.circle(center_x, head_center_y, head_radius, fill=1, stroke=0)

            # AVATAR — CUERPO
            body_width = avatar_size * 0.52
            body_height = avatar_size * 0.34
            body_x = center_x - body_width / 2
            body_y = avatar_y + avatar_size * 0.12
            p.roundRect(body_x, body_y, body_width, body_height, body_height / 2, fill=1, stroke=0)

        y -= 140


        # NOMBRE DEL USUARIO
        full_name = (
            f"{getattr(self.user, 'first_name', '')} "
            f"{getattr(self.user, 'last_name', '')}"
        ).strip()
        full_name = full_name or getattr(self.user, "username", "Usuario")

        components.draw_title_center(p, full_name, y, styles.DARK)
        y -= 25

        # USERNAME
        username = getattr(self.user, "username", "")

        if username:
            components.draw_text_center(p, f"@{username}", y, styles.GRAY)
            y -= 18

        # EMAIL
        email = getattr(self.user, "email", "") or ""

        if email:
            components.draw_text_center(p, email, y, styles.GRAY)
            y -= 35

        # PLAN
        plan = getattr(self.user, "plan", None)

        if plan:
            plan_nombre = getattr(plan, "nombre", "")

            components.draw_title_center(p, f"PLAN {str(plan_nombre).upper()}", y, styles.DARK)
            y -= 25

            beneficios = self.parse_json_field(getattr(plan, "beneficios", []), [])

            if isinstance(beneficios, list) and beneficios:
                beneficio_style = ParagraphStyle(
                    "CoverBenefit",
                    fontName=styles.FONT_NAME,
                    fontSize=styles.FONT_SIZE_SMALL,
                    leading=styles.FONT_SIZE_SMALL * 1.5,
                    textColor=styles.GRAY,
                    alignment=TA_LEFT,
                )

                beneficio_data = []

                for beneficio in beneficios[:5]:
                    beneficio_data.append([Paragraph(f"• {str(beneficio)}", beneficio_style)])

                beneficios_table = Table(beneficio_data, colWidths=[self.WIDTH - 180])

                beneficios_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), styles.LIGHT_BG),
                    ("BOX", (0, 0), (-1, -1), 0.8, styles.LIGHT_BG),
                    ("LEFTPADDING", (0, 0), (-1, -1), 15),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 15),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]))

                beneficios_width, beneficios_height = beneficios_table.wrap(
                    self.WIDTH - 180,
                    self.HEIGHT,
                )

                beneficios_table.drawOn(
                    p,
                    center_x - (beneficios_width / 2),
                    y - beneficios_height,
                )

                y -= beneficios_height + 35

        # LÍNEA DIVISORIA
        p.setStrokeColor(styles.PRIMARY)
        p.setLineWidth(1)
        p.line(styles.MARGIN_LEFT + 40, y, self.WIDTH - styles.MARGIN_RIGHT - 40, y)

        y -= 45

        # TÍTULO DEL REPORTE
        components.draw_title_center(p, "REPORTE DE DIAGNÓSTICOS IA", y, styles.PRIMARY)
        y -= 28

        # SUBTÍTULO
        components.draw_text_center(p, "Análisis inteligente de salud vegetal", y, styles.GRAY)
        y -= 35

        # DESCRIPCIÓN
        cover_description_style = ParagraphStyle(
            "CoverDescription",
            fontName=styles.FONT_NAME,
            fontSize=styles.FONT_SIZE_BODY,
            leading=styles.FONT_SIZE_BODY * 1.5,
            textColor=styles.DARK,
            alignment=TA_CENTER,
        )

        cover_description = Paragraph(
            "Diagnosticar mejor ✓  •  Actuar a tiempo ✓  •  Cuidar mejor ✓",
            cover_description_style,
        )
        description_width = self.WIDTH - 180

        _, description_height = cover_description.wrap(
            description_width,
            self.HEIGHT,
        )

        cover_description.drawOn(
            p,
            center_x - (description_width / 2),
            y - description_height,
        )

        # PIE DE PÁGINA
        self.draw_footer()

        p.showPage()


        

    # ============================================================
    # DOCUMENTO CONTENIDO
    # ============================================================
    def draw_diagnostico(self, d):
        p = self.p
        y = self.HEIGHT - styles.MARGIN_TOP
        
        planta = getattr(d, "planta", None)
        nombre_planta = getattr(planta, "nombre", None) if planta else None
        nombre_planta = str(nombre_planta).upper() if nombre_planta else "PLANTA"

        enfermedad = getattr(d, "enfermedad_detectada", None) or "Sin diagnóstico"
        severidad = getattr(d, "severidad", None) or "No determinada"

        fecha_diagnostico = d.creado_en.strftime("%d de %B de %Y")

        recuperacion = getattr(d,"recuperacion",None) or 0

        # ============================================================
        # ENCABEZADO
        # ============================================================

        components.draw_title_center(
            p,
            f"Diagnóstico de Planta - {nombre_planta}",
            y,
            styles.DARK,
        )

        y -= 25

        # ENFERMEDAD
        p.setFillColor(styles.PRIMARY)
        p.setFont(
            styles.FONT_BOLD,
            styles.FONT_SIZE_H2,
        )

        components.draw_title_center(
            p,
            f"Enfermedad - {enfermedad}",
            y,
            styles.PRIMARY,
        )

        y -= 15

        # INFORMACIÓN DEL DIAGNÓSTICO
        components.draw_text_center(
            p,
            (
                f"•   Fecha: {fecha_diagnostico}   •   Severidad: {severidad}   •   Recuperación: {recuperacion}"
                f""
            ),
            y,
            styles.GRAY,
        )
        y -= 15

        # ============================================================
        # LÍNEA DIVISORIA
        # ============================================================

        p.setStrokeColor(styles.LIGHT)
        p.setLineWidth(1)

        p.line(
            styles.MARGIN_LEFT,
            y,
            self.WIDTH - styles.MARGIN_RIGHT,
            y,
        )

        y -= 25

        # ============================================================
        # IMAGENES
        # ============================================================
        img_planta = self.get_media_path(
            getattr(planta, "imagen", None) if planta else None
        )

        img_diag = self.get_media_path(
            getattr(d, "imagen", None)
        )

        table_width = (
            self.WIDTH
            - styles.MARGIN_LEFT
            - styles.MARGIN_RIGHT
        )

        gap = 10
        img_width = (table_width - gap) / 2
        img_height = 170
        img_y = y - 150

        draw_image(
            p,
            img_planta,
            styles.MARGIN_LEFT,
            img_y,
            img_width,
            img_height,
        )

        draw_image(
            p,
            img_diag,
            styles.MARGIN_LEFT + img_width + gap,
            img_y,
            img_width,
            img_height,
        )

        y = img_y - 10

        # ============================================================
        # RESUMEN DEL DIAGNÓSTICO
        # ============================================================

        salud = getattr(d, "porcentaje_salud", 0) or 0
        confianza = getattr(d, "confianza_ia", 0) or 0
        urgencia = getattr(d, "urgencia", None) or "No determinada"

        health = self.get_health_status(salud)

        # TÍTULO
        summary_title_style = ParagraphStyle(
            "DiagnosticSummaryTitle",
            fontName=styles.FONT_BOLD,
            fontSize=styles.FONT_SIZE_H3,
            leading=styles.FONT_SIZE_H3 * 1.2,
            textColor=health["accent"],
            alignment=TA_LEFT,
        )

        # TEXTO
        summary_style = ParagraphStyle(
            "DiagnosticSummary",
            fontName=styles.FONT_NAME,
            fontSize=styles.DRAW_TEXT_FONT_SIZE,
            leading=styles.DRAW_TEXT_FONT_SIZE * 1.3,
            textColor=styles.DARK,
            alignment=TA_LEFT,
        )

        # RESUMEN
        resumen = (
            f"El análisis identifica <b>{enfermedad or 'una alteración fitosanitaria'}</b> "
            f"con una severidad <b>{severidad.lower()}</b> y un estado de salud estimado "
            f"del <b>{salud} %</b>. La evaluación presenta una confianza de IA del "
            f"<b>{confianza} %</b> y establece una prioridad de atención "
            f"<b>{urgencia.lower()}</b>. Se recomienda seguir el tratamiento indicado "
            f"y realizar un seguimiento periódico, con una recuperación estimada de "
            f"<b>{recuperacion}</b>."
        )

        summary_title = Paragraph("Resumen diagnóstico",summary_title_style,)
        summary = Paragraph(resumen,summary_style,)

        table_width = (
            self.WIDTH
            - styles.MARGIN_LEFT
            - styles.MARGIN_RIGHT
        )

        # CONTENEDOR 1x1
        summary_table = Table(
            [
                [summary_title],
                [summary],
            ],
            colWidths=[table_width],
        )

        summary_table.setStyle(TableStyle([
            # CONTENEDOR
            ("BACKGROUND", (0, 0), (-1, -1), health["light"]),
            ("BOX", (0, 0), (-1, -1), 1.2, health["accent"]),
            ("LINEBEFORE", (0, 0), (0, -1), 5, health["accent"]),

            # TÍTULO
            ("LEFTPADDING", (0, 0), (-1, 0), 12),
            ("RIGHTPADDING", (0, 0), (-1, 0), 12),
            ("TOPPADDING", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 4),

            # TEXTO
            ("LEFTPADDING", (0, 1), (-1, 1), 12),
            ("RIGHTPADDING", (0, 1), (-1, 1), 12),
            ("TOPPADDING", (0, 1), (-1, 1), 4),
            ("BOTTOMPADDING", (0, 1), (-1, 1), 10),

            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))

        _, summary_height = summary_table.wrap(
            table_width,
            self.HEIGHT,
        )

        summary_table.drawOn(
            p,
            styles.MARGIN_LEFT,
            y - summary_height,
        )


        y = y - summary_height - 25

        # ============================================================
        # SINTOMAS DETECTADOS
        # ============================================================

        draw_subtitle(
            p,
            "1. Síntomas detectados",
            y,
            styles.MARGIN_LEFT,
            styles.PRIMARY,
        )

        y -= 5

        # ============================================================
        # LÍNEA DIVISORIA
        # ============================================================

        p.setStrokeColor(styles.PRIMARY)
        p.setLineWidth(1)

        p.line(
            styles.MARGIN_LEFT,
            y,
            self.WIDTH - styles.MARGIN_RIGHT,
            y,
        )

        y -= 15

        # ============================================================
        # DATOS SINTOMAS
        # ============================================================

        sintomas = self.get_list_field(d, "sintomas_detectados")

        for sintoma in sintomas:
            y = draw_text(
                p,
                f"•  {sintoma}",
                y,
                styles.MARGIN_LEFT + 10,
                styles.GRAY,
            )

        y -= 10

        # ============================================================
        # TRATAMIENTO NATURAL
        # ============================================================

        draw_subtitle(
            p,
            "2. Tratamiento natural",
            y,
            styles.MARGIN_LEFT,
            styles.PRIMARY,
        )

        y -= 5

        # ============================================================
        # LÍNEA DIVISORIA
        # ============================================================

        p.setStrokeColor(styles.PRIMARY)
        p.setLineWidth(1)

        p.line(
            styles.MARGIN_LEFT,
            y,
            self.WIDTH - styles.MARGIN_RIGHT,
            y,
        )

        y -= 10

        # ============================================================
        # TRATAMIENTO RECOMENDADO - NATURAL
        # ============================================================

        tratamiento_natural = self.get_list_field(d,"tratamiento_natural")

        data = [
            [
                Paragraph("Tratamiento", styles.TABLE_TEXT_WHITE),
                Paragraph("Producto", styles.TABLE_TEXT_WHITE),
                Paragraph("Dosis", styles.TABLE_TEXT_WHITE),
                Paragraph("Aplicación", styles.TABLE_TEXT_WHITE),
                Paragraph("Frecuencia", styles.TABLE_TEXT_WHITE),
            ]
        ]

        for tratamiento in tratamiento_natural:

            if not isinstance(tratamiento, dict):
                continue

            data.append([
                Paragraph("Natural", styles.SMALL),
                Paragraph(str(tratamiento.get("producto", "")), styles.SMALL),
                Paragraph(str(tratamiento.get("dosis", "")), styles.SMALL),
                Paragraph(str(tratamiento.get("aplicacion", "")), styles.SMALL),
                Paragraph(str(tratamiento.get("frecuencia", "")), styles.SMALL),
            ])

        # ============================================================
        # TABLA NATURAL
        # ============================================================

        table = Table(data, colWidths=[75, 105, 65, table_width - 75 - 105 - 65 - 80, 80], repeatRows=1)

        table.setStyle(styles.TABLE_HEADER)

        _, height = table.wrap(
            table_width,
            self.HEIGHT,
        )

        table.drawOn(
            p,
            styles.MARGIN_LEFT,
            y - height,
        )

        y = y - height - 15

        # ============================================================
        # NOTA SOBRE RECOMENDACIONES DE IA
        # ============================================================

        nota_style = ParagraphStyle(
            "TreatmentNote",
            fontName=styles.FONT_NAME,
            fontSize=styles.FONT_SIZE_SMALL,
            leading=styles.FONT_SIZE_SMALL * 1.4,
            textColor=styles.NOTE_BLUE_DARK,
            alignment=TA_LEFT,
        )

        nota = Paragraph(
            "<b>Nota:</b> Las alternativas de tratamiento natural indicadas "
            "corresponden a recomendaciones generadas mediante inteligencia artificial "
            "a partir del diagnóstico realizado. Su aplicación debe ajustarse a las "
            "condiciones específicas de la planta y del cultivo. Para una evaluación "
            "precisa o ante síntomas persistentes, se recomienda consultar con un "
            "<b>fitopatólogo o especialista en sanidad vegetal</b>.",
            nota_style,
        )

        nota_table = Table(
            [[nota]],
            colWidths=[table_width],
        )

        nota_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), styles.NOTE_BLUE_LIGHT),
            ("BOX", (0, 0), (-1, -1), 1, styles.NOTE_BLUE),
            ("LINEBEFORE", (0, 0), (0, -1), 4, styles.NOTE_BLUE),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))

        _, nota_height = nota_table.wrap(
            table_width,
            self.HEIGHT,
        )

        nota_table.drawOn(
            p,
            styles.MARGIN_LEFT,
            y - nota_height,
        )

        # ============================================================
        # PIE DE PAGINA
        # ============================================================

        self.draw_footer()

        # NUEVA PAGINA
        p.showPage()

        # ============================================================
        # TRATAMIENTO RECOMENDADO - QUIMICO
        # ============================================================

        y = self.HEIGHT - styles.MARGIN_TOP

        draw_subtitle(
            p,
            "3. Tratamiento químico",
            y,
            styles.MARGIN_LEFT,
            styles.PRIMARY,
        )

        y -= 5

        # ============================================================
        # LÍNEA DIVISORIA
        # ============================================================

        p.setStrokeColor(styles.PRIMARY)
        p.setLineWidth(1)

        p.line(
            styles.MARGIN_LEFT,
            y,
            self.WIDTH - styles.MARGIN_RIGHT,
            y,
        )

        y -= 10

        # ============================================================
        # DATOS TRATAMIENTO QUÍMICO
        # ============================================================

        tratamiento_quimico = self.get_list_field(d,"tratamiento_quimico")

        data = [
            [
                Paragraph("Tratamiento", styles.TABLE_TEXT_WHITE),
                Paragraph("Producto", styles.TABLE_TEXT_WHITE),
                Paragraph("Dosis", styles.TABLE_TEXT_WHITE),
                Paragraph("Aplicación", styles.TABLE_TEXT_WHITE),
                Paragraph("Frecuencia", styles.TABLE_TEXT_WHITE),
            ]
        ]

        for tratamiento in tratamiento_quimico:

            if not isinstance(tratamiento, dict):
                continue

            data.append([
                Paragraph("Químico", styles.SMALL),
                Paragraph(str(tratamiento.get("producto", "")), styles.SMALL),
                Paragraph(str(tratamiento.get("dosis", "")), styles.SMALL),
                Paragraph(str(tratamiento.get("aplicacion", "")), styles.SMALL),
                Paragraph(str(tratamiento.get("frecuencia", "")), styles.SMALL),
            ])

        # ============================================================
        # TABLA QUÍMICA
        # ============================================================

        table = Table(
            data,
            colWidths=[
                75,
                105,
                65,
                table_width - 75 - 105 - 65 - 80,
                80,
            ],
            repeatRows=1,
        )

        table.setStyle(styles.TABLE_HEADER)

        _, height = table.wrap(
            table_width,
            self.HEIGHT,
        )

        table.drawOn(
            p,
            styles.MARGIN_LEFT,
            y - height,
        )

        y = y - height - 15

        # ============================================================
        # NOTA SOBRE RECOMENDACIONES DE IA
        # ============================================================

        nota_style = ParagraphStyle(
            "TreatmentNote",
            fontName=styles.FONT_NAME,
            fontSize=styles.FONT_SIZE_SMALL,
            leading=styles.FONT_SIZE_SMALL * 1.4,
            textColor=styles.NOTE_BLUE_DARK,
            alignment=TA_LEFT,
        )

        nota = Paragraph(
            "<b>Nota:</b> Los tratamientos químicos presentados son recomendaciones "
            "generadas mediante inteligencia artificial y deben considerarse únicamente "
            "como orientación. Antes de su aplicación, verifique la autorización del "
            "producto para el cultivo, respete las dosis, intervalos y medidas de "
            "seguridad indicados en su etiqueta. Ante cualquier duda, se recomienda "
            "consultar con un <b>fitopatólogo o profesional especializado en sanidad vegetal</b>.",
            nota_style,
        )

        nota_table = Table(
            [[nota]],
            colWidths=[table_width],
        )

        nota_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), styles.NOTE_BLUE_LIGHT),
            ("BOX", (0, 0), (-1, -1), 1, styles.NOTE_BLUE),
            ("LINEBEFORE", (0, 0), (0, -1), 4, styles.NOTE_BLUE),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))

        _, nota_height = nota_table.wrap(
            table_width,
            self.HEIGHT,
        )

        nota_table.drawOn(
            p,
            styles.MARGIN_LEFT,
            y - nota_height,
        )

        y = y - nota_height - 20

        # ============================================================
        # PLAN DE ACCION
        # ============================================================

        draw_subtitle(
            p,
            "4. Plan de acción",
            y,
            styles.MARGIN_LEFT,
            styles.PRIMARY,
        )

        y -= 5

        # ============================================================
        # LÍNEA DIVISORIA
        # ============================================================

        p.setStrokeColor(styles.PRIMARY)
        p.setLineWidth(1)

        p.line(
            styles.MARGIN_LEFT,
            y,
            self.WIDTH - styles.MARGIN_RIGHT,
            y,
        )

        y -= 10

        # ============================================================
        # DATOS PLAN DE ACCION
        # ============================================================
        
        data = [
            [
                Paragraph("Semana", styles.TABLE_TEXT_WHITE),
                Paragraph("Actividad", styles.TABLE_TEXT_WHITE),
            ]
        ]

        actividades = self.get_actividades(d)

        for actividad_obj in actividades:
            if hasattr(actividad_obj, "semana"):
                semana = getattr(actividad_obj, "semana", "")
                actividad = getattr(actividad_obj, "actividad", "")
            elif isinstance(actividad_obj, dict):
                semana = actividad_obj.get("semana", "")
                actividad = actividad_obj.get("actividad", "")
            else:
                semana = ""
                actividad = str(actividad_obj)

            data.append(
                [
                    Paragraph(f"Semana {semana}", styles.SMALL),
                    Paragraph(str(actividad), styles.SMALL),
                ]
            )

        table = Table(
            data,
            colWidths=[90, table_width - 90],
            repeatRows=1,
        )

        table.setStyle(styles.TABLE_HEADER)

        _, height = table.wrap(table_width, self.HEIGHT)

        table.drawOn(
            p,
            styles.MARGIN_LEFT,
            y - height,
        )

        y -= height + 20
        

        # ============================================================
        # PREVENCION
        # ============================================================

        draw_subtitle(
            p,
            "5. Prevención",
            y,
            styles.MARGIN_LEFT,
            styles.PRIMARY,
        )

        y -= 5

        # ============================================================
        # LÍNEA DIVISORIA
        # ============================================================

        p.setStrokeColor(styles.PRIMARY)
        p.setLineWidth(1)

        p.line(
            styles.MARGIN_LEFT,
            y,
            self.WIDTH - styles.MARGIN_RIGHT,
            y,
        )

        y -= 15

        # ============================================================
        # DATOS PREVENCION
        # ============================================================
        prevenciones = self.get_list_field(d, "prevencion")

        for prevencion in prevenciones:
            y = draw_text(
                p,
                f"•  {prevencion}",
                y,
                styles.MARGIN_LEFT + 10,
                styles.GRAY,
            )

        y -= 10

        # ============================================================
        # PIE DE PAGINA
        # ============================================================

        self.draw_footer()

        # NUEVA PAGINA
        p.showPage()
        
    def build(self):
        self.draw_cover()

        for diagnostico in self.diagnosticos:
            self.draw_diagnostico(diagnostico)

        self.p.save()