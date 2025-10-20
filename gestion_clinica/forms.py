from django import forms
from .models import (
    Paciente, HistoriaClinica, Profesional, ObraSocial, ExamenOftalmologico
)
# ⭐ IMPORTACIÓN DEL MIXIN ⭐
from .mixins import BaseFormMixin


# Las clases de formulario ahora heredan primero de BaseFormMixin
# Esto aplica automáticamente 'form-control' a todos los campos.

class PacienteForm(BaseFormMixin, forms.ModelForm):
    class Meta:
        model = Paciente
        fields = '__all__'
        widgets = {
            # El datepicker debe mantener su tipo para funcionar, el Mixin añade el estilo.
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }


class HistoriaClinicaForm(BaseFormMixin, forms.ModelForm):
    class Meta:
        model = HistoriaClinica
        fields = '__all__'
        exclude = ('paciente', 'examen',)
        widgets = {
            # Los textareas reciben form-control del Mixin, solo definimos las filas.
            'motivo_consulta': forms.Textarea(attrs={'rows': 3}),
            'diagnostico': forms.Textarea(attrs={'rows': 3}),
            'tratamiento': forms.Textarea(attrs={'rows': 3}),
        }


class ExamenOftalmologicoForm(BaseFormMixin, forms.ModelForm):
    class Meta:
        model = ExamenOftalmologico
        fields = '__all__'
        exclude = ('historia_clinica',)
        widgets = {
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
