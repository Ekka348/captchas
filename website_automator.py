#!/usr/bin/env python3
"""
🌐 Автоматизатор сайтов для решения капч
Сам находит, распознает и решает капчи
"""

import time
import random
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from browser_controller import BrowserController
from image_processor import ImageProcessor
from rucaptcha_api import RucaptchaSolver
from config import RUCAPTCHA_API_KEY

logger = logging.getLogger('WebsiteAutomator')

class WebsiteAutomator:
    """Автоматизатор для работы с сайтами капч"""
    
    def __init__(self, api_key: str = RUCAPTCHA_API_KEY):
        self.browser = BrowserController(headless=False)  # Для отладки лучше видно
        self.image_processor = ImageProcessor()
        self.captcha_solver = RucaptchaSolver(api_key)
        self.is_running = False
        self.stats = {
            'captchas_solved': 0,
            'total_earnings': 0.0,
            'errors': 0,
            'start_time': None,
            'current_site': None
        }
        
    def start(self, target_url: str):
        """Запуск автоматизации на сайте"""
        try:
            self.is_running = True
            self.stats['start_time'] = datetime.now()
            self.stats['current_site'] = target_url
            
            logger.info(f"🚀 Запуск автоматизации на {target_url}")
            
            # Открываем сайт
            if not self.browser.open_url(target_url):
                logger.error("Не удалось открыть сайт")
                return False
            
            # Основной цикл работы
            while self.is_running:
                try:
                    self._work_cycle()
                    
                    # Случайная пауза между капчами
                    time.sleep(random.uniform(5, 15))
                    
                except KeyboardInterrupt:
                    logger.info("Остановка по запросу пользователя")
                    break
                except Exception as e:
                    logger.error(f"Ошибка в рабочем цикле: {e}")
                    time.sleep(10)
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска: {e}")
            return False
    
    def _work_cycle(self):
        """Один рабочий цикл: найти, решить, отправить"""
        logger.info("🔄 Начинаю рабочий цикл...")
        
        # 1. Поиск капчи на странице
        captcha_element = self._find_captcha_element()
        if not captcha_element:
            logger.warning("Капча не найдена на странице")
            
            # Проверяем, может быть уже решена и нужно нажать кнопку
            if self._check_for_next_button():
                self._click_next_button()
                time.sleep(random.uniform(3, 7))
            return
        
        # 2. Делаем скриншот капчи
        captcha_image = self._capture_captcha(captcha_element)
        if not captcha_image:
            logger.error("Не удалось получить изображение капчи")
            return
        
        # 3. Обрабатываем изображение
        processed_image = self.image_processor.preprocess_captcha(captcha_image)
        if not processed_image:
            logger.error("Не удалось обработать изображение капчи")
            return
        
        # 4. Конвертируем в base64 для API
        image_base64 = self.image_processor.image_to_base64(processed_image)
        if not image_base64:
            logger.error("Не удалось конвертировать изображение")
            return
        
        # 5. Решаем капчу через API
        logger.info("🔍 Отправляю капчу на распознавание...")
        solution = self.captcha_solver.solve_image_captcha(image_base64)
        
        if not solution:
            logger.error("Не удалось решить капчу")
            self.stats['errors'] += 1
            return
        
        logger.info(f"✅ Решение капчи: {solution}")
        
        # 6. Находим поле ввода
        input_field = self._find_input_field()
        if not input_field:
            logger.error("Не найден input для ввода капчи")
            return
        
        # 7. Вводим решение
        self._type_solution(input_field, solution)
        
        # 8. Находим и нажимаем кнопку отправки
        submit_button = self._find_submit_button()
        if submit_button:
            self._click_submit_button(submit_button)
        else:
            logger.warning("Кнопка отправки не найдена, пытаемся нажать Enter")
            input_field.send_keys("\n")
        
        # 9. Обновляем статистику
        self.stats['captchas_solved'] += 1
        self.stats['total_earnings'] += 0.0003  # Примерная цена за капчу
        
        # 10. Ждем обновления страницы
        time.sleep(random.uniform(2, 4))
        
        logger.info(f"🎯 Капча #{self.stats['captchas_solved']} решена!")
    
    def _find_captcha_element(self) -> Optional[Any]:
        """Поиск элемента капчи на странице"""
        # Попробуем различные селекторы для капч
        captcha_selectors = [
            "img[src*='captcha']",
            "img[src*='captcha']",
            ".captcha img",
            "#captcha img",
            "div.captcha-container img",
            "img.captcha",
            "img#captcha",
            "div[class*='captcha'] img",
            "img[onclick*='captcha']",
            "img[alt*='captcha' i]",
            "img[title*='captcha' i]",
        ]
        
        for selector in captcha_selectors:
            element = self.browser.find_element(selector)
            if element:
                logger.info(f"Найдена капча: {selector}")
                return element
        
        # Если не нашли по селекторам, ищем по src
        all_images = self.browser.find_elements("img")
        for img in all_images:
            src = img.get_attribute("src") or ""
            if any(keyword in src.lower() for keyword in ['captcha', 'code', 'security', 'verify']):
                logger.info("Найдена капча по src атрибуту")
                return img
        
        return None
    
    def _capture_captcha(self, element) -> Optional[bytes]:
        """Скриншот элемента капчи"""
        try:
            # Получаем координаты элемента
            location = element.location
            size = element.size
            
            # Делаем скриншот всего экрана
            screenshot = self.browser.get_screenshot()
            if not screenshot:
                return None
            
            # В реальности здесь нужно использовать PIL для обрезки
            # Для простоты используем метод элемента
            return element.screenshot_as_png
            
        except Exception as e:
            logger.error(f"Ошибка при скриншоте капчи: {e}")
            return None
    
    def _find_input_field(self) -> Optional[Any]:
        """Поиск поля для ввода капчи"""
        input_selectors = [
            "input[name='captcha']",
            "input[name='captcha_code']",
            "input[placeholder*='captcha' i]",
            "input[placeholder*='code' i]",
            "input[placeholder*='введите' i]",
            "input#captcha",
            "input.captcha-input",
            "input[type='text'][name*='captcha']",
            "input[type='text'][id*='captcha']",
        ]
        
        for selector in input_selectors:
            element = self.browser.find_element(selector)
            if element:
                logger.info(f"Найдено поле ввода: {selector}")
                return element
        
        # Ищем все текстовые поля
        all_inputs = self.browser.find_elements("input[type='text']")
        for inp in all_inputs:
            placeholder = inp.get_attribute("placeholder") or ""
            name = inp.get_attribute("name") or ""
            id_attr = inp.get_attribute("id") or ""
            
            if any(keyword in placeholder.lower() for keyword in ['captcha', 'code', 'введите']) or \
               any(keyword in name.lower() for keyword in ['captcha', 'code']) or \
               any(keyword in id_attr.lower() for keyword in ['captcha', 'code']):
                logger.info("Найдено поле ввода по атрибутам")
                return inp
        
        return None
    
    def _find_submit_button(self) -> Optional[Any]:
        """Поиск кнопки отправки"""
        button_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:contains('Submit')",
            "button:contains('Отправить')",
            "button:contains('Проверить')",
            "input[value*='Submit']",
            "input[value*='отправить' i]",
            ".submit-btn",
            "#submit-btn",
            "form button",
            "form input[type='button']",
        ]
        
        for selector in button_selectors:
            element = self.browser.find_element(selector)
            if element:
                logger.info(f"Найдена кнопка отправки: {selector}")
                return element
        
        return None
    
    def _type_solution(self, input_field, solution: str):
        """Ввод решения капчи с человеческим поведением"""
        try:
            # Кликаем на поле
            input_field.click()
            time.sleep(random.uniform(0.2, 0.5))
            
            # Очищаем поле если нужно
            input_field.clear()
            time.sleep(random.uniform(0.1, 0.3))
            
            # Вводим текст посимвольно для естественности
            for char in solution:
                input_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            # Случайная пауза перед отправкой
            time.sleep(random.uniform(0.3, 0.8))
            
            logger.info(f"Введен текст: {solution}")
            
        except Exception as e:
            logger.error(f"Ошибка при вводе текста: {e}")
    
    def _click_submit_button(self, button):
        """Клик по кнопке отправки"""
        try:
            # Пауза перед кликом
            time.sleep(random.uniform(0.3, 0.7))
            
            # Прокручиваем к кнопке
            self.browser.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                button
            )
            time.sleep(random.uniform(0.2, 0.5))
            
            # Клик
            button.click()
            logger.info("Клик по кнопке отправки")
            
        except Exception as e:
            logger.error(f"Ошибка при клике на кнопку: {e}")
    
    def _check_for_next_button(self) -> bool:
        """Проверка наличия кнопки 'Далее' или 'Следующая'"""
        next_selectors = [
            "button:contains('Next')",
            "button:contains('Далее')",
            "button:contains('Продолжить')",
            "button:contains('Следующая')",
            "a:contains('Next')",
            "a:contains('Далее')",
        ]
        
        for selector in next_selectors:
            if self.browser.find_element(selector):
                return True
        
        return False
    
    def _click_next_button(self):
        """Клик по кнопке 'Далее'"""
        next_selectors = [
            "button:contains('Next')",
            "button:contains('Далее')",
            "button:contains('Продолжить')",
            "a:contains('Next')",
            "a:contains('Далее')",
        ]
        
        for selector in next_selectors:
            button = self.browser.find_element(selector)
            if button:
                button.click()
                time.sleep(random.uniform(1, 3))
                logger.info("Нажата кнопка 'Далее'")
                return
    
    def stop(self):
        """Остановка автоматизации"""
        self.is_running = False
        self.browser.close()
        logger.info("Автоматизация остановлена")
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики"""
        if self.stats['start_time']:
            runtime = datetime.now() - self.stats['start_time']
            self.stats['runtime'] = str(runtime).split('.')[0]
        
        return self.stats
