FROM python:3.11-slim

RUN useradd -m appuser
WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000
CMD ["python", "app.py"]