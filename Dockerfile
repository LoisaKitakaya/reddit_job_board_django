FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=UTC

WORKDIR /app

COPY ./requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends && \
    apt-get clean && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "celery -A app.celery worker -l info & celery -A app.celery beat -l info & gunicorn --bind 0.0.0.0:8000 --workers 4 app.wsgi:application"]