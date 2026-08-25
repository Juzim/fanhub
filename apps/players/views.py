from django.shortcuts import render, get_object_or_404
from .models import Player


def player_list(request):
    club_id = request.GET.get("club")
    players = Player.objects.select_related("club").all()
    if club_id:
        players = players.filter(club_id=club_id)
    return render(request, "players/list.html", {"players": players})


def player_detail(request, pk):
    player = get_object_or_404(Player, pk=pk)
    return render(request, "players/detail.html", {"player": player})
