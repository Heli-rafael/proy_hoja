from datetime import date
from ..models import CreditoDiario

def obtener_estado_creditos(usuario):
    plan = usuario.plan

    if not plan:
        return {
            "plan": None,
            "usados": 0,
            "limite": 0,
            "restantes": 0,
            "puede_usar": False
        }

    credito, _ = CreditoDiario.objects.get_or_create(
        usuario=usuario,
        fecha=date.today()
    )

    usados = credito.creditos_usados
    limite = plan.creditos_diarios

    return {
        "plan": plan.nombre,
        "usados": usados,
        "limite": limite,
        "restantes": max(limite - usados, 0),
        "puede_usar": usados < limite
    }


def get_credito_hoy(usuario):
    credito, _ = CreditoDiario.objects.get_or_create(
        usuario=usuario,
        fecha=date.today()
    )
    return credito


def puede_usar_credito(usuario):
    plan = usuario.plan
    if not plan:
        return False

    credito = get_credito_hoy(usuario)

    return credito.creditos_usados < plan.creditos_diarios


def consumir_credito(usuario):
    plan = usuario.plan

    credito = get_credito_hoy(usuario)

    if credito.creditos_usados >= plan.creditos_diarios:
        return False

    credito.creditos_usados += 1
    credito.save()
    return True