from django.db import models
from django.contrib.auth.models import User


class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    documento_identidad = models.CharField(max_length=20)
    telefono = models.CharField(max_length=20)
    nombre_completo = models.CharField(max_length=150)
    vehiculo_registrado = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre_completo

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuarios'


class Vehiculo(models.Model):
    TIPO_CHOICES = [
        ('Moto', 'Moto'),
        ('Carro', 'Carro'),
        ('Camioneta', 'Camioneta'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehiculos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    placa = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    color = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.placa} - {self.tipo}"

    @property
    def es_moto(self):
        return self.tipo == 'Moto'

    @property
    def es_carro(self):
        return self.tipo in ['Carro', 'Camioneta']

    class Meta:
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'


class Bahia(models.Model):
    TIPO_CHOICES = [
        ('Carro', 'Carro'),
        ('Moto', 'Moto'),
    ]
    numero = models.IntegerField(unique=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    ocupada = models.BooleanField(default=False)

    def __str__(self):
        return f"Bahía {self.numero} ({self.tipo})"

    class Meta:
        verbose_name = 'Bahía'
        verbose_name_plural = 'Bahías'
        ordering = ['numero']


class Servicio(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)
    duracion_minutos = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    icono = models.CharField(max_length=50, default='bi-droplet')

    def __str__(self):
        return f"{self.nombre} - ${self.precio:,.0f}"

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'


class OrdenLavado(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completado', 'Completado'),
    ]
    METODO_PAGO_CHOICES = [
        ('Efectivo', 'Efectivo'),
        ('Tarjeta', 'Tarjeta'),
        ('Transferencia', 'Transferencia'),
    ]
    numero_factura = models.CharField(max_length=30, unique=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ordenes')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    bahia = models.ForeignKey(Bahia, on_delete=models.SET_NULL, null=True)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)
    total = models.DecimalField(max_digits=10, decimal_places=0)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.numero_factura} - {self.usuario.get_full_name()}"

    class Meta:
        verbose_name = 'Orden de Lavado'
        verbose_name_plural = 'Órdenes de Lavado'
        ordering = ['-fecha_creacion']
