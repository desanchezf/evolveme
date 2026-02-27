from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from cardio.forms import CardioSessionForm


@login_required
def cardio_session_form_view(request):
    """Vista para el formulario de sesiones de cardio"""
    if request.method == "POST":
        form = CardioSessionForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Sesión de cardio guardada correctamente.")
            return redirect("cardio:cardio_session_form")
    else:
        form = CardioSessionForm(user=request.user)

    return render(request, "cardio/cardio_session_form.html", {"form": form})
