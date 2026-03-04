from django.urls import path

from ia import views

app_name = "ia"

urlpatterns = [
    path("chat/", views.chat_view, name="chat"),
    path("chat/send/", views.chat_send_view, name="chat_send"),
]
