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
# 5. VISTAS PARA CATÁLOGO (LISTADO, CREACIÓN, EDICIÓN Y ELIMINACIÓN)
# -------------------------------------------------------------

# ⭐⭐ VISTAS DE LISTADO Y CREACIÓN (YA IMPLEMENTADAS Y CORREGIDAS) ⭐⭐


class ProfesionalListView(LoginRequiredMixin, ListView):
    model = Profesional
    template_name = 'gestion_clinica/profesional_list.html'
    context_object_name = 'profesionales'
    paginate_by = 10


# <--- MIXIN APLICADO
class ProfesionalCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Profesional
    form_class = ProfesionalForm
    template_name = 'gestion_clinica/profesional_form.html'
    success_url = reverse_lazy('gestion_clinica:lista_profesionales')
    success_message = "Nuevo profesional registrado exitosamente."


# ⭐⭐ VISTAS NUEVAS DE EDICIÓN Y ELIMINACIÓN DE PROFESIONAL ⭐⭐

class ProfesionalUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Profesional
    form_class = ProfesionalForm
    template_name = 'gestion_clinica/profesional_form.html'  # Reutilizamos
    success_url = reverse_lazy('gestion_clinica:lista_profesionales')
    success_message = "Profesional actualizado exitosamente."


class ProfesionalDeleteView(LoginRequiredMixin, DeleteView):
    model = Profesional
    template_name = 'gestion_clinica/confirm_delete.html'
    success_url = reverse_lazy('gestion_clinica:lista_profesionales')

    def form_valid(self, form):
        messages.success(self.request, "Profesional eliminado correctamente.")
        return super().form_valid(form)


class ObraSocialListView(LoginRequiredMixin, ListView):
    model = ObraSocial
    template_name = 'gestion_clinica/obra_social_list.html'
    context_object_name = 'obras_sociales'
    paginate_by = 10


# <--- MIXIN APLICADO
class ObraSocialCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = ObraSocial
    form_class = ObraSocialForm
    template_name = 'gestion_clinica/obra_social_form.html'
    success_url = reverse_lazy('gestion_clinica:lista_obras_sociales')
    success_message = "Nueva Obra Social registrada exitosamente."

# ⭐⭐ VISTAS NUEVAS DE EDICIÓN Y ELIMINACIÓN DE OBRA SOCIAL ⭐⭐


class ObraSocialUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ObraSocial
    form_class = ObraSocialForm
    template_name = 'gestion_clinica/obra_social_form.html'  # Reutilizamos
    success_url = reverse_lazy('gestion_clinica:lista_obras_sociales')
    success_message = "Obra Social actualizada exitosamente."


class ObraSocialDeleteView(LoginRequiredMixin, DeleteView):
    model = ObraSocial
    template_name = 'gestion_clinica/confirm_delete.html'
    success_url = reverse_lazy('gestion_clinica:lista_obras_sociales')

    def form_valid(self, form):
        messages.success(self.request, "Obra Social eliminada correctamente.")
        return super().form_valid(form)


# -------------------------------------------------------------
# ⭐ 6. VISTAS PARA GESTIÓN DE TURNOS (ETAPA 2) ⭐
# -------------------------------------------------------------


class TurnoListView(LoginRequiredMixin, ListView):
    # ⭐ CORRECCIÓN CLAVE: Define el modelo para resolver ImproperlyConfigured ⭐
    model = Turno
    template_name = 'gestion_clinica/turno_list.html'
    context_object_name = 'turnos'
    paginate_by = 20

    def get_queryset(self):
        # 1. Obtener todos los turnos por defecto, ordenados por fecha y hora
        # Usamos filter(fecha_hora__gte=timezone.now()) para mostrar solo los futuros/actuales,
        # pero para el listado general es mejor mostrar todos para auditoría.
        queryset = super().get_queryset().order_by('fecha_hora')

        # 2. Obtener parámetros de filtro de la URL
        fecha_str = self.request.GET.get('fecha')
        profesional_id = self.request.GET.get('profesional')
        estado = self.request.GET.get('estado')

        # 3. Aplicar filtros
        if fecha_str:
            try:
                # Filtrar por turnos que coinciden con la fecha exacta (día)
                fecha_obj = timezone.datetime.strptime(
                    fecha_str, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_hora__date=fecha_obj)
            except ValueError:
                # Ignorar si el formato de fecha es incorrecto
                pass

        if profesional_id:
            # Filtrar por ID de profesional. Asume que 'profesional_id' es un entero.
            if profesional_id.isdigit():
                queryset = queryset.filter(profesional_id=profesional_id)

        if estado and estado != 'todos':
            # Filtrar por el estado del turno (ej: 'PENDIENTE', 'CONFIRMADO', etc.)
            queryset = queryset.filter(estado=estado)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Necesario para el formulario de filtro en la plantilla
        context['profesionales'] = Profesional.objects.all()

        # Pasar los valores de filtro actuales para que el formulario se mantenga seleccionado
        context['fecha_actual'] = self.request.GET.get('fecha', '')
        context['profesional_actual'] = self.request.GET.get('profesional', '')
        context['estado_actual'] = self.request.GET.get('estado', 'todos')

        # Se añaden las opciones de estado (asumiendo que ESTADO_CHOICES está en models.Turno)
        context['estados_choices'] = Turno.ESTADO_CHOICES

        return context


class TurnoCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Turno
    form_class = TurnoForm
    template_name = 'gestion_clinica/turno_form.html'
    success_url = reverse_lazy('gestion_clinica:lista_turnos')
    success_message = "Turno agendado exitosamente."


class TurnoDetailView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    # Usamos UpdateView para permitir cambiar el estado y/o detalles del turno
    model = Turno
    # Usaremos un formulario más simple para el detalle/cambio de estado
    form_class = TurnoEstadoForm
    template_name = 'gestion_clinica/turno_detail.html'
    context_object_name = 'turno'
    success_url = reverse_lazy('gestion_clinica:lista_turnos')
    success_message = "Estado del turno actualizado correctamente."

    # Sobreescribimos get_success_url para redireccionar al mismo detalle
    def get_success_url(self):
        return reverse('gestion_clinica:detalle_turno', kwargs={'pk': self.object.pk})


class TurnosJsonView(LoginRequiredMixin, ListView):
    model = Turno

    # Deshabilita la paginación y la obtención de contexto estándar
    def get_context_data(self, **kwargs):
        return {}

    def get_queryset(self):
        # Filtra turnos para mostrar solo los futuros o confirmados (para el calendario)
        # Esto es un ejemplo, se puede ajustar la lógica de filtro según el calendario JS.
        queryset = Turno.objects.filter(
            fecha_hora__gte=timezone.now() - timezone.timedelta(hours=6)
        ).select_related('paciente', 'profesional')

        return queryset

    def render_to_response(self, context):
        # ⭐ CORRECCIÓN APLICADA AQUÍ: Definimos una duración fija de 30 minutos para evitar AttributeError ⭐
        duracion_defecto = timezone.timedelta(minutes=30)

        # Convierte el queryset a un formato JSON compatible con FullCalendar
        data = []
        for turno in self.get_queryset():

            # Usamos la duración por defecto para calcular la hora de finalización
            hora_fin = turno.fecha_hora + duracion_defecto

            data.append({
                'id': turno.pk,
                'title': f'{turno.paciente.apellido}, {turno.paciente.nombre} ({turno.estado})',
                'start': turno.fecha_hora.isoformat(),
                # ⭐ LÍNEA CORREGIDA PARA USAR hora_fin ⭐
                'end': hora_fin.isoformat(),
                'url': reverse('gestion_clinica:detalle_turno', kwargs={'pk': turno.pk}),
                # Colores basados en el estado (esto es solo un ejemplo de estilo)
                'color': self.get_color_for_estado(turno.estado)
            })
        return JsonResponse(data, safe=False)

    def get_color_for_estado(self, estado):
        colores = {
            'PENDIENTE': '#f39c12',  # Amarillo/Naranja
            'CONFIRMADO': '#007bff',  # Azul
            'ASISTIO': '#28a745',    # Verde
            'CANCELADO': '#dc3545',  # Rojo
            'ANULADO': '#6c757d',    # Gris
        }
        return colores.get(estado, '#000000')  # Negro por defecto


# =================================================================
# ❌ ELIMINADAS: Todas las VISTAS de Prescripción de Lentes
# =================================================================
# class PrescripcionLentesCreateView(LoginRequiredMixin, CreateView): (...)
# class PrescripcionLentesListView(LoginRequiredMixin, ListView): (...)
