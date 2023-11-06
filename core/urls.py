from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.contrib.auth import views as auth_views
from .views import HomeView, FlotasView, DetalleFlotaView, VehiculosView, VencimientosView, CobranzasView, SignInView, SignOutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', SignInView.as_view(), name="login"),
    path('logout/', SignOutView.as_view(), name="logout"),
    path('', HomeView.as_view(), name='home'),
    path('vencimientos/', VencimientosView.as_view(), name='vencimientos'),
    path('cobranzas/', CobranzasView.as_view(), name='cobranzas'),
    path('flotas/', FlotasView.as_view(), name='flotas'),
    path('vehiculos/', VehiculosView.as_view(), name='vehiculos'),
    path('flotas/<int:flota_id>/', DetalleFlotaView.as_view(), name='detalle_flota'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
