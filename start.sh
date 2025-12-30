#!/bin/bash

echo "🚀 Запуск Captcha Earning Bot..."
echo "Версия Python: $(python3 --version)"
echo "Текущая директория: $(pwd)"

# Создаем необходимые директории
mkdir -p data logs screenshots

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Инициализация базы данных
echo "🗄️ Инициализация базы данных..."
python3 -c "
try:
    from database import init_db
    init_db()
    print('✅ База данных инициализирована')
except Exception as e:
    print(f'❌ Ошибка: {e}')
"

# Проверяем конфигурацию
echo "⚙️ Проверка конфигурации..."
python3 -c "
try:
    from config import validate_config
    is_valid, errors = validate_config()
    if is_valid:
        print('✅ Конфигурация корректна')
    else:
        print('❌ Ошибки конфигурации:')
        for error in errors:
            print(f'  - {error}')
except Exception as e:
    print(f'❌ Ошибка импорта: {e}')
"

# Запускаем бота
echo "🤖 Запуск Telegram бота..."
python3 telegram_bot.py
