#!/usr/bin/env python3
"""
🛠️ Установщик и настройщик Captcha AutoBot
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def print_banner():
    """Вывод баннера"""
    print("="*60)
    print("🛠️  УСТАНОВКА И НАСТРОЙКА CAPTCHA AUTOBOT")
    print("="*60)

def check_python():
    """Проверка версии Python"""
    print("\n1. Проверка Python...")
    
    if sys.version_info < (3, 8):
        print(f"❌ Требуется Python 3.8+, у вас {sys.version_info.major}.{sys.version_info.minor}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def install_dependencies():
    """Установка зависимостей"""
    print("\n2. Установка зависимостей...")
    
    try:
        # Обновление pip
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        print("✅ Pip обновлен")
    except:
        print("⚠ Не удалось обновить pip, продолжаем...")
    
    try:
        # Установка зависимостей
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Зависимости установлены")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Ошибка установки зависимостей:")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("❌ Файл requirements.txt не найден")
        return False

def setup_telegram_bot():
    """Настройка Telegram бота"""
    print("\n3. Настройка Telegram бота...")
    
    token = input("Введите токен Telegram бота (получить у @BotFather): ").strip()
    
    if not token:
        print("⚠ Токен не введен, можно настроить позже в config.py")
        token = "YOUR_TELEGRAM_BOT_TOKEN"
    
    admin_ids = input("Введите ID администраторов через запятую (опционально): ").strip()
    
    return token, admin_ids

def setup_coordinates():
    """Настройка координат"""
    print("\n4. Настройка координат...")
    print("Для определения координат запустите позже:")
    print("  python utils/coordinates_helper.py")
    
    print("\nВведите координаты (или Enter для значений по умолчанию):")
    
    # Значения по умолчанию (ваши)
    defaults = {
        'captcha_region': (688, 451, 596, 89),
        'input_coords': (983, 560),
        'button_coords': (1136, 622)
    }
    
    results = {}
    
    for key, default in defaults.items():
        prompt = f"  {key} (по умолчанию {default}): "
        value = input(prompt).strip()
        
        if value:
            try:
                # Парсим ввод вида "688, 451, 596, 89"
                if key == 'captcha_region':
                    values = [int(x.strip()) for x in value.split(',')]
                    if len(values) == 4:
                        results[key] = tuple(values)
                    else:
                        print(f"    ⚠ Нужно 4 числа, использую значение по умолчанию")
                        results[key] = default
                else:
                    values = [int(x.strip()) for x in value.split(',')]
                    if len(values) == 2:
                        results[key] = tuple(values)
                    else:
                        print(f"    ⚠ Нужно 2 числа, использую значение по умолчанию")
                        results[key] = default
            except:
                print(f"    ⚠ Ошибка парсинга, использую значение по умолчанию")
                results[key] = default
        else:
            results[key] = default
    
    return results

def create_config_file(token, admin_ids, coordinates):
    """Создание конфигурационного файла"""
    print("\n5. Создание config.py...")
    
    config_content = f'''"""
