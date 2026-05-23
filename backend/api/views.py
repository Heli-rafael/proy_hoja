from django.http import JsonResponse

from . import models
from . import serializers
from rest_framework import viewsets, status

from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticated
from rest_framework.authentication import SessionAuthentication

from rest_framework.response import Response

from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)

from django.contrib.auth import authenticate, login

from rest_framework import viewsets
from rest_framework import status

from .service.validador_imagen import validar_imagen_planta
from .service.openai_service import (
    analizar_planta_con_openai,
    generar_respuesta_chat
)
from .service.generador_imagen import generar_imagen_anotada
import json
import threading

from .service.services import puede_usar_credito, consumir_credito


from .service.services import obtener_estado_creditos


# ===== USUARIO =====
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = models.Usuario.objects.all()
    serializer_class = serializers.UsuarioSerializer
    permission_classes = [AllowAny]

class PlanViewSet(viewsets.ModelViewSet):
    queryset = models.Plan.objects.all()
    serializer_class = serializers.PlanSerializer
    permission_classes = [IsAuthenticated]

class CreditoDiarioViewSet(viewsets.ModelViewSet):
    queryset = models.CreditoDiario.objects.all()
    serializer_class = serializers.CreditoDiarioSerializer
    permission_classes = [IsAuthenticated]


