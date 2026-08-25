from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, ForumThread


def chat_list(request):
    rooms = ChatRoom.objects.all()
    return render(request, "community/chats.html", {"rooms": rooms})


def chat_detail(request, pk):
    room = get_object_or_404(ChatRoom, pk=pk)
    messages = room.messages.select_related("author")
    return render(request, "community/chat_detail.html", {"room": room, "messages": messages})


def forum_list(request):
    threads = ForumThread.objects.select_related("author", "club")
    return render(request, "community/forum.html", {"threads": threads})
