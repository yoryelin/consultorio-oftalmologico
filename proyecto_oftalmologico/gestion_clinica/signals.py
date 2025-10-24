# gestion_clinica/signals.py

from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Paciente
# Importamos F para un acceso más robusto a los campos de BD
from django.db.models import F


@receiver(pre_save, sender=Paciente)
def set_num_registro_paciente(sender, instance, **kwargs):
    """
    Asigna un número de registro secuencial (000001, 000002, ...)
    solo si el paciente es nuevo (no tiene PK) y no tiene un num_registro asignado.
    """
    if not instance.pk and not instance.num_registro:
        # Lógica para determinar el siguiente ID secuencial sin riesgo de error de recarga:
        try:
            # En entorno de desarrollo, el acceso a .pk puede fallar.
            # Se usa .id del último registro.
            last_paciente = Paciente.objects.all().order_by('id').last()

            if last_paciente:
                # El nuevo ID se basa en el último ID de la base de datos + 1
                new_id = last_paciente.pk + 1
            else:
                new_id = 1
        except Exception:
            # En caso de error (BD bloqueada/no disponible), usamos el ID 1 como fallback.
            new_id = 1

        # Formatear a 6 dígitos con ceros a la izquierda
        instance.num_registro = str(new_id).zfill(6)
