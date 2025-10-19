# core/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Esta línea asegura que la lista de pacientes esté en la raíz del sitio ('/')
    path('', include(('gestion_clinica.urls', 'pacientes'), namespace='pacientes')),
]
