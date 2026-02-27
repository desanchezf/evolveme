from django.urls import path

from cardio.views import cardio_session_form_view

app_name = "cardio"

urlpatterns = [
    path("cardio-session/", cardio_session_form_view, name="cardio_session_form"),
]
