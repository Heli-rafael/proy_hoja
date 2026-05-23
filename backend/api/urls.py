from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path,include

router = DefaultRouter()

router.register('usuario', views.UsuarioViewSet)
router.register('plan', views.PlanViewSet)
router.register('credito-diario', views.CreditoDiarioViewSet)
router.register('planta', views.PlantaViewSet)
router.register('diagnostico', views.DiagnosticoIAViewSet)
router.register('chat', views.ChatViewSet)
router.register('mensaje', views.MensajeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.login_view, name='login'),
    path('google-login/', views.google_login),
    path('logout/', views.logout_view, name='logout'),
    path('me/', views.me, name='me'),
    path('mensajes/enviar/', views.enviar_mensaje, name='enviar_mensaje'),
    path('mensajes/chats/<int:chat_id>/mensajes/',views.obtener_mensajes, name='obtener_mensajes'),
]