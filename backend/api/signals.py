from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import SolicitudCambioPlan, DiagnosticoIA
from .services.planes_service import sincronizar_plan_usuario



@receiver(post_save, sender=SolicitudCambioPlan)
def actualizar_plan_usuario(sender, instance, **kwargs):

    sincronizar_plan_usuario(
        instance.usuario
    )



@receiver(post_save, sender=DiagnosticoIA)
def verificar_plan_al_crear_diagnostico(sender, instance, created, **kwargs):

    if created:

        sincronizar_plan_usuario(
            instance.usuario
        )