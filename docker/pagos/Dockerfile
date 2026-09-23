FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app
COPY src/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY src/common /app/common
COPY src/pagos /app/pagos

USER 65532:65532
EXPOSE 8000
CMD ["uvicorn", "pagos.main:app", "--host", "0.0.0.0", "--port", "8000"]
