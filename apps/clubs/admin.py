from django.contrib import admin
from .models import Club, Standing


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "founded_year", "primary_color")
    search_fields = ("name", "city")


@admin.register(Standing)
class StandingAdmin(admin.ModelAdmin):
    list_display = ("club", "season", "played", "wins", "draws", "losses", "points")
    list_filter = ("season",)
