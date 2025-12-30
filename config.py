"""
КОНФИГУРАЦИЯ CAPTCHA AUTOBOT - ПОЛНОСТЬЮ ГОТОВА
Все координаты определены:
1. Область капчи: 688.451 596x89
2. Поле ввода: 692.543 582x34
3. Кнопка проверки: 986.602 300x41
"""

# ============================================
# КООРДИНАТЫ ЭЛЕМЕНТОВ - ПОЛНОСТЬЮ ОПРЕДЕЛЕНЫ
# ============================================

# 1. ОБЛАСТЬ КАПЧИ: (x, y, width, height)
CAPTCHA_REGION = (688, 451, 596, 89)          # Ваши данные: 688.451 596x89

# 2. ПОЛЕ ВВОДА КАПЧИ: центр для клика
# Ваши данные: 692.543 582x34
INPUT_FIELD_REGION = (692, 543, 582, 34)      # Область поля
INPUT_FIELD_CENTER_X = 692 + 582 // 2         # Центр X: 692 + 291 = 983
INPUT_FIELD_CENTER_Y = 543 + 34 // 2          # Центр Y: 543 + 17 = 560
INPUT_COORDS = (983, 560)                     # Координаты клика

# 3. КНОПКА ПРОВЕРКИ: центр для клика
# Ваши данные: 986.602 300x41
BUTTON_REGION = (986, 602, 300, 41)           # Область кнопки
BUTTON_CENTER_X = 986 + 300 // 2              # Центр X: 986 + 150 = 1136
BUTTON_CENTER_Y = 602 + 41 // 2               # Центр Y: 602 + 20 = 622
BUTTON_COORDS = (1136, 622)                   # Координаты клика

# ============================================
# НАСТРОЙКИ РАБОТЫ (оптимизированные)
# ============================================

# Тайминги (секунды)
CHECK_INTERVAL = 3           # Пауза после кнопки перед след. проверкой
CLICK_DELAY = 0.1            # Задержка между действиями
TYPE_INTERVAL = 0.05         # Интервал ввода символов

# Настройки распознавания
MIN_CAPTCHA_LENGTH = 4       # Минимальная длина капчи
MAX_CAPTCHA_LENGTH = 8       # Максимальная длина
CONFIDENCE_THRESHOLD = 60    # Порог уверенности Tesseract

# Настройки изображения
ENHANCE_IMAGE = True         # Включить улучшение
SAVE_DEBUG_IMAGES = False    # Сохранять отладочные изображения
DEBUG_INTERVAL = 10          # Каждые 10 циклов

# Логирование
LOG_TO_FILE = False          # True для сохранения в файл
LOG_LEVEL = "INFO"           # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"

# ============================================
# ГЕОМЕТРИЧЕСКИЕ РАСЧЕТЫ (для информации)
# ============================================

# Расстояния между элементами
CAPTCHA_TO_INPUT_Y = INPUT_COORDS[1] - (CAPTCHA_REGION[1] + CAPTCHA_REGION[3])  # ~18px
INPUT_TO_BUTTON_Y = BUTTON_COORDS[1] - INPUT_COORDS[1]                          # ~62px

# Центры для отладки
CAPTCHA_CENTER = (CAPTCHA_REGION[0] + CAPTCHA_REGION[2]//2,
                  CAPTCHA_REGION[1] + CAPTCHA_REGION[3]//2)

# ============================================
# ПРОВЕРКА КОНФИГУРАЦИИ
# ============================================

def validate_config():
    """Проверка корректности всех настроек"""
    print("="*60)
    print("ПРОВЕРКА КОНФИГУРАЦИИ CAPTCHA AUTOBOT")
    print("="*60)
    
    print("\n1. КООРДИНАТЫ ЭЛЕМЕНТОВ:")
    print(f"   Капча: область {CAPTCHA_REGION}")
    print(f"         центр для анализа: {CAPTCHA_CENTER}")
    
    print(f"\n   Поле ввода: область {INPUT_FIELD_REGION}")
    print(f"              центр для клика: {INPUT_COORDS}")
    
    print(f"\n   Кнопка: область {BUTTON_REGION}")
    print(f"          центр для клика: {BUTTON_COORDS}")
    
    print("\n2. РАССТОЯНИЯ:")
    print(f"   Капча → Поле ввода: {CAPTCHA_TO_INPUT_Y}px по вертикали")
    print(f"   Поле → Кнопка: {INPUT_TO_BUTTON_Y}px по вертикали")
    
    print("\n3. РАЗМЕРЫ:")
    print(f"   Капча: {CAPTCHA_REGION[2]}x{CAPTCHA_REGION[3]}px")
    print(f"   Поле: {INPUT_FIELD_REGION[2]}x{INPUT_FIELD_REGION[3]}px")
    print(f"   Кнопка: {BUTTON_REGION[2]}x{BUTTON_REGION[3]}px")
    
    # Проверка логики
    print("\n4. ПРОВЕРКИ:")
    
    issues = []
    
    # Проверка: капча выше поля ввода
    if CAPTCHA_REGION[1] + CAPTCHA_REGION[3] > INPUT_FIELD_REGION[1]:
        issues.append("Капча находится ниже поля ввода - необычно!")
    else:
        print("   ✓ Капча выше поля ввода (логично)")
    
    # Проверка: поле выше кнопки
    if INPUT_FIELD_REGION[1] + INPUT_FIELD_REGION[3] > BUTTON_REGION[1]:
        issues.append("Поле ввода ниже кнопки - необычно!")
    else:
        print("   ✓ Поле ввода выше кнопки (логично)")
    
    # Проверка размеров
    if CAPTCHA_REGION[2] < 100 or CAPTCHA_REGION[3] < 30:
        issues.append("Область капчи слишком мала для распознавания")
    else:
        print("   ✓ Размер области капчи достаточный")
    
    if INPUT_FIELD_REGION[2] < 100:
        issues.append("Поле ввода слишком узкое")
    else:
        print("   ✓ Поле ввода достаточно широкое")
    
    if BUTTON_REGION[2] < 50:
        issues.append("Кнопка слишком маленькая")
    else:
        print("   ✓ Кнопка достаточно большая")
    
    print("\n" + "="*60)
    
    if issues:
        print("ВНИМАНИЕ! Обнаружены проблемы:")
        for issue in issues:
            print(f"   ⚠ {issue}")
        return False
    else:
        print("✓ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО")
        print("\nКонфигурация готова к работе!")
        return True

if __name__ == "__main__":
    print("FINAL CONFIG - READY TO USE")
    print()
    
    if validate_config():
        print("\nСкрипт готов к запуску:")
        print("python captcha_bot.py")
    else:
        print("\nПожалуйста, проверьте координаты!")
    
    print("="*60)
