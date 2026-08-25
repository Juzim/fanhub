from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import RegisterForm
from .models import User
from apps.clubs.models import Club


class FanHubLoginView(LoginView):
    template_name = "accounts/login.html"


class FanHubLogoutView(LogoutView):
    next_page = "accounts:login"


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        if self.object.favorite_club:
            from apps.recommendations.services import log_interaction
            log_interaction(self.object, "favorite_club_set", club=self.object.favorite_club)
        return response


@login_required
def profile(request):
    user = request.user
    xp_in_level, xp_needed = user.level_progress
    return render(request, "accounts/profile.html", {
        "xp_in_level": xp_in_level,
        "xp_needed": xp_needed,
        "clubs": Club.objects.all(),
    })


@login_required
def change_favorite_club(request):
    """AJAX/POST-эндпоинт: смена клуба без перезагрузки всей страницы (Шаг 8 демо-сценария)."""
    if request.method == "POST":
        club = get_object_or_404(Club, pk=request.POST.get("club_id"))
        request.user.change_favorite_club(club)
    return redirect(request.POST.get("next") or "core:dashboard")
