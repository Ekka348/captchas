#!/usr/bin/env python3
"""
🛠️ Помощник для определения координат на экране
Интерактивный инструмент для настройки координат
"""

import pyautogui
import time
import json
import os
from datetime import datetime

def print_header():
    """Вывод заголовка"""
    print("="*60)
    print("🖱️  ПОМОЩНИК ДЛЯ ОПРЕДЕЛЕНИЯ КООРДИНАТ")
    print("="*60)
    print("\n⚠️  Внимание: Эта утилита работает только на локальной машине!")
    print("   Для сервера используйте предустановленные координаты.\n")

def get_mouse_position(prompt: str) -> tuple:
    """Получение позиции мыши с ожиданием пользователя"""
    print(prompt)
    print("   Наведите курсор и нажмите Enter...")
    
    input("   Готовы? Нажмите Enter чтобы начать отсчет: ")
    
    print("   Отсчет: ", end="")
    for i in range(3, 0, -1):
        print(f"{i}... ", end="", flush=True)
        time.sleep(1)
    print("ЗАПИСАНО!")
    
    x, y = pyautogui.position()
    print(f"   Координаты: ({x}, {y})")
    
    return (x, y)

def get_region_coordinates():
    """Получение координат области"""
    print("\n" + "="*60)
    print("📐 ОПРЕДЕЛЕНИЕ ОБЛАСТИ КАПЧИ")
    print("="*60)
    
    print("\n1. Верхний левый угол области с капчой:")
    x1, y1 = get_mouse_position("   Наведите курсор в ВЕРХНИЙ ЛЕВЫЙ УГОЛ")
    
    print("\n2. Нижний правый угол области с капчой:")
    x2, y2 = get_mouse_position("   Наведите курсор в НИЖНИЙ ПРАВЫЙ УГОЛ")
    
    # Вычисляем координаты области
    x = min(x1, x2)
    y = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    
    print(f"\n✅ Область капчи определена:")
    print(f"   X: {x}, Y: {y}, Ширина: {width}, Высота: {height}")
    
    return (x, y, width, height)

def get_point_coordinates(point_name: str, description: str) -> tuple:
    """Получение координат точки"""
    print(f"\n🎯 ОПРЕДЕЛЕНИЕ {point_name.upper()}")
    print("-"*40)
    print(f"   {description}")
    
    x, y = get_mouse_position(f"   Наведите курсор в ЦЕНТР {point_name}")
    
    print(f"✅ {point_name} определен:")
    print(f"   Координаты: ({x}, {y})")
    
    return (x, y)

def preview_coordinates(region: tuple, input_coords: tuple, button_coords: tuple):
    """Предпросмотр координат"""
    print("\n" + "="*60)
    print("👁️  ПРЕДПРОСМОТР КООРДИНАТ")
    print("="*60)
    
    # Создаем ASCII визуализацию
    print("\nВизуализация областей на экране:")
    print("┌──────────────────────────────────────┐")
    print("│  🎯 Капча: [══════════════════════]  │")
    print("│  ✏️  Поле: [■]                      │")
    print("│  📌 Кнопка: [●]                    │")
    print("└──────────────────────────────────────┘")
    
    print(f"\n📊 Координаты:")
    print(f"  Капча:      X={region[0]}, Y={region[1]}, W={region[2]}, H={region[3]}")
    print(f"  Поле ввода: X={input_coords[0]}, Y={input_coords[1]}")
    print(f"  Кнопка:     X={button_coords[0]}, Y={button_coords[1]}")
    
    # Проверка расстояний
    from math import sqrt
    dist_input_button = sqrt(
        (button_coords[0] - input_coords[0])**2 + 
        (button_coords[1] - input_coords[1])**2
    )
    
    print(f"\n📏 Расстояния:")
    print(f"  От поля до кнопки: {dist_input_button:.1f} px")
    
    if dist_input_button < 50:
        print("  ⚠️  Слишком близко! Убедитесь что это разные элементы.")
    elif dist_input_button > 500:
        print("  ⚠️  Слишком далеко! Проверьте координаты.")

def save_coordinates(region: tuple, input_coords: tuple, button_coords: tuple):
    """Сохранение координат в файл"""
    print("\n" + "="*60)
    print("💾 СОХРАНЕНИЕ КООРДИНАТ")
    print("="*60)
    
    # Создаем данные для сохранения
    data = {
        "captcha_region": region,
        "input_coords": input_coords,
        "button_coords": button_coords,
        "created_at": datetime.now().isoformat(),
        "screen_size": pyautogui.size()
    }
    
    # Сохраняем в JSON
    try:
        os.makedirs("data", exist_ok=True)
        
        with open("data/coordinates.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print("✅ Координаты сохранены в data/coordinates.json")
        
        # Создаем Python конфиг
        config_content = f'''
# Автоматически сгенерированные координаты
CAPTCHA_REGION = {region}
INPUT_COORDS = {input_coords}
BUTTON_COORDS = {button_coords}
'''
        
        print("\n📋 Для config.py используйте:")
        print(config_content)
        
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")

def test_coordinates(region: tuple, input_coords: tuple, button_coords: tuple):
    """Тестирование координат"""
    print("\n" + "="*60)
    print("🧪 ТЕСТИРОВАНИЕ КООРДИНАТ")
    print("="*60)
    
    choice = input("\nЗапустить тест? (y/n): ").lower()
    
    if choice != 'y':
        return
    
    try:
        print("\n🔄 Тест 1: Перемещение к полю ввода...")
        pyautogui.moveTo(input_coords[0], input_coords[1], duration=1)
        time.sleep(1)
        
        print("🔄 Тест 2: Клик по полю...")
        pyautogui.click()
        time.sleep(0.5)
        
        print("🔄 Тест 3: Ввод тестового текста...")
        pyautogui.write("TEST", interval=0.1)
        time.sleep(0.5)
        
        print("🔄 Тест 4: Перемещение к кнопке...")
        pyautogui.moveTo(button_coords[0], button_coords[1], duration=1)
        time.sleep(1)
        
        print("🔄 Тест 5: Клик по кнопке...")
        pyautogui.click()
        
        print("\n✅ Тест завершен! Проверьте действия на экране.")
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")

def main():
    """Основная функция"""
    try:
        print_header()
        
        # Проверка доступности pyautogui
        screen_size = pyautogui.size()
        print(f"📺 Размер экрана: {screen_size.width}x{screen_size.height}")
        
        # Получение координат
        region = get_region_coordinates()
        input_coords = get_point_coordinates(
            "поля ввода", 
            "Центр поля куда нужно вводить текст капчи"
        )
        button_coords = get_point_coordinates(
            "кнопки отправки", 
            "Центр кнопки для отправки решения"
        )
        
        # Предпросмотр
        preview_coordinates(region, input_coords, button_coords)
        
        # Сохранение
        save_coordinates(region, input_coords, button_coords)
        
        # Тестирование
        test_coordinates(region, input_coords, button_coords)
        
        print("\n" + "="*60)
        print("🎯 КООРДИНАТЫ ОПРЕДЕЛЕНЫ УСПЕШНО!")
        print("="*60)
        print("\nСкопируйте значения в config.py и перезапустите бота.")
        print("\nНажмите Enter для выхода...")
        input()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Отменено пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        print("\nНажмите Enter для выхода...")
        input()

if __name__ == "__main__":
    main()
