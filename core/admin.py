from django.contrib import admin
from .models import PerfilUsuario, Vehiculo, Bahia, Servicio, OrdenLavado


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'documento_identidad', 'telefono', 'user')
    search_fields = ('nombre_completo', 'documento_identidad')


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('placa', 'tipo', 'marca', 'modelo', 'color', 'usuario')
    list_filter = ('tipo',)
    search_fields = ('placa', 'marca')


@admin.register(Bahia)
class BahiaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'tipo', 'ocupada')
    list_filter = ('tipo', 'ocupada')


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'duracion_minutos', 'precio')


@admin.register(OrdenLavado)
class OrdenLavadoAdmin(admin.ModelAdmin):
    list_display = ('numero_factura', 'usuario', 'vehiculo', 'servicio', 'metodo_pago', 'total', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'metodo_pago', 'fecha_creacion')
    search_fields = ('numero_factura',)
