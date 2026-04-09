from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.datastructures import MultiValueDict

from cardio.forms import CardioSessionForm
from cardio.services import extract_cardio_data_from_image
from project.admin_context import with_admin_context


@login_required
def cardio_session_form_view(request):
    """Vista para el formulario de sesiones de cardio. Admin puede elegir usuario; usuario normal solo su cuenta."""
    is_staff = getattr(request.user, "is_staff", False)

    if request.method == "POST":
        post_data = request.POST.copy()
        image_files = request.FILES.getlist("workout_images")
        if image_files:
            extracted = extract_cardio_data_from_image(image_files)
            for key, value in extracted.items():
                if key not in post_data or not str(post_data.get(key)).strip():
                    if hasattr(value, "total_seconds"):
                        s = int(value.total_seconds())
                        post_data[key] = f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"
                    else:
                        post_data[key] = value

        files_for_form = MultiValueDict()
        for key in request.FILES:
            files_for_form.setlist(key, request.FILES.getlist(key))
        if image_files:
            files_for_form.setlist("workout_image", [image_files[0]])

        form = CardioSessionForm(
            post_data,
            files_for_form,
            user=request.user,
            is_staff=is_staff,
        )
        if form.is_valid():
            instance = form.save(commit=False)
            if not is_staff:
                instance.user = request.user
            instance.save()
            messages.success(request, "Sesión de cardio guardada correctamente.")
            return redirect("cardio:cardio_session_form")
    else:
        form = CardioSessionForm(user=request.user, is_staff=is_staff)

    return render(request, "cardio/cardio_session_form.html", with_admin_context(request, {"form": form}))
