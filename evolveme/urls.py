from django.urls import path

from evolveme.views import (
    IndexView,
    dashboard_view,
    measure_analyze_view,
    measure_form_view,
    profile_form_view,
)

app_name = "evolveme"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("profile/", profile_form_view, name="profile_form"),
    path("measure/", measure_form_view, name="measure_form"),
    path("measure/analyze/", measure_analyze_view, name="measure_analyze"),
    path("milestones/", dashboard_view, name="dashboard"),
]
