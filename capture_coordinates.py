#!/usr/bin/env python3
"""
Скрипт для определения координат элементов на экране
Запустите этот скрипт перед использованием основного бота
"""

import pyautogui
import time
import json
import os
from datetime import datetime


class CoordinateCapturer:
    def __init__(self):
        self.coordinates = {}
        self.screen_size = pyautogui.size()
        
    def get_position_with_countdown(self, prompt, countdown=3):
        """Получить позицию курсора с обратным отсчетом"""
        print(f"\n{prompt}")
        print(f"У вас {countdown} секунд...")
        
        for i in range(countdown, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        x, y = pyautogui.position()
        print(f"✓ Захвачено: X={x}, Y={y}")
        return x, y
    
    def capture_captcha_region(self):
        """Захват области капчи"""
        print("\n" + "="*50)
        print("ЗАХВАТ ОБЛАСТИ КАПЧИ")
        print("="*50)
        
        print("1. Наведите курсор в ВЕРХНИЙ ЛЕВЫЙ УГОЛ области с капчой")
        x1, y1 = self.get_position_with_countdown("", 3)
        
        print("\n2. Наведите курсор в НИЖНИЙ ПРАВЫЙ УГОЛ области с капчой")
        x2, y2 = self.get_position_with_countdown("", 3)
        
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        self.coordinates['captcha_region'] = {
            'x': min(x1, x2),
            'y': min(y1, y2),
            'width': width,
            'height': height
        }
        
        print(f"\nОбласть капчи: ({x1}, {y1}) -> ({x2}, {y2})")
        print(f"Размеры: {width}x{height} пикселей")
        
        # Показать предварительный просмотр
        try:
            screenshot = pyautogui.screenshot(region=(
                self.coordinates['captcha_region']['x'],
                self.coordinates['captcha_region']['y'],
                width, height
            ))
            screenshot.save('captcha_preview_tmp.png')
            print("✓ Превью сохранено в captcha_preview_tmp.png")
        except:
            print("⚠ Не удалось сохранить превью")
    
    def capture_input_field(self):
        """Захват поля ввода"""
        print("\n" + "="*50)
        print("ЗАХВАТ ПОЛЯ ВВОДА")
        print("="*50)
        
        print("Наведите курсор в ЦЕНТР поля для ввода капчи")
        x, y = self.get_position_with_countdown("", 3)
        
        self.coordinates['input_field'] = {'x': x, 'y': y}
        print(f"\nПоле ввода: X={x}, Y={y}")
    
    def capture_button(self):
        """Захват кнопки проверки"""
        print("\n" + "="*50)
        print("ЗАХВАТ КНОПКИ ПРОВЕРКИ")
        print("="*50)
        
        print("Наведите курсор в ЦЕНТР кнопки проверки/отправки")
        x, y = self.get_position_with_countdown("", 3)
        
        self.coordinates['button'] = {'x': x, 'y': y}
        print(f"\nКнопка: X={x}, Y={y}")
    
    def save_config(self):
        """Сохранение конфигурации в config.py"""
        config_content = f'''"""
Автоматически сгенерированный конфиг
Создан: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

# Область капчи: (x, y, width, height)
CAPTCHA_REGION = ({self.coordinates['captcha_region']['x']}, 
                  {self.coordinates['captcha_region']['y']}, 
                  {self.coordinates['captcha_region']['width']}, 
                  {self.coordinates['captcha_region']['height']})

# Поле ввода капчи: (x, y)
INPUT_COORDS = ({self.coordinates['input_field']['x']}, 
                {self.coordinates['input_field']['y']})

# Кнопка проверки/отправки: (x, y)
BUTTON_COORDS = ({self.coordinates['button']['x']}, 
                 {self.coordinates['button']['y']})

# Настройки работы
CHECK_INTERVAL = 10
CLICK_DELAY = 0.15
TYPE_INTERVAL = 0.07
MIN_CAPTCHA_LENGTH = 3
CONFIDENCE_THRESHOLD = 60
'''
        
        with open('config.py', 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print("\n" + "="*50)
        print("КОНФИГУРАЦИЯ СОХРАНЕНА")
        print("="*50)
        print("Файл config.py обновлен с вашими координатами")
        print("\nТеперь можно запустить основной скрипт:")
        print("  python captcha_bot.py")
    
    def run(self):
        """Основной процесс захвата координат"""
        print("="*50)
        print("CAPTCHA COORDINATE CAPTURER")
        print("="*50)
        print(f"Размер экрана: {self.screen_size.width}x{self.screen_size.height}")
        print("\nЭтот скрипт поможет определить координаты элементов.")
        print("Следуйте инструкциям на экране.")
        
        input("\nНажмите Enter чтобы начать...")
        
        self.capture_captcha_region()
        self.capture_input_field()
        self.capture_button()
        self.save_config()


if __name__ == "__main__":
    try:
        capturer = CoordinateCapturer()
        capturer.run()
    except KeyboardInterrupt:
        print("\n\n✗ Процесс прерван пользователем")
    except Exception as e:
        print(f"\n⚠ Ошибка: {e}")