⚙️ Конфигурация Captcha AutoBot
Автоматически сгенерирована setup.py
"""

import os
from typing import Tuple, List

# ============================================
# ТЕЛЕГРАМ НАСТРОЙКИ
# ============================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "{token}")
ADMIN_IDS: List[int] = []
try:
    admin_ids_str = os.getenv("ADMIN_IDS", "{admin_ids}")
    if admin_ids_str:
        ADMIN_IDS = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip()]
except:
    ADMIN_IDS = []

# ============================================
# КООРДИНАТЫ ОБРАБОТКИ
# ============================================

CAPTCHA_REGION: Tuple[int, int, int, int] = {coordinates['captcha_region']}
INPUT_COORDS: Tuple[int, int] = {coordinates['input_coords']}
BUTTON_COORDS: Tuple[int, int] = {coordinates['button_coords']}

# ============================================
# НАСТРОЙКИ ПОВЕДЕНИЯ
# ============================================

CYCLE_DELAY_MIN: float = 10.0
CYCLE_DELAY_MAX: float = 29.0
CYCLE_DELAY_DISTRIBUTION: str = "normal"

TYPING_SPEED_BASE: float = 0.1
TYPING_SPEED_VARIATION: float = 0.5

MISTAKE_PROBABILITY: float = 0.06
THINKING_PAUSE_PROB: float = 0.25

CLICK_ACCURACY_FRESH: int = 5
CLICK_ACCURACY_TIRED: int = 15

MOUSE_SPEED_MIN: float = 0.3
MOUSE_SPEED_MAX: float = 1.2
MOUSE_CURVE_VARIATION: float = 0.4

# ============================================
# РАБОЧИЙ РЕЖИМ
# ============================================

WORK_START_HOUR: int = 9
WORK_END_HOUR: int = 18
BREAK_PROBABILITY_DAY: float = 0.03
BREAK_PROBABILITY_NIGHT: float = 0.01

# ============================================
# ПУТИ К ФАЙЛАМ
# ============================================

DATA_DIR: str = "data"
LOGS_DIR: str = "logs"

STATS_FILE: str = f"{{DATA_DIR}}/stats.json"
ACTIVITY_FILE: str = f"{{DATA_DIR}}/activity.log"
WORKER_STATE_FILE: str = f"{{DATA_DIR}}/worker_state.json"
WORKER_STATUS_FILE: str = f"{{DATA_DIR}}/worker_status.json"

CAPTCHA_LOG_FILE: str = f"{{LOGS_DIR}}/captcha_bot.log"
TELEGRAM_LOG_FILE: str = f"{{LOGS_DIR}}/telegram_bot.log"

# ============================================
# НАСТРОЙКИ ЛОГИРОВАНИЯ
# ============================================

LOG_LEVEL: str = "INFO"
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
'''
    
    try:
        with open("config.py", "w", encoding="utf-8") as f:
            f.write(config_content)
        print("✅ config.py создан")
        return True
    except Exception as e:
        print(f"❌ Ошибка создания config.py: {e}")
        return False

def create_directories():
    """Создание необходимых директорий"""
    print("\n6. Создание структуры проекта...")
    
    directories = ["data", "logs", "utils"]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Создана папка: {directory}/")
        except Exception as e:
            print(f"❌ Ошибка создания {directory}/: {e}")
    
    return True

def create_utils_files():
    """Создание вспомогательных файлов"""
    print("\n7. Создание вспомогательных файлов...")
    
    # coordinates_helper.py
    coordinates_helper = '''#!/usr/bin/env python3
"""
🛠️ Помощник для определения координат на экране
"""

import pyautogui
import time

def get_coordinates():
    """Интерактивное получение координат"""
    print("="*60)
    print("🖱️  ПОМОЩНИК ДЛЯ ОПРЕДЕЛЕНИЯ КООРДИНАТ")
    print("="*60)
    
    print("\\n1. Определение области капчи:")
    print("   Наведите курсор в ВЕРХНИЙ ЛЕВЫЙ УГОЛ области с капчой")
    input("   Нажмите Enter когда готовы...")
    x1, y1 = pyautogui.position()
    
    print("\\n   Наведите курсор в НИЖНИЙ ПРАВЫЙ УГОЛ области с капчой")
    input("   Нажмите Enter когда готовы...")
    x2, y2 = pyautogui.position()
    
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    x = min(x1, x2)
    y = min(y1, y2)
    
    print(f"\\n   Область капчи: ({x}, {y}, {width}, {height})")
    
    print("\\n2. Определение поля ввода:")
    print("   Наведите курсор в ЦЕНТР поля для ввода капчи")
    input("   Нажмите Enter когда готовы...")
    input_x, input_y = pyautogui.position()
    
    print(f"\\n   Поле ввода: ({input_x}, {input_y})")
    
    print("\\n3. Определение кнопки отправки:")
    print("   Наведите курсор в ЦЕНТР кнопки отправки/проверки")
    input("   Нажмите Enter когда готовы...")
    button_x, button_y = pyautogui.position()
    
    print(f"\\n   Кнопка: ({button_x}, {button_y})")
    
    print("\\n" + "="*60)
    print("🎯 ВАШИ КООРДИНАТЫ ДЛЯ config.py:")
    print("="*60)
    print(f"\\nCAPTCHA_REGION = ({x}, {y}, {width}, {height})")
    print(f"INPUT_COORDS = ({input_x}, {input_y})")
    print(f"BUTTON_COORDS = ({button_x}, {button_y})")
    print("\\n" + "="*60)
    print("\\nСкопируйте эти значения в config.py")
    
    return (x, y, width, height), (input_x, input_y), (button_x, button_y)

if __name__ == "__main__":
    try:
        get_coordinates()
        input("\\nНажмите Enter для выхода...")
    except KeyboardInterrupt:
        print("\\n\\n🛑 Отменено пользователем")
    except Exception as e:
        print(f"\\n❌ Ошибка: {e}")
'''
    
    try:
        utils_dir = Path("utils")
        utils_dir.mkdir(exist_ok=True)
        
        # coordinates_helper.py
        with open(utils_dir / "coordinates_helper.py", "w", encoding="utf-8") as f:
            f.write(coordinates_helper)
        print("✅ utils/coordinates_helper.py создан")
        
        # __init__.py
        with open(utils_dir / "__init__.py", "w", encoding="utf-8") as f:
            f.write("# Вспомогательные модули")
        print("✅ utils/__init__.py создан")
        
        # logger.py (опционально)
        logger_content = '''"""
📝 Настройка логирования
"""

import logging
import sys

def setup_logger(name: str, log_file: str, level: str = "INFO"):
    """Настройка логгера"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Форматтер
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Файловый handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    
    # Консольный handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
'''
        
        with open(utils_dir / "logger.py", "w", encoding="utf-8") as f:
            f.write(logger_content)
        print("✅ utils/logger.py создан")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка создания вспомогательных файлов: {e}")
        return False

def main():
    """Основная функция установки"""
    print_banner()
    
    # Проверки
    if not check_python():
        sys.exit(1)
    
    # Установка зависимостей
    if not install_dependencies():
        print("⚠ Продолжаем без зависимостей...")
    
    # Настройка Telegram
    token, admin_ids = setup_telegram_bot()
    
    # Настройка координат
    coordinates = setup_coordinates()
    
    # Создание файлов
    create_directories()
    create_utils_files()
    
    if not create_config_file(token, admin_ids, coordinates):
        print("⚠ Не удалось создать config.py, создайте вручную")
    
    print("\n" + "="*60)
    print("✅ УСТАНОВКА ЗАВЕРШЕНА!")
    print("="*60)
    
    print("\n🎯 Следующие шаги:")
    print("1. Проверьте координаты в config.py")
    print("2. Запустите бота: python start.py")
    print("3. Или запустите отдельно:")
    print("   • Telegram бот: python telegram_bot.py")
    print("   • Воркер: python captcha_worker.py")
    print("   • Помощник координат: python utils/coordinates_helper.py")
    
    print("\n📱 Команды Telegram бота:")
    print("   /start - Главное меню")
    print("   /status - Статус системы")
    print("   /start_bot - Запуск обработки")
    print("   /stop_bot - Остановка обработки")
    
    print("\n" + "="*60)
    print("🚀 Удачи в использовании Captcha AutoBot!")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Установка прервана пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Непредвиденная ошибка: {e}")
        sys.exit(1)
