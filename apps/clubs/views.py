from django.shortcuts import render, get_object_or_404
from .models import Club, Standing


def club_list(request):
    standings = Standing.objects.select_related("club").order_by(
        "-wins", "club__name"
    )
    # сортировка по очкам (свойство, не поле БД) — считаем в Python
    standings = sorted(standings, key=lambda s: s.points, reverse=True)
    return render(request, "clubs/list.html", {"standings": standings})


def club_detail(request, pk):
    club = get_object_or_404(Club, pk=pk)
    return render(request, "clubs/detail.html", {"club": club})
