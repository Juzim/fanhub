from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),  # /i18n/setlang/ — переключение языка
    path("", include("apps.core.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("news/", include("apps.news.urls")),
    path("videos/", include("apps.videos.urls")),
    path("matches/", include("apps.matches.urls")),
    path("clubs/", include("apps.clubs.urls")),
    path("players/", include("apps.players.urls")),
    path("community/", include("apps.community.urls")),
    path("merch/", include("apps.merch.urls")),
    path("api/", include("apps.recommendations.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
