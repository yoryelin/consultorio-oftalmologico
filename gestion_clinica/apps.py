# gestion_clinica/apps.py

from django.apps import AppConfig


class GestionClinicaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestion_clinica'

    # ----------------- NUEVA FUNCIÓN READY -----------------
    def ready(self):
        """Importa las señales de la aplicación para que Django las detecte."""
        import gestion_clinica.signals  # <-- Se asegura de que signals.py se ejecute.
