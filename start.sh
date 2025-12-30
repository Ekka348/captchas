#!/bin/bash

echo "🚀 Запуск Captcha Earning Bot..."
echo "Версия Python: $(python --version)"
echo "Текущая директория: $(pwd)"

# Создаем необходимые директории
mkdir -p data logs

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

# Устанавливаем Chrome для Selenium
echo "🌐 Установка Chrome..."
apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Создаем базу данных
echo "🗄️ Инициализация базы данных..."
python -c "from database import init_db; init_db()"

# Проверяем конфигурацию
echo "⚙️ Проверка конфигурации..."
python -c "from config import validate_config; is_valid, errors = validate_config(); print('✅ Конфигурация корректна' if is_valid else '❌ Ошибки: ' + str(errors))"

# Запускаем бота
echo "🤖 Запуск Telegram бота..."
python telegram_bot.py
