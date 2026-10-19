# Optional: container image for Koyeb (or any Docker host). Render uses build.sh instead.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# collectstatic needs a key at build time only; the real one comes from the environment at runtime.
RUN SECRET_KEY=build-only python manage.py collectstatic --no-input

RUN useradd --create-home app && chown -R app /app
USER app

EXPOSE 8000
# Migrations + bootstrap run on start because Koyeb has no separate release step.
CMD python manage.py migrate --no-input && python manage.py createcachetable && python manage.py bootstrap && \
    gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 60 --access-logfile -
