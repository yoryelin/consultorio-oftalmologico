from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
# Asegúrate de que todos los modelos necesarios están importados
from .models import Paciente, HistoriaClinica, ExamenOftalmologico, Profesional, ObraSocial
from .forms import (
    PacienteForm, HistoriaClinicaForm, ExamenOftalmologicoForm,
    ProfesionalForm, ObraSocialForm
)

# --- Vistas de Catálogo (Uso Rápido) ---


class ProfesionalCreateView(CreateView):
    model = Profesional
    form_class = ProfesionalForm
    template_name = 'gestion_clinica/medico_form.html'
    success_url = reverse_lazy('admin:gestion_clinica_profesional_changelist')


class ObraSocialCreateView(CreateView):
    model = ObraSocial
    form_class = ObraSocialForm
    template_name = 'gestion_clinica/form_base.html'
    success_url = reverse_lazy('admin:gestion_clinica_obrasocial_changelist')

# --- Vistas Operacionales: Paciente ---


class PacienteListView(ListView):
    model = Paciente
    template_name = 'gestion_clinica/paciente_list.html'
    context_object_name = 'pacientes'
    ordering = ['apellido', 'nombre']


class PacienteCreateView(CreateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'gestion_clinica/paciente_form.html'
    # success_url se maneja con get_absolute_url en el modelo Paciente


class PacienteUpdateView(UpdateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'gestion_clinica/paciente_form.html'
    context_object_name = 'paciente'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Editar Paciente: {self.object.num_registro}'
        return context

# 6. Detalle de Paciente (Vista Maestra que muestra el historial)


class PacienteDetailView(DetailView):
    model = Paciente
    template_name = 'gestion_clinica/paciente_detail.html'
    context_object_name = 'paciente'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente = self.get_object()

        # ⭐ CORRECCIÓN CLAVE: 'examen_oftalmologico' cambiado a 'examen' ⭐
        # Esto resuelve el FieldError
        context['historias'] = paciente.historias_clinicas.all().select_related(
            'profesional', 'examen'  # <--- ¡CAMBIO HECHO AQUÍ!
        )
        return context

# --- Vistas Operacionales: Historia Clínica y Examen ---

# 7. Creación de Historia Clínica (Desde el Detalle del Paciente)


class HistoriaClinicaCreateView(CreateView):
    model = HistoriaClinica
    form_class = HistoriaClinicaForm
    template_name = 'gestion_clinica/historia_clinica_form.html'

    def form_valid(self, form):
        # 1. Asigna el paciente a la HC usando la PK pasada en la URL
        paciente_pk = self.kwargs['paciente_pk']
        paciente = Paciente.objects.get(pk=paciente_pk)
        form.instance.paciente = paciente

        # Guardar la Historia Clínica para obtener su PK
        response = super().form_valid(form)

        # ⭐ CORRECCIÓN CLAVE: CREAR EL EXAMEN OFTALMOLÓGICO VACÍO AQUÍ ⭐
        # Esto establece inmediatamente la relación OneToOne para la plantilla
        ExamenOftalmologico.objects.create(historia_clinica=self.object)

        return response

    def get_success_url(self):
        """Redirige al detalle del paciente después de guardar la HC."""
        # Se usa self.object.paciente.pk para obtener el PK del paciente recién asignado (soluciona NoReverseMatch)
        return reverse('pacientes:detalle_paciente', kwargs={'pk': self.object.paciente.pk})

    def get_context_data(self, **kwargs):
        """Añade el título del formulario y el objeto Paciente al contexto."""
        context = super().get_context_data(**kwargs)
        paciente_pk = self.kwargs.get('paciente_pk')
        paciente = Paciente.objects.get(pk=paciente_pk)
        context['paciente'] = paciente
        context['form_title'] = f'Nueva Historia Clínica para: {paciente.apellido}, {paciente.nombre}'
        return context

# 8. Edición de Historia Clínica


class HistoriaClinicaUpdateView(UpdateView):
    model = HistoriaClinica
    form_class = HistoriaClinicaForm
    template_name = 'gestion_clinica/historia_clinica_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente = self.object.paciente
        context['paciente'] = paciente
        context['form_title'] = f'Editando Historia Clínica de: {paciente.apellido}, {paciente.nombre}'
        return context

# 9. Edición/Creación de Examen Oftalmológico (Usado como UpdateView)


class ExamenOftalmologicoUpdateView(UpdateView):
    model = ExamenOftalmologico
    form_class = ExamenOftalmologicoForm
    template_name = 'gestion_clinica/examen_oftalmologico_form.html'

    def get_object(self, queryset=None):
        """Intenta obtener el Examen asociado a la HC si se usa hc_pk."""
        hc_pk = self.kwargs.get('hc_pk')

        if hc_pk:
            try:
                # Intenta obtener el Examen asociado a esa Historia Clínica
                return ExamenOftalmologico.objects.get(historia_clinica__pk=hc_pk)
            except ExamenOftalmologico.DoesNotExist:
                # Si no existe, devuelve None (aunque la HCCreateView ya lo crea)
                return None

        return super().get_object(queryset)

    def form_valid(self, form):
        hc_pk = self.kwargs.get('hc_pk')

        if hc_pk and not form.instance.pk:
            historia_clinica = HistoriaClinica.objects.get(pk=hc_pk)
            form.instance.historia_clinica = historia_clinica

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hc = None

        if self.kwargs.get('hc_pk'):
            hc = HistoriaClinica.objects.get(pk=self.kwargs['hc_pk'])
        elif self.object and self.object.historia_clinica:
            hc = self.object.historia_clinica

        if hc:
            context['historia_clinica'] = hc
            context['paciente'] = hc.paciente
            context['form_title'] = f'Examen Oftalmológico para HC N° {hc.pk} - {hc.paciente.apellido}, {hc.paciente.nombre}'

        return context

    def get_success_url(self):
        """Redirige al detalle del paciente después de guardar."""
        if self.object and self.object.historia_clinica:
            return reverse('pacientes:detalle_paciente',
                           kwargs={'pk': self.object.historia_clinica.paciente.pk})
        return reverse('pacientes:lista_pacientes')
