FROM python:3.12-alpine

WORKDIR /app

RUN apk update && \
    apk add --no-cache python3-dev \
    gcc \
    musl-dev \
    libpq-dev \
    nmap 
    
COPY pyproject.toml poetry.lock* /app/

RUN pip install --upgrade pip && \
    pip install poetry

RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

COPY . /app/
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh