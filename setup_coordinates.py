#!/usr/bin/env python3
"""
🛠️ Утилита для настройки координат областей капчи
"""

import time
import json
import pyautogui
from datetime import datetime

from config import (
    save_coordinates, load_coordinates,
    DATA_DIR, COORDINATES_FILE
)

def print_header():
    """Вывод заголовка"""
    print("="*60)
    print("🛠️  ПОМОЩНИК ДЛЯ ОПРЕДЕЛЕНИЯ КООРДИНАТ")
    print("="*60)
    print("\n⚠️  Внимание: Эта утилита работает только на локальной машине!")
    print("   Для сервера используйте предустановленные координаты.\n")

def get_mouse_position_with_countdown(prompt: str, countdown: int = 3) -> tuple:
    """Получение позиции мыши с обратным отсчетом"""
    print(f"\n{prompt}")
    print(f"Наведите курсор и нажмите Enter...")
    
    input("Готовы? Нажмите Enter чтобы начать отсчет: ")
    
    print("Отсчет: ", end="", flush=True)
    for i in range(countdown, 0, -1):
        print(f"{i}... ", end="", flush=True)
        time.sleep(1)
    print("ЗАПИСАНО!")
    
    x, y = pyautogui.position()
    print(f"Координаты: ({x}, {y})")
    
    return (x, y)

def setup_coordinates_interactive():
    """Интерактивная настройка координат"""
    try:
        print_header()
        
        # Получаем размер экрана
        screen_width, screen_height = pyautogui.size()
        print(f"📺 Размер экрана: {screen_width}x{screen_height}")
        
        print("\n" + "="*60)
        print("📐 ОПРЕДЕЛЕНИЕ ОБЛАСТИ КАПЧИ")
        print("="*60)
        
        # 1. Область капчи
        print("\n1. ВЕРХНИЙ ЛЕВЫЙ УГОЛ области с капчой:")
        x1, y1 = get_mouse_position_with_countdown("Наведите курсор в ВЕРХНИЙ ЛЕВЫЙ УГОЛ")
        
        print("\n2. НИЖНИЙ ПРАВЫЙ УГОЛ области с капчой:")
        x2, y2 = get_mouse_position_with_countdown("Наведите курсор в НИЖНИЙ ПРАВЫЙ УГОЛ")
        
        # Вычисляем координаты области
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        print(f"\n✅ Область капчи определена:")
        print(f"   X: {x}, Y: {y}, Ширина: {width}, Высота: {height}")
        
        # 2. Поле ввода
        print("\n" + "="*60)
        print("⌨️  ОПРЕДЕЛЕНИЕ ПОЛЯ ВВОДА")
        print("="*60)
        
        print("\n3. ЦЕНТР поля для ввода капчи:")
        input_x, input_y = get_mouse_position_with_countdown("Наведите курсор в ЦЕНТР поля ввода")
        
        print(f"\n✅ Поле ввода определено:")
        print(f"   Координаты: ({input_x}, {input_y})")
        
        # 3. Кнопка
        print("\n" + "="*60)
        print("🖱️  ОПРЕДЕЛЕНИЕ КНОПКИ")
        print("="*60)
        
        print("\n4. ЦЕНТР кнопки 'следующая' или 'отправить':")
        button_x, button_y = get_mouse_position_with_countdown("Наведите курсор в ЦЕНТР кнопки")
        
        print(f"\n✅ Кнопка определена:")
        print(f"   Координаты: ({button_x}, {button_y})")
        
        # 4. Предпросмотр
        print("\n" + "="*60)
        print("👁️  ПРЕДПРОСМОТР КООРДИНАТ")
        print("="*60)
        
        # Создаем данные для сохранения
        coordinates = {
            'captcha_region': (x, y, width, height),
            'input_coords': (input_x, input_y),
            'button_coords': (button_x, button_y),
            'screen_size': (screen_width, screen_height),
            'created_at': datetime.now().isoformat()
        }
        
        print(f"\n📊 Ваши координаты:")
        print(f"  Капча:      X={x}, Y={y}, W={width}, H={height}")
        print(f"  Поле ввода: X={input_x}, Y={input_y}")
        print(f"  Кнопка:     X={button_x}, Y={button_y}")
        
        # Проверка расстояний
        import math
        dist_input_button = math.sqrt(
            (button_x - input_x)**2 + 
            (button_y - input_y)**2
        )
        
        print(f"\n📏 Расстояния:")
        print(f"  От поля до кнопки: {dist_input_button:.1f} px")
        
        if dist_input_button < 30:
            print("  ⚠️  Слишком близко! Убедитесь что это разные элементы.")
        elif dist_input_button > 500:
            print("  ⚠️  Слишком далеко! Проверьте координаты.")
        
        # 5. Сохранение
        print("\n" + "="*60)
        print("💾 СОХРАНЕНИЕ КООРДИНАТ")
        print("="*60)
        
        choice = input("\nСохранить эти координаты? (y/n): ").lower()
        
        if choice == 'y':
            if save_coordinates(coordinates):
                print("✅ Координаты сохранены!")
                
                # Показываем где файл
                print(f"\n📁 Файл: {COORDINATES_FILE}")
                
                # Тестовый запуск
                test_choice = input("\nЗапустить тест координат? (y/n): ").lower()
                if test_choice == 'y':
                    test_coordinates(coordinates)
            else:
                print("❌ Ошибка сохранения координат")
        else:
            print("❌ Координаты не сохранены")
        
        print("\n" + "="*60)
        print("🎯 КООРДИНАТЫ ОПРЕДЕЛЕНЫ!")
        print("="*60)
        
        # Показываем как использовать
        print(f"\n📋 Для использования в коде:")
        print(f"CAPTCHA_REGION = ({x}, {y}, {width}, {height})")
        print(f"INPUT_COORDS = ({input_x}, {input_y})")
        print(f"BUTTON_COORDS = ({button_x}, {button_y})")
        
        input("\nНажмите Enter для выхода...")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Отменено пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")

