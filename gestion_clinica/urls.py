# gestion_clinica/urls.py

from django.urls import path
from .views import (
    DashboardView,
    PacienteListView, PacienteDetailView, PacienteCreateView, PacienteUpdateView,
    HistoriaClinicaCreateView, HistoriaClinicaUpdateView,
    ExamenOftalmologicoUpdateView,
    ProfesionalCreateView, ObraSocialCreateView,
    TurnoListView, TurnoCreateView,  # ⭐ Nuevo: Importar vistas de Turnos ⭐
)

app_name = 'pacientes'

urlpatterns = [
    # --- Rutas de Gestión Principal ---
    path('', DashboardView.as_view(), name='dashboard'),

    # --- Rutas de Pacientes ---
    path('pacientes/', PacienteListView.as_view(), name='lista_pacientes'),
    path('pacientes/nuevo/', PacienteCreateView.as_view(), name='crear_paciente'),
    path('pacientes/<int:pk>/', PacienteDetailView.as_view(),
         name='detalle_paciente'),
    path('pacientes/<int:pk>/editar/',
         PacienteUpdateView.as_view(), name='editar_paciente'),

    # --- Rutas de Historia Clínica y Examen ---
    path('pacientes/<int:paciente_pk>/hc/nuevo/',
         HistoriaClinicaCreateView.as_view(), name='crear_historia_clinica'),
    path('hc/<int:pk>/editar/', HistoriaClinicaUpdateView.as_view(),
         name='editar_historia_clinica'),
    path('hc/<int:hc_pk>/examen/editar/', ExamenOftalmologicoUpdateView.as_view(),
         name='editar_examen_oftalmologico'),

    # --- Rutas de Catálogo (Uso interno) ---
    path('profesionales/nuevo/', ProfesionalCreateView.as_view(),
         name='crear_profesional'),
    path('obrasocial/nuevo/', ObraSocialCreateView.as_view(),
         name='crear_obra_social'),

    # ⭐ RUTAS DE TURNOS (Objetivo 2.2) ⭐
    path('turnos/', TurnoListView.as_view(), name='lista_turnos'),
    path('turnos/nuevo/', TurnoCreateView.as_view(), name='crear_turno'),
    # Nota: Las vistas de Detalle y Edición del Turno las haremos más adelante.
]
