from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.FanHubLoginView.as_view(), name="login"),
    path("logout/", views.FanHubLogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("profile/", views.profile, name="profile"),
    path("change-club/", views.change_favorite_club, name="change_club"),
]
