import json
import random
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import PerfilUsuario, Vehiculo, Bahia, Servicio, OrdenLavado
from .forms import LoginForm, RegistroUsuarioForm, VehiculoForm, ActualizarPerfilForm


def liberar_bahias_expiradas():
    """Libera automáticamente las bahías cuyo tiempo de servicio ya expiró."""
    ordenes_expiradas = OrdenLavado.objects.filter(
        estado='en_progreso',
        fecha_fin__lte=timezone.now()
    )
    for orden in ordenes_expiradas:
        orden.estado = 'completado'
        orden.save()
        if orden.bahia:
            orden.bahia.ocupada = False
            orden.bahia.save()


# ======================== AUTH ========================

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_panel')
        return redirect('dashboard')

    form = LoginForm()
    error = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # Try authenticate by username first, then by email
            user = authenticate(request, username=username, password=password)
            if user is None:
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
            if user is not None:
                login(request, user)
                if user.is_staff:
                    return redirect('admin_panel')
                # Check if user has registered a vehicle
                if hasattr(user, 'perfil') and not user.perfil.vehiculo_registrado:
                    return redirect('registrar_vehiculo')
                return redirect('dashboard')
            else:
                error = 'Credenciales inválidas.'
    return render(request, 'core/login.html', {'form': form, 'error': error})


def register_view(request):
    form = RegistroUsuarioForm()
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre_completo']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            documento = form.cleaned_data['documento_identidad']
            telefono = form.cleaned_data['telefono']

            # Create username from email
            username = email.split('@')[0]
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=nombre.split(' ')[0],
                last_name=' '.join(nombre.split(' ')[1:]) if len(nombre.split(' ')) > 1 else '',
            )
            PerfilUsuario.objects.create(
                user=user,
                nombre_completo=nombre,
                documento_identidad=documento,
                telefono=telefono,
                vehiculo_registrado=False,
            )
            login(request, user)
            return redirect('registrar_vehiculo')
    return render(request, 'core/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# ======================== VEHICLE ========================

@login_required
def registrar_vehiculo_view(request):
    form = VehiculoForm()
    if request.method == 'POST':
        form = VehiculoForm(request.POST)
        if form.is_valid():
            vehiculo = form.save(commit=False)
            vehiculo.usuario = request.user
            vehiculo.save()
            if hasattr(request.user, 'perfil'):
                request.user.perfil.vehiculo_registrado = True
                request.user.perfil.save()
            return redirect('dashboard')
    return render(request, 'core/registrar_vehiculo.html', {'form': form})


@login_required
def actualizar_vehiculo_view(request, vehiculo_id):
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id, usuario=request.user)
    form = VehiculoForm(instance=vehiculo)
    if request.method == 'POST':
        form = VehiculoForm(request.POST, instance=vehiculo)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    return render(request, 'core/actualizar_vehiculo.html', {'form': form, 'vehiculo': vehiculo})


@login_required
@require_POST
def eliminar_vehiculo_view(request, vehiculo_id):
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id, usuario=request.user)
    vehiculo.delete()
    if not Vehiculo.objects.filter(usuario=request.user).exists():
        if hasattr(request.user, 'perfil'):
            request.user.perfil.vehiculo_registrado = False
            request.user.perfil.save()
    return redirect('dashboard')


# ======================== PROFILE ========================

@login_required
def perfil_view(request):
    perfil = getattr(request.user, 'perfil', None)
    context = {
        'perfil': perfil,
    }
    return render(request, 'core/perfil.html', context)


@login_required
def actualizar_perfil_view(request):
    perfil = getattr(request.user, 'perfil', None)
    if request.method == 'POST':
        form = ActualizarPerfilForm(request.POST)
        if form.is_valid():
            if perfil:
                perfil.nombre_completo = form.cleaned_data['nombre_completo']
                perfil.documento_identidad = form.cleaned_data['documento_identidad']
                perfil.telefono = form.cleaned_data['telefono']
                perfil.save()
            request.user.email = form.cleaned_data['email']
            request.user.save()
            return redirect('perfil')
    else:
        form = ActualizarPerfilForm(initial={
            'nombre_completo': perfil.nombre_completo if perfil else '',
            'documento_identidad': perfil.documento_identidad if perfil else '',
            'telefono': perfil.telefono if perfil else '',
            'email': request.user.email,
        })
    return render(request, 'core/actualizar_perfil.html', {'form': form})


