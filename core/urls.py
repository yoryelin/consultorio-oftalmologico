# core/urls.py

from django.contrib import admin
from django.urls import path, include
from gestion_clinica.views import DashboardView

urlpatterns = [
    path('admin/', admin.site.urls),

    # CORRECCIÓN CLAVE: Usamos la inclusión estándar (SIN namespace ni app_name)
    # Django encontrará el nombre 'logout' aquí.
    path('accounts/', include('django.contrib.auth.urls')),

    # URL de la aplicación principal (Dashboard)
    path('', DashboardView.as_view(), name='dashboard'),

    # URLs de la aplicación 'gestion_clinica' (Pacientes, Turnos, etc.)
    path('', include('gestion_clinica.urls')),
]
