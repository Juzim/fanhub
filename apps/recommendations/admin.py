from django.contrib import admin
from .models import Interaction


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ("user", "interaction_type", "club", "weight", "created_at")
    list_filter = ("interaction_type", "club")
    date_hierarchy = "created_at"
