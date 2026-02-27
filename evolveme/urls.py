from django.urls import path

from evolveme.views import IndexView, measure_form_view

app_name = "evolveme"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("measure/", measure_form_view, name="measure_form"),
]
