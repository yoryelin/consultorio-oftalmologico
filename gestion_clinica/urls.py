# gestion_clinica/urls.py

from django.urls import path
from . import views

# 1. Refactorización de URLs y Nombres de Apps
app_name = 'gestion_clinica'

urlpatterns = [
    # --- Rutas de Gestión Principal (Raíz de la app: /pacientes/) ---
    path('', views.DashboardView.as_view(), name='dashboard'),

    # --- Rutas de Pacientes (CRUD de Datos Filiatorios) ---
    path('lista/', views.PacienteListView.as_view(), name='lista_pacientes'),
    path('nuevo/', views.PacienteCreateView.as_view(), name='crear_paciente'),
    path('<int:pk>/', views.PacienteDetailView.as_view(),
         name='detalle_paciente'),
    path('<int:pk>/editar/',
         views.PacienteUpdateView.as_view(), name='editar_paciente'),

    # --- Rutas de HC y Examen ---
    path('<int:paciente_pk>/hc/nuevo/',
         views.ExamenOftalmologicoFirstCreateView.as_view(), name='crear_historia_clinica'),
    path('hc/<int:hc_pk>/examen/ver/',
         views.ExamenOftalmologicoDetailView.as_view(), name='detalle_examen_oftalmologico'),

    # ⭐ RUTAS DE CATÁLOGO (CRUD COMPLETO) ⭐

    # VISTAS DE PROFESIONALES
    path('profesionales/', views.ProfesionalListView.as_view(),
         name='lista_profesionales'),
    path('profesional/nuevo/', views.ProfesionalCreateView.as_view(),
         name='crear_profesional'),
    path('profesional/<int:pk>/editar/', views.ProfesionalUpdateView.as_view(),
         name='editar_profesional'),
    path('profesional/<int:pk>/eliminar/', views.ProfesionalDeleteView.as_view(),
         name='eliminar_profesional'),

    # VISTAS DE OBRAS SOCIALES
    path('obras-sociales/', views.ObraSocialListView.as_view(),
         name='lista_obras_sociales'),
    path('obrasocial/nuevo/', views.ObraSocialCreateView.as_view(),
         name='crear_obra_social'),
    path('obrasocial/<int:pk>/editar/', views.ObraSocialUpdateView.as_view(),
         name='editar_obra_social'),
    path('obrasocial/<int:pk>/eliminar/', views.ObraSocialDeleteView.as_view(),
         name='eliminar_obra_social'),

    # ⭐ RUTAS DE TURNOS (CORREGIDAS) ⭐
    path('turnos/', views.TurnoListView.as_view(),
         name='lista_turnos'),  # <--- CORREGIDO
    path('turnos/nuevo/', views.TurnoCreateView.as_view(), name='crear_turno'),
    path('turnos/<int:pk>/detalle/',
         views.TurnoDetailView.as_view(), name='detalle_turno'),
    path('turnos/api/json/', views.TurnosJsonView.as_view(), name='turnos_json_api'),

    # =================================================================
    # ❌ RUTAS ELIMINADAS
    # =================================================================
]
