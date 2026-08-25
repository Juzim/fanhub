from django.contrib import admin
from .models import Match


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("home_club", "away_club", "kickoff_at", "status", "home_score", "away_score")
    list_filter = ("status", "tournament")
