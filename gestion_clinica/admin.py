from django.contrib import admin
from .models import (
    Profesional,
    ObraSocial,
    Paciente,
    HistoriaClinica,
    ExamenOftalmologico,
    Turno  # ⭐ Nuevo: Importar el modelo Turno ⭐
)

# -------------------------------------------------------------
# 1. Administración de Modelos de Catálogo
# -------------------------------------------------------------


@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = ['apellido', 'nombre', 'matricula']
    search_fields = ['apellido', 'nombre', 'matricula']


@admin.register(ObraSocial)
class ObraSocialAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'siglas']
    search_fields = ['nombre', 'siglas']

# -------------------------------------------------------------
# 2. Administración de Modelos Operativos
# -------------------------------------------------------------

# Se utiliza en PacienteAdmin


class ExamenInline(admin.StackedInline):
    model = ExamenOftalmologico
    extra = 0
    max_num = 1  # Solo puede haber un examen por HC


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = [
        'num_registro',
        'apellido',
        'nombre',
        'dni',
        'fecha_nacimiento',
        'obra_social'
    ]
    search_fields = ['num_registro', 'apellido', 'nombre', 'dni']
    list_filter = ['genero', 'obra_social']
    readonly_fields = ['num_registro']  # Se genera vía signal


class ExamenOftalmologicoInline(admin.StackedInline):
    model = ExamenOftalmologico
    extra = 0


@admin.register(HistoriaClinica)
class HistoriaClinicaAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'fecha',  # ⭐ CORREGIDO: Usar 'fecha' en lugar de 'fecha_consulta'
        'paciente',
        'diagnostico',  # ⭐ CORREGIDO: Usar 'diagnostico' en lugar de 'diagnostico_principal'
        'profesional',
    ]
    list_filter = [
        'profesional',
        'fecha',  # ⭐ CORREGIDO: Usar 'fecha' en lugar de 'fecha_consulta'
    ]
    search_fields = ['paciente__apellido', 'diagnostico']
    date_hierarchy = 'fecha'  # ⭐ CORREGIDO: Usar 'fecha'
    autocomplete_fields = ['paciente', 'profesional']
    inlines = [ExamenOftalmologicoInline]
    fieldsets = (
        (None, {
            'fields': ('paciente', 'profesional')
        }),
        ('Detalles de la Consulta', {
            'fields': ('motivo_consulta', 'diagnostico', 'tratamiento', 'observaciones')
        }),
    )


@admin.register(ExamenOftalmologico)
class ExamenOftalmologicoAdmin(admin.ModelAdmin):
    list_display = ['historia_clinica', 'pio_od',
                    'pio_oi', 'agudeza_visual_od', 'agudeza_visual_oi']
    search_fields = ['historia_clinica__paciente__apellido']

# -------------------------------------------------------------
# 3. Administración del Nuevo Modelo Turno (Objetivo 2.1)
# -------------------------------------------------------------


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ['fecha_hora', 'paciente', 'profesional', 'estado']
    list_filter = ['estado', 'profesional']
    search_fields = ['paciente__apellido', 'profesional__apellido']
    date_hierarchy = 'fecha_hora'
    autocomplete_fields = ['paciente', 'profesional']
    fieldsets = (
        (None, {
            'fields': ('paciente', 'profesional', 'fecha_hora', 'estado')
        }),
        ('Notas', {
            'fields': ('observaciones',),
            'classes': ('collapse',),  # Oculta las observaciones por defecto
        })
    )
