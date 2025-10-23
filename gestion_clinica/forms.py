from django import forms
from .models import (
    # <--- Agregado Turno
    Paciente, HistoriaClinica, Profesional, ObraSocial, ExamenOftalmologico, Turno
)
# ⭐ IMPORTACIÓN DEL MIXIN ⭐
from .mixins import BaseFormMixin

# ⭐ IMPORTACIONES PARA CRISPY FORMS (TurnoForm) ⭐
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit

# --------------------------------------------------------------------------
# Lógica para la escala de Agudeza Visual (AV) en incrementos de 0.25
# --------------------------------------------------------------------------
# Generamos los valores de 0.25 (25) hasta 20.00 (2000)
# Usamos i / 100 para convertir el entero a flotante para las etiquetas
AV_CHOICES = [
    ('', '---------')] + [
    (str(i / 100), str(i / 100))
    for i in range(25, 2025, 25)
]

# --------------------------------------------------------------------------
# Las clases de formulario ahora heredan primero de BaseFormMixin
# Esto aplica automáticamente 'form-control' a todos los campos.
# --------------------------------------------------------------------------


class PacienteForm(BaseFormMixin, forms.ModelForm):
    class Meta:
        model = Paciente
        fields = '__all__'
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }


class HistoriaClinicaForm(BaseFormMixin, forms.ModelForm):
    class Meta:
        model = HistoriaClinica
        fields = '__all__'
        exclude = ('paciente', 'examen',)
        widgets = {
            'motivo_consulta': forms.Textarea(attrs={'rows': 3}),
            'diagnostico': forms.Textarea(attrs={'rows': 3}),
            'tratamiento': forms.Textarea(attrs={'rows': 3}),
        }


class ExamenOftalmologicoForm(BaseFormMixin, forms.ModelForm):
    # ⭐ CAMPOS PERSONALIZADOS CON LA ESCALA INCREMENTAL DE 0.25 ⭐
    agudeza_visual_od = forms.ChoiceField(
        choices=AV_CHOICES,
        required=False,
        label="Agudeza Visual OD (Lejos)",
    )
    agudeza_visual_oi = forms.ChoiceField(
        choices=AV_CHOICES,
        required=False,
        label="Agudeza Visual OI (Lejos)"
    )

    class Meta:
        model = ExamenOftalmologico
        fields = '__all__'
        exclude = ('historia_clinica',)
        widgets = {
            # ⭐ CORRECCIÓN CLAVE: Usamos los nombres de campo EXACTOS del modelo (pio_od, pio_oi) ⭐
            'pio_od': forms.TextInput(attrs={'placeholder': 'Ej: 14'}),
            'pio_oi': forms.TextInput(attrs={'placeholder': 'Ej: 14'}),
            'biomicroscopia': forms.Textarea(attrs={'rows': 3}),
            'fondo_ojo': forms.Textarea(attrs={'rows': 3}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }


class ProfesionalForm(BaseFormMixin, forms.ModelForm):
    class Meta:
        model = Profesional
        fields = '__all__'
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }


class ObraSocialForm(BaseFormMixin, forms.ModelForm):
    class Meta:
        model = ObraSocial
        fields = '__all__'

# --------------------------------------------------------------------------
# ⭐ FORMULARIO PARA TURNOS (ETAPA 2) ⭐
# --------------------------------------------------------------------------


class TurnoForm(BaseFormMixin, forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['paciente', 'profesional',
                  'fecha_hora', 'estado', 'observaciones']
        # Definimos widgets para mejorar la UX (especialmente para fecha_hora)
        widgets = {
            # Usamos 'datetime-local' para un selector de fecha y hora moderno
            'fecha_hora': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Usamos FormHelper para configurar el botón de submit (ya que no lo hace el Mixin)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Detalles del Turno',
                'paciente',
                'profesional',
                'fecha_hora',
                'estado',
                'observaciones',
            ),
            Submit('submit', 'Guardar Turno', css_class='btn-success')
        )
