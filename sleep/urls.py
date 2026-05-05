from django.urls import path

from sleep.views import sleep_analyze_view, sleep_record_form_view

app_name = "sleep"

urlpatterns = [
    path("sleep/", sleep_record_form_view, name="sleep_form"),
    path("sleep/analyze/", sleep_analyze_view, name="sleep_analyze"),
]
