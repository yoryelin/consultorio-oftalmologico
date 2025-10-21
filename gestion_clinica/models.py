from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string
from datetime import date
# ⭐ IMPORTACIÓN AÑADIDA para el campo fecha_hora en Turno ⭐
from django.utils import timezone

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
        max_length=6,
        unique=True,
        blank=True,
        null=True,
        editable=False,
        verbose_name='Número de Registro'
    )

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField()
    GENERO_CHOICES = [('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')]
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    telefono = models.CharField(max_length=50)
    domicilio = models.CharField(max_length=255, verbose_name='Domicilio')

    # Relación de Catálogo
    obra_social = models.ForeignKey(
        ObraSocial, on_delete=models.SET_NULL, null=True, blank=True)
    num_afiliado = models.CharField(max_length=50, blank=True, null=True)
    antecedentes_sistemicos = models.TextField(
        blank=True, verbose_name="Antecedentes Sistémicos")

    # MÉTODO DE CÁLCULO DE EDAD
    @property
    def edad(self):
        """Calcula la edad actual del paciente a partir de la fecha de nacimiento."""
        if self.fecha_nacimiento:
            hoy = date.today()
            edad_calculada = hoy.year - self.fecha_nacimiento.year
            if (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
                edad_calculada -= 1
            return edad_calculada
        return None

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
    # ⭐ Campo renombrado de 'fecha_consulta' a 'fecha' ⭐
    fecha = models.DateTimeField(
        auto_now_add=True, verbose_name='Fecha de Consulta')
    motivo_consulta = models.TextField()
    # ⭐ Campo renombrado de 'diagnostico_principal' a 'diagnostico' ⭐
    diagnostico = models.TextField(verbose_name='Diagnóstico Principal')
    tratamiento = models.TextField()
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f'HC de {self.paciente} - {self.fecha.strftime("%Y-%m-%d")}'

    def get_absolute_url(self):
        return reverse('pacientes:detalle_paciente', kwargs={'pk': self.paciente.pk})

    class Meta:
        verbose_name = "Historia Clínica"
        verbose_name_plural = "Historias Clínicas"
        ordering = ['-fecha']


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
    # ⭐ Nombres de campo simplificados ⭐
    pio_od = models.CharField(
        max_length=20, blank=True, verbose_name="PIO OD")
    pio_oi = models.CharField(
        max_length=20, blank=True, verbose_name="PIO OI")
    observaciones = models.TextField(
        blank=True, verbose_name='Observaciones del Examen')

    def __str__(self):
        return f'Examen para HC: {self.historia_clinica}'

    def get_absolute_url(self):
        return reverse('pacientes:detalle_paciente', kwargs={'pk': self.historia_clinica.paciente.pk})

    class Meta:
        verbose_name = "Examen Oftalmológico"
        verbose_name_plural = "Exámenes Oftalmológicos"

# --- Modelo Turno (Objetivo 2.1) ---


class Turno(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='turnos'
    )
    profesional = models.ForeignKey(
        Profesional,
        on_delete=models.PROTECT,
        related_name='turnos_asignados'
    )
    # Fecha y hora del turno
    fecha_hora = models.DateTimeField(default=timezone.now)

    # Estado del turno
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADO', 'Confirmado'),
        ('ATENDIDO', 'Atendido'),
        ('CANCELADO', 'Cancelado'),
    ]
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='PENDIENTE'
    )

    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones del Turno'
    )

    class Meta:
        verbose_name = "Turno"
        verbose_name_plural = "Turnos"
        ordering = ['fecha_hora']

    def __str__(self):
        return f"Turno {self.estado} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')} - {self.paciente.apellido}"
