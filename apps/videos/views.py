from django.shortcuts import render, get_object_or_404
from .models import Video
from apps.recommendations.services import log_interaction


def video_list(request):
    category = request.GET.get("category")
    videos = Video.objects.select_related("club").all()
    if category:
        videos = videos.filter(category=category)
    return render(request, "videos/list.html", {"videos": videos, "categories": Video.CATEGORY_CHOICES})


def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk)
    if request.user.is_authenticated:
        log_interaction(request.user, "video_watch", video=video, club=video.club)
    return render(request, "videos/detail.html", {"video": video})
