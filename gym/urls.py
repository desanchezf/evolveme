from django.urls import path

from gym.views import (
    cardio_analyze_view,
    cardio_session_form_view,
    musculation_record_form_view,
    routine_form_view,
    session_analyze_view,
    session_form_view,
    training_analyze_view,
    training_session_form_view,
)

app_name = "gym"

urlpatterns = [
    path("routine/", routine_form_view, name="routine_form"),
    path("session/", session_form_view, name="session_form"),
    path("session/analyze/", session_analyze_view, name="session_analyze"),
    path("training-session/", training_session_form_view, name="training_session_form"),
    path("training-session/analyze/", training_analyze_view, name="training_analyze"),
    path("cardio-session/", cardio_session_form_view, name="cardio_session_form"),
    path("cardio-session/analyze/", cardio_analyze_view, name="cardio_analyze"),
    path("musculation-record/", musculation_record_form_view, name="musculation_record_form"),
]
