# gestion_clinica/admin.py
from django.contrib import admin
from .models import Profesional, ObraSocial, Paciente, HistoriaClinica, ExamenOftalmologico

# Catálogos (Simples)
admin.site.register(Profesional)
admin.site.register(ObraSocial)

# Modelos Operativos


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('num_registro', 'apellido', 'nombre',
                    'dni', 'obra_social', 'fecha_nacimiento')
    search_fields = ('dni', 'num_registro', 'apellido', 'nombre')
    list_filter = ('obra_social', 'genero')
    readonly_fields = ('num_registro',)

# Inline para editar Examen al mismo tiempo que la Historia Clínica


class ExamenOftalmologicoInline(admin.StackedInline):
    model = ExamenOftalmologico
    can_delete = False
    verbose_name_plural = 'Examen Oftalmológico'


@admin.register(HistoriaClinica)
class HistoriaClinicaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'fecha_consulta',
                    'profesional', 'diagnostico_principal')
    list_filter = ('profesional', 'fecha_consulta')
    search_fields = ('paciente__apellido', 'diagnostico_principal')
    inlines = [ExamenOftalmologicoInline]
