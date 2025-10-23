from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone  # Necesario para filtrar turnos
# ⭐ NUEVA IMPORTACIÓN para transacciones atómicas
from django.db import transaction
# ⭐ NUEVAS IMPORTACIONES para la vista JSON de Turnos ⭐
from django.http import JsonResponse

from .models import (
    Paciente, HistoriaClinica, ExamenOftalmologico, Profesional, ObraSocial, Turno
)
from .forms import (
    PacienteForm, HistoriaClinicaForm, ExamenOftalmologicoForm, ProfesionalForm, ObraSocialForm, TurnoForm
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
    form_class = PacienteForm
    template_name = 'gestion_clinica/paciente_form.html'

    def get_success_url(self):
        # Redirige a la creación del turno, pasando el ID del paciente como parámetro GET.
        return reverse('pacientes:crear_turno') + f'?paciente_id={self.object.pk}'


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


class ExamenOftalmologicoFirstCreateView(LoginRequiredMixin, CreateView):
    """
    Vista prioritaria para la primera consulta. Utiliza el formulario de E.O.
    para crear primero el E.O. y luego la Historia Clínica (HC) asociada.
    """
    model = ExamenOftalmologico
    form_class = ExamenOftalmologicoForm
    template_name = 'gestion_clinica/examen_oftalmologico_first_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paciente'] = get_object_or_404(
            Paciente, pk=self.kwargs['paciente_pk'])
        return context

    def form_valid(self, form):
        paciente = get_object_or_404(Paciente, pk=self.kwargs['paciente_pk'])

        profesional_asignado = None
        try:
            profesional_asignado = self.request.user.profesional
        except AttributeError:
            try:
                profesional_asignado = Profesional.objects.first()
            except Profesional.DoesNotExist:
                profesional_asignado = None
        except Profesional.DoesNotExist:
            try:
                profesional_asignado = Profesional.objects.first()
            except Profesional.DoesNotExist:
                profesional_asignado = None

        with transaction.atomic():
            # 1. Crear la Historia Clínica (el "contenedor")
            historia_clinica = HistoriaClinica.objects.create(
                paciente=paciente,
                profesional=profesional_asignado,
                motivo_consulta="Registro Inicial (E.O. Prioritario)",
                diagnostico="Pendiente de evaluación",
                tratamiento="Pendiente de indicación",
            )

            # 2. Asignar la HC al Examen y guardarlo
            form.instance.historia_clinica = historia_clinica
            self.object = form.save()

        return redirect(self.get_success_url())

    def get_success_url(self):
        # Redirige al detalle del paciente después de crear HC y E.O.
        return reverse('pacientes:detalle_paciente', kwargs={'pk': self.kwargs['paciente_pk']})


class HistoriaClinicaCreateView(LoginRequiredMixin, CreateView):
    model = HistoriaClinica
    form_class = HistoriaClinicaForm
    template_name = 'gestion_clinica/historia_clinica_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
    success_url = reverse_lazy('pacientes:lista_pacientes')


class ObraSocialCreateView(LoginRequiredMixin, CreateView):
    model = ObraSocial
    form_class = ObraSocialForm
    template_name = 'gestion_clinica/obra_social_form.html'
    success_url = reverse_lazy('pacientes:crear_turno')

# -------------------------------------------------------------
# ⭐ 6. VISTAS PARA GESTIÓN DE TURNOS (ETAPA 2) ⭐
# -------------------------------------------------------------


class TurnoListView(LoginRequiredMixin, ListView):
    """Muestra la lista de turnos (la agenda)."""
    model = Turno
    template_name = 'gestion_clinica/turno_list.html'
    context_object_name = 'turnos'

    def get_queryset(self):
        # Muestra solo turnos a partir de la fecha y hora actual, ordenados por fecha
        return Turno.objects.filter(fecha_hora__gte=timezone.now()).order_by('fecha_hora')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Turnos pasados (últimos 15) para historial rápido
        context['turnos_pasados'] = Turno.objects.filter(
            fecha_hora__lt=timezone.now()).order_by('-fecha_hora')[:15]
        return context


class TurnoCreateView(LoginRequiredMixin, CreateView):
    """Permite crear un nuevo turno y maneja la preselección del paciente."""
    model = Turno
    form_class = TurnoForm
    template_name = 'gestion_clinica/turno_form.html'
    success_url = reverse_lazy('pacientes:lista_turnos')

    def get_initial(self):
        initial = super().get_initial()
        paciente_id = self.request.GET.get('paciente_id')

        if paciente_id:
            initial['paciente'] = paciente_id

        return initial


# ⭐ VISTA DE DETALLE DE TURNO (AÑADIDA PARA RESOLVER NoReverseMatch) ⭐
class TurnoDetailView(LoginRequiredMixin, DetailView):
    """Muestra los detalles de un turno."""
    model = Turno
    template_name = 'gestion_clinica/turno_detail.html'
    context_object_name = 'turno'


# ⭐ VISTA PARA EL API DEL CALENDARIO (FULLCALENDAR) ⭐
class TurnosJsonView(LoginRequiredMixin, ListView):
    """
    Devuelve los turnos en formato JSON para ser consumidos por FullCalendar.
    """
    model = Turno

    def get_queryset(self):
        queryset = super().get_queryset().exclude(estado='CANCELADO')
        return queryset

    def render_to_response(self, context, **response_kwargs):
        turnos = self.get_queryset()
        eventos = []

        for turno in turnos:
            # FullCalendar necesita un diccionario con campos específicos
            eventos.append({
                'id': turno.pk,
                'title': f'{turno.paciente.apellido}, {turno.paciente.nombre}',
                'start': turno.fecha_hora.isoformat(),
                'end': turno.fecha_hora.isoformat(),
                'allDay': False,
                'color': self.get_color_for_estado(turno.estado),
                # ESTO YA NO FALLARÁ
                'url': reverse('pacientes:detalle_turno', kwargs={'pk': turno.pk}),
            })

        return JsonResponse(eventos, safe=False)

    def get_color_for_estado(self, estado):
        """Asigna un color CSS basado en el estado del turno."""
        colores = {
            'PENDIENTE': '#007bff',
            'CONFIRMADO': '#ffc107',
            'ATENDIDO': '#28a745',
            'CANCELADO': '#dc3545',
        }
        return colores.get(estado, '#6c757d')
