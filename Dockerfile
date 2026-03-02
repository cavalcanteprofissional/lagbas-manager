FROM python:3.11-slim

WORKDIR /app

COPY frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend/ .

EXPOSE 8000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]
