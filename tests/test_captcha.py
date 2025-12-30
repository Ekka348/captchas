#!/usr/bin/env python3
"""
Тесты для Captcha AutoBot
"""

import unittest
import numpy as np
import cv2
from pathlib import Path
import sys
import os

# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from captcha_bot import CaptchaAutoBot
except ImportError:
    print("Ошибка импорта модулей. Запустите из корневой директории проекта.")
    sys.exit(1)


class TestCaptchaProcessing(unittest.TestCase):
    """Тесты обработки капчи"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.bot = CaptchaAutoBot()
        
        # Создаем тестовое изображение
        self.test_image = np.zeros((100, 300, 3), dtype=np.uint8)
        cv2.putText(self.test_image, "TEST123", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    def test_image_enhancement(self):
        """Тест улучшения изображения"""
        enhanced = self.bot.enhance_image(self.test_image)
        
        # Проверяем, что изображение стало одноканальным
        self.assertEqual(len(enhanced.shape), 2)
        
        # Проверяем размеры
        self.assertEqual(enhanced.shape[0], 100)
        self.assertEqual(enhanced.shape[1], 300)
    
    def test_recognize_simple_text(self):
        """Тест распознавания простого текста"""
        # Создаем более четкое изображение для теста
        clear_image = np.ones((50, 200), dtype=np.uint8) * 255
        cv2.putText(clear_image, "ABCD", (20, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, 0, 2)
        
        # Распознаем
        text = self.bot.recognize_captcha(clear_image)
        
        # Проверяем, что получили текст
        self.assertIsNotNone(text)
        self.assertGreater(len(text), 0)
    
    def test_config_import(self):
        """Тест импорта конфигурации"""
        try:
            from config import CAPTCHA_REGION, INPUT_COORDS
            self.assertTrue(len(CAPTCHA_REGION) == 4)
            self.assertTrue(len(INPUT_COORDS) == 2)
        except ImportError:
            self.fail("Не удалось импортировать конфигурацию")


class TestUtilities(unittest.TestCase):
    """Тесты вспомогательных функций"""
    
    def test_save_preview(self):
        """Тест сохранения превью"""
        bot = CaptchaAutoBot()
        
        # Создаем тестовые изображения
        original = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        processed = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        
        # Пытаемся сохранить
        bot.save_captcha_preview(original, processed, "TEST")
        
        # Проверяем, что директория создана
        self.assertTrue(Path("screenshots").exists())


def run_tests():
    """Запуск всех тестов"""
    # Создаем тестовый runner
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestCaptchaProcessing)
    suite.addTests(loader.loadTestsFromTestCase(TestUtilities))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Запуск тестов Captcha AutoBot...")
    print("="*50)
    
    success = run_tests()
    
    print("="*50)
    if success:
        print("✓ Все тесты пройдены успешно!")
    else:
        print("✗ Некоторые тесты не пройдены")
    
    sys.exit(0 if success else 1)
