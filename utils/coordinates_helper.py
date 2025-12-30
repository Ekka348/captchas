#!/usr/bin/env python3
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
    
    print("\n1. Определение области капчи:")
    print("   Наведите курсор в ВЕРХНИЙ ЛЕВЫЙ УГОЛ области с капчой")
    input("   Нажмите Enter когда готовы...")
    x1, y1 = pyautogui.position()
    
    print("\n   Наведите курсор в НИЖНИЙ ПРАВЫЙ УГОЛ области с капчой")
    input("   Нажмите Enter когда готовы...")
    x2, y2 = pyautogui.position()
    
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    x = min(x1, x2)
    y = min(y1, y2)
    
    print(f"\n   Область капчи: ({x}, {y}, {width}, {height})")
    
    print("\n2. Определение поля ввода:")
    print("   Наведите курсор в ЦЕНТР поля для ввода капчи")
    input("   Нажмите Enter когда готовы...")
    input_x, input_y = pyautogui.position()
    
    print(f"\n   Поле ввода: ({input_x}, {input_y})")
    
    print("\n3. Определение кнопки отправки:")
    print("   Наведите курсор в ЦЕНТР кнопки отправки/проверки")
    input("   Нажмите Enter когда готовы...")
    button_x, button_y = pyautogui.position()
    
    print(f"\n   Кнопка: ({button_x}, {button_y})")
    
    print("\n" + "="*60)
    print("🎯 ВАШИ КООРДИНАТЫ ДЛЯ config.py:")
    print("="*60)
    print(f"\nCAPTCHA_REGION = ({x}, {y}, {width}, {height})")
    print(f"INPUT_COORDS = ({input_x}, {input_y})")
    print(f"BUTTON_COORDS = ({button_x}, {button_y})")
    print("\n" + "="*60)
    print("\nСкопируйте эти значения в config.py")
    
    return (x, y, width, height), (input_x, input_y), (button_x, button_y)

if __name__ == "__main__":
    try:
        get_coordinates()
        input("\nНажмите Enter для выхода...")
    except KeyboardInterrupt:
        print("\n\n🛑 Отменено пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
