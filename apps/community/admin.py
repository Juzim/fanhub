from django.contrib import admin
from .models import ChatRoom, ChatMessage, ForumThread, ForumPost

admin.site.register(ChatRoom)
admin.site.register(ChatMessage)
admin.site.register(ForumThread)
admin.site.register(ForumPost)
