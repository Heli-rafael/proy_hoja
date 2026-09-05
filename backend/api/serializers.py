from rest_framework import serializers
from datetime import date
from . import models

import threading

from .services.validador_imagen import validar_imagen_planta

from .services.openai_service import (
    analizar_planta_con_openai
)

from .services.gemini_service import generar_imagen_anotada

from .services.creditos_service import (
    puede_usar_credito,
    consumir_credito
)
from django.utils import timezone
from django.core.files.storage import default_storage

from django.db import transaction
from io import BytesIO


from django.contrib.auth import get_user_model
User = get_user_model()

# PLAN
class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Plan
        fields = [
            'id',
            'orden',
            'nombre',
            'creditos_diarios',
            'beneficios',
            'estado',
            'destacado',
        ]

class PlanPrecioSerializer(serializers.ModelSerializer):

    plan = PlanSerializer(read_only=True)

    class Meta:
        model = models.PlanPrecio
        fields = [
            'id',
            'plan',
            'periodo',
            'precio',
        ]

class SolicitudCambioPlanSerializer(serializers.ModelSerializer):

    plan_solicitado = PlanPrecioSerializer(read_only=True)

    plan_solicitado_id = serializers.PrimaryKeyRelatedField(
        queryset=models.PlanPrecio.objects.all(),
        source='plan_solicitado',
        write_only=True
    )
    
    class Meta:
        model = models.SolicitudCambioPlan
        fields = [
            'id',
            'usuario',
            'plan_actual',
            'plan_solicitado',
            'plan_solicitado_id',
            'metodo_pago',
            'comprobante',
            'observacion',
            'estado',
            'creado_en',
        ]

        read_only_fields = [
            'usuario',
            'plan_actual',
            'estado',
            'creado_en',
        ]

# USUARIO

