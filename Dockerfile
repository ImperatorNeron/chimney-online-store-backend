# ---- Етап збирання залежностей ----
FROM python:3.12-alpine AS builder

WORKDIR /app

# Встановлюємо тільки необхідне для компіляції
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    libpq-dev \
    python3-dev

COPY pyproject.toml poetry.lock* /app/

RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi --only main

# ---- Фінальний образ ----
FROM python:3.12-alpine

# Встановлюємо tini для сигналів (опційно)
RUN apk add --no-cache \
    libmagic \
    file \
    libpq \
    tini

# Створюємо непривілейованого користувача
RUN addgroup -g 1001 -S appuser && \
    adduser -S appuser -u 1001 -G appuser

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY --chown=appuser:appuser . /app

COPY --chown=appuser:appuser entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER appuser

ENTRYPOINT ["/sbin/tini", "--", "/entrypoint.sh"]