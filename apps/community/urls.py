from django.urls import path
from . import views

app_name = "community"

urlpatterns = [
    path("chats/", views.chat_list, name="chat_list"),
    path("chats/<int:pk>/", views.chat_detail, name="chat_detail"),
    path("forum/", views.forum_list, name="forum_list"),
]
