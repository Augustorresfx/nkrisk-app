from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.contrib.auth import views as auth_views
from .views import HomeView, InicioView, FlotasView, EliminarMovimientoView, ExportarMovimientoView, ClientesView, DetalleClienteView, EliminarClienteView, DetalleFlotaView, EliminarFlotaView ,DetalleTarifaFlotaView, EliminarTarifaFlotaView,TarifasFlotasView, VencimientosView, CobranzasView, SignInView, SignOutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', SignInView.as_view(), name="login"),
    path('logout/', SignOutView.as_view(), name="logout"),
    path('', HomeView.as_view(), name='home'),
    path('inicio/', InicioView.as_view(), name='inicio'),
    path('vencimientos/', VencimientosView.as_view(), name='vencimientos'),
    path('cobranzas/', CobranzasView.as_view(), name='cobranzas'),
    path('clientes/', ClientesView.as_view(), name='clientes'),
    path('clientes/<int:cliente_id>/', DetalleClienteView.as_view(), name='detalle_cliente'),
    path('clientes/<int:cliente_id>/eliminar/', EliminarClienteView.as_view(), name='delete_cliente'),
    path('movimientos/<int:flota_id>/<int:movimiento_id>/eliminar/', EliminarMovimientoView.as_view(), name='delete_movimiento'),
    path('movimientos/<int:flota_id>/<int:movimiento_id>/exportar/', ExportarMovimientoView.as_view(), name='exportar_movimiento'),
    path('flotas/', FlotasView.as_view(), name='flotas'),
    path('flotas/', FlotasView.as_view(), name='flotas'),
    path('flotas/<int:flota_id>/eliminar/', EliminarFlotaView.as_view(), name='delete_flota'),
    path('flotas/<int:flota_id>/', DetalleFlotaView.as_view(), name='detalle_flota'),
    path('tarifas_flotas/', TarifasFlotasView.as_view(), name='tarifas_flotas'),
    path('tarifas_flotas/<int:tarifa_id>/', DetalleTarifaFlotaView.as_view(), name='detalle_tarifa_flota'),
    path('tarifas_flotas/<int:tarifa_id>/eliminar/', EliminarTarifaFlotaView.as_view(), name='delete_tarifa'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
