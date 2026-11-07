# Dockerfile opcional para el backend (si en el futuro prefieres contenedor)
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "backend.main"]
