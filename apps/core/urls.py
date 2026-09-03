from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("analytics/", views.analytics, name="analytics"),
    path("search/", views.search, name="search"),
    path("notifications/", views.notifications, name="notifications"),
]
