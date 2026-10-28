FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app
COPY src/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY src/common /app/common
COPY src/api /app/api
COPY src/auth /app/auth
COPY src/catalogo /app/catalogo

USER 65532:65532
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn api.core:app --host 0.0.0.0 --port ${PORT:-8000}"]
