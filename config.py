"""
⚙️ Конфигурация Captcha AutoBot
"""

import os
from typing import Tuple, List

# ============================================
# ТЕЛЕГРАМ НАСТРОЙКИ
# ============================================

# Токен вашего бота (получить у @BotFather)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8263845138:AAEqRm0UgjwF3uUG2UAIDcuNbLAxYMqEnBI")

# ID администраторов (можно получить у @userinfobot)
ADMIN_IDS: List[int] = []
try:
    admin_ids_str = os.getenv("ADMIN_IDS", "")
    if admin_ids_str:
        ADMIN_IDS = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip()]
except:
    ADMIN_IDS = []

# ============================================
# КООРДИНАТЫ ОБРАБОТКИ
# ============================================

# Область капчи: (x, y, width, height)
CAPTCHA_REGION: Tuple[int, int, int, int] = (688, 451, 596, 89)

# Центр поля ввода: (x, y)
INPUT_COORDS: Tuple[int, int] = (983, 560)

# Центр кнопки отправки: (x, y)
BUTTON_COORDS: Tuple[int, int] = (1136, 622)

# ============================================
# НАСТРОЙКИ ПОВЕДЕНИЯ
# ============================================

# Задержки между циклами (секунды)
CYCLE_DELAY_MIN: float = 10.0
CYCLE_DELAY_MAX: float = 29.0
CYCLE_DELAY_DISTRIBUTION: str = "normal"  # normal, uniform

# Настройки ввода
TYPING_SPEED_BASE: float = 0.1  # секунд между символами
TYPING_SPEED_VARIATION: float = 0.5  # ±50%

# Ошибки (имитация человека)
MISTAKE_PROBABILITY: float = 0.06  # 6% шанс ошибки
THINKING_PAUSE_PROB: float = 0.25  # 25% шанс задуматься

# Точность кликов (пиксели)
CLICK_ACCURACY_FRESH: int = 5   # ±5 пикселей когда свежий
CLICK_ACCURACY_TIRED: int = 15  # ±15 когда устал

# Движение мыши
MOUSE_SPEED_MIN: float = 0.3
MOUSE_SPEED_MAX: float = 1.2
MOUSE_CURVE_VARIATION: float = 0.4  # извилистость траектории

# ============================================
# РАБОЧИЙ РЕЖИМ
# ============================================

# Часы работы (по умолчанию 9-18)
WORK_START_HOUR: int = 9
WORK_END_HOUR: int = 18

# Вероятность перерыва
BREAK_PROBABILITY_DAY: float = 0.03  # 3% днем
BREAK_PROBABILITY_NIGHT: float = 0.01  # 1% ночью

# ============================================
# ПУТИ К ФАЙЛАМ
# ============================================

# Директории (создаются автоматически)
DATA_DIR: str = "data"
LOGS_DIR: str = "logs"

# Файлы данных
STATS_FILE: str = f"{DATA_DIR}/stats.json"
ACTIVITY_FILE: str = f"{DATA_DIR}/activity.log"
WORKER_STATE_FILE: str = f"{DATA_DIR}/worker_state.json"
WORKER_STATUS_FILE: str = f"{DATA_DIR}/worker_status.json"

# Файлы логов
CAPTCHA_LOG_FILE: str = f"{LOGS_DIR}/captcha_bot.log"
TELEGRAM_LOG_FILE: str = f"{LOGS_DIR}/telegram_bot.log"

# ============================================
# НАСТРОЙКИ ЛОГИРОВАНИЯ
# ============================================

LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

# ============================================
# ВАЛИДАЦИЯ КОНФИГУРАЦИИ
# ============================================

def validate_config() -> Tuple[bool, List[str]]:
    """Проверка корректности конфигурации"""
    errors = []
    
    # Проверка токена
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        errors.append("Токен Telegram бота не установлен")
    
    # Проверка координат
    if len(CAPTCHA_REGION) != 4:
        errors.append("CAPTCHA_REGION должен содержать 4 числа (x, y, width, height)")
    
    if len(INPUT_COORDS) != 2:
        errors.append("INPUT_COORDS должен содержать 2 числа (x, y)")
    
    if len(BUTTON_COORDS) != 2:
        errors.append("BUTTON_COORDS должен содержать 2 числа (x, y)")
    
    # Проверка интервалов
    if CYCLE_DELAY_MIN < 3:
        errors.append("CYCLE_DELAY_MIN должен быть >= 3 секунд")
    
    if CYCLE_DELAY_MAX <= CYCLE_DELAY_MIN:
        errors.append("CYCLE_DELAY_MAX должен быть больше CYCLE_DELAY_MIN")
    
    if not (0 <= MISTAKE_PROBABILITY <= 1):
        errors.append("MISTAKE_PROBABILITY должен быть от 0 до 1")
    
    if CYCLE_DELAY_DISTRIBUTION not in ["normal", "uniform"]:
        errors.append("CYCLE_DELAY_DISTRIBUTION должен быть 'normal' или 'uniform'")
    
    return len(errors) == 0, errors

def print_config_summary():
    """Вывод сводки конфигурации"""
    print("="*60)
    print("⚙️  КОНФИГУРАЦИЯ CAPTCHA AUTOBOT")
    print("="*60)
    
    print(f"\n📱 Telegram:")
    token_display = TELEGRAM_TOKEN[:10] + "..." + TELEGRAM_TOKEN[-10:] if TELEGRAM_TOKEN else "Нет"
    print(f"  Токен: {token_display}")
    print(f"  Админы: {len(ADMIN_IDS)} пользователей")
    
    print(f"\n🎯 Координаты:")
    print(f"  Капча: {CAPTCHA_REGION}")
    print(f"  Поле ввода: {INPUT_COORDS}")
    print(f"  Кнопка: {BUTTON_COORDS}")
    
    print(f"\n⚡ Поведение:")
    print(f"  Задержки: {CYCLE_DELAY_MIN}-{CYCLE_DELAY_MAX} сек ({CYCLE_DELAY_DISTRIBUTION})")
    print(f"  Ошибки: {MISTAKE_PROBABILITY*100:.1f}%")
    print(f"  Рабочие часы: {WORK_START_HOUR}:00 - {WORK_END_HOUR}:00")
    
    print(f"\n📁 Файлы:")
    print(f"  Данные: {DATA_DIR}/")
    print(f"  Логи: {LOGS_DIR}/")
    
    # Валидация
    is_valid, errors = validate_config()
    print(f"\n{'✅ Конфигурация корректна' if is_valid else '❌ Ошибки конфигурации:'}")
    
    if errors:
        for error in errors:
            print(f"  • {error}")
    
    print("="*60)

if __name__ == "__main__":
    print_config_summary()
