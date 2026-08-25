from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .services import log_interaction, get_recommendations


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def track_interaction(request):
    """Лёгкий JSON-эндпоинт для фронтенда: лайк, клик по видео/новости и т.д.
    Не требует полного DRF CRUD — проекту нужен только этот один вызов."""
    interaction_type = request.data.get("type")
    club_id = request.data.get("club_id")
    if not interaction_type or not club_id:
        return Response({"error": "type и club_id обязательны"}, status=400)

    from apps.clubs.models import Club
    club = Club.objects.filter(pk=club_id).first()
    if not club:
        return Response({"error": "клуб не найден"}, status=404)

    log_interaction(request.user, interaction_type, club=club)
    return Response({"status": "ok"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_recommendations(request):
    recs = get_recommendations(request.user)
    data = {
        "top_clubs": [c.name for c in recs["top_clubs"]],
        "articles": [a.title for a in recs["articles"]],
        "videos": [v.title for v in recs["videos"]],
    }
    return Response(data)