def test_coordinates(coordinates: dict):
    """Тестирование настроенных координат"""
    print("\n" + "="*60)
    print("🧪 ТЕСТИРОВАНИЕ КООРДИНАТ")
    print("="*60)
    
    try:
        region = coordinates['captcha_region']
        input_coords = coordinates['input_coords']
        button_coords = coordinates['button_coords']
        
        print("\n🔄 Тест 1: Перемещение к полю ввода...")
        pyautogui.moveTo(input_coords[0], input_coords[1], duration=1)
        time.sleep(1)
        
        print("🔄 Тест 2: Клик по полю...")
        pyautogui.click()
        time.sleep(0.5)
        
        print("🔄 Тест 3: Ввод тестового текста...")
        pyautogui.write("TEST123", interval=0.1)
        time.sleep(0.5)
        
        print("🔄 Тест 4: Перемещение к кнопке...")
        pyautogui.moveTo(button_coords[0], button_coords[1], duration=1)
        time.sleep(1)
        
        print("🔄 Тест 5: Клик по кнопке...")
        pyautogui.click()
        
        print("\n✅ Тест завершен! Проверьте действия на экране.")
        
        # Тест области капчи
        test_area = input("\nПротестировать область капчи? (y/n): ").lower()
        if test_area == 'y':
            print("🔄 Тест 6: Скриншот области капчи...")
            x, y, width, height = region
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            screenshot.save("test_captcha_area.png")
            print("✅ Скриншот сохранен: test_captcha_area.png")
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")

def view_current_coordinates():
    """Просмотр текущих координат"""
    print("\n" + "="*60)
    print("👁️  ТЕКУЩИЕ КООРДИНАТЫ")
    print("="*60)
    
    coordinates = load_coordinates()
    
    if coordinates:
        region = coordinates.get('captcha_region', 'не настроено')
        input_coords = coordinates.get('input_coords', 'не настроено')
        button_coords = coordinates.get('button_coords', 'не настроено')
        
        print(f"\n📍 Область капчи: {region}")
        print(f"⌨️  Поле ввода: {input_coords}")
        print(f"🖱️  Кнопка: {button_coords}")
        
        if coordinates.get('screen_size'):
            print(f"📺 Размер экрана: {coordinates['screen_size']}")
        
        if coordinates.get('created_at'):
            try:
                created = datetime.fromisoformat(coordinates['created_at'].replace('Z', '+00:00'))
                print(f"📅 Создано: {created.strftime('%Y-%m-%d %H:%M')}")
            except:
                pass
        
        print(f"\n📁 Файл: {COORDINATES_FILE}")
    else:
        print("❌ Координаты не настроены")
    
    print("\n" + "="*60)

