# ---- Етап збирання залежностей ----
FROM python:3.12-alpine AS builder

WORKDIR /app

RUN apk add --no-cache --virtual .build-deps \
    gcc musl-dev libpq-dev python3-dev

COPY pyproject.toml poetry.lock* /app/

RUN pip install --upgrade pip && \
    pip install poetry

# Аргумент для вибору групи залежностей (за замовчуванням тільки main)
ARG INSTALL_DEV=false
RUN if [ "$INSTALL_DEV" = "true" ]; then \
        poetry config virtualenvs.create false && \
        poetry install --no-root --no-interaction --no-ansi --with dev; \
    else \
        poetry config virtualenvs.create false && \
        poetry install --no-root --no-interaction --no-ansi --only main; \
    fi

# ---- Фінальний образ ----
FROM python:3.12-alpine

RUN apk add --no-cache libmagic file libpq tini

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . /app
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/sbin/tini", "--", "/entrypoint.sh"]