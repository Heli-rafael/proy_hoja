from django.utils import timezone

from .models import SolicitudCambioPlan


def verificar_planes():

    ahora = timezone.now()

    solicitudes_vencidas = SolicitudCambioPlan.objects.filter(
        estado=SolicitudCambioPlan.EstadoSolicitud.APROBADA,
        fecha_fin_plan__isnull=False,
        fecha_fin_plan__lte=ahora
    )


    for solicitud in solicitudes_vencidas:

        usuario = solicitud.usuario


        # Verificamos que siga teniendo ese plan
        if usuario.plan_id == solicitud.plan_solicitado.plan_id:

            usuario.plan = None
            usuario.save(update_fields=["plan"])


            print(
                f"Plan removido a {usuario.email}. "
                f"Plan vencido: {solicitud.plan_solicitado.plan.nombre}"
            )