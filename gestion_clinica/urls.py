# gestion_clinica/urls.py
from django.urls import path
from . import views

# app_name se usa en el namespace definido en core/urls.py ('pacientes')
app_name = 'pacientes'

urlpatterns = [
    # Rutas de Catálogo (para uso rápido)
    path('profesional/nuevo/', views.ProfesionalCreateView.as_view(),
         name='crear_profesional'),
    path('obrasocial/nuevo/', views.ObraSocialCreateView.as_view(),
         name='crear_obrasocial'),

    # Rutas de Pacientes
    path('', views.PacienteListView.as_view(), name='lista_pacientes'),
    path('nuevo/', views.PacienteCreateView.as_view(), name='crear_paciente'),
    path('<int:pk>/detalle/', views.PacienteDetailView.as_view(),
         name='detalle_paciente'),
    path('<int:pk>/editar/', views.PacienteUpdateView.as_view(),
         name='editar_paciente'),

    # Rutas de Historia Clínica
    path('<int:paciente_pk>/hc/nueva/',
         views.HistoriaClinicaCreateView.as_view(), name='crear_hc'),
    path('hc/<int:pk>/editar/',
         views.HistoriaClinicaUpdateView.as_view(), name='editar_hc'),

    # Rutas de Examen Oftalmológico

    # ⭐ 1. RUTA DE CREACIÓN AÑADIDA: Usa la PK de la Historia Clínica (hc_pk) ⭐
    path('hc/<int:hc_pk>/examen/nuevo/', views.ExamenOftalmologicoUpdateView.as_view(),
         name='examen_oftalmologico_crear'),

    # 2. RUTA DE EDICIÓN: Usa la PK del Examen (pk)
    path('examen/<int:pk>/editar/',
         views.ExamenOftalmologicoUpdateView.as_view(), name='examen_oftalmologico_editar'),
]
