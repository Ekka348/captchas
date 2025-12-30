FROM python:3.10-slim

WORKDIR /app

# Устанавливаем зависимости для Playwright
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем браузеры через Playwright
RUN playwright install chromium
RUN playwright install-deps

# Копируем код
COPY . .

# Создаем необходимые директории
RUN mkdir -p data logs screenshots

# Открываем порт
EXPOSE 8080

# Запускаем бота
CMD ["python3", "telegram_bot.py"]
