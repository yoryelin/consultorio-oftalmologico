from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone  # Necesario para filtrar turnos
from .models import (
    Paciente, HistoriaClinica, ExamenOftalmologico, Profesional, ObraSocial, Turno
)
from .forms import (
    PacienteForm, HistoriaClinicaForm, ExamenOftalmologicoForm, ProfesionalForm, ObraSocialForm
)

# -------------------------------------------------------------
# 1. DASHBOARD
# -------------------------------------------------------------


class DashboardView(LoginRequiredMixin, TemplateView):
    """Vista principal que muestra métricas resumidas."""
    template_name = 'gestion_clinica/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Métricas simples para el dashboard
        context['total_pacientes'] = Paciente.objects.count()
        # Ejemplo: Consultas/Registros en el último mes
        hace_un_mes = timezone.now() - timezone.timedelta(days=30)
        context['consultas_mes'] = HistoriaClinica.objects.filter(
            fecha__gte=hace_un_mes).count()
        # Ejemplo: Próximos turnos en los próximos 7 días
        hace_siete_dias = timezone.now() + timezone.timedelta(days=7)
        context['proximos_turnos'] = Turno.objects.filter(
            fecha_hora__range=[timezone.now(), hace_siete_dias]
        ).count()
        return context

# -------------------------------------------------------------
# 2. VISTAS PARA PACIENTES (CRUD)
# -------------------------------------------------------------


class PacienteListView(LoginRequiredMixin, ListView):
    model = Paciente
    template_name = 'gestion_clinica/paciente_list.html'
    context_object_name = 'pacientes'
    paginate_by = 10


class PacienteDetailView(LoginRequiredMixin, DetailView):
    model = Paciente
    template_name = 'gestion_clinica/paciente_detail.html'
    context_object_name = 'paciente'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ordenamos las historias de la más reciente a la más antigua
        context['historias'] = HistoriaClinica.objects.filter(
            paciente=self.object
        ).order_by('-fecha')
        return context


class PacienteCreateView(LoginRequiredMixin, CreateView):
    model = Paciente
    form_class = PacienteForm  # Usamos el formulario del archivo forms.py
    template_name = 'gestion_clinica/paciente_form.html'
    success_url = reverse_lazy('pacientes:lista_pacientes')


class PacienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'gestion_clinica/paciente_form.html'

    def get_success_url(self):
        # Redirige al detalle del paciente después de editar
        return reverse('pacientes:detalle_paciente', kwargs={'pk': self.object.pk})

# -------------------------------------------------------------
# 3. VISTAS PARA HISTORIA CLÍNICA (CRUD Parcial)
# -------------------------------------------------------------


class HistoriaClinicaCreateView(LoginRequiredMixin, CreateView):
    model = HistoriaClinica
    form_class = HistoriaClinicaForm
    template_name = 'gestion_clinica/historia_clinica_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Aseguramos que el paciente se muestre en el formulario
        context['paciente'] = get_object_or_404(
            Paciente, pk=self.kwargs['paciente_pk'])
        return context

    def form_valid(self, form):
        # Asignamos el paciente antes de guardar
        paciente = get_object_or_404(Paciente, pk=self.kwargs['paciente_pk'])
        form.instance.paciente = paciente
        return super().form_valid(form)

    def get_success_url(self):
        # Redirige al detalle del paciente después de crear la HC
        return reverse('pacientes:detalle_paciente', kwargs={'pk': self.object.paciente.pk})


class HistoriaClinicaUpdateView(LoginRequiredMixin, UpdateView):
    model = HistoriaClinica
    form_class = HistoriaClinicaForm
    template_name = 'gestion_clinica/historia_clinica_form.html'

    def get_success_url(self):
        # Redirige al detalle del paciente
        return reverse('pacientes:detalle_paciente', kwargs={'pk': self.object.paciente.pk})

# -------------------------------------------------------------
# 4. VISTAS PARA EXAMEN OFTALMOLÓGICO (CRUD Parcial)
# -------------------------------------------------------------


class ExamenOftalmologicoUpdateView(LoginRequiredMixin, UpdateView):
    model = ExamenOftalmologico
    form_class = ExamenOftalmologicoForm
    template_name = 'gestion_clinica/examen_oftalmologico_form.html'

    # Sobrescribimos get_object para que use el hc_pk en lugar del pk del examen
    def get_object(self, queryset=None):
        hc = get_object_or_404(HistoriaClinica, pk=self.kwargs['hc_pk'])
        # Intenta obtener el examen existente o crea uno nuevo si no existe
        return ExamenOftalmologico.objects.get_or_create(historia_clinica=hc)[0]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pasamos la HC y el Paciente al contexto para el breadcrumb
        context['historia_clinica'] = self.object.historia_clinica
        context['paciente'] = self.object.historia_clinica.paciente
        return context

    def get_success_url(self):
        # Redirige al detalle del paciente
        return reverse('pacientes:detalle_paciente', kwargs={'pk': self.object.historia_clinica.paciente.pk})

# -------------------------------------------------------------
# 5. VISTAS PARA CATÁLOGO (CRUD Parcial)
# -------------------------------------------------------------


class ProfesionalCreateView(LoginRequiredMixin, CreateView):
    model = Profesional
    form_class = ProfesionalForm
    template_name = 'gestion_clinica/profesional_form.html'
    # Retornamos al listado de pacientes por simplicidad, aunque lo ideal es al detalle del paciente
    success_url = reverse_lazy('pacientes:lista_pacientes')


class ObraSocialCreateView(LoginRequiredMixin, CreateView):
    model = ObraSocial
    form_class = ObraSocialForm
    template_name = 'gestion_clinica/obra_social_form.html'
    success_url = reverse_lazy('pacientes:lista_pacientes')

# -------------------------------------------------------------
# ⭐ 6. VISTAS PARA GESTIÓN DE TURNOS (Objetivo 2.2) ⭐
# -------------------------------------------------------------


class TurnoListView(LoginRequiredMixin, ListView):
    """Muestra la lista de turnos (la agenda)."""
    model = Turno
    template_name = 'gestion_clinica/turno_list.html'
    context_object_name = 'turnos'

    # Sobrescribimos get_queryset para filtrar por la fecha actual o futura
    def get_queryset(self):
        # Muestra solo turnos a partir de la fecha y hora actual, ordenados por fecha
        # Usamos filter(fecha_hora__date__gte=timezone.localdate()) para incluir el día actual
        return Turno.objects.filter(fecha_hora__gte=timezone.now()).order_by('fecha_hora')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Turnos pasados (últimos 15) para historial rápido
        context['turnos_pasados'] = Turno.objects.filter(
            fecha_hora__lt=timezone.now()).order_by('-fecha_hora')[:15]
        return context


class TurnoCreateView(LoginRequiredMixin, CreateView):
    """Permite crear un nuevo turno."""
    model = Turno
    template_name = 'gestion_clinica/turno_form.html'
    # Importante: Usamos el campo fecha_hora que acepta fecha y tiempo
    fields = ['paciente', 'profesional',
              'fecha_hora', 'estado', 'observaciones']

    def get_success_url(self):
        # Redirigir al listado de turnos después de crear uno nuevo
        return reverse_lazy('pacientes:lista_turnos')
