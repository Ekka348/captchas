"""
⚙️ Конфигурация Captcha AutoBot
"""

import os
from typing import Tuple, List, Optional
from dotenv import load_dotenv

load_dotenv()

# ============================================
# НАСТРОЙКИ TELEGRAM
# ============================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
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

RUCAPTCHA_API_KEY = os.getenv("RUCAPTCHA_API_KEY", "99461b14be32f596e034e2459b05e645")
RUCAPTCHA_BASE_URL = "https://rucaptcha.com"

# ============================================
# НАСТРОЙКИ БРАУЗЕРА
# ============================================

CHROME_HEADLESS = os.getenv("CHROME_HEADLESS", "false").lower() == "true"
CHROME_WINDOW_SIZE: Tuple[int, int] = (1920, 1080)
CHROME_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Прокси (опционально)
PROXY_ENABLED = False
PROXY_SERVER = os.getenv("PROXY_SERVER")
PROXY_USERNAME = os.getenv("PROXY_USERNAME")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")

# ============================================
# НАСТРОЙКИ АВТОМАТИЗАЦИИ
# ============================================

# Поведение бота
AUTO_SCROLL = True
HUMAN_LIKE_DELAYS = True
RANDOM_MISTAKES = 0.05  # 5% вероятность ошибки

# Время работы
WORK_CYCLE_DELAY_MIN = 3
WORK_CYCLE_DELAY_MAX = 10
MAX_ERRORS_BEFORE_STOP = 10

# ============================================
# ПУТИ И ФАЙЛЫ
# ============================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")

# Файлы базы данных
DATABASE_FILE = os.path.join(DATA_DIR, "captcha_bot.db")

# ============================================
# ВАЛИДАЦИЯ
# ============================================

def validate_config() -> Tuple[bool, List[str]]:
    """Проверка корректности конфигурации"""
    errors = []
    
    if not TELEGRAM_TOKEN:
        errors.append("TELEGRAM_TOKEN не установлен")
    
    if not RUCAPTCHA_API_KEY or RUCAPTCHA_API_KEY == "ваш_api_ключ":
        errors.append("RUCAPTCHA_API_KEY не установлен")
    
    for dir_path in [DATA_DIR, LOGS_DIR, SCREENSHOTS_DIR]:
        try:
            os.makedirs(dir_path, exist_ok=True)
        except:
            errors.append(f"Не удалось создать директорию: {dir_path}")
    
    return len(errors) == 0, errors
