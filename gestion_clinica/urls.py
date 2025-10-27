# gestion_clinica/urls.py

from django.urls import path
from . import views  # <--- Importación Simplificada

# 1. Refactorización de URLs y Nombres de Apps
# A. Renombrar el app_name para coincidir con el nombre real de la aplicación (gestion_clinica)
app_name = 'gestion_clinica'

urlpatterns = [
    # --- Rutas de Gestión Principal (Raíz de la app: /pacientes/) ---
    # 3. Limpieza de Imports: Se usa views.DashboardView.as_view()
    path('', views.DashboardView.as_view(), name='dashboard'),

    # --- Rutas de Pacientes (CREATE, READ, UPDATE de DATOS FILIATORIOS - PERMITIDO EDITAR) ---
    path('lista/', views.PacienteListView.as_view(), name='lista_pacientes'),
    path('nuevo/', views.PacienteCreateView.as_view(), name='crear_paciente'),
    path('<int:pk>/', views.PacienteDetailView.as_view(),
         name='detalle_paciente'),
    path('<int:pk>/editar/',
         views.PacienteUpdateView.as_view(), name='editar_paciente'),

    # --- Rutas de HISTORIA CLÍNICA y EXAMEN: SOLO CREATE y READ (INMUTABLES) ---

    # RUTA DE CREACIÓN DE NUEVA CONSULTA (HC y EO inicial)
    path('<int:paciente_pk>/hc/nuevo/',
         views.ExamenOftalmologicoFirstCreateView.as_view(), name='crear_historia_clinica'),

    # ❌ RUTA DE EDICIÓN DE HISTORIA CLÍNICA ELIMINADA (Principio de Inmutabilidad)
    # path('hc/<int:pk>/editar/', views.HistoriaClinicaUpdateView.as_view(), name='editar_historia_clinica'),

    # ⭐ RUTAS LECTURA (READ) PARA EXAMEN OFTALMOLÓGICO ⭐
    path('hc/<int:hc_pk>/examen/ver/',
         views.ExamenOftalmologicoDetailView.as_view(), name='detalle_examen_oftalmologico'),

    # ❌ RUTAS ELIMINADAS (Mantenidas como referencia comentada)
    # path('hc/<int:hc_pk>/examen/editar/', views.ExamenOftalmologicoUpdateView.as_view(), name='editar_examen_oftalmologico'),
    # path('hc/<int:hc_pk>/examen/anular/', views.ExamenOftalmologicoAnularView.as_view(), name='anular_examen_oftalmologico'),
    # ----------------------------------------------------------------------

    # =================================================================
    # ❌ ELIMINADAS: RUTAS PRESCRIPCIÓN DE LENTES (Mantenidas como referencia comentada)
    # =================================================================
    # path(
    #     '<int:paciente_pk>/prescripciones/crear/',
    #     views.PrescripcionLentesCreateView.as_view(),
    #     name='crear_prescripcion_lentes'
    # ),
    # path(
    #     '<int:paciente_pk>/prescripciones/',
    #     views.PrescripcionLentesListView.as_view(),
    #     name='lista_prescripcion_lentes'
    # ),
    # =================================================================

    # --- Rutas de Catálogo y Turnos ---
    path('profesionales/nuevo/', views.ProfesionalCreateView.as_view(),
         name='crear_profesional'),
    path('obrasocial/nuevo/', views.ObraSocialCreateView.as_view(),
         name='crear_obra_social'),

    # ⭐ RUTAS DE TURNOS ⭐
    path('turnos/', views.TurnoListView.as_view(), name='lista_turnos'),
    path('turnos/nuevo/', views.TurnoCreateView.as_view(), name='crear_turno'),

    # RUTA DE DETALLE DE TURNO
    path('turnos/<int:pk>/detalle/',
         views.TurnoDetailView.as_view(), name='detalle_turno'),

    # URL para el API de FullCalendar
    path('turnos/api/json/', views.TurnosJsonView.as_view(), name='turnos_json_api'),
]
