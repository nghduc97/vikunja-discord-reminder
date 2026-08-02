FROM python:3.13-slim-bookworm
COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/
COPY . /app
WORKDIR /app
RUN uv sync
CMD ["uv", "run", "main.py"]
