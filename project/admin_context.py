"""
Helper para inyectar el contexto del admin site en vistas públicas
que extienden admin/base.html (necesario para que Jazzmin renderice
el sidebar y el top menu correctamente).
"""
from django.contrib.admin import site as admin_site


def with_admin_context(request: object, extra: dict | None = None) -> dict:
    """
    Devuelve el contexto base del admin site más cualquier dato extra.
    Usar en lugar de pasar un dict vacío a render() en vistas públicas.
    """
    ctx = admin_site.each_context(request)
    if extra:
        ctx.update(extra)
    return ctx
