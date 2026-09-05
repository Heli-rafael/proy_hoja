from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path,include

router = DefaultRouter()

router.register('usuario', views.UsuarioViewSet, basename='usuario')
router.register('plan', views.PlanViewSet, basename='plan')
router.register('plan-precio', views.PlanPrecioViewSet, basename='plan-precio')
router.register('credito-diario', views.CreditoDiarioViewSet, basename='credito-diario')
router.register('planta', views.PlantaViewSet, basename='planta')
router.register('diagnostico', views.DiagnosticoIAViewSet, basename='diagnostico')
router.register('chat', views.ChatViewSet, basename='chat')
router.register('mensaje', views.MensajeViewSet, basename='mensaje')
router.register("actividad-tratamiento", views.ActividadTratamientoViewSet, basename='actividad-tratamiento')
router.register('solicitud-plan', views.SolicitudCambioPlanViewSet, basename='solicitud-plan')

urlpatterns = [
    path('', include(router.urls)),

    # OTP
    path('otp/request', views.RequestOTPView.as_view(), name='otp_respuesta'),
    path('otp/verify', views.VerifyOTPView.as_view(), name='otp_verificar'),

    # REGISTRO
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # SESION
    path('login/', views.login_view, name='login'),
    path('google-login/', views.google_login),
    path('logout/', views.logout_view, name='logout'),
    path('me/', views.me, name='me'),
    path('me/password/', views.ChangePasswordView.as_view()),
    path('mensajes/enviar/', views.enviar_mensaje, name='enviar_mensaje'),
    path('mensajes/chats/<int:chat_id>/mensajes/',views.obtener_mensajes, name='obtener_mensajes'),

    # PROGRESO DIAGNÓSTICO
    path("diagnostico/<int:diagnostico_id>/progreso/",views.DiagnosticoProgresoView.as_view(),name="diagnostico-progreso"),

    # FIJAR CHAT
    path('chat/<int:id>/fijar/', views.toggle_pinned),

    # EXPORTAR FORMATOS
    path('chat/export/excel/', views.export_chats_excel),

    path('diagnostico/export/excel/', views.export_diagnosticos_excel),
    path('diagnostico/export/pdf/', views.export_diagnosticos_pdf),
    path('diagnostico/export/pdfindividual/<int:id>/', views.export_diagnostico_pdf),

]