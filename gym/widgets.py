from django import forms
from django.utils.safestring import mark_safe

from gym.enums import ExerciseTypesChoices, IntensityTechniqueChoices


class ExerciseTypesCheckboxWidget(forms.Widget):
    """Widget personalizado para seleccionar tipos de ejercicios con checkboxes"""

    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.choices = ExerciseTypesChoices.choices()

    def format_value(self, value):
        """Convierte el valor JSON a una lista para los checkboxes"""
        if value is None:
            return []
        # Si ya es una lista, devolverla directamente
        if isinstance(value, list):
            return value
        # Si es un string, intentar parsearlo como JSON
        if isinstance(value, str):
            # Si es un string vacío, devolver lista vacía
            if not value.strip():
                return []
            try:
                import json
                parsed = json.loads(value)
                # Asegurar que sea una lista
                if isinstance(parsed, list):
                    return parsed
                return []
            except (json.JSONDecodeError, ValueError, TypeError):
                return []
        # Para cualquier otro tipo, devolver lista vacía
        return []

    def value_from_datadict(self, data, files, name):
        """Extrae los valores seleccionados del formulario y los convierte a lista"""
        # Primero intentar obtener el valor del campo oculto (JSON serializado)
        if name in data:
            value = data[name]
            if value:
                try:
                    import json
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return parsed
                except (json.JSONDecodeError, ValueError, TypeError):
                    pass

        # Fallback: obtener valores de los checkboxes individuales
        selected = []
        for choice_value, _ in self.choices:
            checkbox_name = f"{name}_{choice_value}"
            if checkbox_name in data:
                selected.append(choice_value)
        # Devolver lista vacía si no hay selección, no None
        return selected if selected else []

    def render(self, name, value, attrs=None, renderer=None):
        """Renderiza el widget con checkboxes"""
        if attrs is None:
            attrs = {}
        attrs.setdefault("id", f"id_{name}")

        selected = self.format_value(value)

        # Serializar la lista seleccionada a JSON para el campo oculto
        import json
        json_value = json.dumps(selected) if selected else "[]"

        html = []
        # Campo oculto con el valor JSON serializado
        html.append(
            f'<input type="hidden" name="{name}" id="id_{name}" value=\'{json_value}\'>'
        )

        html.append(
            '<div class="exercise-types-checkboxes" '
            'style="display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 1rem;">'
        )

        for choice_value, choice_label in self.choices:
            checkbox_id = f"{name}_{choice_value}"
            checked = "checked" if choice_value in selected else ""
            html.append(
                f'<div class="form-check" style="min-width: 150px;">'
                f'<input type="checkbox" '
                f'name="{checkbox_id}" '
                f'id="{checkbox_id}" '
                f'value="{choice_value}" '
                f'{checked} '
                f'class="form-check-input exercise-type-checkbox" '
                f'data-field-name="{name}">'
                f'<label class="form-check-label" for="{checkbox_id}" '
                f'style="margin-left: 0.5rem;">'
                f"{choice_label}"
                f"</label>"
                f"</div>"
            )

        html.append("</div>")

        # JavaScript para actualizar el campo oculto cuando cambien los checkboxes
        html.append(
            f'<script>'
            f'(function() {{'
            f'  const hiddenField = document.getElementById("id_{name}");'
            f'  const checkboxes = document.querySelectorAll(\'input[data-field-name="{name}"][type="checkbox"]\');'
            f'  '
            f'  function updateHiddenField() {{'
            f'    const selected = [];'
            f'    checkboxes.forEach(function(checkbox) {{'
            f'      if (checkbox.checked) {{'
            f'        selected.push(checkbox.value);'
            f'      }}'
            f'    }});'
            f'    hiddenField.value = JSON.stringify(selected);'
            f'  }}'
            f'  '
            f'  checkboxes.forEach(function(checkbox) {{'
            f'    checkbox.addEventListener("change", updateHiddenField);'
            f'  }});'
            f'}})();'
            f'</script>'
        )

        return mark_safe("".join(html))


class IntensityTechniquesCheckboxWidget(ExerciseTypesCheckboxWidget):
    """Widget para seleccionar técnicas de intensidad con checkboxes."""

    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.choices = IntensityTechniqueChoices.choices()
