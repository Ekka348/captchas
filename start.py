#!/usr/bin/env python3
"""
🚀 Точка входа для запуска Captcha AutoBot
"""

import os
import sys
import logging
import threading
import time
from datetime import datetime

# Добавляем путь к текущей директории
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_environment():
    """Настройка окружения"""
    print("="*60)
    print("🚀 ЗАПУСК CAPTCHA AUTOBOT")
    print("="*60)
    
    # Проверяем и создаем директории
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Проверяем конфигурацию
    try:
        from config import validate_config, print_config_summary
        is_valid, errors = validate_config()
        
        if not is_valid:
            print("❌ Ошибки конфигурации:")
            for error in errors:
                print(f"  • {error}")
            print("\nИсправьте config.py перед запуском")
            return False
        
        print_config_summary()
        return True
        
    except ImportError as e:
        print(f"❌ Не удалось загрузить конфигурацию: {e}")
        print("Создайте файл config.py или запустите setup.py")
        return False

def start_telegram_bot():
    """Запуск Telegram бота"""
    print("\n🤖 Запуск Telegram бота...")
    
    try:
        from telegram_bot import main as telegram_main
        telegram_main()
    except ImportError as e:
        print(f"❌ Не удалось импортировать telegram_bot: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка запуска Telegram бота: {e}")
        return False
    
    return True

def start_captcha_worker():
    """Запуск фонового воркера"""
    print("\n🎯 Запуск фонового воркера...")
    
    try:
        from captcha_worker import CaptchaWorker
        worker = CaptchaWorker()
        worker.run()
    except ImportError as e:
        print(f"❌ Не удалось импортировать captcha_worker: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка запуска воркера: {e}")
        return False
    
    return True

def main():
    """Основная функция"""
    # Настройка окружения
    if not setup_environment():
        sys.exit(1)
    
    print("\n🎯 Выберите режим запуска:")
    print("1. Только Telegram бот (рекомендуется)")
    print("2. Только воркер (для тестирования)")
    print("3. Оба (Telegram + воркер в отдельных процессах)")
    print("4. Выход")
    
    try:
        choice = input("\nВведите номер (1-4): ").strip()
        
        if choice == "1":
            # Только Telegram бот
            print("\n" + "="*60)
            print("🤖 ЗАПУСК ТОЛЬКО TELEGRAM БОТА")
            print("="*60)
            start_telegram_bot()
            
        elif choice == "2":
            # Только воркер
            print("\n" + "="*60)
            print("🎯 ЗАПУСК ТОЛЬКО ВОРКЕРА")
            print("="*60)
            start_captcha_worker()
            
        elif choice == "3":
            # Оба в отдельных потоках
            print("\n" + "="*60)
            print("🚀 ЗАПУСК ВСЕЙ СИСТЕМЫ")
            print("="*60)
            print("Telegram бот + фоновый воркер")
            print("="*60)
            
            # В реальности здесь нужно запускать в разных процессах
            # Для простоты запускаем только Telegram бота
            # (воркер будет запускаться через команды бота)
            start_telegram_bot()
            
        elif choice == "4":
            print("\n👋 Выход")
            sys.exit(0)
            
        else:
            print("\n❌ Неверный выбор")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Остановлено пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
