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
        
        # 1. Guardamos la planta (esto guarda la imagen)
        planta = serializer.save()

        # 2. Lógica de "IA" (Aquí iría tu modelo real, ahora usamos datos ficticios)
        # En el futuro, aquí llamas a tu función de detección
        diagnostico = models.DiagnosticoIA.objects.create(
            usuario=request.user if request.user.is_authenticated else models.Usuario.objects.first(),
            planta=planta,
            imagen=planta.imagen, # Usamos la misma imagen
            enfermedad_detectada="Roya del Café",
            severidad="grave",
            porcentaje_salud=45.0,
            confianza_ia=98.5,
            tratamiento="Aplicar fungicida sistémico...",
            como_prevenir="Controlar la sombra y humedad..."
        )

        # 3. Creamos el Chat automáticamente
        chat = models.Chat.objects.create(
            usuario=diagnostico.usuario,
            diagnostico=diagnostico,
            titulo=f"Análisis: {diagnostico.enfermedad_detectada}"
        )

        # 4. Respondemos a Angular con el Chat (para que se ilumine en el sidebar)
        # Necesitarás un ChatSerializer para devolverlo limpio
        from .serializers import ChatSerializer
        chat_data = ChatSerializer(chat).data
        
        return Response(chat_data, status=status.HTTP_201_CREATED)

class DiagnosticoIAViewSet(viewsets.ModelViewSet):
    queryset = models.DiagnosticoIA.objects.all()
    serializer_class = serializers.DiagnosticoIASerializer
    permission_classes = [AllowAny]

class ChatViewSet(viewsets.ModelViewSet):
    queryset = models.Chat.objects.all()
    serializer_class = serializers.ChatSerializer
    permission_classes = [AllowAny]

class MensajeViewSet(viewsets.ModelViewSet):
    queryset = models.Mensaje.objects.all()
    serializer_class = serializers.MensajeSerializer
    permission_classes = [AllowAny]




















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