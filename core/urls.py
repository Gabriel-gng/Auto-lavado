from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.register_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('registrar-vehiculo/', views.registrar_vehiculo_view, name='registrar_vehiculo'),
    path('actualizar-vehiculo/<int:vehiculo_id>/', views.actualizar_vehiculo_view, name='actualizar_vehiculo'),
    path('eliminar-vehiculo/<int:vehiculo_id>/', views.eliminar_vehiculo_view, name='eliminar_vehiculo'),
    path('panel/', views.dashboard_view, name='dashboard'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('perfil/actualizar/', views.actualizar_perfil_view, name='actualizar_perfil'),
    path('perfil/eliminar/', views.eliminar_cuenta_view, name='eliminar_cuenta'),
    path('servicio/<int:vehiculo_id>/<int:bahia_id>/', views.seleccionar_servicio_view, name='seleccionar_servicio'),
    path('pago/<int:vehiculo_id>/<int:bahia_id>/<int:servicio_id>/', views.pago_view, name='pago'),
    path('factura/<int:orden_id>/', views.factura_view, name='factura'),
    path('timer/<int:orden_id>/', views.timer_view, name='timer'),
    path('completar/<int:orden_id>/', views.completar_lavado_view, name='completar_lavado'),
    path('admin-panel/', views.admin_panel_view, name='admin_panel'),
    path('exportar-ventas/', views.exportar_ventas_view, name='exportar_ventas'),
]
