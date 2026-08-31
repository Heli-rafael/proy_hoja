from django.utils import timezone

from ..models import Plan, SolicitudCambioPlan


def sincronizar_plan_usuario(usuario):
    """
    Sincroniza el plan del usuario con su suscripción vigente.
    Si no tiene una suscripción activa, se asigna el plan base (orden=1).
    """

    ahora = timezone.now()

    solicitud = (
        SolicitudCambioPlan.objects
        .select_related("plan_solicitado__plan")
        .filter(
            usuario=usuario,
            estado=SolicitudCambioPlan.EstadoSolicitud.APROBADA,
            fecha_inicio_plan__lte=ahora,
            fecha_fin_plan__gt=ahora,
        )
        .order_by("-fecha_fin_plan")
        .first()
    )

    # Existe una suscripción vigente
    if solicitud:
        nuevo_plan = solicitud.plan_solicitado.plan

        if usuario.plan_id != nuevo_plan.id:
            usuario.plan = nuevo_plan
            usuario.save(update_fields=["plan"])

        return

    # No existe una suscripción vigente: asignar el plan base (orden=1)
    plan_base = (
        Plan.objects
        .filter(orden=1, estado=True)
        .first()
    )

    if plan_base and usuario.plan_id != plan_base.id:
        usuario.plan = plan_base
        usuario.save(update_fields=["plan"])