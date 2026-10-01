# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y build-essential

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --default-timeout=100 --retries 5 -r requirements.txt

COPY . .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Use entrypoint to run migrations, then hand off to CMD
ENTRYPOINT ["/app/entrypoint.sh"]

RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]