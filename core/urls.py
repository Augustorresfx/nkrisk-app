from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.contrib.auth import views as auth_views
from .views import HomeView, VehiculosInfoAutoView, EditarDatosMovimientoView, ObtenerDatosMovimientoView, ExportarUltimoEstadoFlotaView, obtener_datos_vehiculo, buscar_vehiculo_por_codigo, autocomplete_marcas, obtener_vehiculos_por_marca, BuscarVehiculoView, InicioView, FlotasView, EliminarMovimientoView, ExportarMovimientoView, ClientesView, LocalidadesView, DetalleClienteView, EliminarClienteView, DetalleFlotaView, EliminarFlotaView ,DetalleTarifaFlotaView, DeleteAllTarifasFlotasView, EliminarTarifaFlotaView,TarifasFlotasView, VencimientosView, CobranzasView, SignInView, SignOutView
from .views import CreditosView, DetalleCreditoView, EliminarAseguradoCreditoView
from django.conf.urls import handler404
from .views import pagina_no_encontrada

handler404 = pagina_no_encontrada

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', SignInView.as_view(), name="login"),
    path('logout/', SignOutView.as_view(), name="logout"),
    path('', HomeView.as_view(), name='home'),
    path('inicio/', InicioView.as_view(), name='inicio'),
    path('vencimientos/', VencimientosView.as_view(), name='vencimientos'),
    path('localidades/', LocalidadesView.as_view(), name='localidades'),
    path('cobranzas/', CobranzasView.as_view(), name='cobranzas'),
    
    # CLIENTES
    path('clientes/', ClientesView.as_view(), name='clientes'),
    path('clientes/<int:cliente_id>/', DetalleClienteView.as_view(), name='detalle_cliente'),
    path('clientes/<int:cliente_id>/eliminar/', EliminarClienteView.as_view(), name='delete_cliente'),
    
    # CREDITOS
    path('creditos/', CreditosView.as_view(), name='creditos'),
    path('creditos/<int:asegurado_id>/eliminar/', EliminarAseguradoCreditoView.as_view(), name='delete_asegurado'),
    path('creditos/<int:asegurado_id>/', DetalleCreditoView.as_view(), name='detalle_credito'),
    
    # MOVIMIENTOS (ENDOSOS DE FLOTAS)
    path('obtener_datos_movimiento/<int:movimiento_id>/', ObtenerDatosMovimientoView.as_view(), name='obtener_datos_movimiento'),
    path('editar_movimiento/<int:flota_id>/<int:movimiento_id>/', EditarDatosMovimientoView.as_view(), name='editar_movimiento'),
    path('movimientos/<int:flota_id>/<int:movimiento_id>/eliminar/', EliminarMovimientoView.as_view(), name='delete_movimiento'),
    path('movimientos/<int:flota_id>/<int:movimiento_id>/exportar/', ExportarMovimientoView.as_view(), name='exportar_movimiento'),
    
    # FLOTAS
    path('flotas/', FlotasView.as_view(), name='flotas'),
    path('flotas/<int:flota_id>/eliminar/', EliminarFlotaView.as_view(), name='delete_flota'),
    path('flotas/<int:flota_id>/', DetalleFlotaView.as_view(), name='detalle_flota'),
    path('flotas/<int:flota_id>/<int:movimiento_id>/', DetalleFlotaView.as_view(), name='detalle_flota_con_movimiento'),
    path('flotas/<int:flota_id>/exportar_ult_estado/', ExportarUltimoEstadoFlotaView.as_view(), name='exportar_ult_estado'),
    
    # VEHICULOS INFO AUTO
    path('vehiculos/', VehiculosInfoAutoView.as_view(), name='vehiculos'),
    path('buscar_vehiculo/', BuscarVehiculoView.as_view(), name='buscar_vehiculo'),
    path('autocomplete_marcas/', autocomplete_marcas, name='autocomplete_marcas'),
    path('obtener_vehiculos/<int:marca_id>/', obtener_vehiculos_por_marca, name='obtener_vehiculos_por_marca'),
    path('buscar_vehiculo_por_codigo/<int:codigo>/', buscar_vehiculo_por_codigo, name='buscar_vehiculo_por_codigo'),
    path('obtener_datos_vehiculo/<int:vehiculo_id>/', obtener_datos_vehiculo, name='obtener_datos_vehiculo'),
    
    # TARIFAS
    path('tarifas_flotas/', TarifasFlotasView.as_view(), name='tarifas_flotas'),
    path('tarifas_flotas/<int:tarifa_id>/', DetalleTarifaFlotaView.as_view(), name='detalle_tarifa_flota'),
    path('tarifas_flotas/<int:tarifa_id>/eliminar/', EliminarTarifaFlotaView.as_view(), name='delete_tarifa'),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