def edit_coordinates_manually():
    """Ручное редактирование координат"""
    print("\n" + "="*60)
    print("✏️  РУЧНОЕ РЕДАКТИРОВАНИЕ КООРДИНАТ")
    print("="*60)
    
    current = load_coordinates()
    
    print(f"\nТекущие значения:")
    print(f"1. Область капчи: {current.get('captcha_region', 'не настроено')}")
    print(f"2. Поле ввода: {current.get('input_coords', 'не настроено')}")
    print(f"3. Кнопка: {current.get('button_coords', 'не настроено')}")
    
    choice = input("\nЧто изменить? (1-3 или 0 для отмены): ").strip()
    
    if choice == "1":
        print("\nФормат: x y width height")
        print("Пример: 688 451 596 89")
        new_value = input("Новое значение: ").strip()
        
        try:
            x, y, w, h = map(int, new_value.split())
            current['captcha_region'] = (x, y, w, h)
            print("✅ Обновлено")
        except:
            print("❌ Неверный формат")
            
    elif choice == "2":
        print("\nФормат: x y")
        print("Пример: 983 560")
        new_value = input("Новое значение: ").strip()
        
        try:
            x, y = map(int, new_value.split())
            current['input_coords'] = (x, y)
            print("✅ Обновлено")
        except:
            print("❌ Неверный формат")
            
    elif choice == "3":
        print("\nФормат: x y")
        print("Пример: 1136 622")
        new_value = input("Новое значение: ").strip()
        
        try:
            x, y = map(int, new_value.split())
            current['button_coords'] = (x, y)
            print("✅ Обновлено")
        except:
            print("❌ Неверный формат")
    
    if choice in ["1", "2", "3"]:
        save_coordinates(current)
        print("✅ Координаты сохранены")

def main():
    """Главное меню утилиты"""
    print("="*60)
    print("🛠️  УТИЛИТА НАСТРОЙКИ КООРДИНАТ CAPTCHA AUTOBOT")
    print("="*60)
    
    while True:
        print("\nВыберите действие:")
        print("1. 🎯 Интерактивная настройка координат")
        print("2. 👁️  Просмотр текущих координат")
        print("3. ✏️  Ручное редактирование координат")
        print("4. 🧪 Тестирование текущих координат")
        print("5. 📋 Экспорт координат в Python код")
        print("0. 🚪 Выход")
        
        choice = input("\nВаш выбор (0-5): ").strip()
        
        if choice == "1":
            setup_coordinates_interactive()
            
        elif choice == "2":
            view_current_coordinates()
            
        elif choice == "3":
            edit_coordinates_manually()
            
        elif choice == "4":
            coordinates = load_coordinates()
            if coordinates:
                test_coordinates(coordinates)
            else:
                print("❌ Сначала настройте координаты")
                
        elif choice == "5":
            coordinates = load_coordinates()
            if coordinates:
                print("\n" + "="*60)
                print("📋 КОД ДЛЯ ВСТАВКИ В PYTHON:")
                print("="*60)
                
                region = coordinates['captcha_region']
                input_coords = coordinates['input_coords']
                button_coords = coordinates['button_coords']
                
                print(f"\nCAPTCHA_REGION = {region}")
                print(f"INPUT_COORDS = {input_coords}")
                print(f"BUTTON_COORDS = {button_coords}")
                
                print("\n" + "="*60)
            else:
                print("❌ Сначала настройте координаты")
                
        elif choice == "0":
            print("\n👋 До свидания!")
            break
            
        else:
            print("❌ Неверный выбор")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Отменено пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
