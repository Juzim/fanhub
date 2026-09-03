from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from apps.clubs.models import Standing, Club
from apps.matches.models import Match
from apps.news.models import Article
from apps.videos.models import Video
from apps.players.models import Player
from apps.accounts.models import User
from apps.recommendations.services import get_recommendations, get_analytics, get_recommendation_explanation


@login_required
def dashboard(request):
    user = request.user
    standings = sorted(
        Standing.objects.select_related("club").all(), key=lambda s: s.points, reverse=True
    )
    next_match = None
    if user.favorite_club:
        next_match = (
            Match.objects.filter(status="scheduled")
            .filter(models_q(user.favorite_club))
            .order_by("kickoff_at")
            .first()
        )
    recent_matches = Match.objects.filter(status="finished").order_by("-kickoff_at")[:4]
    top_fans = User.objects.order_by("-xp")[:5]
    recs = get_recommendations(user)
    explanation = get_recommendation_explanation(user)
    xp_in_level, xp_needed = user.level_progress

    return render(request, "dashboard/home.html", {
        "standings": standings,
        "next_match": next_match,
        "recent_matches": recent_matches,
        "top_fans": top_fans,
        "recs": recs,
        "explanation": explanation,
        "xp_in_level": xp_in_level,
        "xp_needed": xp_needed,
    })


def models_q(club):
    from django.db.models import Q
    return Q(home_club=club) | Q(away_club=club)


@login_required
def analytics(request):
    data = get_analytics(request.user)
    return render(request, "analytics/dashboard.html", data)


@login_required
def search(request):
    """Реальный поиск по новостям, видео, матчам, клубам и игрокам —
    поле в topbar ("Поиск матчей, новостей, игроков...") ведёт сюда.
    Простой icontains по нескольким моделям — для датасета такого размера
    (сотни, не миллионы записей) полнотекстовый индекс избыточен."""
    query = (request.GET.get("q") or "").strip()
    results = {"articles": [], "videos": [], "matches": [], "clubs": [], "players": []}

    if query:
        results["articles"] = Article.objects.select_related("club").filter(
            Q(title__icontains=query) | Q(summary__icontains=query)
        )[:8]
        results["videos"] = Video.objects.select_related("club").filter(
            title__icontains=query
        )[:8]
        results["clubs"] = Club.objects.filter(
            Q(name__icontains=query) | Q(city__icontains=query)
        )[:8]
        results["players"] = Player.objects.select_related("club").filter(
            full_name__icontains=query
        )[:8]
        results["matches"] = Match.objects.select_related("home_club", "away_club").filter(
            Q(home_club__name__icontains=query) | Q(away_club__name__icontains=query)
        )[:8]

    total = sum(len(v) for v in results.values())
    return render(request, "core/search.html", {"query": query, "results": results, "total": total})


@login_required
def notifications(request):
    """Список уведомлений. При открытии всё непрочитанное помечается
    прочитанным — так же ведут себя GitHub/Twitter и большинство приложений,
    проще и понятнее, чем ручные чекбоксы "отметить как прочитанное"."""
    items = list(request.user.notifications.all()[:40])
    unread_ids = [n.id for n in items if not n.is_read]
    if unread_ids:
        from .models import Notification
        Notification.objects.filter(id__in=unread_ids).update(is_read=True)
    return render(request, "core/notifications.html", {"notifications": items})
