from django.http import HttpResponse

from .config import (
    EXCEL_CONTENT_TYPE,
    create_workbook
)
from .components import (
    add_header,
    add_row
)


def export_chats(chats):

    wb, ws = create_workbook("Chats")

    add_header(ws, [
        "ID",
        "Título",
        "Fecha"
    ])

    for chat in chats:
        add_row(ws, [
            chat.id,
            chat.titulo,
            chat.creado_en.strftime("%Y-%m-%d %H:%M")
        ])

    response = HttpResponse(content_type=EXCEL_CONTENT_TYPE)
    response["Content-Disposition"] = 'attachment; filename="chats.xlsx"'

    wb.save(response)

    return response


def export_diagnosticos(data):

    wb, ws = create_workbook("Diagnosticos")

    add_header(ws, [
        "ID",
        "Planta",
        "Enfermedad",
        "Severidad",
        "Estado Imagen",
        "Salud (%)",
        "Confianza IA (%)",
        "Urgencia",
        "Contagio",
        "Etapa",
        "Recuperación",

        "Temperatura",
        "Humedad",
        "Viento",

        "Síntomas",
        "Tratamiento Natural",
        "Tratamiento Químico",
        "Prevención",

        "Predicción Evolución",
        "Plagas Relacionadas",
        "Plan de Acción",

        "Fecha"
    ])

    for d in data:

        clima = d.factores_climaticos_favorables or {}

        evolucion = "\n".join(
            f"{e['periodo']}: {e['descripcion']}"
            for e in d.prediccion_evolucion
        )

        plagas = "\n".join(
            f"{p['plaga']} ({p['riesgo']})"
            for p in d.plagas_relacionadas
        )

        actividades = "\n".join(
            f"Semana {a.semana}: {a.actividad}"
            for a in d.actividades.all()
        )

        add_row(ws, [

            d.id,
            d.planta.nombre,
            d.enfermedad_detectada,
            d.severidad,
            d.estado_imagen,
            d.porcentaje_salud,
            d.confianza_ia,
            d.urgencia,
            d.contagio,
            d.etapa,
            d.recuperacion,

            clima.get("temperatura", ""),
            clima.get("humedad", ""),
            clima.get("viento", ""),

            "\n".join(d.sintomas_detectados),

            "\n".join(d.tratamiento_natural),

            "\n".join(d.tratamiento_quimico),

            "\n".join(d.prevencion),

            evolucion,
            plagas,
            actividades,

            d.creado_en.strftime("%Y-%m-%d %H:%M")
        ])

    response = HttpResponse(content_type=EXCEL_CONTENT_TYPE)
    response["Content-Disposition"] = 'attachment; filename="diagnosticos.xlsx"'

    wb.save(response)

    return response