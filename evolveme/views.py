from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from evolveme.forms import MeasureForm
from evolveme.models import MeasureImage
from evolveme.services import extract_measure_data_from_image
from project.admin_context import with_admin_context


class IndexView(LoginRequiredMixin, TemplateView):
    """Vista para la página principal con tarjetas de acceso"""

    template_name = "evolveme/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(with_admin_context(self.request))
        return ctx


@login_required
def measure_form_view(request):
    """Vista para el formulario de medidas corporales.

    Soporta subida de imágenes de báscula para extracción automática
    de datos mediante LLM con visión (Ollama).
    """
    if request.method == "POST":
        image_files = request.FILES.getlist("measure_images")
        initial_data = request.POST.copy()

        # Si se suben imágenes, extraer datos con IA y prerellenar el form
        if image_files:
            extracted = extract_measure_data_from_image(image_files)
            for field, value in extracted.items():
                if field not in initial_data or not initial_data[field]:
                    initial_data[field] = value

        form = MeasureForm(initial_data, user=request.user)
        if form.is_valid():
            measure = form.save()
            # Guardar imágenes asociadas
            for f in image_files:
                f.seek(0)
                MeasureImage.objects.create(measure=measure, image=f)
            messages.success(request, "Medidas guardadas correctamente.")
            return redirect("evolveme:measure_form")
    else:
        form = MeasureForm(user=request.user)

    return render(request, "evolveme/measure_form.html", with_admin_context(request, {"form": form}))
