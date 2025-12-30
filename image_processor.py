#!/usr/bin/env python3
"""
🖼️ Обработка и распознавание изображений капч
"""

import os
import logging
from typing import Optional
from datetime import datetime

import pytesseract
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import cv2
import numpy as np

from config import (
    TESSERACT_CONFIG, TESSERACT_LANG,
    PREPROCESS_CONFIG, SCREENSHOTS_DIR
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ImageProcessor')

class ImageProcessor:
    """Класс для обработки и распознавания капч"""
    
    def __init__(self):
        self.config = PREPROCESS_CONFIG
        logger.info("✅ Процессор изображений инициализирован")
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Предобработка изображения для лучшего распознавания"""
        try:
            img = image.copy()
            
            # Конвертация в grayscale
            if img.mode != 'L':
                img = img.convert('L')
            
            # Увеличение контраста
            if self.config.get('contrast', 1.0) != 1.0:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(self.config['contrast'])
            
            # Бинаризация (черно-белое)
            threshold = self.config.get('threshold', 150)
            img = img.point(lambda p: 255 if p > threshold else 0)
            
            # Увеличение резкости
            if self.config.get('sharpen', True):
                img = img.filter(ImageFilter.SHARPEN)
            
            # Убираем шум
            if self.config.get('denoise', True):
                img = img.filter(ImageFilter.MedianFilter(size=3))
            
            # Инвертируем если темный текст на светлом фоне
            pixels = np.array(img)
            white_pixels = np.sum(pixels > 128)
            black_pixels = np.sum(pixels <= 128)
            
            if black_pixels > white_pixels:
                img = ImageOps.invert(img)
            
            return img
            
        except Exception as e:
            logger.error(f"Ошибка обработки изображения: {e}")
            return image
    
    def recognize_text(self, image: Image.Image) -> Optional[str]:
        """Распознавание текста с изображения"""
        try:
            # Настройки Tesseract
            custom_config = f'{TESSERACT_CONFIG}'
            
            # Распознавание
            text = pytesseract.image_to_string(
                image,
                config=custom_config,
                lang=TESSERACT_LANG
            )
            
            # Очистка текста
            text = text.strip()
            
            # Убираем лишние символы, оставляем только буквы и цифры
            text = ''.join(c for c in text if c.isalnum())
            
            # Проверяем длину
            if len(text) < 3 or len(text) > 10:
                logger.warning(f"Подозрительная длина текста: {len(text)} символов")
                return None
            
            logger.debug(f"Распознанный текст: '{text}'")
            return text
            
        except Exception as e:
            logger.error(f"Ошибка распознавания текста: {e}")
            return None
    
    def process_and_recognize(self, image: Image.Image) -> Optional[str]:
        """Полный цикл обработки и распознавания"""
        try:
            # Предобработка
            processed_img = self.preprocess_image(image)
            
            # Распознавание
            text = self.recognize_text(processed_img)
            
            # Сохраняем для отладки если включен режим отладки
            if text:
                self._save_debug_images(image, processed_img, text)
            
            return text
            
        except Exception as e:
            logger.error(f"Ошибка в process_and_recognize: {e}")
            return None
    
    def _save_debug_images(self, original: Image.Image, processed: Image.Image, text: str):
        """Сохранение изображений для отладки"""
        try:
            os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            original.save(f"{SCREENSHOTS_DIR}/original_{timestamp}.png")
            processed.save(f"{SCREENSHOTS_DIR}/processed_{timestamp}_{text}.png")
            
            logger.debug(f"Изображения сохранены: {timestamp}")
        except Exception as e:
            logger.error(f"Ошибка сохранения отладочных изображений: {e}")
    
    def test_recognition_from_file(self, filepath: str) -> Optional[str]:
        """Тест распознавания из файла"""
        try:
            if not os.path.exists(filepath):
                logger.error(f"Файл не найден: {filepath}")
                return None
            
            image = Image.open(filepath)
            text = self.process_and_recognize(image)
            
            print(f"\n🔍 ТЕСТ РАСПОЗНАВАНИЯ:")
            print(f"Файл: {filepath}")
            print(f"Результат: '{text}'")
            
            return text
            
        except Exception as e:
            logger.error(f"Ошибка теста распознавания: {e}")
            return None

def test_recognition():
    """Функция для тестирования распознавания"""
    print("\n" + "="*60)
    print("🧪 ТЕСТ РАСПОЗНАВАНИЯ КАПЧИ")
    print("="*60)
    
    processor = ImageProcessor()
    
    # Вариант 1: Сделать скриншот сейчас
    print("\n1. Сделать скриншот сейчас")
    print("2. Использовать существующий файл")
    
    choice = input("\nВаш выбор (1-2): ").strip()
    
    if choice == "1":
        import pyautogui
        from config import load_coordinates
        
        coords = load_coordinates()
        region = coords.get('captcha_region')
        
        if not region:
            print("❌ Координаты не настроены!")
            return
        
        print(f"\n📸 Делаю скриншот области: {region}")
        print("Подготовьте капчу на экране...")
        input("Нажмите Enter когда готовы...")
        
        image = pyautogui.screenshot(region=region)
        
        # Сохраняем оригинал
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"test_captcha_{timestamp}.png"
        image.save(filename)
        print(f"✅ Скриншот сохранен: {filename}")
        
        # Распознавание
        text = processor.process_and_recognize(image)
        print(f"📝 Распознанный текст: '{text}'")
        
    elif choice == "2":
        filepath = input("Введите путь к файлу: ").strip()
        if not filepath:
            filepath = "test_captcha.png"
        
        processor.test_recognition_from_file(filepath)
        
    else:
        print("❌ Неверный выбор")

if __name__ == "__main__":
    test_recognition()
