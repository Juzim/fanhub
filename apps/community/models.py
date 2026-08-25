from django.db import models
from apps.clubs.models import Club


class ChatRoom(models.Model):
    title = models.CharField("Название чата", max_length=150)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="chat_rooms", null=True, blank=True)

    class Meta:
        verbose_name = "Фан-чат"
        verbose_name_plural = "Фан-чаты"

    def __str__(self):
        return self.title

    @property
    def participants_count(self):
        return self.messages.values("author").distinct().count()


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="chat_messages")
    text = models.TextField("Сообщение", max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["created_at"]


class ForumThread(models.Model):
    title = models.CharField("Тема", max_length=200)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="forum_threads", null=True, blank=True)
    author = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="forum_threads")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Тема форума"
        verbose_name_plural = "Форум"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ForumPost(models.Model):
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name="posts")
    author = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="forum_posts")
    text = models.TextField("Ответ")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ответ на форуме"
        verbose_name_plural = "Ответы на форуме"
        ordering = ["created_at"]
