from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ia.services import is_model_downloaded
from sleep.forms import SleepRecordForm
from project.admin_context import with_admin_context


@login_required
def sleep_record_form_view(request):
    is_staff = getattr(request.user, "is_staff", False)

    if request.method == "POST":
        form = SleepRecordForm(request.POST, user=request.user)
        if form.is_valid():
            instance = form.save(commit=False)
            if not is_staff:
                instance.user = request.user
            instance.save()
            messages.success(request, "Registro de sueño guardado correctamente.")
            return redirect("sleep:sleep_form")
    else:
        form = SleepRecordForm(user=request.user)

    return render(request, "sleep/sleep_form.html", with_admin_context(request, {
        "form": form,
        "vision_available": is_model_downloaded("llama3.2-vision:11b"),
    }))


@login_required
def sleep_analyze_view(request):
    """AJAX: analiza imágenes de sueño y devuelve campos extraídos."""
    from django.http import JsonResponse
    from sleep.services import extract_sleep_data_from_image

    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)
    image_files = request.FILES.getlist("sleep_images")
    if not image_files:
        return JsonResponse({"error": "No se recibieron imágenes."}, status=400)

    extracted = extract_sleep_data_from_image(image_files)
    if not extracted:
        return JsonResponse({"error": "No se pudieron extraer datos."}, status=422)

    result = {}
    for k, v in extracted.items():
        if hasattr(v, "total_seconds"):
            s = int(v.total_seconds())
            result[k] = f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"
        elif not isinstance(v, (str, int, float, bool, type(None))):
            result[k] = str(v)
        else:
            result[k] = v
    return JsonResponse({"data": result})
