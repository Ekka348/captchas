#!/usr/bin/env python3
"""
🚀 Главный запускающий скрипт Captcha Earning Bot
"""

import os
import sys
import threading
import time
from datetime import datetime

# Добавляем путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_banner():
    """Вывод баннера"""
    print("="*60)
    print("🤖 CAPTCHA EARNING BOT")
    print("="*60)
    print(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version}")
    print(f"Рабочая директория: {os.getcwd()}")
    print("="*60)

def check_environment():
    """Проверка окружения"""
    print("\n🔍 Проверка окружения...")
    
    # Проверяем директории
    required_dirs = ['data', 'logs', 'screenshots']
    for dir_name in required_dirs:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✅ Директория {dir_name}/ создана")
    
    # Проверяем конфигурацию
    try:
        from config import validate_config
        is_valid, errors = validate_config()
        
        if not is_valid:
            print("❌ Ошибки конфигурации:")
            for error in errors:
                print(f"  • {error}")
            return False
        
        print("✅ Конфигурация корректна")
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта конфигурации: {e}")
        return False

def start_services():
    """Запуск сервисов"""
    print("\n🚀 Запуск сервисов...")
    
    try:
        # Импортируем после проверки
        from telegram_bot import main as start_telegram_bot
        from captcha_worker import CaptchaWorker
        
        # Запускаем воркер в отдельном потоке
        worker = CaptchaWorker()
        worker_thread = threading.Thread(target=worker.run, daemon=True)
        worker_thread.start()
        
        print("✅ Воркер запущен в фоновом режиме")
        
        # Запускаем Telegram бота (блокирующий вызов)
        print("🤖 Запуск Telegram бота...")
        start_telegram_bot()
        
    except KeyboardInterrupt:
        print("\n🛑 Остановлено пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка запуска: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Основная функция"""
    print_banner()
    
    if not check_environment():
        print("\n❌ Не удалось запустить из-за ошибок конфигурации")
        print("Проверьте файл config.py")
        sys.exit(1)
    
    try:
        start_services()
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
