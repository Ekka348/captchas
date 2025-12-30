FROM python:3.10-slim

WORKDIR /app

# Устанавливаем минимальные зависимости
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Создаем необходимые директории
RUN mkdir -p data logs

# Запускаем бота
CMD ["python3", "telegram_bot.py"]
