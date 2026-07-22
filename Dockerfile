# ---- Étape 1 : compilation du CSS Tailwind ----
FROM node:20-alpine AS cssbuilder
WORKDIR /app
COPY package.json package-lock.json tailwind.config.js ./
RUN npm ci
COPY . .
RUN npm run build

# ---- Étape 2 : application Django ----
FROM python:3.11-slim AS app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY --from=cssbuilder /app/static/css/output.css static/css/output.css

RUN mkdir -p /code/staticfiles /code/media

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["gunicorn", "cogerent_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
