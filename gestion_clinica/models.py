from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string
from datetime import date  # Importado para el cálculo de edad

# --- Catálogos ---


class Profesional(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    matricula = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f'{self.apellido}, {self.nombre} ({self.matricula})'

    class Meta:
        verbose_name_plural = "Profesionales"
        ordering = ['apellido', 'nombre']


class ObraSocial(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    siglas = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Obra Social"
        verbose_name_plural = "Obras Sociales"
        ordering = ['nombre']

# --- Modelos Operativos ---


class Paciente(models.Model):

    num_registro = models.CharField(
        max_length=6,  # Se ajusta a 6 dígitos
        unique=True,
        blank=True,
        null=True,
        editable=False,
        verbose_name='Número de Registro'
    )

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField()  # Campo clave para calcular la edad
    GENERO_CHOICES = [('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')]
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    telefono = models.CharField(max_length=50)
    direccion = models.CharField(max_length=255)

    # Relación de Catálogo
    obra_social = models.ForeignKey(
        ObraSocial, on_delete=models.SET_NULL, null=True, blank=True)
    num_afiliado = models.CharField(max_length=50, blank=True, null=True)
    antecedentes_sistemicos = models.TextField(
        blank=True, verbose_name="Antecedentes Sistémicos")

    # -----------------------------------------------------------
    # ⭐ NUEVO MÉTODO DE CÁLCULO DE EDAD ⭐
    # -----------------------------------------------------------
    @property
    def edad(self):
        """Calcula la edad actual del paciente a partir de la fecha de nacimiento."""
        if self.fecha_nacimiento:
            hoy = date.today()
            edad_calculada = hoy.year - self.fecha_nacimiento.year
            # Ajuste: Si aún no ha llegado su cumpleaños este año, resta 1
            if (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
                edad_calculada -= 1
            return edad_calculada
        return None
    # -----------------------------------------------------------

    # EL MÉTODO save() HA SIDO ELIMINADO Y MOVADO A signals.py

    def __str__(self):
        return f'{self.num_registro} - {self.apellido}, {self.nombre}'

    def get_absolute_url(self):
        return reverse('pacientes:detalle_paciente', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['apellido', 'nombre']


class HistoriaClinica(models.Model):
    paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, related_name='historias_clinicas')
    profesional = models.ForeignKey(Profesional, on_delete=models.PROTECT)
    fecha_consulta = models.DateTimeField(auto_now_add=True)
    motivo_consulta = models.TextField()
    diagnostico_principal = models.TextField()
    tratamiento = models.TextField()
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f'HC de {self.paciente} - {self.fecha_consulta.strftime("%Y-%m-%d")}'

    def get_absolute_url(self):
        return reverse('pacientes:detalle_paciente', kwargs={'pk': self.paciente.pk})

    class Meta:
        verbose_name = "Historia Clínica"
        verbose_name_plural = "Historias Clínicas"
        ordering = ['-fecha_consulta']


class ExamenOftalmologico(models.Model):
    # Relación One-to-One
    historia_clinica = models.OneToOneField(
        HistoriaClinica, on_delete=models.CASCADE, related_name='examen')

    # Campos para el examen (simplificados)
    agudeza_visual_od = models.CharField(
        max_length=50, blank=True, verbose_name="AV OD")
    agudeza_visual_oi = models.CharField(
        max_length=50, blank=True, verbose_name="AV OI")
    biomicroscopia = models.TextField(blank=True)
    fondo_ojo = models.TextField(blank=True, verbose_name="Fondo de Ojo")
    presion_intraocular_od = models.CharField(
        max_length=20, blank=True, verbose_name="PIO OD")
    presion_intraocular_oi = models.CharField(
        max_length=20, blank=True, verbose_name="PIO OI")

    def __str__(self):
        return f'Examen para HC: {self.historia_clinica}'

    def get_absolute_url(self):
        return reverse('pacientes:detalle_paciente', kwargs={'pk': self.historia_clinica.paciente.pk})

    class Meta:
        verbose_name = "Examen Oftalmológico"
        verbose_name_plural = "Exámenes Oftalmológicos"
