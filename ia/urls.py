from django.urls import path

from ia import views

app_name = "ia"

urlpatterns = [
    path("chat/", views.chat_view, name="chat"),
    path("chat/send/", views.chat_send_view, name="chat_send"),
    path("chat/save-routine/", views.chat_save_routine_view, name="chat_save_routine"),
    path("chat/clear/", views.chat_clear_view, name="chat_clear"),
    path(
        "admin/ollama-model/<int:pk>/pull/",
        views.ollama_model_pull_view,
        name="ollama_model_pull",
    ),
    path(
        "admin/ollama-model/<int:pk>/delete/",
        views.ollama_model_delete_view,
        name="ollama_model_delete",
    ),
    path(
        "admin/ollama-model/<int:pk>/pull/start/",
        views.ollama_model_pull_start_view,
        name="ollama_model_pull_start",
    ),
    path(
        "admin/ollama-model/<int:pk>/pull/progress/",
        views.ollama_model_pull_progress_view,
        name="ollama_model_pull_progress",
    ),
]