@login_required
def eliminar_cuenta_view(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        return redirect('login')
    return redirect('perfil')


# ======================== DASHBOARD ========================

@login_required
def dashboard_view(request):
    liberar_bahias_expiradas()
    vehiculos = Vehiculo.objects.filter(usuario=request.user)

    # Determine which bay types the user can see
    tipos_vehiculo = set(vehiculos.values_list('tipo', flat=True))
    tiene_moto = 'Moto' in tipos_vehiculo
    tiene_carro = 'Carro' in tipos_vehiculo or 'Camioneta' in tipos_vehiculo

    bahias = []
    if tiene_moto and tiene_carro:
        bahias = Bahia.objects.all()
    elif tiene_moto:
        bahias = Bahia.objects.filter(tipo='Moto')
    elif tiene_carro:
        bahias = Bahia.objects.filter(tipo='Carro')

    # Check active orders
    orden_activa = OrdenLavado.objects.filter(
        usuario=request.user,
        estado='en_progreso'
    ).first()

    vehiculos_en_lavado = set(
        OrdenLavado.objects.filter(
            usuario=request.user,
            estado='en_progreso'
        ).values_list('vehiculo_id', flat=True)
    )

    tiene_orden_activa = OrdenLavado.objects.filter(
        usuario=request.user,
        estado='en_progreso'
    ).exists()

    context = {
        'vehiculos': vehiculos,
        'bahias': bahias,
        'tiene_moto': tiene_moto,
        'tiene_carro': tiene_carro,
        'orden_activa': orden_activa,
        'vehiculos_en_lavado': vehiculos_en_lavado,
        'tiene_orden_activa': tiene_orden_activa,
    }
    return render(request, 'core/dashboard.html', context)


# ======================== SERVICE SELECTION ========================

@login_required
def seleccionar_servicio_view(request, vehiculo_id, bahia_id):
    # Bloquear si ya tiene un lavado en progreso
    if OrdenLavado.objects.filter(usuario=request.user, estado='en_progreso').exists():
        return redirect('dashboard')
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id, usuario=request.user)
    bahia = get_object_or_404(Bahia, id=bahia_id, ocupada=False)
    servicios = Servicio.objects.all()

    context = {
        'vehiculo': vehiculo,
        'bahia': bahia,
        'servicios': servicios,
    }
    return render(request, 'core/seleccionar_servicio.html', context)


# ======================== PAYMENT ========================

@login_required
def pago_view(request, vehiculo_id, bahia_id, servicio_id):
    # Bloquear si ya tiene un lavado en progreso
    if OrdenLavado.objects.filter(usuario=request.user, estado='en_progreso').exists():
        return redirect('dashboard')
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id, usuario=request.user)
    bahia = get_object_or_404(Bahia, id=bahia_id)
    servicio = get_object_or_404(Servicio, id=servicio_id)

    if request.method == 'POST':
        metodo_pago = request.POST.get('metodo_pago')
        if metodo_pago in ['Efectivo', 'Tarjeta', 'Transferencia']:
            # Generate invoice number
            now = timezone.now()
            numero_factura = f"FAC-{now.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

            orden = OrdenLavado.objects.create(
                numero_factura=numero_factura,
                usuario=request.user,
                vehiculo=vehiculo,
                servicio=servicio,
                bahia=bahia,
                metodo_pago=metodo_pago,
                total=servicio.precio,
                estado='en_progreso',
                # El tiempo de lavado debe iniciar cuando el usuario entra al timer de lavado,
                # no cuando termina de pagar (hay un timer de llegada previo e independiente).
                fecha_inicio=None,
                fecha_fin=None,
            )
            # Mark bay as occupied
            bahia.ocupada = True
            bahia.save()

            return redirect('factura', orden_id=orden.id)

    context = {
        'vehiculo': vehiculo,
        'bahia': bahia,
        'servicio': servicio,
    }
    return render(request, 'core/pago.html', context)


# ======================== INVOICE ========================

@login_required
def factura_view(request, orden_id):
    orden = get_object_or_404(OrdenLavado, id=orden_id, usuario=request.user)
    context = {'orden': orden}
    return render(request, 'core/factura.html', context)


# ======================== TIMER ========================

@login_required
def timer_view(request, orden_id):
    orden = get_object_or_404(OrdenLavado, id=orden_id, usuario=request.user)

    # Inicia el lavado al abrir esta vista por primera vez.
    # Esto evita que el timer de llegada descuente tiempo al servicio.
    if orden.estado == 'en_progreso' and (orden.fecha_inicio is None or orden.fecha_fin is None):
        fecha_inicio = timezone.now()
        orden.fecha_inicio = fecha_inicio
        orden.fecha_fin = fecha_inicio + timedelta(minutes=orden.servicio.duracion_minutos)
        orden.save(update_fields=['fecha_inicio', 'fecha_fin'])

    context = {
        'orden': orden,
        'duracion_segundos': orden.servicio.duracion_minutos * 60,
        'fecha_fin_iso': orden.fecha_fin.isoformat() if orden.fecha_fin else '',
    }
    return render(request, 'core/timer.html', context)