class UsuarioSerializer(serializers.ModelSerializer):

    plan = PlanSerializer(read_only=True)

    # Campos para usar las validaciones personalizadas
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(required=False, write_only=True, allow_blank=False)

    class Meta:
        model = models.Usuario
        fields = [
            'id', 
            #'autenticacion',
            'username', 
            'password',
            'first_name', 
            'last_name',

            'email', 
            'phone',
            'state', 
            'picture',
            'plan',

            #'last_login', 
            #'is_superuser', 
            #'is_staff', 
            #'is_active'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password', None)

        if not password:
            raise serializers.ValidationError("El campo contraseña es obligatorio")
    
        user = models.Usuario(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        nueva_imagen = validated_data.pop('picture', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        if nueva_imagen:
            if instance.picture:
                if default_storage.exists(instance.picture.name):
                    default_storage.delete(instance.picture.name)

            instance.picture = nueva_imagen

        instance.save()
        return instance

    def delete(self, instance):
        instance.delete()
        return instance

class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    nickname = serializers.CharField(
        source='username',
        min_length=3
    )

    name = serializers.CharField(source='first_name')
    lastname = serializers.CharField(source='last_name')

    class Meta:
        model = models.Usuario
        fields = [
            'email',
            'password',
            'nickname',
            'name',
            'lastname',
            'phone',
        ]

    def validate_email(self, value):
        if models.Usuario.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Ya existe una cuenta con este correo."
            )

        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        default_plan = models.Plan.objects.get(orden=1)

        user = models.Usuario(
            autenticacion=models.Usuario.TipoAutenticacion.LOCAL,
            plan=default_plan,
            **validated_data
        )

        user.set_password(password)
        user.save()

        return user


# OTP

class RequestOTPSerializer(serializers.Serializer):

    email = serializers.EmailField()
    purpose = serializers.ChoiceField(
        choices=[
            "login",
            "register",
            "reset_password",
        ],
        default="login",
    )

    def validate(self, attrs):

        email = attrs["email"]
        purpose = attrs["purpose"]

        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:

            if purpose == "register":
                self.user = None
                return attrs

            raise serializers.ValidationError({
                "email": "No existe un usuario con este email."
            })

        if purpose == "register":
            raise serializers.ValidationError({
                "detail": "Ya existe un usuario con este email."
            })

        self.user = user

        return attrs


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.RegexField(
        regex=r"^\d{6}$",
        error_messages={
            "invalid": "El código debe tener 6 dígitos."
        },
    )
    purpose = serializers.ChoiceField(
        choices=[
            "login",
            "register",
            "reset_password",
        ],
        default="login",
    )

class MeSerializer(serializers.ModelSerializer):

    plan = PlanSerializer(read_only=True)
    creditos = serializers.SerializerMethodField()
    suscripcion = serializers.SerializerMethodField()


    def get_creditos(self, obj):

        plan = obj.plan

        if not plan:
            return {
                "creditos_diarios": 0,
                "usados": 0,
                "restantes": 0
            }

        credito, _ = models.CreditoDiario.objects.get_or_create(
            usuario=obj,
            fecha=date.today()
        )

        usados = credito.creditos_usados

        return {
            "creditos_diarios": plan.creditos_diarios,
            "usados": usados,
            "restantes": max(plan.creditos_diarios - usados, 0)
        }


    def get_suscripcion(self, obj):

        solicitud = (
            obj.solicitudes_plan
            .filter(
                estado="APROBADA",
                fecha_fin_plan__gt=timezone.now()
            )
            .order_by("fecha_fin_plan")
            .first()
        )

        if not solicitud:
            return None

        diferencia = solicitud.fecha_fin_plan - timezone.now()

        if diferencia.total_seconds() <= 0:
            return None

        dias = diferencia.days
        horas, resto = divmod(diferencia.seconds, 3600)
        minutos, _ = divmod(resto, 60)

        return {
            "inicio": solicitud.fecha_inicio_plan,
            "fin": solicitud.fecha_fin_plan,
            "dias_restantes": dias,
            "horas_restantes": horas,
            "minutos_restantes": minutos
        }


    class Meta:
        model = models.Usuario
        fields = [
            'id',
            'autenticacion',
            'username',
            'first_name',
            'last_name',
            'email',
            'phone',
            'state',
            'picture',
            'plan',
            'creditos',
            'suscripcion',
            'last_login',
            'is_superuser',
            'is_staff',
            'is_active'
        ]

class CreditoDiarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CreditoDiario
        fields = ['id', 'usuario', 'fecha', 'creditos_usados']

# Planta

class PlantaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Planta
        fields = ['id', 'nombre', 'descripcion', 'imagen']

class ActividadTratamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ActividadTratamiento
        fields = ["id", "diagnostico", "actividad", "tipo", "semana", "completada"]


class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Mensaje
        fields = ['id', 'chat', 'tipo', 'texto', 'creado_en']
    
class DiagnosticoIASerializer(serializers.ModelSerializer):

    planta = PlantaSerializer(read_only=True)
    actividades = ActividadTratamientoSerializer(many=True, read_only=True)
    
    class Meta:
        model = models.DiagnosticoIA
        fields = [
            'id',
            'usuario', 
            'planta', 
            'imagen', 
            'estado_imagen',
            'enfermedad_detectada', 
            'severidad', 
            'porcentaje_salud', 
            'confianza_ia', 
            'lesiones_detectadas',
            'tratamiento_natural', 
            'tratamiento_quimico', 
            'prevencion', 
            'sintomas_detectados',
            'prediccion_evolucion',
            'plagas_relacionadas',
            'factores_climaticos_favorables',
            'urgencia',
            'contagio',
            'recuperacion',
            'etapa',
            'actividades',
            'creado_en',
            'progreso'
        ]

class ChatSerializer(serializers.ModelSerializer):

    diagnostico = DiagnosticoIASerializer(read_only=True)
    mensajes = MensajeSerializer(many=True, read_only=True)
    
    class Meta:
        model = models.Chat
        fields = [
            "id",
            "titulo",
            "diagnostico",
            "is_pinned",
            "creado_en",
            "mensajes",
        ]


class DiagnosticoProgresoSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.DiagnosticoIA

        fields = [
            "id",
            "progreso",
            "estado_imagen",
        ]

# ==============================
# CREAR PLANTA Y DIAGNOSTICOS
# ==============================
class PlantaCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Planta
        fields = ['id', 'nombre', 'descripcion', 'imagen']

    # ========================================================
    # VALIDAR IMAGEN
    # ========================================================
    def validate_imagen(self, value):

        request = self.context.get("request")

        if not request or not request.user.is_authenticated:

            raise serializers.ValidationError(
                "Usuario no autenticado."
            )

        usuario = request.user

        # 1. VALIDAR CRÉDITOS
        if not puede_usar_credito(usuario):

            raise serializers.ValidationError({
                "error": "No tienes créditos disponibles."
            })

        # 2. VALIDAR TAMAÑO
        if value.size > 10 * 1024 * 1024:

            raise serializers.ValidationError(
                "La imagen supera el límite permitido de 10MB."
            )

        # 3. VALIDAR IMAGEN
        try:

            value.seek(0)

            validacion = validar_imagen_planta(value)

        except Exception as e:

            raise serializers.ValidationError(
                f"Error validando imagen: {str(e)}"
            )

        # 4. COMPROBAR RESULTADO
        if (
            not validacion.get("es_hoja_planta")
            or not validacion.get("es_apta_para_analisis")
        ):

            raise serializers.ValidationError(
                validacion.get(
                    "motivo",
                    "La imagen no contiene hojas de planta válidas."
                )
            )

        # 5. REGRESAR PUNTERO AL INICIO
        value.seek(0)

        return value

    # ========================================================
    # CREAR DIAGNOSTICO Y CHAT
    # ========================================================
    def create(self, validated_data):

        request = self.context.get("request")

        if not request or not request.user.is_authenticated:

            raise serializers.ValidationError(
                "Usuario no autenticado."
            )

        usuario = request.user

        # 1. OBTENER IMAGEN
        imagen = validated_data.get("imagen")

        if not imagen:

            raise serializers.ValidationError({
                "imagen": "La imagen es obligatoria."
            })

        # 2. LEER IMAGEN EN MEMORIA
        imagen.seek(0)

        image_bytes = imagen.read()

        # 3. TRANSACCIÓN
        with transaction.atomic():

            # 4. VALIDACIÓN FINAL DEL CRÉDITO
            if not puede_usar_credito(usuario):

                raise serializers.ValidationError({
                    "error": "No tienes créditos disponibles."
                })

            # 5. CONSUMIR CRÉDITO
            consumir_credito(usuario)

            # 6. CREAR PLANTA
            planta = models.Planta.objects.create(
                **validated_data
            )

            # 7. CREAR DIAGNÓSTICO INICIAL
            diagnostico = models.DiagnosticoIA.objects.create(
                usuario=usuario,
                planta=planta,
                estado_imagen=models.EstadoImagen.PENDIENTE,
                progreso=0,
                enfermedad_detectada="",
                severidad="",
                porcentaje_salud=0,
                confianza_ia=0,
                urgencia="",
                contagio="",
                recuperacion="",
                etapa="",
                sintomas_detectados=[],
                prediccion_evolucion=[],
                plagas_relacionadas=[],
                factores_climaticos_favorables={},
                tratamiento_natural=[],
                tratamiento_quimico=[],
                prevencion=[],
                lesiones_detectadas=[],
            )

            # 8. CREAR CHAT
            chat = models.Chat.objects.create(
                usuario=usuario,
                diagnostico=diagnostico,
                titulo="Analizando cultivo",
            )

            # 9. INICIAR BACKGROUND DESPUÉS DEL COMMIT
            transaction.on_commit(

                lambda: threading.Thread(
                    target=self.procesar_diagnostico_background,

                    args=(
                        diagnostico.id,
                        image_bytes,
                    ),

                    daemon=True,

                ).start()

            )

        # 10. DEVOLVER CHAT
        return chat
    
    # ========================================================
    # PROCESAMIENTO DEL DIAGNÓSTICO
    # ========================================================
    def procesar_diagnostico_background(
        self,
        diagnostico_id,
        image_bytes,
    ):

        diagnostico = None

        try:

            # 1. OBTENER DIAGNÓSTICO
            diagnostico = models.DiagnosticoIA.objects.select_related("planta").get(
                id=diagnostico_id
            )

            # 2. INICIAR PROCESAMIENTO
            diagnostico.estado_imagen = (models.EstadoImagen.PROCESANDO)

            diagnostico.progreso = 10

            diagnostico.save(
                update_fields=[
                    "estado_imagen",
                    "progreso",
                ]
            )

            # 3. PREPARAR IMAGEN

            image_buffer = BytesIO(image_bytes)
            image_buffer.name = "plant.jpg"

            # 4. PROGRESO 20
            diagnostico.progreso = 20

            diagnostico.save(
                update_fields=[
                    "progreso",
                ]
            )

            # 5. ANALIZAR CON OPENAI
            data = analizar_planta_con_openai(
                image_buffer
            )

            # 6. PROGRESO 50
            diagnostico.progreso = 50

            diagnostico.save(
                update_fields=[
                    "progreso",
                ]
            )

            # 7. ACTUALIZAR PLANTA
            planta = diagnostico.planta

            planta.nombre = data.get(
                "nombre_planta",
                planta.nombre,
            )

            planta.descripcion = data.get(
                "descripcion_planta",
                "",
            )

            planta.save(
                update_fields=[
                    "nombre",
                    "descripcion",
                ]
            )

            # 8. CALCULAR RECUPERACIÓN
            semana_max = max(
                [
                    actividad.get(
                        "semana",
                        1
                    )

                    for actividad in data.get(
                        "calendario_tratamiento",
                        []
                    )
                ],

                default=1,
            )

            if semana_max <= 2:
                recuperacion = "1-2 semanas"
            elif semana_max <= 4:
                recuperacion = "1-4 semanas"
            else:
                recuperacion = "2-6 semanas"

            # 9. ACTUALIZAR DIAGNÓSTICO
            diagnostico.enfermedad_detectada = data.get(
                "enfermedad_detectada",
                "Sin detección",
            )

            diagnostico.severidad = data.get(
                "severidad",
                "Leve",
            )

            diagnostico.porcentaje_salud = data.get(
                "porcentaje_salud",
                0,
            )

            diagnostico.confianza_ia = data.get(
                "confianza_ia",
                0,
            )

            diagnostico.urgencia = data.get(
                "urgencia",
                "",
            )

            diagnostico.contagio = data.get(
                "contagio",
                "",
            )

            diagnostico.recuperacion = recuperacion

            diagnostico.etapa = data.get(
                "etapa",
                "",
            )

            diagnostico.sintomas_detectados = data.get(
                "sintomas_detectados",
                [],
            )

            diagnostico.prediccion_evolucion = data.get(
                "prediccion_evolucion",
                [],
            )

            diagnostico.plagas_relacionadas = data.get(
                "plagas_relacionadas",
                [],
            )

            diagnostico.factores_climaticos_favorables = data.get(
                "factores_climaticos_favorables",
                {},
            )

            diagnostico.tratamiento_natural = data.get(
                "tratamiento_natural",
                [],
            )

            diagnostico.tratamiento_quimico = data.get(
                "tratamiento_quimico",
                [],
            )

            diagnostico.prevencion = data.get(
                "prevencion",
                [],
            )

            # 10. PROGRESO 70
            diagnostico.progreso = 70
            diagnostico.save()

            # 11. CREAR ACTIVIDADES
            for actividad in data.get(
                "calendario_tratamiento",
                []
            ):

                models.ActividadTratamiento.objects.create(

                    diagnostico=diagnostico,

                    actividad=actividad.get(
                        "actividad",
                        "",
                    ),

                    tipo=actividad.get(
                        "tipo",
                        "",
                    ),

                    semana=actividad.get(
                        "semana",
                        1,
                    ),

                )

            # 12. PROGRESO 80
            diagnostico.progreso = 80

            diagnostico.save(
                update_fields=[
                    "progreso",
                ]
            )

            # 13. PREPARAR IMAGEN PARA ANÁLISIS VISUAL
            image_buffer.seek(0)

            # 14. GENERAR IMAGEN ANOTADA
            resultado = generar_imagen_anotada(
                image_buffer,
                data,
            )

            # 15. GUARDAR RESULTADO DE IMAGEN
            diagnostico.imagen = resultado["imagen"]

            diagnostico.lesiones_detectadas = resultado.get(
                "lesiones",
                [],
            )

            # 16. PROGRESO 90
            diagnostico.progreso = 90

            diagnostico.save(
                update_fields=[
                    "imagen",
                    "lesiones_detectadas",
                    "progreso",
                ]
            )

            # 17. COMPLETAR DIAGNÓSTICO
            diagnostico.estado_imagen = (
                models.EstadoImagen.COMPLETADO
            )

            diagnostico.progreso = 100

            diagnostico.save(
                update_fields=[
                    "estado_imagen",
                    "progreso",
                ]
            )

            # 18. ACTUALIZAR CHAT
            chat = diagnostico.chat

            chat.titulo = (
                diagnostico.enfermedad_detectada
            )

            chat.save(
                update_fields=[
                    "titulo",
                ]
            )

            print(
                f"Diagnóstico {diagnostico.id} completado."
            )

        except Exception as e:

            # ERROR
            print(
                "ERROR PROCESANDO DIAGNÓSTICO:",
                e,
            )

            if diagnostico:

                diagnostico.estado_imagen = (
                    models.EstadoImagen.ERROR
                )

                diagnostico.save(
                    update_fields=[
                        "estado_imagen",
                    ]
                )