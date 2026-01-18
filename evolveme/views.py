from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from evolveme.forms import MeasureForm


class IndexView(LoginRequiredMixin, TemplateView):
    """Vista para la página principal con tarjetas de acceso"""

    template_name = "evolveme/index.html"


@login_required
def measure_form_view(request):
    """Vista para el formulario de medidas corporales"""
    if request.method == "POST":
        form = MeasureForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Medidas guardadas correctamente.")
            return redirect("evolveme:measure_form")
    else:
        form = MeasureForm(user=request.user)

    return render(request, "evolveme/measure_form.html", {"form": form})
