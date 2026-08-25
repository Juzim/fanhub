"""
Сервисный слой поверх recommender.py:
- логирование взаимодействий пользователя (log_interaction)
- получение готовой подборки рекомендаций с кэшированием в Redis
  (чтобы не пересчитывать CF-модель на каждый запрос дашборда)
"""
from django.core.cache import cache
from django.conf import settings

from apps.news.models import Article
from apps.videos.models import Video
from apps.matches.models import Match
from apps.merch.models import Product
from .models import Interaction, INTERACTION_WEIGHTS
from .recommender import get_top_clubs_for_user, get_interest_breakdown, generate_explanation


def _cache_key(user):
    return f"recs:user:{user.id}"


def _explain_cache_key(user):
    return f"recs:explain:{user.id}"


def invalidate_recommendations_cache(user):
    cache.delete(_cache_key(user))
    cache.delete(_explain_cache_key(user))


def log_interaction(user, interaction_type, club=None, article=None, video=None, match=None):
    club = club or (article.club if article else None) or (video.club if video else None)
    if club is None:
        return None
    interaction = Interaction.objects.create(
        user=user,
        interaction_type=interaction_type,
        club=club,
        article=article,
        video=video,
        match=match,
        weight=INTERACTION_WEIGHTS.get(interaction_type, 1.0),
    )
    # Начисляем реальный XP за действие — единая точка входа для всей
    # геймификации: любое взаимодействие, залогированное здесь, сразу
    # отражается на уровне пользователя, без ручных/захардкоженных чисел.
    from apps.accounts.models import XP_PER_WEIGHT_POINT
    user.add_xp(round(interaction.weight * XP_PER_WEIGHT_POINT))
    invalidate_recommendations_cache(user)
    return interaction


def get_recommendations(user, limit_per_type=2):
    """Собирает персональную ленту: топ-клубы пользователя (через CF) ->
    свежий контент по этим клубам, отдельно новости/видео/матчи/мерч."""
    cached = cache.get(_cache_key(user))
    if cached is not None:
        return cached

    top_clubs = get_top_clubs_for_user(user, n=3)
    club_ids = [c.id for c in top_clubs] or None

    recs = {
        "top_clubs": top_clubs,
        "articles": list(
            Article.objects.filter(club_id__in=club_ids).order_by("-published_at")[:limit_per_type]
        ) if club_ids else [],
        "videos": list(
            Video.objects.filter(club_id__in=club_ids).order_by("-published_at")[:limit_per_type]
        ) if club_ids else [],
        "matches": list(
            Match.objects.filter(
                home_club_id__in=club_ids
            ).order_by("kickoff_at")[:limit_per_type]
        ) if club_ids else [],
        "products": list(
            Product.objects.filter(club_id__in=club_ids, in_stock=True)[:limit_per_type]
        ) if club_ids else [],
    }
    cache.set(_cache_key(user), recs, settings.RECOMMENDATIONS_CACHE_TTL)
    return recs


def get_analytics(user):
    return {
        "interest_breakdown": get_interest_breakdown(user),
        "videos_watched": Interaction.objects.filter(user=user, interaction_type="video_watch").count(),
        "news_read": Interaction.objects.filter(user=user, interaction_type="news_read").count(),
        "total_interactions": Interaction.objects.filter(user=user).count(),
        "explanation": get_recommendation_explanation(user),
    }


def get_recommendation_explanation(user):
    """Кэшированная обёртка над бесплатным AI-модулем объяснения рекомендаций
    (см. recommender.generate_explanation) — не пересчитываем KNN-соседей
    на каждый рендер дашборда/аналитики, только когда меняются данные."""
    cached = cache.get(_explain_cache_key(user))
    if cached is not None:
        return cached
    explanation = generate_explanation(user)
    cache.set(_explain_cache_key(user), explanation, settings.RECOMMENDATIONS_CACHE_TTL)
    return explanation
