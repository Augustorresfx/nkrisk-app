from django.contrib.auth.models import Group

def permisos(request):
    user = request.user
    is_permiso_basico = False
    is_permiso_avanzado = False
    is_staff = False

    if user.is_authenticated:
        if user.groups.filter(name='PermisoBasico').exists():
            is_permiso_basico = True
        if user.groups.filter(name='PermisoAvanzado').exists():
            is_permiso_avanzado = True
        if user.is_staff:
            is_staff = True

    return {'is_permiso_basico': is_permiso_basico, 'is_permiso_avanzado': is_permiso_avanzado, 'is_staff': is_staff,}