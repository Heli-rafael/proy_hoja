from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Usuario(AbstractUser):
    estado = models.BooleanField(default=True)
    picture = models.URLField(blank=True, null=True)

    plan = models.ForeignKey(
        "Plan",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usuarios"
    )
    
    def __str__(self):
        return f"{self.username}"
    
class Plan(models.Model):
    nombre = models.CharField(max_length=50)
    creditos_diarios = models.IntegerField(default=3)
    descripcion = models.TextField(blank=True, null=True)

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

    tratamiento = models.TextField()
    como_prevenir = models.TextField()

    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.planta} - {self.enfermedad_detectada}"
    
class Chat(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="chats")
    titulo = models.CharField(max_length=200, default="Nuevo chat")

    diagnostico = models.OneToOneField(
        DiagnosticoIA,
        on_delete=models.CASCADE,
        related_name="chat"
    )

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