"""
Уведомления генерируются на реальных событиях платформы, а не по расписанию:
- новая новость/видео по клубу -> уведомление всем, у кого этот клуб любимый
- матч завершён -> уведомление фанатам обеих команд
Подключается в apps/core/apps.py::CoreConfig.ready().
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.news.models import Article
from apps.videos.models import Video
from apps.matches.models import Match
from .models import Notification


@receiver(post_save, sender=Article)
def notify_new_article(sender, instance, created, **kwargs):
    if not created or not instance.club_id:
        return
    Notification.objects.bulk_create([
        Notification(
            user=fan, notif_type="new_content",
            title=f"Новая новость: {instance.club.name}",
            body=instance.title,
            link="/news/%d/" % instance.pk,
        )
        for fan in instance.club.fans.all()
    ])


@receiver(post_save, sender=Video)
def notify_new_video(sender, instance, created, **kwargs):
    if not created or not instance.club_id:
        return
    Notification.objects.bulk_create([
        Notification(
            user=fan, notif_type="new_content",
            title=f"Новое видео: {instance.club.name}",
            body=instance.title,
            link="/videos/%d/" % instance.pk,
        )
        for fan in instance.club.fans.all()
    ])


@receiver(post_save, sender=Match)
def notify_match_result(sender, instance, created, **kwargs):
    if instance.status != "finished":
        return
    title = f"{instance.home_club.short_name} {instance.score_display} {instance.away_club.short_name}"
    fans = set(instance.home_club.fans.all()) | set(instance.away_club.fans.all())
    for fan in fans:
        # get_or_create по (user, тип, заголовок) — при повторном сохранении
        # того же результата дубль не создастся; если счёт поменяют — это
        # уже другой title, значит новое, справедливо новое уведомление.
        Notification.objects.get_or_create(
            user=fan, notif_type="match_result", title=title,
            defaults=dict(
                body=f"Матч {instance.kickoff_at:%d.%m.%Y} завершён.",
                link="/matches/",
            ),
        )
