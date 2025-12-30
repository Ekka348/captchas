#!/usr/bin/env python3
"""
🚀 Главный запускающий скрипт Captcha AutoBot
"""

import os
import sys
import time
from datetime import datetime

# Добавляем путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_banner():
    """Вывод баннера"""
    print("="*60)
    print("🤖 CAPTCHA AUTO BOT - ЛОКАЛЬНАЯ ВЕРСИЯ")
    print("="*60)
    print(f"Запуск: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version}")
    print(f"Рабочая директория: {os.getcwd()}")
    print("="*60)

def check_environment():
    """Проверка окружения"""
    print("\n🔍 Проверка окружения...")
    
    # Создаем необходимые директории
    directories = ['data', 'logs', 'screenshots']
    for dir_name in directories:
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

def main_menu():
    """Главное меню"""
    print("\n" + "="*60)
    print("🏠 ГЛАВНОЕ МЕНЮ")
    print("="*60)
    
    print("\nВыберите режим работы:")
    print("1. 🎯 Автоматический решатель капч (локальный)")
    print("2. 🤖 Telegram бот управления")
    print("3. 🛠️ Настройка координат")
    print("4. 🧪 Тест распознавания капчи")
    print("5. 📊 Просмотр статистики")
    print("0. 🚪 Выход")
    
    choice = input("\nВаш выбор (0-5): ").strip()
    
    return choice

def main():
    """Основная функция"""
    print_banner()
    
    if not check_environment():
        print("\n❌ Не удалось запустить из-за ошибок конфигурации")
        sys.exit(1)
    
    while True:
        choice = main_menu()
        
        if choice == "1":
            # Запуск автоматического решателя
            from screen_solver import ScreenCaptchaSolver
            solver = ScreenCaptchaSolver()
            solver.run()
            
        elif choice == "2":
            # Запуск Telegram бота
            from telegram_manager import main as start_telegram_bot
            start_telegram_bot()
            
        elif choice == "3":
            # Настройка координат
            from setup_coordinates import setup_coordinates_interactive
            setup_coordinates_interactive()
            
        elif choice == "4":
            # Тест распознавания
            from image_processor import test_recognition
            test_recognition()
            
        elif choice == "5":
            # Просмотр статистики
            from screen_solver import load_stats
            stats = load_stats()
            if stats:
                print("\n📊 СТАТИСТИКА:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
            else:
                print("📊 Статистика пока не собрана")
                
        elif choice == "0":
            print("\n👋 До свидания!")
            break
            
        else:
            print("❌ Неверный выбор")
        
        input("\nНажмите Enter чтобы продолжить...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Программа остановлена пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
