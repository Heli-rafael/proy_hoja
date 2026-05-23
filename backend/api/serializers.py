from rest_framework import serializers
from datetime import date
from . import models

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
            'tratamiento', 
            'como_prevenir', 
            'creado_en'
        ]

class ChatSerializer(serializers.ModelSerializer):

    diagnostico = DiagnosticoIASerializer(read_only=True)
    
    class Meta:
        model = models.Chat
        fields = ['id', 'usuario', 'titulo', 'diagnostico', 'creado_en']

    def delete(self, *args, **kwargs):
        # 1. borrar diagnóstico
        if self.diagnostico:
            # 2. borrar planta del diagnóstico
            if self.diagnostico.planta:
                self.diagnostico.planta.delete()

            self.diagnostico.delete()

        # 3. borrar chat
        super().delete(*args, **kwargs)

class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Mensaje
        fields = ['id', 'chat', 'tipo', 'texto', 'creado_en']
    