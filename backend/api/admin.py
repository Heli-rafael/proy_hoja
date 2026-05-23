from django.contrib import admin
import api.models as models
# Register your models here.
admin.site.register(models.Usuario)
admin.site.register(models.CreditoDiario)
admin.site.register(models.Plan)
admin.site.register(models.DiagnosticoIA)