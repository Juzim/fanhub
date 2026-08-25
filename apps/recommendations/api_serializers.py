from rest_framework import serializers
from .models import Interaction


class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = ["id", "interaction_type", "club", "article", "video", "match", "created_at"]
        read_only_fields = ["id", "created_at"]
