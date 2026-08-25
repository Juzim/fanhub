from django.urls import path
from . import views

app_name = "recommendations"

urlpatterns = [
    path("interactions/track/", views.track_interaction, name="track_interaction"),
    path("recommendations/mine/", views.my_recommendations, name="my_recommendations"),
]
