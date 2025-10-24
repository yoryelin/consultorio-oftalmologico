# core/urls.py

from django.contrib import admin
from django.urls import path, include
from gestion_clinica.views import DashboardView

urlpatterns = [
    path('admin/', admin.site.urls),

    # URLs de autenticación
    path('accounts/', include('django.contrib.auth.urls')),

    # 1. Dashboard (la única URL de gestion_clinica que NO usa el prefijo 'pacientes/')
    path('', DashboardView.as_view(), name='dashboard'),

    # 2. URLs de la aplicación 'gestion_clinica' (Pacientes, Turnos, etc.)
    # ⭐ CORRECCIÓN CLAVE: Prefijamos TODAS las rutas de la app con 'pacientes/'
    # Esto soluciona la inconsistencia en el log de Django.
    path('pacientes/', include('gestion_clinica.urls')),
]
