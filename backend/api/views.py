from django.http import JsonResponse

from . import models
from . import serializers
import json
from rest_framework import viewsets, status


# PERMISOS SESION
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import SessionAuthentication

# SERVICIO
from .services.openai_service import generar_respuesta_chat

# RESPUESTAS
from rest_framework.response import Response
from django.http import JsonResponse

# DECORADORES
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.contrib.auth import login, logout, authenticate

# GOOGLE
from google.oauth2 import id_token
from google.auth.transport import requests

# SETTINGS
from django.conf import settings

from rest_framework.views import APIView

# REPORTES
from django.http import HttpResponse
from api.services.pdf.report import DiagnosticosPDFReport
from api.services.excel.report import (
    export_chats,
    export_diagnosticos
)


# ===== USUARIO =====
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = models.Usuario.objects.all()
    serializer_class = serializers.UsuarioSerializer
    permission_classes = [IsAuthenticated]

# CONTRASEÑA
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        actual_password = request.data.get("actualPassword")
        new_password = request.data.get("password")

        if not user.check_password(actual_password):
            return Response(
                {"error": "Contraseña actual incorrecta"},
                status=400
            )

        user.set_password(new_password)
        user.save()

        return Response({"message": "Contraseña actualizada"})
    
class PlanViewSet(viewsets.ModelViewSet):
    queryset = models.Plan.objects.all()
    serializer_class = serializers.PlanSerializer
    permission_classes = [AllowAny]

class CreditoDiarioViewSet(viewsets.ModelViewSet):
    queryset = models.CreditoDiario.objects.all()
    serializer_class = serializers.CreditoDiarioSerializer
    permission_classes = [IsAuthenticated]


class PlantaViewSet(viewsets.ModelViewSet):
    queryset = models.Planta.objects.all()
    serializer_class = serializers.PlantaCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        chat = serializer.save()

        response_serializer = serializers.ChatSerializer(chat)

        return Response(
            {"chat": response_serializer.data},
            status=status.HTTP_201_CREATED
        )

class DiagnosticoIAViewSet(viewsets.ModelViewSet):
    queryset = models.DiagnosticoIA.objects.all()
    serializer_class = serializers.DiagnosticoIASerializer
    permission_classes = [IsAuthenticated]

class ActividadTratamientoViewSet(viewsets.ModelViewSet):
    queryset = models.ActividadTratamiento.objects.all()
    serializer_class = serializers.ActividadTratamientoSerializer
    permission_classes = [IsAuthenticated]

class ChatViewSet(viewsets.ModelViewSet):
    queryset = models.Chat.objects.all()
    serializer_class = serializers.ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.Chat.objects.filter(usuario=self.request.user)

class MensajeViewSet(viewsets.ModelViewSet):
    queryset = models.Mensaje.objects.all()
    serializer_class = serializers.MensajeSerializer
    permission_classes = [IsAuthenticated]

# =========================
# ESTADO DEL USUARIO
# =========================
def set_estado_usuario(user, estado: bool):
    user.estado = estado
    user.save(update_fields=['state'])

# =========================
# FIJAR CHAT
# =========================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_pinned(request, id):

    chat = models.Chat.objects.get(id=id, usuario=request.user)

    chat.is_pinned = not chat.is_pinned
    chat.save()

    return Response({
        "id": chat.id,
        "is_pinned": chat.is_pinned
    })

# =========================
# ENVIAR MENSAJE
# =========================
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

    # GUARDAR MENSAJE USUARIO
    mensaje_usuario = models.Mensaje.objects.create(
        chat=chat,
        tipo="usuario",
        texto=texto
    )

    # RESPUESTA IA

    diagnostico = chat.diagnostico

    respuesta_ia = generar_respuesta_chat(
        texto,
        diagnostico
    )

    mensaje_ia = models.Mensaje.objects.create(
        chat=chat,
        tipo="ia",
        texto=respuesta_ia
    )

    return Response({
        "usuario": serializers.MensajeSerializer(mensaje_usuario).data,
        "ia": serializers.MensajeSerializer(mensaje_ia).data
    })

