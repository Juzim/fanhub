def favorite_club(request):
    """Делает любимый клуб пользователя доступным во всех шаблонах —
    используется в sidebar/topbar на каждой странице."""
    if request.user.is_authenticated:
        return {"favorite_club": request.user.favorite_club}
    return {"favorite_club": None}
