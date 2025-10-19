# gestion_clinica/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
# Asegúrate de que todos los modelos necesarios están importados
from .models import Paciente, HistoriaClinica, ExamenOftalmologico, Profesional, ObraSocial
from .forms import (
    PacienteForm, HistoriaClinicaForm, ExamenOftalmologicoForm,
    ProfesionalForm, ObraSocialForm
)

# --- Vistas de Catálogo (Uso Rápido) ---

# 1. Vista para la creación de un nuevo Profesional (médico)


class ProfesionalCreateView(CreateView):
    model = Profesional
    form_class = ProfesionalForm
    template_name = 'gestion_clinica/medico_form.html'
    # Redirige al listado de Admin para poder ver los datos cargados
    success_url = reverse_lazy('admin:gestion_clinica_profesional_changelist')

# 2. Vista para la creación de una Obra Social


class ObraSocialCreateView(CreateView):
    model = ObraSocial
    form_class = ObraSocialForm
    template_name = 'gestion_clinica/form_base.html'
    success_url = reverse_lazy('admin:gestion_clinica_obrasocial_changelist')

# --- Vistas Operacionales: Paciente ---

# 3. Listado de Pacientes (pantalla principal)


class PacienteListView(ListView):
    model = Paciente
    template_name = 'gestion_clinica/paciente_list.html'
    context_object_name = 'pacientes'
    ordering = ['apellido', 'nombre']

# 4. Creación de Nuevo Paciente


class PacienteCreateView(CreateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'gestion_clinica/paciente_form.html'
    # success_url se maneja con get_absolute_url en el modelo Paciente

# 5. Edición de Paciente Existente


class PacienteUpdateView(UpdateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'gestion_clinica/paciente_form.html'
    # success_url se maneja con get_absolute_url en el modelo Paciente

# 6. Detalle de Paciente (Vista Maestra que muestra el historial)


class PacienteDetailView(DetailView):
    model = Paciente
    template_name = 'gestion_clinica/paciente_detail.html'
    context_object_name = 'paciente'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente = self.get_object()

        # Obtiene todas las historias clínicas relacionadas
        context['historias'] = paciente.historias_clinicas.all()

        return context

# --- Vistas Operacionales: Historia Clínica y Examen ---

# 7. Creación de Historia Clínica (Desde el Detalle del Paciente)


class HistoriaClinicaCreateView(CreateView):
    model = HistoriaClinica
    form_class = HistoriaClinicaForm
    template_name = 'gestion_clinica/historia_clinica_form.html'

    def form_valid(self, form):
        # Asigna el paciente a la HC usando la PK pasada en la URL
        paciente_pk = self.kwargs['paciente_pk']
        paciente = Paciente.objects.get(pk=paciente_pk)
        form.instance.paciente = paciente
        return super().form_valid(form)

# 8. Edición de Historia Clínica


class HistoriaClinicaUpdateView(UpdateView):
    model = HistoriaClinica
    form_class = HistoriaClinicaForm
    template_name = 'gestion_clinica/historia_clinica_form.html'

# 9. Edición/Creación de Examen Oftalmológico (Usado como UpdateView)


class ExamenOftalmologicoUpdateView(UpdateView):
    model = ExamenOftalmologico
    form_class = ExamenOftalmologicoForm
    template_name = 'gestion_clinica/examen_oftalmologico_form.html'

    # Redirige a la vista de detalle del paciente después de guardar
    def get_success_url(self):
        # El Examen tiene una relación OneToOne con la HC, y la HC con el Paciente.
        return self.object.historia_clinica.paciente.get_absolute_url()
