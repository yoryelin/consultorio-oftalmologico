
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
    # Específicamente, agregamos el tuple ('gestion_clinica.urls', 'gestion_clinica')
    # y el argumento 'namespace' para que reverse_lazy('gestion_clinica:...') funcione.
    path('pacientes/', include(('gestion_clinica.urls',
         'gestion_clinica'), namespace='gestion_clinica')),
]
