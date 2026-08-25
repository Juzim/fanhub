#!/bin/sh
set -e

# Если передана явная команда (например `sh`, `bash`, конкретная manage.py-команда) —
# выполняем именно её и выходим, не запуская встроенный сценарий автозапуска.
# Это то, что нужно для `docker compose run --rm web sh` или
# `docker compose run --rm web python manage.py makemigrations`.
if [ "$#" -gt 0 ]; then
  exec "$@"
fi

echo "⏳ Ждём PostgreSQL (${DB_HOST}:${DB_PORT})..."
until pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" >/dev/null 2>&1; do
  sleep 1
done
echo "✅ PostgreSQL готов"

# accounts — кастомная модель пользователя (AUTH_USER_MODEL), от неё зависят
# почти все остальные приложения. Генерируем её миграции явно и первыми,
# чтобы граф зависимостей строился корректно.
python manage.py makemigrations accounts --noinput
python manage.py makemigrations --noinput
python manage.py migrate --noinput

if [ "$SEED_DEMO_DATA" = "true" ]; then
  echo "🌱 Наполняем БД демо-данными FAN-HUB..."
  python manage.py seed_demo_data
fi

if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ] && [ "$DJANGO_SUPERUSER_EMAIL" ]; then
  python manage.py createsuperuser --noinput || true
fi

python manage.py collectstatic --noinput

# PORT задаётся хостингом динамически (например, Render) — 8000 остаётся
# дефолтом для локального Docker Compose, где порт фиксирован в compose-файле.
PORT="${PORT:-8000}"

if [ "$DEBUG" = "True" ]; then
  echo "🚀 Запуск dev-сервера Django (DEBUG=True) на порту ${PORT}"
  exec python manage.py runserver "0.0.0.0:${PORT}"
else
  echo "🚀 Запуск gunicorn (production) на порту ${PORT}"
  exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT}" --workers 3
fi