class PlantaViewSet(viewsets.ModelViewSet):
    queryset = models.Planta.objects.all()
    serializer_class = serializers.PlantaSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        
        usuario = request.user if request.user.is_authenticated else None

        # ==================================================
        # VALIDAMOS CREDITOS
        # ==================================================

        if not puede_usar_credito(usuario):
            return Response(
                {"error": "No tienes créditos disponibles para realizar esta consulta."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # ==================================================
        # VALIDAMOS SERILIZERS
        # ==================================================

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # ==================================================
        # VALIDAR IMAGEN EXISTENTE
        # ==================================================

        if 'imagen' not in request.FILES:

            return Response(
                {
                    "error": "Debes enviar una imagen."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        original_file = request.FILES['imagen']

        # ==================================================
        # VALIDAR TAMAÑO
        # ==================================================

        if original_file.size > 10 * 1024 * 1024:

            return Response(
                {
                    "error": "La imagen supera el límite permitido de 10MB."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==================================================
        # VALIDACIÓN IA RÁPIDA
        # ==================================================

        try:

            original_file.seek(0)

            validacion = validar_imagen_planta(
                original_file
            )

        except Exception as e:

            return Response(
                {
                    "error": "Error validando imagen",
                    "detalle": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if (
            not validacion.get("es_planta")
            or not validacion.get("es_apta_para_analisis")
        ):

            return Response(
                {
                    "error": "Imagen inválida",
                    "detalle": validacion.get(
                        "motivo",
                        "La imagen no contiene hojas o plantas válidas."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==================================================
        # GUARDAR PLANTA
        # ==================================================

        planta = serializer.save()

        # CONSUMIR CRÉDITO AQUÍ
        consumir_credito(usuario)
        
        # USUARIO
        usuario = request.user

        # ==================================================
        # ANALIZAR PLANTA CON IA
        # ==================================================

        try:

            original_file.seek(0)

            try:
                data = analizar_planta_con_openai(
                    original_file
                    )
            except:
                return error

        except Exception as e:

            return Response(
                {
                    "error": "Error analizando planta",
                    "detalle": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # ==================================================
        # ACTUALIZAR DATOS PLANTA
        # ==================================================

        planta.nombre = data.get(
            "nombre_planta",
            planta.nombre
        )

        planta.descripcion = data.get(
            "descripcion_planta",
            ""
        )

        planta.save()

        # ==================================================
        # CREAR DIAGNÓSTICO
        # ==================================================

        diagnostico = models.DiagnosticoIA.objects.create(

            usuario=usuario,

            planta=planta,

            estado_imagen=models.EstadoImagen.PENDIENTE,

            enfermedad_detectada=data.get(
                "enfermedad_detectada",
                "Sin detección"
            ),

            severidad=data.get(
                "severidad",
                "leve"
            ),

            porcentaje_salud=data.get(
                "porcentaje_salud",
                0
            ),

            confianza_ia=data.get(
                "confianza_ia",
                0
            ),

            tratamiento=data.get(
                "tratamiento",
                ""
            ),

            como_prevenir=data.get(
                "como_prevenir",
                ""
            )
        )

        # ==================================================
        # BACKGROUND IMAGE GENERATION
        # ==================================================

        original_file.seek(0)

        image_bytes = original_file.read()

        threading.Thread(
            target=self.procesar_imagen_background,
            args=(
                diagnostico.id,
                image_bytes,
                data
            ),
            daemon=True
        ).start()

        # ==================================================
        # CREAR CHAT
        # ==================================================

        chat = models.Chat.objects.create(

            usuario=usuario,

            diagnostico=diagnostico,

            titulo=f"Análisis: {diagnostico.enfermedad_detectada}"
        )

        response_serializer = serializers.ChatSerializer(chat)

        return Response(
            {
                "chat": response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    
    def procesar_imagen_background(
        self,
        diagnostico_id,
        image_bytes,
        data
    ):
        try:

            diagnostico = models.DiagnosticoIA.objects.get(
                id=diagnostico_id
            )

            diagnostico.estado_imagen = models.EstadoImagen.PROCESANDO
            diagnostico.save()

            from io import BytesIO

            image_buffer = BytesIO(image_bytes)
            image_buffer.name = "plant.jpg"

            imagen_anotada = generar_imagen_anotada(
                image_buffer,
                data
            )

            diagnostico.imagen = imagen_anotada
            diagnostico.estado_imagen = models.EstadoImagen.COMPLETADO

            diagnostico.save()

        except Exception as e:

            try:
                diagnostico.estado_imagen = models.EstadoImagen.ERROR
                diagnostico.save()
            except:
                pass

            print(e)

class DiagnosticoIAViewSet(viewsets.ModelViewSet):
    queryset = models.DiagnosticoIA.objects.all()
    serializer_class = serializers.DiagnosticoIASerializer
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

@api_view(['GET'])
def obtener_mensajes(request, chat_id):

    mensajes = models.Mensaje.objects.filter(
        chat_id=chat_id
    ).order_by('creado_en')

    serializer = serializers.MensajeSerializer(mensajes, many=True)

    return Response(serializer.data)













def set_estado_usuario(user, estado: bool):
    user.estado = estado
    user.save(update_fields=['estado'])



from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication])
def me(request):
    user = request.user
    return Response(serializers.MeSerializer(user).data)

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

    # Cambiar Estado
    set_estado_usuario(user, True)

    login(request, user)
    
    return Response({
        'message': 'Login exitoso',
        'user_id': user.pk,
        'email': user.email,
        'first_name': user.first_name
    })

from django.contrib.auth import logout
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from google.oauth2 import id_token
from google.auth.transport import requests

from django.contrib.auth import login

from django.http import JsonResponse
import json

GOOGLE_CLIENT_ID = "706928771973-055jk48vvstl4sj8pu2seht1qhfolint.apps.googleusercontent.com"


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
            requests.Request(),
            GOOGLE_CLIENT_ID
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

            default_plan = models.Plan.objects.get(id=1)

            user = models.Usuario.objects.create_user(
                username=name,
                email=email,
                first_name=given_name,
                last_name=family_name,
                picture=picture,
                plan=default_plan
            )

            user.set_unusable_password()
            user.save()

        # Cambiamos Estado
        set_estado_usuario(user, True)

        # login django session
        login(request, user)
        print(idinfo)

        return JsonResponse({
            "success": True,
            "email": email,
            "first_name": user.first_name,
            "picture": picture
        })

    except ValueError:

        return JsonResponse({
            "error": "Token inválido"
        }, status=400)
    

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