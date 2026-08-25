from django.shortcuts import render
from django.utils import timezone
from .models import Match


def match_list(request):
    upcoming = Match.objects.filter(kickoff_at__gte=timezone.now()).exclude(status="finished")
    finished = Match.objects.filter(status="finished").order_by("-kickoff_at")
    return render(request, "matches/list.html", {"upcoming": upcoming, "finished": finished})
