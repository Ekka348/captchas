FROM python:3.10-slim

WORKDIR /app

# Устанавливаем системные зависимости для Playwright (обновленные для Debian Trixie)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    unzip \
    fonts-unifont \
    fonts-ubuntu \
    fonts-liberation \
    libgdk-pixbuf-2.0-0 \
    libgtk-3-0 \
    libnotify4 \
    libnss3 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    libatspi2.0-0 \
    libdrm2 \
    libgbm1 \
    libasound2 \
    libx264-dev \
    libenchant-2-2 \
    libicu72 \
    libjpeg62-turbo \
    libvpx7 \
    libwebp7 \
    libopus0 \
    libharfbuzz-icu0 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем Playwright и браузер
RUN playwright install chromium
# Пропускаем install-deps, так как уже установили вручную

# Копируем код
COPY . .

# Создаем необходимые директории
RUN mkdir -p data logs screenshots

# Открываем порт
EXPOSE 8080

# Запускаем бота
CMD ["python3", "telegram_bot.py"]