# =========================
# OBTENER MENSAJE
# =========================
@api_view(['GET'])
def obtener_mensajes(request, chat_id):

    mensajes = models.Mensaje.objects.filter(
        chat_id=chat_id
    ).order_by('creado_en')

    serializer = serializers.MensajeSerializer(mensajes, many=True)

    return Response(serializer.data)

# =========================
# DATOS PROPIOS
# =========================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication])
def me(request):
    user = request.user

    serializer = serializers.MeSerializer(
        user,
        context={"request": request}
    )

    return Response(serializer.data)

# =========================
# LOGIN EN BASE DE DATOS
# =========================
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Se requieren email y contraseña'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, email=email, password=password)

    if user is None:
        return Response({'error': 'Email o contraseña incorrectos'}, status=status.HTTP_400_BAD_REQUEST)

    # Cambiar Estado
    set_estado_usuario(user, True)

    login(request, user)
    
    return Response({
        'message': 'Login exitoso',
        'user_id': user.pk,
        'email': user.email,
        'username': user.username,
        'first_name': user.first_name
    })

# =========================
# LOGIN CON GOOGLE
# =========================

import requests
from google.auth.transport.requests import Request
from django.core.files.base import ContentFile
from django.utils.text import slugify

@csrf_exempt
def google_login(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Método inválido"},
            status=400
        )

    try:

        body = json.loads(request.body)
        token = body.get("token")

        # validar token con Google
        idinfo = id_token.verify_oauth2_token(
            token,
            Request(),
            settings.GOOGLE_CLIENT_ID
        )

        email = idinfo["email"]
        name = idinfo.get("name")
        given_name = idinfo["given_name"]
        family_name = idinfo["family_name"]
        picture = idinfo.get("picture")

        # buscar usuario
        user = models.Usuario.objects.filter(email=email).first()

        # crear si no existe
        if not user:

            default_plan = models.Plan.objects.get(orden=1)

            user = models.Usuario.objects.create_user(
                username=name,
                email=email,
                first_name=given_name,
                last_name=family_name,
                plan=default_plan,
                autenticacion=models.Usuario.TipoAutenticacion.GOOGLE
            )

            user.set_unusable_password()

            if picture:
                response = requests.get(picture)

                if response.status_code == 200:
                    filename = f"{slugify(user.username)}.jpg"

                    user.picture.save(
                        filename,
                        ContentFile(response.content),
                        save=False
                    )

            user.save()

        # Cambiamos Estado
        set_estado_usuario(user, True)

        # login django session
        login(request, user)

        return JsonResponse({
            "success": True,
            "email": email,
            "first_name": user.first_name,
            "picture": user.picture.url if user.picture else None
        })

    except ValueError:

        return JsonResponse({
            "error": "Token inválido"
        }, status=400)
    
# =========================
# CERRAR SESION
# =========================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication])
def logout_view(request):
    
    user = request.user
    # Cambiar el estado
    set_estado_usuario(user, False)

    # Cerrar sesión
    logout(request)
    return Response({'detail': 'Logged out'})


# =========================
# EXPORTAR REPORTES
# =========================
# EXPORT CHATS EXCEL
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_chats_excel(request):

    chats = models.Chat.objects.filter(
        usuario=request.user
    )

    return export_chats(chats)

# EXPORT DIAGNOSTICO EXCEL
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_diagnosticos_excel(request):

    diagnosticos = models.DiagnosticoIA.objects.filter(
        usuario=request.user
    )

    return export_diagnosticos(diagnosticos)

# EXPORT DIAGNOSTICOS PDF
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_diagnosticos_pdf(request):

    user = request.user
    diagnosticos = models.DiagnosticoIA.objects.filter(usuario=user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=reporte_premium.pdf'

    report = DiagnosticosPDFReport(user, diagnosticos, response)
    report.build()

    return response

# EXPORT DIAGNOSTICO PDF
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_diagnostico_pdf(request, id):

    user = request.user

    try:
        diagnostico = models.DiagnosticoIA.objects.get(
            id=id,
            usuario=user
        )
    except models.DiagnosticoIA.DoesNotExist:
        return HttpResponse(status=404)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=diagnostico_{id}.pdf'

    report = DiagnosticosPDFReport(user, [diagnostico], response)
    report.build()

    return response