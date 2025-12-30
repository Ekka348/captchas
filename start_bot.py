#!/usr/bin/env python3
"""
Простой скрипт для запуска Captcha Bot
"""

import subprocess
import sys
import time

def main():
    print("="*60)
    print("CAPTCHA AUTOBOT - ПРОСТОЙ ЗАПУСК")
    print("="*60)
    print()
    print("Конфигурация:")
    print("  • Капча: область 688x451, размер 596x89")
    print("  • Поле ввода: клик в (983, 560)")
    print("  • Кнопка: клик в (1136, 622)")
    print("  • Интервал: 3 секунды")
    print()
    print("Подготовка к запуску...")
    
    # Обратный отсчет
    for i in range(5, 0, -1):
        print(f"Запуск через {i}...")
        time.sleep(1)
    
    print()
    print("Запуск основного бота...")
    print("Нажмите Ctrl+C для остановки")
    print("="*60)
    print()
    
    # Запуск основного скрипта
    try:
        subprocess.run([sys.executable, "captcha_bot.py"])
    except KeyboardInterrupt:
        print("\nОстановлено пользователем")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
