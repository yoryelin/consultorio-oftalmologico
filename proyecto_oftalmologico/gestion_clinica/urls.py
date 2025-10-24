from django.urls import path
from .views import (
    DashboardView,
    PacienteListView, PacienteDetailView, PacienteCreateView, PacienteUpdateView,
    HistoriaClinicaCreateView, HistoriaClinicaUpdateView,
    ExamenOftalmologicoFirstCreateView,
    ExamenOftalmologicoUpdateView,
    ProfesionalCreateView, ObraSocialCreateView,
    TurnoListView, TurnoCreateView,
    TurnosJsonView,
    TurnoDetailView,  # <--- NUEVA VISTA IMPORTADA
)

app_name = 'pacientes'

urlpatterns = [
    # --- Rutas de Gestión Principal (Raíz de la app: /pacientes/) ---
    path('', DashboardView.as_view(), name='dashboard'),

    # --- Rutas de Pacientes (Quitamos el prefijo 'pacientes/') ---
    path('lista/', PacienteListView.as_view(), name='lista_pacientes'),
    path('nuevo/', PacienteCreateView.as_view(), name='crear_paciente'),
    path('<int:pk>/', PacienteDetailView.as_view(),
         name='detalle_paciente'),
    path('<int:pk>/editar/',
         PacienteUpdateView.as_view(), name='editar_paciente'),

    # --- Rutas de Historia Clínica y Examen (Quitamos el prefijo 'pacientes/') ---
    path('<int:paciente_pk>/hc/nuevo/',
         ExamenOftalmologicoFirstCreateView.as_view(), name='crear_historia_clinica'),

    path('hc/<int:pk>/editar/', HistoriaClinicaUpdateView.as_view(),
         name='editar_historia_clinica'),
    path('hc/<int:hc_pk>/examen/editar/', ExamenOftalmologicoUpdateView.as_view(),
         name='editar_examen_oftalmologico'),

    # --- Rutas de Catálogo ---
    path('profesionales/nuevo/', ProfesionalCreateView.as_view(),
         name='crear_profesional'),
    path('obrasocial/nuevo/', ObraSocialCreateView.as_view(),
         name='crear_obra_social'),

    # ⭐ RUTAS DE TURNOS ⭐
    path('turnos/', TurnoListView.as_view(), name='lista_turnos'),
    path('turnos/nuevo/', TurnoCreateView.as_view(), name='crear_turno'),

    # ⭐ AÑADIDA: RUTA DE DETALLE DE TURNO (SOLUCIÓN AL ERROR 500) ⭐
    path('turnos/<int:pk>/detalle/',
         TurnoDetailView.as_view(), name='detalle_turno'),

    # ⭐ URL para el API de FullCalendar ⭐
    path('turnos/api/json/', TurnosJsonView.as_view(), name='turnos_json_api'),
]
