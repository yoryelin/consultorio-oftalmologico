from django import forms
from .models import Paciente, HistoriaClinica, Profesional, ObraSocial, ExamenOftalmologico

# Mixin para aplicar la clase CSS 'form-control' a todos los campos


class BaseFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                # Evita sobrescribir widgets ya definidos si no son CheckboxInput
                current_classes = field.widget.attrs.get('class', '')
                if 'form-control' not in current_classes:
                    field.widget.attrs['class'] = (
                        current_classes + ' form-control').strip()

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
    # ⭐ CORRECCIÓN: Aplicación del formato ISO 8601 para el DateInput. ⭐

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

        widgets = {
            'fecha_nacimiento': forms.DateInput(
                # Solución: Usar format='%Y-%m-%d' para que el valor precargado
                # del modelo sea compatible con el input type='date' de HTML5.
                format='%Y-%m-%d',
                attrs={'type': 'date'}
            ),
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
