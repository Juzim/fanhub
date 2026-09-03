def favorite_club(request):
    """Делает любимый клуб пользователя доступным во всех шаблонах —
    используется в sidebar/topbar на каждой странице."""
    if request.user.is_authenticated:
        return {"favorite_club": request.user.favorite_club}
    return {"favorite_club": None}


def cart_count(request):
    """Количество товаров в корзине — для иконки корзины в topbar на любой странице."""
    if not request.user.is_authenticated:
        return {"cart_items_count": 0}
    from apps.merch.cart import Cart
    return {"cart_items_count": len(Cart(request))}


def notifications_unread_count(request):
    """Счётчик непрочитанных уведомлений — для бейджа на колокольчике в topbar."""
    if not request.user.is_authenticated:
        return {"notifications_unread_count": 0}
    return {"notifications_unread_count": request.user.notifications.filter(is_read=False).count()}
