from django.shortcuts import render, get_object_or_404
from .models import Article
from apps.clubs.models import Club
from apps.recommendations.services import log_interaction


def news_list(request):
    club_id = request.GET.get("club")
    articles = Article.objects.select_related("club").all()
    if club_id:
        articles = articles.filter(club_id=club_id)
    clubs = Club.objects.all()
    return render(request, "news/list.html", {"articles": articles, "clubs": clubs, "active_club": club_id})


def news_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.user.is_authenticated:
        log_interaction(request.user, "news_read", article=article, club=article.club)
    return render(request, "news/detail.html", {"article": article})
