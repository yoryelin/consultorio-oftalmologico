# gestion_clinica/urls.py

from django.urls import path
from .views import (
    DashboardView,  # ⭐ Nuevo: Importar DashboardView
    PacienteListView, PacienteDetailView, PacienteCreateView, PacienteUpdateView,
    HistoriaClinicaCreateView, HistoriaClinicaUpdateView,
    ExamenOftalmologicoUpdateView,
    ProfesionalCreateView, ObraSocialCreateView
)

app_name = 'pacientes'

urlpatterns = [
    # ⭐ 1. DASHBOARD: Se convierte en la página de inicio (/) ⭐
    path('', DashboardView.as_view(), name='dashboard'),

    # --- Rutas de Pacientes ---
    # 2. LISTADO: Ahora con el prefijo 'pacientes/'
    path('pacientes/', PacienteListView.as_view(), name='lista_pacientes'),
    path('pacientes/nuevo/', PacienteCreateView.as_view(), name='crear_paciente'),
    path('pacientes/<int:pk>/', PacienteDetailView.as_view(),
         name='detalle_paciente'),
    path('pacientes/<int:pk>/editar/',
         PacienteUpdateView.as_view(), name='editar_paciente'),

    # --- Rutas de Historia Clínica ---
    path('pacientes/<int:paciente_pk>/hc/nuevo/',
         HistoriaClinicaCreateView.as_view(), name='crear_historia_clinica'),
    path('hc/<int:pk>/editar/', HistoriaClinicaUpdateView.as_view(),
         name='editar_historia_clinica'),

    # --- Rutas de Examen Oftalmológico ---
    # hc_pk se usa para obtener el examen asociado a esa historia clínica
    path('hc/<int:hc_pk>/examen/editar/', ExamenOftalmologicoUpdateView.as_view(),
         name='editar_examen_oftalmologico'),

    # --- Rutas de Catálogo ---
    path('profesionales/nuevo/', ProfesionalCreateView.as_view(),
         name='crear_profesional'),
    path('obrasocial/nuevo/', ObraSocialCreateView.as_view(),
         name='crear_obra_social'),
]
