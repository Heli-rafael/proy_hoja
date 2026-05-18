from django.http import JsonResponse

from . import models
from . import serializers
from rest_framework import viewsets, status

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication

from rest_framework.response import Response

from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)

from django.contrib.auth import authenticate, login

from rest_framework import viewsets
from rest_framework import status

from .service.openai_service import analizar_planta_con_openai
from .service.image_processing import dibujar_zonas_afectadas
import json


# ===== USUARIO =====
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = models.Usuario.objects.all()
    serializer_class = serializers.UsuarioSerializer
    permission_classes = [AllowAny]


class PlantaViewSet(viewsets.ModelViewSet):
    queryset = models.Planta.objects.all()
    serializer_class = serializers.PlantaSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 1. guardar planta base
        planta = serializer.save()

        usuario = request.user if request.user.is_authenticated else models.Usuario.objects.first()

        # 2. OpenAI
        try:
            file = request.FILES['imagen']
            file.seek(0)

            resultado_json = analizar_planta_con_openai(file)
            data = json.loads(resultado_json)

        except Exception as e:
            return Response(
                {"error": "Error IA", "detalle": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 3. generar imagen anotada
        file.seek(0)
        zonas = data.get("zonas_afectadas", [])

        imagen_anotada = dibujar_zonas_afectadas(file, zonas)

        # 4. actualizar nombre y descripcion planta
        planta.nombre = data.get("nombre_planta", planta.nombre)
        planta.descripcion = data.get("descripcion_planta", "")
        planta.save()

        # 5. guardar diagnostico con imagen marcada
        diagnostico = models.DiagnosticoIA.objects.create(
            usuario=usuario,
            planta=planta,
            imagen=imagen_anotada,
            enfermedad_detectada=data["enfermedad_detectada"],
            severidad=data["severidad"],
            porcentaje_salud=data["porcentaje_salud"],
            confianza_ia=data["confianza_ia"],
            tratamiento=data["tratamiento"],
            como_prevenir=data["como_prevenir"]
        )

        # 6. chat
        chat = models.Chat.objects.create(
            usuario=usuario,
            diagnostico=diagnostico,
            titulo=f"Análisis: {diagnostico.enfermedad_detectada}"
        )

        serializer = serializers.ChatSerializer(chat)
        return Response({
            "chat": serializer.data
        })

class DiagnosticoIAViewSet(viewsets.ModelViewSet):
    queryset = models.DiagnosticoIA.objects.all()
    serializer_class = serializers.DiagnosticoIASerializer
    permission_classes = [AllowAny]

class ChatViewSet(viewsets.ModelViewSet):
    queryset = models.Chat.objects.all()
    serializer_class = serializers.ChatSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return models.Chat.objects.filter(usuario=self.request.user)

class MensajeViewSet(viewsets.ModelViewSet):
    queryset = models.Mensaje.objects.all()
    serializer_class = serializers.MensajeSerializer
    permission_classes = [AllowAny]



@api_view(['POST'])
def enviar_mensaje(request):

    chat_id = request.data.get("chat")
    texto = request.data.get("texto")

    try:
        chat = models.Chat.objects.get(id=chat_id)
    except models.Chat.DoesNotExist:
        return Response(
            {"error": "Chat no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )

    # =========================
    # GUARDAR MENSAJE USUARIO
    # =========================
    mensaje_usuario = models.Mensaje.objects.create(
        chat=chat,
        tipo="usuario",
        texto=texto
    )

    # =========================
    # RESPUESTA IA (FAKE)
    # =========================

    respuesta_ia = generar_respuesta_predeterminada(texto)

    mensaje_ia = models.Mensaje.objects.create(
        chat=chat,
        tipo="ia",
        texto=respuesta_ia
    )

    return Response({
        "usuario": serializers.MensajeSerializer(mensaje_usuario).data,
        "ia": serializers.MensajeSerializer(mensaje_ia).data
    })


def generar_respuesta_predeterminada(texto):

    texto = texto.lower()

    if "hojas" in texto:
        return "Las hojas presentan posibles signos de estrés hídrico."

    elif "amarillo" in texto:
        return "La coloración amarilla puede indicar falta de nitrógeno."

    elif "hongos" in texto:
        return "Se detectan posibles hongos. Recomendamos fungicida preventivo."

    else:
        return "La planta necesita una revisión más detallada."


@api_view(['GET'])
def obtener_mensajes(request, chat_id):

    mensajes = models.Mensaje.objects.filter(
        chat_id=chat_id
    ).order_by('creado_en')

    serializer = serializers.MensajeSerializer(mensajes, many=True)

    return Response(serializer.data)

















from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication])
def me(request):
    user = request.user
    return Response({
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "rol": getattr(user, 'rol', None),
        "estado": getattr(user, 'estado', None),
        "last_login": user.last_login,

        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "is_active": user.is_active,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Se requieren email y contraseña'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=email, password=password)

    if user is None:
        return Response({'error': 'Email o contraseña incorrectos'}, status=status.HTTP_400_BAD_REQUEST)

    # Cambiar estado
    user.estado = True
    user.save(update_fields=['estado'])

    login(request, user)
    return Response({
        'message': 'Login exitoso',
        'user_id': user.pk,
        'email': user.email,
        'username': user.username
    })

from django.contrib.auth import logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication])
def logout_view(request):
    
    user = request.user
    # Cambiar el estado
    user.estado = False
    user.save(update_fields=['estado'])

    # Cerrar sesión
    logout(request)
    return Response({'detail': 'Logged out'})