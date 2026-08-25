from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from apps.clubs.models import Club


class RegisterForm(UserCreationForm):
    favorite_club = forms.ModelChoiceField(
        queryset=Club.objects.all(), label="Любимый клуб", empty_label="Выберите клуб",
    )

    class Meta:
        model = User
        fields = ("username", "email", "favorite_club", "password1", "password2")
