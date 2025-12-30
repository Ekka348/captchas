#!/usr/bin/env python3
"""
🖼️ Обработка изображений для распознавания капч
"""

import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import io
import base64
from typing import Optional, Tuple
import logging

class ImageProcessor:
    """Класс для обработки изображений капч"""
    
    def __init__(self):
        self.logger = logging.getLogger('ImageProcessor')
    
    def load_image(self, image_source) -> Optional[Image.Image]:
        """Загрузка изображения из различных источников"""
        try:
            if isinstance(image_source, str):
                # Путь к файлу
                if image_source.startswith('http'):
                    import requests
                    response = requests.get(image_source)
                    return Image.open(io.BytesIO(response.content))
                else:
                    return Image.open(image_source)
            elif isinstance(image_source, bytes):
                # Байты
                return Image.open(io.BytesIO(image_source))
            elif isinstance(image_source, Image.Image):
                # Уже изображение PIL
                return image_source
            elif isinstance(image_source, np.ndarray):
                # Массив numpy (OpenCV)
                return Image.fromarray(cv2.cvtColor(image_source, cv2.COLOR_BGR2RGB))
            else:
                self.logger.error(f"Неизвестный тип источника: {type(image_source)}")
                return None
        except Exception as e:
            self.logger.error(f"Ошибка загрузки изображения: {e}")
            return None
    
    def preprocess_captcha(self, image_source, target_size: Tuple[int, int] = (300, 100)) -> Optional[Image.Image]:
        """Предобработка изображения капчи для лучшего распознавания"""
        try:
            img = self.load_image(image_source)
            if img is None:
                return None
            
            # Конвертация в RGB если нужно
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 1. Изменение размера
            img = img.resize(target_size, Image.Resampling.LANCZOS)
            
            # 2. Конвертация в grayscale
            img = img.convert('L')
            
            # 3. Повышение контраста
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)  # Увеличение контраста в 2 раза
            
            # 4. Повышение резкости
            img = img.filter(ImageFilter.SHARPEN)
            
            # 5. Бинаризация (черно-белое)
            threshold = 150
            img = img.point(lambda p: 255 if p > threshold else 0)
            
            # 6. Удаление шума (медианный фильтр)
            img = img.filter(ImageFilter.MedianFilter(size=3))
            
            # 7. Инвертирование если белый текст на черном фоне
            pixels = np.array(img)
            white_pixels = np.sum(pixels > 128)
            black_pixels = np.sum(pixels <= 128)
            
            if black_pixels > white_pixels:
                img = Image.fromarray(255 - pixels)
            
            return img
            
        except Exception as e:
            self.logger.error(f"Ошибка предобработки изображения: {e}")
            return None
    
    def extract_captcha_from_screenshot(self, screenshot, region: Tuple[int, int, int, int]) -> Optional[Image.Image]:
        """Извлечение области капчи из скриншота"""
        try:
            if isinstance(screenshot, bytes):
                img = Image.open(io.BytesIO(screenshot))
            elif isinstance(screenshot, Image.Image):
                img = screenshot
            else:
                img = self.load_image(screenshot)
            
            if img is None:
                return None
            
            # Извлечение области (x, y, width, height)
            x, y, w, h = region
            cropped = img.crop((x, y, x + w, y + h))
            
            return cropped
            
        except Exception as e:
            self.logger.error(f"Ошибка извлечения области: {e}")
            return None
    
    def image_to_base64(self, image: Image.Image) -> Optional[str]:
        """Конвертация изображения в base64"""
        try:
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            return img_str
        except Exception as e:
            self.logger.error(f"Ошибка конвертации в base64: {e}")
            return None
    
    def save_image(self, image: Image.Image, filepath: str) -> bool:
        """Сохранение изображения в файл"""
        try:
            image.save(filepath)
            self.logger.debug(f"Изображение сохранено: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка сохранения изображения: {e}")
            return False
    
    def compare_images(self, img1: Image.Image, img2: Image.Image, threshold: float = 0.9) -> float:
        """Сравнение двух изображений"""
        try:
            # Приведение к одинаковому размеру
            img1 = img1.resize((100, 100))
            img2 = img2.resize((100, 100))
            
            # Конвертация в массивы
            arr1 = np.array(img1.convert('L'))
            arr2 = np.array(img2.convert('L'))
            
            # Нормализация
            arr1 = arr1 / 255.0
            arr2 = arr2 / 255.0
            
            # Вычисление схожести
            similarity = np.sum(arr1 * arr2) / np.sqrt(np.sum(arr1**2) * np.sum(arr2**2))
            
            return float(similarity)
            
        except Exception as e:
            self.logger.error(f"Ошибка сравнения изображений: {e}")
            return 0.0
    
    def detect_text_regions(self, image: Image.Image) -> list:
        """Обнаружение регионов с текстом"""
        try:
            # Конвертация в OpenCV формат
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Применение адаптивного порога
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY_INV, 11, 2)
            
            # Поиск контуров
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Фильтрация маленьких регионов
                if w > 10 and h > 10 and w * h > 100:
                    regions.append((x, y, w, h))
            
            return regions
            
        except Exception as e:
            self.logger.error(f"Ошибка обнаружения регионов: {e}")
            return []
    
    def remove_background(self, image: Image.Image) -> Optional[Image.Image]:
        """Удаление фона с изображения"""
        try:
            # Конвертация в массив
            img_array = np.array(image)
            
            # Преобразование в HSV для выделения цвета
            hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
            
            # Создание маски для белого фона
            lower_white = np.array([0, 0, 200])
            upper_white = np.array([180, 30, 255])
            mask = cv2.inRange(hsv, lower_white, upper_white)
            
            # Инвертирование маски
            mask = cv2.bitwise_not(mask)
            
            # Применение маски
            result = cv2.bitwise_and(img_array, img_array, mask=mask)
            
            # Конвертация обратно в PIL
            result_image = Image.fromarray(result)
            
            return result_image
            
        except Exception as e:
            self.logger.error(f"Ошибка удаления фона: {e}")
            return None

# Пример использования
if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)
    
    processor = ImageProcessor()
    
    # Пример загрузки и обработки изображения
    test_image_path = "test_captcha.png"  # Замените на путь к тестовому изображению
    
    try:
        processed = processor.preprocess_captcha(test_image_path)
        if processed:
            processed.save("processed_captcha.png")
            print("✅ Изображение обработано и сохранено")
            
            # Конвертация в base64
            base64_str = processor.image_to_base64(processed)
            if base64_str:
                print(f"Base64 (первые 100 символов): {base64_str[:100]}...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
