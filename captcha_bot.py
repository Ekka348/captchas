#!/usr/bin/env python3
"""
CAPTCHA AUTOBOT - ФИНАЛЬНАЯ РАБОЧАЯ ВЕРСИЯ
Автоматический ввод капчи с полным циклом:
1. Захват капчи (688,451 596x89)
2. Распознавание текста
3. Ввод в поле (983,560)
4. Клик по кнопке (1136,622)
5. Пауза 3 сек → повтор
"""

import pyautogui
import pytesseract
import time
import cv2
import numpy as np
import logging
import sys
from datetime import datetime

# Импорт конфигурации
try:
    from config import (
        CAPTCHA_REGION,
        INPUT_COORDS,
        BUTTON_COORDS,
        CHECK_INTERVAL,
        CLICK_DELAY,
        TYPE_INTERVAL,
        MIN_CAPTCHA_LENGTH,
        MAX_CAPTCHA_LENGTH,
        CONFIDENCE_THRESHOLD,
        ENHANCE_IMAGE,
        LOG_LEVEL,
        LOG_FORMAT,
        validate_config
    )
except ImportError as e:
    print(f"Ошибка загрузки конфигурации: {e}")
    sys.exit(1)

class CaptchaBot:
    def __init__(self):
        """Инициализация бота"""
        self.setup_logging()
        self.check_dependencies()
        
        self.cycle = 0
        self.success = 0
        self.start_time = time.time()
        
        self.logger.info("="*60)
        self.logger.info("CAPTCHA AUTOBOT ЗАПУЩЕН")
        self.logger.info("="*60)
        self.logger.info(f"Капча: область {CAPTCHA_REGION}")
        self.logger.info(f"Поле ввода: клик в {INPUT_COORDS}")
        self.logger.info(f"Кнопка: клик в {BUTTON_COORDS}")
        self.logger.info(f"Интервал: {CHECK_INTERVAL} сек")
        self.logger.info("="*60)
    
    def setup_logging(self):
        """Настройка системы логирования"""
        self.logger = logging.getLogger("CaptchaBot")
        
        # Уровень логирования
        level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # Форматтер
        formatter = logging.Formatter(LOG_FORMAT)
        
        # Консольный вывод
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def check_dependencies(self):
        """Проверка зависимостей"""
        try:
            pytesseract.get_tesseract_version()
            self.logger.debug("✓ Tesseract доступен")
        except:
            self.logger.error("✗ Tesseract не найден!")
            self.logger.error("Установите: https://github.com/UB-Mannheim/tesseract/wiki")
            sys.exit(1)
    
    def capture_captcha(self):
        """Захват области с капчей"""
        try:
            screenshot = pyautogui.screenshot(region=CAPTCHA_REGION)
            return np.array(screenshot)
        except Exception as e:
            self.logger.error(f"Ошибка захвата: {e}")
            return None
    
    def process_image(self, image):
        """Обработка изображения капчи"""
        if not ENHANCE_IMAGE:
            return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        try:
            # Конвертация в градации серого
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Увеличение контраста
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # Бинаризация
            _, binary = cv2.threshold(enhanced, 0, 255, 
                                     cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            return binary
        except Exception as e:
            self.logger.warning(f"Ошибка обработки: {e}, использую оригинал")
            return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    def recognize_text(self, image):
        """Распознавание текста на капче"""
        try:
            # Основная конфигурация для смешанных символов
            configs = [
                '--oem 3 --psm 8',  # Одна строка
                '--oem 3 --psm 7',  # Альтернативный режим
            ]
            
            best_text = ""
            best_confidence = 0
            
            for config in configs:
                # Получаем детальные данные для оценки уверенности
                data = pytesseract.image_to_data(
                    image, config=config, 
                    output_type=pytesseract.Output.DICT
                )
                
                # Собираем текст из символов с высокой уверенностью
                text_parts = []
                confidences = []
                
                for i in range(len(data['text'])):
                    text = data['text'][i].strip()
                    conf = int(data['conf'][i])
                    
                    if text and conf >= CONFIDENCE_THRESHOLD:
                        text_parts.append(text)
                        confidences.append(conf)
                
                if text_parts:
                    text = ''.join(text_parts)
                    avg_conf = sum(confidences) / len(confidences)
                    
                    if (avg_conf > best_confidence and 
                        MIN_CAPTCHA_LENGTH <= len(text) <= MAX_CAPTCHA_LENGTH):
                        best_confidence = avg_conf
                        best_text = text
            
            # Если не нашли с хорошей уверенностью, пробуем простой способ
            if not best_text or best_confidence < 50:
                simple_text = pytesseract.image_to_string(
                    image, config='--oem 3 --psm 8'
                )
                # Очищаем: оставляем только печатные символы
                simple_text = ''.join(
                    c for c in simple_text 
                    if c.isprintable() and not c.isspace()
                )
                
                if (simple_text and 
                    MIN_CAPTCHA_LENGTH <= len(simple_text) <= MAX_CAPTCHA_LENGTH):
                    return simple_text
            
            # Окончательная очистка
            if best_text:
                cleaned = ''.join(
                    c for c in best_text 
                    if c.isprintable() and not c.isspace()
                )
                return cleaned
            
            return None
            
        except Exception as e:
            self.logger.error(f"Ошибка распознавания: {e}")
            return None
    
    def input_text(self, text):
        """Ввод текста в поле"""
        try:
            # Клик в поле ввода
            self.logger.debug(f"Клик в поле: {INPUT_COORDS}")
            pyautogui.click(INPUT_COORDS[0], INPUT_COORDS[1])
            time.sleep(CLICK_DELAY)
            
            # Очистка поля (Ctrl+A, Delete)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(CLICK_DELAY)
            pyautogui.press('delete')
            time.sleep(CLICK_DELAY)
            
            # Ввод текста
            self.logger.debug(f"Ввод: '{text}'")
            for char in text:
                pyautogui.write(char, interval=TYPE_INTERVAL)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка ввода: {e}")
            return False
    
    def click_button(self):
        """Клик по кнопке проверки"""
        try:
            self.logger.debug(f"Клик по кнопке: {BUTTON_COORDS}")
            pyautogui.click(BUTTON_COORDS[0], BUTTON_COORDS[1])
            return True
        except Exception as e:
            self.logger.error(f"Ошибка клика: {e}")
            return False
    
    def run_cycle(self):
        """Выполнение одного полного цикла"""
        self.cycle += 1
        cycle_start = time.time()
        
        self.logger.info(f"\nЦИКЛ #{self.cycle} [{time.strftime('%H:%M:%S')}]")
        
        # 1. ЗАХВАТ КАПЧИ
        self.logger.debug("Захват капчи...")
        original = self.capture_captcha()
        if original is None:
            self.logger.warning("Не удалось захватить капчу")
            return False
        
        # 2. ОБРАБОТКА И РАСПОЗНАВАНИЕ
        self.logger.debug("Обработка изображения...")
        processed = self.process_image(original)
        
        self.logger.debug("Распознавание текста...")
        captcha_text = self.recognize_text(processed)
        
        if not captcha_text:
            self.logger.warning("Не удалось распознать капчу")
            return False
        
        self.logger.info(f"Распознано: '{captcha_text}'")
        
        # 3. ВВОД ТЕКСТА
        self.logger.debug("Ввод в поле...")
        if not self.input_text(captcha_text):
            return False
        
        # 4. КЛИК ПО КНОПКЕ
        self.logger.debug("Клик по кнопке...")
        if not self.click_button():
            return False
        
        # 5. УСПЕШНОЕ ВЫПОЛНЕНИЕ
        self.success += 1
        cycle_time = time.time() - cycle_start
        
        # Статистика
        success_rate = (self.success / self.cycle) * 100
        total_time = time.time() - self.start_time
        avg_time = total_time / self.cycle if self.cycle > 0 else 0
        
        self.logger.info(
            f"✓ Успешно! Время цикла: {cycle_time:.1f}с | "
            f"Успешность: {success_rate:.1f}% | "
            f"Среднее время: {avg_time:.1f}с"
        )
        
        return True
    
    def run(self):
        """Основной цикл работы"""
        try:
            while True:
                success = self.run_cycle()
                
                if success:
                    # Успешный цикл - ждем CHECK_INTERVAL
                    self.logger.debug(f"Ожидание {CHECK_INTERVAL} сек...")
                    time.sleep(CHECK_INTERVAL)
                else:
                    # Ошибка - ждем меньше
                    self.logger.debug("Ожидание 2 сек после ошибки...")
                    time.sleep(2)
                    
        except KeyboardInterrupt:
            self.logger.info("\n" + "="*60)
            self.logger.info("БОТ ОСТАНОВЛЕН")
            self.logger.info("="*60)
            
            # Финальная статистика
            if self.cycle > 0:
                total_time = time.time() - self.start_time
                success_rate = (self.success / self.cycle) * 100
                
                self.logger.info(f"Всего циклов: {self.cycle}")
                self.logger.info(f"Успешных: {self.success}")
                self.logger.info(f"Успешность: {success_rate:.1f}%")
                self.logger.info(f"Общее время: {total_time:.1f} сек")
                self.logger.info(f"Среднее время цикла: {total_time/self.cycle:.1f} сек")
            
            self.logger.info("="*60)
            
        except Exception as e:
            self.logger.error(f"Критическая ошибка: {e}")
            import traceback
            self.logger.error(traceback.format_exc())

def main():
    """Точка входа"""
    # Проверка конфигурации
    if not validate_config():
        print("Проверьте конфигурацию перед запуском!")
        sys.exit(1)
    
    # Запуск бота
    bot = CaptchaBot()
    bot.run()

if __name__ == "__main__":
    main()
