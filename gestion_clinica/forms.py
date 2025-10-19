# gestion_clinica/forms.py
from django import forms
from .models import Paciente, HistoriaClinica, Profesional, ObraSocial, ExamenOftalmologico

# Mixin para aplicar la clase CSS 'form-control' a todos los campos


class BaseFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})

# --- Formularios de Catálogo ---


class ProfesionalForm(BaseFormMixin, forms.ModelForm):
    class Meta:
        model = Profesional
        fields = '__all__'


class ObraSocialForm(BaseFormMixin, forms.ModelForm):
    class Meta:
        model = ObraSocial
        fields = '__all__'

# --- Formularios Operacionales ---


class PacienteForm(BaseFormMixin, forms.ModelForm):
    # Sobrescribimos el widget de fecha para usar un selector de fecha HTML5 (date)
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model = Paciente
        # Excluimos num_registro porque se genera automáticamente
        exclude = ('num_registro',)
        labels = {
            'dni': 'DNI / Identificación',
            'obra_social': 'Obra Social',
            'num_afiliado': 'N° Afiliado',
            'antecedentes_sistemicos': 'Antecedentes Sistémicos',
        }


class HistoriaClinicaForm(BaseFormMixin, forms.ModelForm):
    class Meta:
        model = HistoriaClinica
        # Excluimos paciente porque se añadirá automáticamente desde la vista de detalle
        exclude = ('paciente',)
        widgets = {
            # Usar un campo de texto amplio para las descripciones largas
            'motivo_consulta': forms.Textarea(attrs={'rows': 3}),
            'diagnostico_principal': forms.Textarea(attrs={'rows': 3}),
            'tratamiento': forms.Textarea(attrs={'rows': 3}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }


class ExamenOftalmologicoForm(BaseFormMixin, forms.ModelForm):
    class Meta:
        model = ExamenOftalmologico
        # Excluimos historia_clinica porque es un OneToOneField que se maneja automáticamente
        exclude = ('historia_clinica',)
        widgets = {
            # Usar un campo de texto amplio para las descripciones largas
            'biomicroscopia': forms.Textarea(attrs={'rows': 3}),
            'fondo_ojo': forms.Textarea(attrs={'rows': 3}),
        }
