from django.urls import path

from gym.views import (
    cardio_session_form_view,
    musculation_record_form_view,
    training_session_form_view,
)

app_name = "gym"

urlpatterns = [
    path("cardio-session/", cardio_session_form_view, name="cardio_session_form"),
    path(
        "musculation-record/",
        musculation_record_form_view,
        name="musculation_record_form",
    ),
    path("training-session/", training_session_form_view, name="training_session_form"),
]
