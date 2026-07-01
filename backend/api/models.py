from django.db import models
from django.contrib.auth.models import AbstractUser

import os
from django.utils.text import slugify

def nombre_imagen_usuario(instance, filename):
    extension = os.path.splitext(filename)[1]
    return f"usuarios/{slugify(instance.username)}{extension}"

# Create your models here.
class Usuario(AbstractUser):

    class TipoAutenticacion(models.TextChoices):
        LOCAL = "LOCAL", "Local"
        GOOGLE = "GOOGLE", "Google"

    autenticacion = models.CharField(
        max_length=10,
        choices=TipoAutenticacion.choices,
        default=TipoAutenticacion.LOCAL
    )

    email = models.EmailField(unique=True)
    picture = models.ImageField(
        upload_to=nombre_imagen_usuario,
        blank=True,
        null=True
    )
    plan = models.ForeignKey(
        "Plan",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usuarios"
    )
    
    phone = models.CharField(max_length=20, blank=True, null=True)
    state = models.BooleanField(default=True)

   
    def __str__(self):
        return f"{self.username}"
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    
class Plan(models.Model):
    
    orden = models.PositiveIntegerField(unique=True, default=1)
    nombre = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    creditos_diarios = models.IntegerField(default=3)

    beneficios = models.JSONField(default=list, blank=True)

    estado = models.BooleanField(default=True)

    destacado = models.BooleanField(default=False)


    def __str__(self):
        return self.nombre

class CreditoDiario(models.Model):
    usuario = models.ForeignKey("Usuario", on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    creditos_usados = models.IntegerField(default=0)

    class Meta:
        unique_together = ("usuario", "fecha")

# Plantas
class Planta(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to="plantas/", blank=True, null=True)

    def __str__(self):
        return self.nombre

class EstadoImagen(models.TextChoices):
    PENDIENTE = "Pendiente", "Pendiente"
    PROCESANDO = "Procesando", "Procesando"
    COMPLETADO = "Completado", "Completado"
    ERROR = "Error", "Error"

class DiagnosticoIA(models.Model):
    SEVERIDAD_CHOICES = [
        ("Leve", "Leve"),
        ("Moderada", "Moderada"),
        ("Grave", "Grave"),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="diagnosticos")
    planta = models.ForeignKey(Planta, on_delete=models.CASCADE, related_name="diagnosticos")

    imagen = models.ImageField(upload_to="diagnosticos/")
    estado_imagen = models.CharField(
        max_length=30,
        choices=EstadoImagen.choices,
        default=EstadoImagen.PENDIENTE
    )

    enfermedad_detectada = models.CharField(max_length=200)

    severidad = models.CharField(max_length=20, choices=SEVERIDAD_CHOICES)

    porcentaje_salud = models.FloatField()     # 0–100
    confianza_ia = models.FloatField()         # 0–100

    tratamiento_natural = models.JSONField(default=list, blank=True)
    tratamiento_quimico = models.JSONField(default=list, blank=True)
    prevencion = models.JSONField(default=list, blank=True)

    sintomas_detectados = models.JSONField(default=list, blank=True)
    prediccion_evolucion = models.JSONField(default=list, blank=True)
    plagas_relacionadas = models.JSONField(default=list, blank=True)
    factores_climaticos_favorables = models.JSONField(default=dict, blank=True)
    
    urgencia = models.CharField(max_length=20, blank=True)
    contagio = models.CharField(max_length=20, blank=True)
    recuperacion = models.CharField(max_length=20, blank=True)
    etapa = models.CharField(max_length=50, blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.planta} - {self.enfermedad_detectada}"

class ActividadTratamiento(models.Model):
    diagnostico = models.ForeignKey(
        DiagnosticoIA,
        on_delete=models.CASCADE,
        related_name="actividades"
    )

    actividad = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20)
    semana = models.IntegerField()
    completada = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.diagnostico} - {self.tipo}"

class Chat(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="chats")
    titulo = models.CharField(max_length=200, default="Nuevo chat")

    diagnostico = models.OneToOneField(
        DiagnosticoIA,
        on_delete=models.CASCADE,
        related_name="chat"
    )
    
    is_pinned = models.BooleanField(default=False)

    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
    
class Mensaje(models.Model):
    TIPO_CHOICES = [
        ("usuario", "Usuario"),
        ("ia", "IA"),
    ]

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="mensajes")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)

    texto = models.TextField()

    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - Chat {self.chat_id}"