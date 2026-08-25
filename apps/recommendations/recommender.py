"""
Ядро рекомендательной системы FAN-HUB.

Идея: у нас есть неявные взаимодействия пользователь -> клуб (Interaction, см. models.py).
Мы агрегируем их в матрицу "user x club = affinity_score" и обучаем на ней
Collaborative Filtering модель (KNNBasic из библиотеки Surprise, user-based,
метрика косинусного сходства). Модель находит пользователей с похожим
профилем интересов и предсказывает, насколько текущему пользователю может
быть интересен клуб, с которым он взаимодействовал мало или не взаимодействовал
вообще — это и есть "похожие пользователи" из ТЗ.

В проде обучение модели запускается периодически (cron / Celery beat),
а не на каждый запрос. Для дипломной демонстрации функция train_model()
достаточно быстрая, чтобы вызывать её синхронно.
"""
from collections import defaultdict

import pandas as pd
from django.db.models import Sum
from surprise import Dataset, KNNBasic, Reader

from apps.clubs.models import Club
from .models import Interaction


def build_affinity_dataframe():
    """user_id, club_id, affinity_score (сумма весов взаимодействий)."""
    rows = Interaction.objects.values("user_id", "club_id").annotate(score=Sum("weight"))
    df = pd.DataFrame(list(rows))
    return df


def train_model(min_interactions=5):
    """Обучает KNNBasic на текущих данных. Возвращает None, если данных мало
    (тогда используется fallback на простую популярность/собственные интересы)."""
    df = build_affinity_dataframe()
    if df.empty or len(df) < min_interactions:
        return None, df

    # Surprise ожидает рейтинги в фиксированной шкале — нормализуем 0..10
    max_score = df["score"].max() or 1
    df["rating"] = (df["score"] / max_score * 10).clip(upper=10)

    reader = Reader(rating_scale=(0, 10))
    data = Dataset.load_from_df(df[["user_id", "club_id", "rating"]], reader)
    trainset = data.build_full_trainset()

    algo = KNNBasic(sim_options={"name": "cosine", "user_based": True}, verbose=False)
    algo.fit(trainset)
    return algo, df


def get_top_clubs_for_user(user, n=3):
    """Возвращает до n клубов, отсортированных по релевантности для пользователя:
    любимый клуб всегда первый, дальше — предсказания CF / собственная история."""
    algo, df = train_model()
    all_clubs = list(Club.objects.all())
    club_by_id = {c.id: c for c in all_clubs}

    scores = defaultdict(float)
    if user.favorite_club_id:
        scores[user.favorite_club_id] += 100  # явный сигнал важнее всего

    if algo is not None and user.id in df["user_id"].values:
        for club in all_clubs:
            try:
                pred = algo.predict(user.id, club.id)
                scores[club.id] += pred.est
            except Exception:
                continue
    else:
        # Fallback пока данных мало: собственная история взаимодействий пользователя
        own = (
            Interaction.objects.filter(user=user)
            .values("club_id")
            .annotate(total=Sum("weight"))
        )
        for row in own:
            scores[row["club_id"]] += row["total"]

    ranked_ids = sorted(scores, key=scores.get, reverse=True)
    ranked_clubs = [club_by_id[cid] for cid in ranked_ids if cid in club_by_id]
    if not ranked_clubs and user.favorite_club:
        ranked_clubs = [user.favorite_club]
    return ranked_clubs[:n] or all_clubs[:n]


def get_interest_breakdown(user):
    """Проценты интереса по клубам — используется на странице Analytics."""
    rows = (
        Interaction.objects.filter(user=user)
        .values("club__name")
        .annotate(total=Sum("weight"))
        .order_by("-total")
    )
    total_all = sum(r["total"] for r in rows) or 1
    breakdown = [
        {"club": r["club__name"], "percent": round(r["total"] / total_all * 100, 1)}
        for r in rows
    ]
    return breakdown


def get_similar_fans_count(user, k=5):
    """Сколько пользователей CF-модель считает 'похожими' на текущего —
    берётся напрямую из обученного KNN (ближайшие соседи в пространстве
    предпочтений), используется только для объяснения рекомендаций."""
    algo, df = train_model()
    if algo is None or df.empty or user.id not in df["user_id"].values:
        return 0
    try:
        inner_uid = algo.trainset.to_inner_uid(user.id)
        neighbors = algo.get_neighbors(inner_uid, k=k)
        return len(neighbors)
    except Exception:
        return 0


def generate_explanation(user):
    """Небольшой бесплатный AI-модуль: превращает уже посчитанные данные
    рекомендательной системы (интересы пользователя + похожие болельщики
    из CF-модели) в понятное человеку объяснение "почему вам это показано".

    Важно: это НЕ вызов внешней LLM — модуль детерминированный, работает
    полностью локально поверх данных, которые Interaction/recommender.py
    и так уже посчитали. Логика простая (шаблонизация по данным), но она
    честно объясняет именно то, что реально происходит внутри CF-модели,
    а не выдаёт красивые, но бессмысленные фразы."""
    breakdown = get_interest_breakdown(user)

    if not breakdown:
        return {
            "mode": "cold_start",
            "headline": "Пока изучаем ваши интересы",
            "detail": (
                "Прочитайте пару новостей или посмотрите видео — и здесь появится "
                "объяснение того, почему мы рекомендуем именно этот контент."
            ),
        }

    top = breakdown[0]
    club_name, percent = top["club"], top["percent"]
    similar_fans = get_similar_fans_count(user)

    if similar_fans > 0:
        detail = (
            f"{percent}% вашей активности связано с клубом «{club_name}» — это самый "
            f"сильный сигнал. Дополнительно мы сравнили ваш профиль интересов с "
            f"{similar_fans} похожими болельщиками через коллаборативную фильтрацию "
            f"(KNN, косинусное сходство) и подмешали их предпочтения в подборку — "
            f"так рекомендации учитывают не только вашу историю, но и то, что "
            f"обычно смотрят люди со схожими вкусами."
        )
        mode = "collaborative"
    else:
        detail = (
            f"{percent}% вашей активности связано с клубом «{club_name}» — пока "
            f"рекомендации строятся только на вашей собственной истории. Как только "
            f"в системе накопится больше данных по другим пользователям, подключится "
            f"сравнение с похожими болельщиками (коллаборативная фильтрация)."
        )
        mode = "own_history"

    return {
        "mode": mode,
        "headline": "Почему вам это показано",
        "detail": detail,
        "top_club": club_name,
        "percent": percent,
        "similar_fans": similar_fans,
    }
