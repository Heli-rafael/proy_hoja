from rest_framework import serializers
from . import models

class UsuarioSerializer(serializers.ModelSerializer):

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
    
class PlantaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Planta
        fields = ['id', 'nombre', 'descripcion', 'imagen']

class DiagnosticoIASerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DiagnosticoIA
        fields = [
            'id',
            'usuario', 
            'planta', 
            'imagen', 
            'enfermedad_detectada', 
            'severidad', 
            'porcentaje_salud', 
            'confianza_ia', 
            'tratamiento', 
            'como_prevenir', 
            'creado_en'
        ]

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Chat
        fields = ['id', 'usuario', 'titulo', 'diagnostico', 'creado_en']

class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Mensaje
        fields = ['id', 'chat', 'tipo', 'contenido', 'creado_en']
    