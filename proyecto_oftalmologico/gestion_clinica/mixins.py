# gestion_clinica/mixins.py

class BaseFormMixin:
    """
    Mixin para aplicar automáticamente la clase 'form-control'
    de Bootstrap a todos los campos del formulario (Input, Select, Textarea),
    siguiendo el principio DRY.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Itera sobre todos los campos definidos en el formulario
        for field_name, field in self.fields.items():
            # Aplicar 'form-control' a la lista de atributos CSS del widget
            field.widget.attrs['class'] = 'form-control'
