# gestion_clinica/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    # Agregamos 'View'
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
)
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone  # Necesario para filtrar turnos
# ⭐ AGREGAR: Necesario para mensajes
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin  # <--- NUEVA IMPORTACIÓN
# ⭐ NUEVA IMPORTACIÓN para transacciones atómicas
from django.db import transaction
# ⭐ NUEVAS IMPORTACIONES para la vista JSON de Turnos ⭐
from django.http import JsonResponse, Http404

# ⭐ IMPORTACIÓN NECESARIA PARA FILTROS OR (Q objects) ⭐
from django.db.models import Q

from .models import (
    Paciente, HistoriaClinica, ExamenOftalmologico, Profesional, ObraSocial, Turno,
    # ❌ ELIMINADA: PrescripcionLentes ya no se importa
)
from .forms import (
    PacienteForm, HistoriaClinicaForm, ExamenOftalmologicoForm, ProfesionalForm, ObraSocialForm, TurnoForm,
    TurnoEstadoForm,
    # ❌ ELIMINADA: PrescripcionLentesForm ya no se importa
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

    def get_queryset(self):
        queryset = super().get_queryset()

        # 1. Obtener el término de búsqueda, asumiendo que el campo en el template es 'q'.
        query = self.request.GET.get('q')

        if query:
            # 2. Aplicar el filtro de búsqueda OR en DNI y Apellido (insensible a mayúsculas)
            queryset = queryset.filter(
                Q(dni__icontains=query) |
                Q(apellido__icontains=query)
            ).distinct()  # Evita resultados duplicados

        return queryset


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

        # ⭐ SE MANTIENE SOLO LA LISTA COMPLETA DE EXÁMENES (Inmutables)
        context['examenes_oftalmologicos_todos'] = ExamenOftalmologico.objects.filter(
            historia_clinica__paciente=self.object
        ).order_by('-historia_clinica__fecha')

        # Compatibilidad con la plantilla: todos son 'activos' ahora
        context['examenes_oftalmologicos_activos'] = context['examenes_oftalmologicos_todos']

        # ❌ ELIMINADO: Contexto para Prescripciones de Lentes
        # context['prescripciones_lentes'] = PrescripcionLentes.objects.filter(
        #     paciente=self.object
        # ).order_by('-fecha_emision')

        return context


# <--- MIXIN APLICADO
class PacienteCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'gestion_clinica/paciente_form.html'
    # <--- MENSAJE DE ÉXITO
    success_message = "Paciente %(nombre)s %(apellido)s registrado exitosamente."

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data

    def get_success_url(self):
        # Redirige a la creación del turno, pasando el ID del paciente como parámetro GET.
        # URL corregida
        return reverse('gestion_clinica:crear_turno') + f'?paciente_id={self.object.pk}'


# <--- MIXIN APLICADO
class PacienteUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'gestion_clinica/paciente_form.html'
    # <--- MENSAJE DE ÉXITO
    success_message = "Datos del paciente %(nombre)s %(apellido)s actualizados correctamente."

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data

    def get_success_url(self):
        # Redirige al detalle del paciente después de editar
        # URL corregida
        return reverse('gestion_clinica:detalle_paciente', kwargs={'pk': self.object.pk})

# -------------------------------------------------------------
# 3. VISTAS PARA HISTORIA CLÍNICA (INMUTABLE)
# -------------------------------------------------------------

# La vista de creación atómica no usa SuccessMessageMixin porque ya maneja
# el mensaje de forma manual dentro del bloque 'transaction.atomic'.


class ExamenOftalmologicoFirstCreateView(LoginRequiredMixin, CreateView):
    """
    Vista prioritaria para la primera consulta (o nueva consulta). Utiliza el 
    formulario de E.O. para crear primero el E.O. y luego la Historia Clínica (HC) asociada.
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

        # Intenta asignar el profesional
        profesional_asignado = None
        # NOTA: Esto asume una relación OneToOne entre User y Profesional.
        if self.request.user.is_authenticated and hasattr(self.request.user, 'profesional'):
            profesional_asignado = self.request.user.profesional
        elif Profesional.objects.exists():
            profesional_asignado = Profesional.objects.first()

        with transaction.atomic():
            # 1. Crear la Historia Clínica (el "contenedor")
            historia_clinica = HistoriaClinica.objects.create(
                paciente=paciente,
                profesional=profesional_asignado,
                # Tomamos campos de HC si están en EOForm
                motivo_consulta=form.cleaned_data.get(
                    'motivo_consulta', "Registro Inicial"),
                diagnostico=form.cleaned_data.get(
                    'diagnostico', "Pendiente de evaluación"),
                tratamiento=form.cleaned_data.get(
                    'tratamiento', "Pendiente de indicación"),
            )

            # 2. Asignar la HC al Examen y guardarlo
            form.instance.historia_clinica = historia_clinica
            self.object = form.save()
            messages.success(
                self.request, "Nueva Historia Clínica (Consulta) y Examen Oftalmológico creados con éxito.")

        return redirect(self.get_success_url())

    def get_success_url(self):
        # Redirige al detalle del paciente después de crear HC y E.O.
        # URL corregida
        return reverse('gestion_clinica:detalle_paciente', kwargs={'pk': self.kwargs['paciente_pk']})


# -------------------------------------------------------------
# 4. VISTAS PARA EXAMEN OFTALMOLÓGICO (INMUTABLE: SOLO DETALLE/LECTURA)
# -------------------------------------------------------------

# ⭐ VISTA: DETALLE DE E.O. (Se mantiene)
class ExamenOftalmologicoDetailView(LoginRequiredMixin, DetailView):
    model = ExamenOftalmologico
    template_name = 'gestion_clinica/examen_oftalmologico_detail.html'
    context_object_name = 'examen'

    def get_object(self, queryset=None):
        # 1. Obtener la Historia Clínica (HC) primero
        hc = get_object_or_404(HistoriaClinica, pk=self.kwargs['hc_pk'])

        # 2. Intentar acceder al examen a través de la relación inversa
        try:
            return ExamenOftalmologico.objects.get(historia_clinica=hc)

        except ExamenOftalmologico.DoesNotExist:
            # Si la HC existe pero el EO no, lanzamos 404
            raise Http404(
                f"No se encontró Examen Oftalmológico para la Historia Clínica #{hc.pk}."
            )

# -------------------------------------------------------------
# 5. VISTAS PARA CATÁLOGO (CRUD Parcial)
# -------------------------------------------------------------


# <--- MIXIN APLICADO
class ProfesionalCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Profesional
    form_class = ProfesionalForm
    template_name = 'gestion_clinica/profesional_form.html'
    # URL corregida
    success_url = reverse_lazy('gestion_clinica:lista_pacientes')
    success_message = "Nuevo profesional registrado exitosamente."  # <--- MENSAJE DE ÉXITO


# <--- MIXIN APLICADO
class ObraSocialCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = ObraSocial
    form_class = ObraSocialForm
    template_name = 'gestion_clinica/obra_social_form.html'
    # URL corregida
    success_url = reverse_lazy('gestion_clinica:crear_turno')
    success_message = "Nueva Obra Social registrada exitosamente."  # <--- MENSAJE DE ÉXITO

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


class TurnoCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):  # <--- MIXIN APLICADO
    """Permite crear un nuevo turno y maneja la preselección del paciente."""
    model = Turno
    form_class = TurnoForm
    template_name = 'gestion_clinica/turno_form.html'
    # URL corregida
    success_url = reverse_lazy('gestion_clinica:lista_turnos')
    success_message = "Turno creado exitosamente."  # <--- MENSAJE DE ÉXITO

    def get_initial(self):
        initial = super().get_initial()
        paciente_id = self.request.GET.get('paciente_id')

        if paciente_id:
            initial['paciente'] = paciente_id

        return initial


# ⭐ VISTA DE DETALLE/ACTUALIZACIÓN DE TURNO (REEMPLAZADA: DetailView -> UpdateView) ⭐
# <--- MIXIN APLICADO (UpdateView)
class TurnoDetailView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Muestra los detalles de un turno y permite cambiar su estado."""
    model = Turno
    # Usamos el formulario simple que creamos en forms.py
    form_class = TurnoEstadoForm
    template_name = 'gestion_clinica/turno_detail.html'
    context_object_name = 'turno'
    success_message = "Estado del turno actualizado correctamente."  # <--- MENSAJE DE ÉXITO

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añadimos el paciente asociado al turno para mostrar sus detalles
        context['paciente'] = self.object.paciente
        return context

    def get_success_url(self):
        # Redirige a la lista de turnos (la agenda) después de actualizar
        # URL corregida
        return reverse_lazy('gestion_clinica:lista_turnos')


# ⭐ VISTA PARA EL API DEL CALENDARIO (FULLCALENDAR) ⭐
class TurnosJsonView(LoginRequiredMixin, ListView):
    """
    Devuelve los turnos en formato JSON para ser consumidos por FullCalendar.
    """
    model = Turno

    def get_queryset(self):
        # Excluye turnos cancelados de la vista del calendario
        queryset = super().get_queryset().exclude(
            estado='CANCELADO').select_related('paciente')
        return queryset

    def get_color_for_estado(self, estado):
        """Asigna un color CSS basado en el estado del turno."""
        colores = {
            'PENDIENTE': '#007bff',  # Azul
            'CONFIRMADO': '#ffc107',  # Amarillo (Advertencia)
            'ATENDIDO': '#28a745',  # Verde (Éxito)
            'CANCELADO': '#dc3545',  # Rojo (Peligro)
        }
        return colores.get(estado, '#6c757d')  # Gris por defecto

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
                # Redirige al DETALLE DEL TURNO
                # URL corregida
                'url': reverse('gestion_clinica:detalle_turno', kwargs={'pk': turno.pk}),
            })

        return JsonResponse(eventos, safe=False)


# =================================================================
# ❌ ELIMINADAS: Todas las VISTAS de Prescripción de Lentes
# =================================================================
# class PrescripcionLentesCreateView(LoginRequiredMixin, CreateView): (...)
# class PrescripcionLentesListView(LoginRequiredMixin, ListView): (...)
