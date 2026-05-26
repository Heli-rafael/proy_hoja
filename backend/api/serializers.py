from rest_framework import serializers
from datetime import date
from . import models

import threading

from .service.validador_imagen import validar_imagen_planta

from .service.openai_service import (
    analizar_planta_con_openai
)

from .service.generador_imagen import generar_imagen_anotada

from .service.services import (
    puede_usar_credito,
    consumir_credito
)

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Plan
        fields = ['id', 'nombre', 'creditos_diarios', 'descripcion']


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
            'username', 
            'password',
            'first_name', 
            'last_name', 
            'email', 
            'estado', 
            'picture',
            'plan',

            'last_login', 
            'is_superuser', 
            'is_staff', 
            'is_active'
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

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance

    def delete(self, instance):
        instance.delete()
        return instance

class MeSerializer(serializers.ModelSerializer):
    plan = PlanSerializer()
    creditos = serializers.SerializerMethodField()

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

    class Meta:
        model = models.Usuario
        fields = '__all__'

class CreditoDiarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CreditoDiario
        fields = ['id', 'usuario', 'fecha', 'creditos_usados']

# Planta

class PlantaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Planta
        fields = ['id', 'nombre', 'descripcion', 'imagen']
        
class DiagnosticoIASerializer(serializers.ModelSerializer):

    planta = PlantaSerializer(read_only=True)
    
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
            'tratamiento_natural', 
            'tratamiento_quimico', 
            'prevencion', 
            'creado_en'
        ]

class ChatSerializer(serializers.ModelSerializer):

    diagnostico = DiagnosticoIASerializer(read_only=True)
    
    class Meta:
        model = models.Chat
        fields = ['id', 'usuario', 'titulo', 'diagnostico', 'creado_en']

class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Mensaje
        fields = ['id', 'chat', 'tipo', 'texto', 'creado_en']

# ==============================
# CREAR PLANTA Y DIAGNOSTICOS
# ==============================
class PlantaCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Planta
        fields = ['id', 'nombre', 'descripcion', 'imagen']
    
    def create(self, validated_data):

        request = self.context.get("request")

        usuario = request.user

        # VALIDAR CRÉDITOS

        if not puede_usar_credito(usuario):

            raise serializers.ValidationError({
                "error": "No tienes créditos disponibles."
            })

        imagen = validated_data.get("imagen")

        # CREAR PLANTA

        planta = models.Planta.objects.create(
            **validated_data
        )

        # CONSUMIR CRÉDITO

        consumir_credito(usuario)

        # ANALIZAR IA

        imagen.seek(0)

        data = analizar_planta_con_openai(imagen)

        # ACTUALIZAR PLANTA

        planta.nombre = data.get(
            "nombre_planta",
            planta.nombre
        )

        planta.descripcion = data.get(
            "descripcion_planta",
            ""
        )

        planta.save()

        # CREAR DIAGNÓSTICO

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

            tratamiento_natural=data.get(
                "tratamiento_natural",
                ""
            ),

            tratamiento_quimico=data.get(
                "tratamiento_quimico",
                ""
            ),

            prevencion=data.get(
                "prevencion",
                ""
            )
        )

        # CREAR CHAT

        chat = models.Chat.objects.create(

            usuario=usuario,
            diagnostico=diagnostico,
            titulo=f"Análisis: {diagnostico.enfermedad_detectada}"
        )

        # GENERAR IMAGEN EN BACKGROUND

        imagen.seek(0)

        image_bytes = imagen.read()

        threading.Thread(
            target=self.procesar_imagen_background,
            args=(
                diagnostico.id,
                image_bytes,
                data
            ),
            daemon=True
        ).start()

        return chat
    
    # VALIDAR LA IMAGEM
    def validate_imagen(self, value):

        # VALIDAR TAMAÑO
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError(
                "La imagen supera el límite permitido de 10MB."
            )

        # VALIDAR IA
        try:

            value.seek(0)

            validacion = validar_imagen_planta(value)

        except Exception as e:
            raise serializers.ValidationError(
                f"Error validando imagen: {str(e)}"
            )

        if (
            not validacion.get("es_planta_papa")
            or not validacion.get("es_apta_para_analisis")
        ):

            raise serializers.ValidationError(
                validacion.get(
                    "motivo",
                    "La imagen no contiene hojas de papa válidas."
                )
            )

        return value
    
    # PROCESAR LA IMAGEN
    def procesar_imagen_background(self, diagnostico_id, image_bytes, data):

        try:

            diagnostico = models.DiagnosticoIA.objects.get(
                id=diagnostico_id
            )

            diagnostico.estado_imagen = (
                models.EstadoImagen.PROCESANDO
            )

            diagnostico.save()

            from io import BytesIO

            image_buffer = BytesIO(image_bytes)

            image_buffer.name = "plant.jpg"

            imagen_anotada = generar_imagen_anotada(
                image_buffer,
                data
            )

            diagnostico.imagen = imagen_anotada

            diagnostico.estado_imagen = (
                models.EstadoImagen.COMPLETADO
            )

            diagnostico.save()

        except Exception as e:

            try:

                diagnostico.estado_imagen = (
                    models.EstadoImagen.ERROR
                )

                diagnostico.save()

            except:
                pass

            print(e)