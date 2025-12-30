"""
Конфигурационный файл для Captcha AutoBot
Замените координаты на свои после запуска capture_coordinates.py
"""

# ============================================
# КООРДИНАТЫ ЭЛЕМЕНТОВ (заполните свои значения)
# ============================================

# Область капчи: (x, y, width, height)
CAPTCHA_REGION = (100, 200, 300, 100)

# Поле ввода капчи: (x, y)
INPUT_COORDS = (150, 350)

# Кнопка проверки/отправки: (x, y)
BUTTON_COORDS = (400, 350)

# ============================================
# НАСТРОЙКИ РАБОТЫ
# ============================================

# Интервалы времени (в секундах)
CHECK_INTERVAL = 10          # Пауза между циклами проверки
CLICK_DELAY = 0.15           # Задержка между кликами
TYPE_INTERVAL = 0.07         # Интервал между вводом символов

# Настройки распознавания
MIN_CAPTCHA_LENGTH = 3       # Минимальная длина распознанной капчи
CONFIDENCE_THRESHOLD = 60    # Порог уверенности Tesseract (0-100)

# Настройки улучшения изображения
ENHANCE_IMAGE = True         # Включить улучшение изображения
SAVE_PREVIEW = True          # Сохранять превью капчи для отладки
PREVIEW_INTERVAL = 5         # Сохранять превью каждые N циклов

# Настройки логирования
LOG_TO_FILE = True           # Сохранять логи в файл
LOG_LEVEL = "INFO"           # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# ============================================
# ПРОВЕРКА КОНФИГУРАЦИИ
# ============================================

def validate_config():
    """Проверяет корректность настроек"""
    errors = []
    
    # Проверка координат
    if CAPTCHA_REGION[2] <= 0 or CAPTCHA_REGION[3] <= 0:
        errors.append("Некорректные размеры области капчи")
    
    if not all(isinstance(coord, (int, float)) for coord in CAPTCHA_REGION):
        errors.append("Координаты области капчи должны быть числами")
    
    # Проверка интервалов
    if CHECK_INTERVAL < 1:
        errors.append("CHECK_INTERVAL должен быть >= 1 секунды")
    
    if CONFIDENCE_THRESHOLD < 0 or CONFIDENCE_THRESHOLD > 100:
        errors.append("CONFIDENCE_THRESHOLD должен быть от 0 до 100")
    
    return errors

if __name__ == "__main__":
    errors = validate_config()
    if errors:
        print("Ошибки в конфигурации:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Конфигурация корректна")
