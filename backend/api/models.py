from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Usuario(AbstractUser):
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username}"

class Planta(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to="plantas/", blank=True, null=True)

    def __str__(self):
        return self.nombre
    
class DiagnosticoIA(models.Model):
    SEVERIDAD_CHOICES = [
        ("leve", "Leve"),
        ("moderada", "Moderada"),
        ("grave", "Grave"),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="diagnosticos")
    planta = models.ForeignKey(Planta, on_delete=models.SET_NULL, null=True)

    imagen = models.ImageField(upload_to="diagnosticos/")

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