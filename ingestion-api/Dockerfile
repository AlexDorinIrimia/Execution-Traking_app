FROM python:3.11-slim

RUN useradd -m appuser
WORKDIR /app

# Install dependencies first (Docker layer cache)
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .
RUN chown -R appuser:appuser /app

USER appuser

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# FIX: original CMD ran "python app.py" which uses Flask's dev server —
#      not suitable for production/containers. Use gunicorn instead.
#      The module path "app:app" works because __init__.py re-exports `app`.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "60", "app:app"]
