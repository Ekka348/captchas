"""
⚙️ Конфигурация Captcha AutoBot - Локальная версия
"""

import os
import json
from typing import Tuple, Dict, Any
from datetime import datetime

# ============================================
# ПУТИ И ФАЙЛЫ
# ============================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Директории
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")

# Файлы конфигурации
COORDINATES_FILE = os.path.join(DATA_DIR, "coordinates.json")
STATS_FILE = os.path.join(DATA_DIR, "stats.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

# ============================================
# КООРДИНАТЫ ПО УМОЛЧАНИЮ
# ============================================

# Область капчи (x, y, width, height)
DEFAULT_CAPTCHA_REGION: Tuple[int, int, int, int] = (718, 426, 545, 141)

# Координаты поля ввода (x, y)
DEFAULT_INPUT_COORDS: Tuple[int, int] = (982, 597)

# Координаты кнопки "следующая" (x, y)
DEFAULT_BUTTON_COORDS: Tuple[int, int] = (1136, 622)

# ============================================
# НАСТРОЙКИ РАСПОЗНАВАНИЯ
# ============================================

# Tesseract OCR настройки
TESSERACT_CONFIG = r'--oem 3 --psm 8'
TESSERACT_LANG = 'eng'  # 'eng+rus' для русских капч

# Обработка изображения
PREPROCESS_CONFIG = {
    'contrast': 2.0,      # Увеличение контраста
    'threshold': 150,     # Порог бинаризации
    'denoise': True,      # Убрать шум
    'sharpen': True       # Увеличить резкость
}

# ============================================
# НАСТРОЙКИ ПОВЕДЕНИЯ
# ============================================

# Задержки (секунды)
DELAY_BETWEEN_CAPTCHAS_MIN = 5.0
DELAY_BETWEEN_CAPTCHAS_MAX = 15.0
DELAY_TYPING_MIN = 0.05
DELAY_TYPING_MAX = 0.15
DELAY_CLICK_MIN = 0.3
DELAY_CLICK_MAX = 0.7

# Поведение мыши
MOUSE_MOVE_DURATION_MIN = 0.3
MOUSE_MOVE_DURATION_MAX = 0.8
MOUSE_ACCURACY = 5  # +/- пикселей для клика

# ============================================
# ФУНКЦИИ РАБОТЫ С КОНФИГУРАЦИЕЙ
# ============================================

def load_coordinates() -> Dict[str, Any]:
    """Загрузка координат из файла"""
    try:
        if os.path.exists(COORDINATES_FILE):
            with open(COORDINATES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    
    # Возвращаем значения по умолчанию
    return {
        'captcha_region': DEFAULT_CAPTCHA_REGION,
        'input_coords': DEFAULT_INPUT_COORDS,
        'button_coords': DEFAULT_BUTTON_COORDS,
        'screen_size': None,
        'created_at': datetime.now().isoformat()
    }

def save_coordinates(coordinates: Dict[str, Any]) -> bool:
    """Сохранение координат в файл"""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        coordinates['updated_at'] = datetime.now().isoformat()
        
        with open(COORDINATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(coordinates, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения координат: {e}")
        return False

def load_settings() -> Dict[str, Any]:
    """Загрузка настроек из файла"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    
    # Настройки по умолчанию
    return {
        'auto_start': False,
        'human_like': True,
        'save_screenshots': True,
        'debug_mode': False,
        'max_errors_before_stop': 10,
        'created_at': datetime.now().isoformat()
    }

def save_settings(settings: Dict[str, Any]) -> bool:
    """Сохранение настроек в файл"""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        settings['updated_at'] = datetime.now().isoformat()
        
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения настроек: {e}")
        return False

def validate_config() -> Tuple[bool, list]:
    """Проверка корректности конфигурации"""
    errors = []
    
    # Проверяем директории
    for dir_path in [DATA_DIR, LOGS_DIR, SCREENSHOTS_DIR]:
        try:
            os.makedirs(dir_path, exist_ok=True)
        except Exception as e:
            errors.append(f"Не удалось создать {dir_path}: {e}")
    
    # Проверяем наличие координат
    try:
        coords = load_coordinates()
        if not all(key in coords for key in ['captcha_region', 'input_coords', 'button_coords']):
            errors.append("Координаты не настроены")
    except:
        errors.append("Ошибка загрузки координат")
    
    return len(errors) == 0, errors

def print_config_summary():
    """Вывод сводки конфигурации"""
    coords = load_coordinates()
    settings = load_settings()
    
    print("="*60)
    print("⚙️ КОНФИГУРАЦИЯ CAPTCHA AUTOBOT")
    print("="*60)
    
    print(f"\n📍 Координаты:")
    print(f"  Область капчи: {coords.get('captcha_region', 'не настроено')}")
    print(f"  Поле ввода: {coords.get('input_coords', 'не настроено')}")
    print(f"  Кнопка: {coords.get('button_coords', 'не настроено')}")
    
    print(f"\n⚙️ Настройки:")
    print(f"  Человекоподобное поведение: {'Да' if settings.get('human_like', True) else 'Нет'}")
    print(f"  Сохранение скриншотов: {'Да' if settings.get('save_screenshots', True) else 'Нет'}")
    print(f"  Автозапуск: {'Да' if settings.get('auto_start', False) else 'Нет'}")
    
    print(f"\n📁 Файлы:")
    print(f"  Данные: {DATA_DIR}/")
    print(f"  Логи: {LOGS_DIR}/")
    print(f"  Скриншоты: {SCREENSHOTS_DIR}/")
    
    is_valid, errors = validate_config()
    print(f"\n{'✅ Конфигурация корректна' if is_valid else '❌ Ошибки:'}")
    
    for error in errors:
        print(f"  • {error}")
    
    print("="*60)

if __name__ == "__main__":
    print_config_summary()
