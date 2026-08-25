from django.contrib import admin
from .models import Player, FavoritePlayer


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "club", "position", "matches_played", "goals", "assists", "rating")
    list_filter = ("club", "position")
    search_fields = ("full_name",)


@admin.register(FavoritePlayer)
class FavoritePlayerAdmin(admin.ModelAdmin):
    list_display = ("user", "player", "added_at")