@login_required
@require_POST
def completar_lavado_view(request, orden_id):
    orden = get_object_or_404(OrdenLavado, id=orden_id, usuario=request.user)
    if orden.estado == 'en_progreso':
        orden.estado = 'completado'
        orden.fecha_fin = timezone.now()
        orden.save()
        # Free the bay
        if orden.bahia:
            orden.bahia.ocupada = False
            orden.bahia.save()
    return JsonResponse({'status': 'ok'})


# ======================== ADMIN PANEL ========================

def is_admin(user):
    return user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_panel_view(request):
    liberar_bahias_expiradas()
    filtro = request.GET.get('filtro', 'hoy')
    today = timezone.localdate()

    if filtro == 'hoy':
        ordenes = OrdenLavado.objects.filter(
            fecha_creacion__date=today,
            estado__in=['en_progreso', 'completado']
        )
    elif filtro == 'mes':
        ordenes = OrdenLavado.objects.filter(
            fecha_creacion__year=today.year,
            fecha_creacion__month=today.month,
            estado__in=['en_progreso', 'completado']
        )
    elif filtro == 'rango':
        fecha_desde = request.GET.get('fecha_desde', '')
        fecha_hasta = request.GET.get('fecha_hasta', '')
        ordenes = OrdenLavado.objects.filter(estado__in=['en_progreso', 'completado'])
        if fecha_desde:
            ordenes = ordenes.filter(fecha_creacion__date__gte=fecha_desde)
        if fecha_hasta:
            ordenes = ordenes.filter(fecha_creacion__date__lte=fecha_hasta)
    else:
        ordenes = OrdenLavado.objects.filter(
            fecha_creacion__date=today,
            estado__in=['en_progreso', 'completado']
        )

    total_recaudado = sum(o.total for o in ordenes)
    total_ventas = ordenes.count()
    promedio = total_recaudado / total_ventas if total_ventas > 0 else 0

    context = {
        'ordenes': ordenes,
        'total_recaudado': total_recaudado,
        'total_ventas': total_ventas,
        'promedio': promedio,
        'filtro': filtro,
        'fecha_desde': request.GET.get('fecha_desde', ''),
        'fecha_hasta': request.GET.get('fecha_hasta', ''),
    }
    return render(request, 'core/admin_panel.html', context)


@login_required
@user_passes_test(is_admin)
def exportar_ventas_view(request):
    import csv
    from django.http import HttpResponse

    filtro = request.GET.get('filtro', 'hoy')
    today = timezone.localdate()

    if filtro == 'hoy':
        ordenes = OrdenLavado.objects.filter(
            fecha_creacion__date=today,
            estado__in=['en_progreso', 'completado']
        )
    elif filtro == 'mes':
        ordenes = OrdenLavado.objects.filter(
            fecha_creacion__year=today.year,
            fecha_creacion__month=today.month,
            estado__in=['en_progreso', 'completado']
        )
    elif filtro == 'rango':
        fecha_desde = request.GET.get('fecha_desde', '')
        fecha_hasta = request.GET.get('fecha_hasta', '')
        ordenes = OrdenLavado.objects.filter(estado__in=['en_progreso', 'completado'])
        if fecha_desde:
            ordenes = ordenes.filter(fecha_creacion__date__gte=fecha_desde)
        if fecha_hasta:
            ordenes = ordenes.filter(fecha_creacion__date__lte=fecha_hasta)
    else:
        ordenes = OrdenLavado.objects.filter(
            fecha_creacion__date=today,
            estado__in=['en_progreso', 'completado']
        )

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ventas.csv"'

    writer = csv.writer(response)
    writer.writerow(['Factura', 'Fecha/Hora', 'Cliente', 'Vehículo', 'Servicio', 'Pago', 'Total'])

    for orden in ordenes:
        writer.writerow([
            orden.numero_factura,
            orden.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
            orden.usuario.perfil.nombre_completo if hasattr(orden.usuario, 'perfil') else orden.usuario.username,
            orden.vehiculo.placa,
            orden.servicio.nombre,
            orden.metodo_pago,
            f"${orden.total:,.0f}",
        ])

    return response
