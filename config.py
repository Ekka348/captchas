"""
⚙️ Конфигурация Captcha Earning Bot
"""

import os
from typing import Tuple, List, Optional
from dotenv import load_dotenv

# Загружаем .env файл
load_dotenv()

# ============================================
# НАСТРОЙКИ TELEGRAM
# ============================================

TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
ADMIN_IDS: List[int] = []
try:
    admin_ids_str = os.getenv("ADMIN_IDS", "")
    if admin_ids_str:
        ADMIN_IDS = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip()]
except:
    ADMIN_IDS = []

# ============================================
# НАСТРОЙКИ RUCAPTCHA
# ============================================

RUCAPTCHA_API_KEY: str = os.getenv("RUCAPTCHA_API_KEY", "")
RUCAPTCHA_BASE_URL: str = "https://rucaptcha.com"

# Типы капч для решения
CAPTCHA_TYPES: List[str] = [
    "ImageToTextTask",      # Простые текстовые
    "RecaptchaV2Task",      # Google ReCaptcha v2
    "HCaptchaTask",         # hCaptcha
    "RecaptchaV3Task",      # Google ReCaptcha v3
]

# ============================================
# НАСТРОЙКИ БРАУЗЕРА
# ============================================

# Прокси (опционально)
PROXY_ENABLED: bool = False
PROXY_SERVER: Optional[str] = os.getenv("PROXY_SERVER")
PROXY_USERNAME: Optional[str] = os.getenv("PROXY_USERNAME")
PROXY_PASSWORD: Optional[str] = os.getenv("PROXY_PASSWORD")

# Настройки Chrome
CHROME_HEADLESS: bool = True  # Для сервера
CHROME_WINDOW_SIZE: Tuple[int, int] = (1920, 1080)
CHROME_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# ============================================
# НАСТРОЙКИ РАБОТЫ
# ============================================

# Интервалы работы (секунды)
WORK_CYCLE_DELAY_MIN: int = 10
WORK_CYCLE_DELAY_MAX: int = 30
BREAK_AFTER_CYCLES: int = 50  # Перерыв после N циклов
BREAK_DURATION_MIN: int = 300  # 5 минут
BREAK_DURATION_MAX: int = 900  # 15 минут

# Настройки заработка
MIN_CAPTCHA_PRICE: float = 0.0003  # $ за капчу
TARGET_DAILY_EARNINGS: float = 1.0  # $ в день

# ============================================
# ПУТИ И ФАЙЛЫ
# ============================================

# Директории
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
DATA_DIR: str = os.path.join(BASE_DIR, "data")
LOGS_DIR: str = os.path.join(BASE_DIR, "logs")
SCREENSHOTS_DIR: str = os.path.join(BASE_DIR, "screenshots")

# Файлы базы данных
DATABASE_FILE: str = os.path.join(DATA_DIR, "captcha_bot.db")
STATS_FILE: str = os.path.join(DATA_DIR, "stats.json")

# Файлы логов
TELEGRAM_LOG_FILE: str = os.path.join(LOGS_DIR, "telegram_bot.log")
CAPTCHA_LOG_FILE: str = os.path.join(LOGS_DIR, "captcha_worker.log")
ERROR_LOG_FILE: str = os.path.join(LOGS_DIR, "errors.log")

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
    
    # Проверка токенов
    if not TELEGRAM_TOKEN:
        errors.append("Токен Telegram бота не установлен (TELEGRAM_TOKEN)")
    
    if not RUCAPTCHA_API_KEY:
        errors.append("API ключ rucaptcha не установлен (RUCAPTCHA_API_KEY)")
    
    # Проверка директорий
    for dir_path in [DATA_DIR, LOGS_DIR, SCREENSHOTS_DIR]:
        try:
            os.makedirs(dir_path, exist_ok=True)
        except:
            errors.append(f"Не удалось создать директорию: {dir_path}")
    
    return len(errors) == 0, errors

def print_config_summary():
    """Вывод сводки конфигурации"""
    print("="*60)
    print("⚙️ КОНФИГУРАЦИЯ CAPTCHA EARNING BOT")
    print("="*60)
    
    # Маскируем чувствительные данные
    token_display = f"{TELEGRAM_TOKEN[:10]}...{TELEGRAM_TOKEN[-10:]}" if TELEGRAM_TOKEN else "Нет"
    api_display = f"{RUCAPTCHA_API_KEY[:5]}...{RUCAPTCHA_API_KEY[-5:]}" if RUCAPTCHA_API_KEY else "Нет"
    
    print(f"\n📱 Telegram:")
    print(f"  Токен: {token_display}")
    print(f"  Админы: {len(ADMIN_IDS)}")
    
    print(f"\n🎯 Rucaptcha:")
    print(f"  API ключ: {api_display}")
    print(f"  Типы капч: {len(CAPTCHA_TYPES)}")
    
    print(f"\n🌐 Браузер:")
    print(f"  Headless: {'Да' if CHROME_HEADLESS else 'Нет'}")
    print(f"  Прокси: {'Да' if PROXY_ENABLED else 'Нет'}")
    
    print(f"\n💼 Работа:")
    print(f"  Интервал: {WORK_CYCLE_DELAY_MIN}-{WORK_CYCLE_DELAY_MAX} сек")
    print(f"  Цель: ${TARGET_DAILY_EARNINGS}/день")
    
    print(f"\n📁 Файлы:")
    print(f"  Данные: {DATA_DIR}/")
    print(f"  Логи: {LOGS_DIR}/")
    print(f"  База: {DATABASE_FILE}")
    
    is_valid, errors = validate_config()
    print(f"\n{'✅ Конфигурация корректна' if is_valid else '❌ Ошибки:'}")
    
    for error in errors:
        print(f"  • {error}")
    
    print("="*60)

if __name__ == "__main__":
    print_config_summary()
