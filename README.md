# FAN-HUB

Интеллектуальная мультимедийная рекомендательная веб-платформа для болельщиков
Казахстанской Премьер-лиги. Django + PostgreSQL + Redis + Collaborative Filtering.

## Стек

- **Backend**: Django 5, Django Templates (server-rendered), пара JSON-эндпоинтов через DRF
- **БД**: PostgreSQL
- **Кэш / очередь данных для рекомендаций**: Redis (django-redis)
- **Рекомендательная система**: pandas + scikit-surprise (KNNBasic, collaborative filtering)
- **Frontend**: Django Templates + чистый CSS (design tokens в `static/css/theme.css`)

## Бесплатный хостинг (Render.com) — открыть по ссылке из любого места

Не требует Docker на компьютере — Render соберёт образ из `Dockerfile` сам.

### 1. Загрузите проект на GitHub
Render деплоит из Git-репозитория, не из zip-файла.
1. Зарегистрируйтесь на https://github.com, если ещё нет аккаунта.
2. Создайте новый пустой репозиторий (Settings → New repository), например `fanhub`.
3. В папке проекта:
   ```bash
   git init
   git add .
   git commit -m "FAN-HUB"
   git branch -M main
   git remote add origin https://github.com/<ваш-логин>/fanhub.git
   git push -u origin main
   ```

### 2. Создайте бесплатную PostgreSQL на Render
1. Зарегистрируйтесь на https://render.com (можно через GitHub-аккаунт).
2. Dashboard → New → PostgreSQL → Free план → Create Database.
3. Дождитесь статуса "Available", откройте базу — понадобятся поля **Hostname**, **Port**, **Database**, **Username**, **Password** (не сама строка подключения, а отдельные поля — они пригодятся на шаге 4).

### 3. Создайте Web Service
1. Dashboard → New → Web Service → Build and deploy from a Git repository → выберите репозиторий `fanhub`.
2. Runtime: **Docker** (Render сам найдёт `Dockerfile` в корне).
3. Instance Type: **Free**.

### 4. Задайте переменные окружения (Environment)
В настройках сервиса → Environment → добавьте:

| Ключ | Значение |
|---|---|
| `DEBUG` | `False` |
| `SECRET_KEY` | любая длинная случайная строка (например, сгенерируйте на https://djecrety.ir) |
| `ALLOWED_HOSTS` | `<имя-сервиса>.onrender.com` (Render покажет точный адрес после первого деплоя) |
| `CSRF_TRUSTED_ORIGINS` | `https://<имя-сервиса>.onrender.com` |
| `DB_NAME` | Database (из шага 2) |
| `DB_USER` | Username (из шага 2) |
| `DB_PASSWORD` | Password (из шага 2) |
| `DB_HOST` | Hostname (из шага 2) |
| `DB_PORT` | `5432` |
| `SEED_DEMO_DATA` | `true` (один раз, чтобы наполнить БД реальными данными КПЛ) |
| `DJANGO_SUPERUSER_USERNAME` | например `admin` |
| `DJANGO_SUPERUSER_EMAIL` | ваш email |
| `DJANGO_SUPERUSER_PASSWORD` | свой пароль |

`REDIS_URL` не указываем — на бесплатном тарифе Redis нет, и `settings.py` автоматически переключится на кэш в памяти процесса (сайт работает точно так же, кэш просто не переживает перезапуск).

### 5. Deploy
Нажмите **Create Web Service** (или **Manual Deploy** → **Deploy latest commit**, если сервис уже создан). Первая сборка занимает 5–10 минут — Render выполнит `Dockerfile`, `entrypoint.sh` сам применит миграции и заполнит демо-данными. Готовый адрес появится наверху страницы сервиса: `https://<имя-сервиса>.onrender.com`.

**Особенность бесплатного тарифа**: сервис "засыпает" после 15 минут без запросов и первый запрос после этого грузится ~30–50 секунд — это нормально, не ошибка. Free PostgreSQL на Render также ограничена по времени жизни (обычно 30 дней) — для показа проекта на защите этого достаточно, но не рассчитывайте на неё как на постоянное хранилище.

После первого деплоя проверьте `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` — Render покажет реальный адрес вида `fanhub-xyz12.onrender.com` (с случайным суффиксом, если имя занято), обновите переменные под него, если отличается от того, что вы указали заранее.

## Быстрый старт (Docker Compose — рекомендуется для локальной разработки)

Самый быстрый способ поднять проект целиком (PostgreSQL + Redis + Django)
одной командой, без ручной установки зависимостей на хост:

```bash
cp .env.docker.example .env.docker   # при желании поменяйте пароли/логин админа
docker compose up --build
```

Что произойдёт автоматически (см. `entrypoint.sh`):
1. Контейнер `web` дождётся готовности PostgreSQL.
2. Выполнится `migrate`.
3. Если `SEED_DEMO_DATA=true` в `.env.docker` — наполнит БД клубами КПЛ,
   матчами, новостями, видео и демо-пользователем `nurbek_demo` / `demo12345`.
4. Если заданы `DJANGO_SUPERUSER_*` — создастся суперпользователь для `/admin/`.
5. Запустится dev-сервер Django на `http://127.0.0.1:8000/`.

Полезные команды:

```bash
docker compose logs -f web          # логи Django
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py seed_demo_data
docker compose down                 # остановить
docker compose down -v              # остановить и стереть тома (БД/Redis/медиа)
```

Код проекта примонтирован как volume (`.:/app`) — изменения в файлах на хосте
сразу подхватываются dev-сервером без пересборки образа. Если поменяли
`requirements.txt` — нужно `docker compose up --build`.

## Быстрый старт (без Docker, вручную)

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # и подставьте свои данные PostgreSQL/Redis

# Поднимите PostgreSQL и Redis локально (или через docker-compose, если добавите)
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo_data    # наполняет БД клубами КПЛ, матчами, новостями
                                    # и создаёт демо-пользователя nurbek_demo/demo12345
python manage.py runserver
```

Откройте http://127.0.0.1:8000/accounts/login/ и войдите под `nurbek_demo` / `demo12345`
(любимый клуб — ФК Актобе) — либо зарегистрируйте нового пользователя.

## Структура проекта

```
config/                 настройки Django, корневые urls
apps/
  accounts/              кастомный User (favorite_club, XP, level — геймификация)
  clubs/                 Club, Standing (турнирная таблица)
  players/               Player, FavoritePlayer
  matches/                Match
  news/                   Article
  videos/                 Video (YouTube embed)
  merch/                  Product
  community/              ChatRoom/ChatMessage, ForumThread/ForumPost
  recommendations/        Interaction (лог действий) + recommender.py (CF-модель)
                           + services.py (кэш в Redis, сборка ленты рекомендаций)
  core/                   dashboard, analytics, seed_demo_data
templates/                Django-шаблоны (base.html + партиалы + страницы)
docker-compose.yml         PostgreSQL + Redis + Django одной командой
Dockerfile / entrypoint.sh образ и логика запуска (migrate → seed → runserver)
static/css/theme.css      единая цветовая/типографическая система интерфейса
```

## Как работает рекомендательная система (кратко)

1. Каждое действие пользователя (прочитана новость, просмотрено видео, лайк,
   смена любимого клуба) сохраняется как `Interaction` с весом
   (см. `apps/recommendations/models.py::INTERACTION_WEIGHTS`).
2. `recommender.py` агрегирует эти взаимодействия в матрицу
   `пользователь × клуб = степень интереса` и обучает на ней
   `KNNBasic` (collaborative filtering, user-based, косинусное сходство) —
   находит пользователей с похожими интересами.
3. `services.get_recommendations()` берёт топ-клубы пользователя (свои +
   предсказанные моделью) и подбирает под них свежие новости, видео,
   ближайшие матчи и мерч. Результат кэшируется в Redis на 15 минут
   (`RECOMMENDATIONS_CACHE_TTL` в settings.py) и сбрасывается при новом
   взаимодействии или смене клуба (`invalidate_recommendations_cache`).
4. При смене любимого клуба (`User.change_favorite_club`) кэш сбрасывается
   сразу — дашборд перестраивается на следующей загрузке. Это и есть
   демо-сценарий из ТЗ: Актобе → Кайрат.

Подробнее — в `docs/architecture.md`.

## Реальные данные КПЛ

`seed_demo_data` больше не генерирует случайные числа — турнирная таблица,
результаты последних матчей, расписание ближайшего тура и часть новостей
взяты с официального сайта КПЛ (kffleague.kz) и спортивных СМИ (sports.kz,
vesti.kz, kz.kursiv.media) на момент написания (август 2026, 22-й тур).
Ссылки на источники сохранены в `Article.source_url` и `Video.external_url`.

Поскольку сезон продолжается, эти цифры со временем устареют. Чтобы
актуализировать: откройте `apps/core/management/commands/seed_demo_data.py`,
обновите списки `REAL_STANDINGS` / `REAL_FINISHED_MATCHES` /
`REAL_UPCOMING_MATCHES` / `REAL_NEWS` свежими данными с kffleague.kz/ru/table
и перезапустите `python manage.py seed_demo_data` (команда идемпотентна —
данные обновятся через `update_or_create`/`get_or_create`, дубликатов не будет).

Статистика по игрокам (голы/ассисты/рейтинг) и цены на мерч по-прежнему
условные — открытого источника по составам команд не нашлось; их можно
уточнить вручную через `/admin/`.

## Логотипы клубов

Официальные эмблемы всех 18 клубов КПЛ и логотип лиги лежат в
`static/img/clubs/*.png` и `static/img/league/kpl-logo.png`. Они подключены
через поле `Club.crest_static` (путь к файлу в `static/`) — `seed_demo_data`
проставляет его автоматически при создании клубов. Если позже загрузите
логотип через админку в поле `crest` (`ImageField`), он будет иметь
приоритет над статичным файлом — это учтено в
`templates/partials/crest.html`, переиспользуемом везде, где отображается
эмблема клуба.

## Важно

- Проект написан вручную как чистый Django-скелет — в текущей песочнице нет
  доступа к сети и не установлен Django, поэтому `runserver`/`migrate` здесь
  не запускались. Все `.py`-файлы прошли проверку синтаксиса (`py_compile`),
  но перед защитой обязательно прогоните `python manage.py migrate` и
  `python manage.py check` в своём окружении.
- Фото игроков в проекте нет — поле `Player.photo` (`ImageField`) готово
  принимать файлы через админку Django (`/admin/`, доступна после
  `createsuperuser`).
