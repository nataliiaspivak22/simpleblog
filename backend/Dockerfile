# backend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# спочатку скопіюємо файл з залежностями
COPY requirements.txt .

# встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# копіюємо весь код з цієї папки (тут вже app/)
COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
