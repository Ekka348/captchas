#!/usr/bin/env python3
"""
Основной скрипт Captcha AutoBot
Автоматически распознает и вводит капчи
"""

import pyautogui
import pytesseract
import time
import cv2
import numpy as np
import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path

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
        CONFIDENCE_THRESHOLD,
        ENHANCE_IMAGE,
        SAVE_PREVIEW,
        PREVIEW_INTERVAL,
        LOG_TO_FILE,
        LOG_LEVEL,
        LOG_FORMAT
    )
except ImportError as e:
    print(f"Ошибка загрузки конфигурации: {e}")
    print("Запустите сначала capture_coordinates.py")
    sys.exit(1)


class CaptchaAutoBot:
    def __init__(self):
        """Инициализация бота"""
        self.setup_logging()
        self.cycle_count = 0
        self.success_count = 0
        self.last_captcha_text = ""
        
        # Проверка Tesseract
        try:
            pytesseract.get_tesseract_version()
            self.logger.info("Tesseract OCR инициализирован")
        except Exception as e:
            self.logger.error(f"Tesseract не найден: {e}")
            self.logger.error("Установите Tesseract OCR:")
            self.logger.error("Windows: https://github.com/UB-Mannheim/tesseract/wiki")
            self.logger.error("Linux: sudo apt install tesseract-ocr")
            self.logger.error("macOS: brew install tesseract")
            sys.exit(1)
    
    def setup_logging(self):
        """Настройка системы логирования"""
        self.logger = logging.getLogger(__name__)
        
        if LOG_LEVEL == "DEBUG":
            level = logging.DEBUG
        elif LOG_LEVEL == "INFO":
            level = logging.INFO
        elif LOG_LEVEL == "WARNING":
            level = logging.WARNING
        elif LOG_LEVEL == "ERROR":
            level = logging.ERROR
        else:
            level = logging.INFO
        
        self.logger.setLevel(level)
        
        # Форматтер
        formatter = logging.Formatter(LOG_FORMAT)
        
        # Консольный handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Файловый handler
        if LOG_TO_FILE:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / f"captcha_bot_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        self.logger.info("Логирование инициализировано")
    
    def capture_screen_region(self):
        """Захват области экрана с капчей"""
        try:
            screenshot = pyautogui.screenshot(region=CAPTCHA_REGION)
            return np.array(screenshot)
        except Exception as e:
            self.logger.error(f"Ошибка захвата экрана: {e}")
            return None
    
    def enhance_image(self, image):
        """Улучшение качества изображения капчи"""
        if not ENHANCE_IMAGE:
            return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        try:
            # Конвертация в градации серого
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Удаление шума
            denoised = cv2.medianBlur(gray, 3)
            
            # Улучшение контраста с помощью CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)
            
            # Бинаризация
            _, binary = cv2.threshold(
                enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
            
            # Удаление мелких шумов
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
            
            return cleaned
            
        except Exception as e:
            self.logger.warning(f"Ошибка улучшения изображения: {e}, использую оригинал")
            return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    def recognize_captcha(self, image):
        """Распознавание текста на капче"""
        try:
            # Пробуем разные конфигурации Tesseract
            configs = [
                '--oem 3 --psm 8',      # Одна строка текста
                '--oem 3 --psm 7',      # Одна строка (альтернативный режим)
                '--oem 3 --psm 13',     # Неструктурированный текст
            ]
            
            best_text = ""
            best_confidence = 0
            
            for config in configs:
                try:
                    # Получаем детальную информацию о распознавании
                    data = pytesseract.image_to_data(
                        image, config=config, output_type=pytesseract.Output.DICT
                    )
                    
                    # Собираем текст с учетом уверенности
                    text_chars = []
                    for char, conf in zip(data['text'], data['conf']):
                        if char.strip() and int(conf) >= CONFIDENCE_THRESHOLD:
                            text_chars.append(char)
                    
                    text = ''.join(text_chars)
                    
                    # Рассчитываем среднюю уверенность
                    confidences = [int(c) for c in data['conf'] if int(c) > 0]
                    avg_confidence = (
                        sum(confidences) / len(confidences) 
                        if confidences else 0
                    )
                    
                    if avg_confidence > best_confidence and len(text) >= MIN_CAPTCHA_LENGTH:
                        best_confidence = avg_confidence
                        best_text = text
                        
                except Exception as e:
                    self.logger.debug(f"Ошибка в конфигурации {config}: {e}")
            
            # Если не нашли с хорошей уверенностью, пробуем простой способ
            if not best_text or best_confidence < 50:
                simple_text = pytesseract.image_to_string(
                    image, config='--oem 3 --psm 8'
                )
                # Очищаем текст
                simple_text = ''.join(
                    c for c in simple_text 
                    if c.isprintable() and not c.isspace()
                )
                
                if simple_text and len(simple_text) >= MIN_CAPTCHA_LENGTH:
                    return simple_text
            
            # Очищаем окончательный результат
            cleaned_text = ''.join(
                c for c in best_text 
                if c.isprintable() and not c.isspace()
            )
            
            return cleaned_text
            
        except Exception as e:
            self.logger.error(f"Ошибка распознавания: {e}")
            return None
    
    def save_captcha_preview(self, original_image, processed_image, captcha_text):
        """Сохранение превью капчи для отладки"""
        if not SAVE_PREVIEW or self.cycle_count % PREVIEW_INTERVAL != 0:
            return
        
        try:
            screenshots_dir = Path("screenshots")
            screenshots_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Сохраняем оригинал
            original_path = screenshots_dir / f"original_{timestamp}.png"
            cv2.imwrite(str(original_path), cv2.cvtColor(original_image, cv2.COLOR_RGB2BGR))
            
            # Сохраняем обработанное изображение
            processed_path = screenshots_dir / f"processed_{timestamp}.png"
            cv2.imwrite(str(processed_path), processed_image)
            
            # Создаем файл с информацией
            info_path = screenshots_dir / f"info_{timestamp}.txt"
            with open(info_path, 'w', encoding='utf-8') as f:
                f.write(f"Время: {datetime.now()}\n")
                f.write(f"Распознанный текст: {captcha_text}\n")
                f.write(f"Цикл: {self.cycle_count}\n")
                f.write(f"Координаты: {CAPTCHA_REGION}\n")
            
            self.logger.debug(f"Сохранены скриншоты: {timestamp}")
            
        except Exception as e:
            self.logger.warning(f"Не удалось сохранить превью: {e}")
    
    def input_captcha_text(self, text):
        """Ввод текста капчи в поле"""
        try:
            # Клик в поле ввода
            self.logger.debug(f"Клик в поле ввода: {INPUT_COORDS}")
            pyautogui.click(INPUT_COORDS[0], INPUT_COORDS[1])
            time.sleep(CLICK_DELAY)
            
            # Очистка поля (Ctrl+A, Delete)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(CLICK_DELAY)
            pyautogui.press('delete')
            time.sleep(CLICK_DELAY)
            
            # Ввод текста посимвольно
            self.logger.debug(f"Ввод текста: {text}")
            for char in text:
                pyautogui.write(char, interval=TYPE_INTERVAL)
            
            self.last_captcha_text = text
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка ввода текста: {e}")
            return False
    
    def click_submit_button(self):
        """Нажатие кнопки проверки"""
        try:
            self.logger.debug(f"Клик по кнопке: {BUTTON_COORDS}")
            pyautogui.click(BUTTON_COORDS[0], BUTTON_COORDS[1])
            return True
        except Exception as e:
            self.logger.error(f"Ошибка клика по кнопке: {e}")
            return False
    
    def run_cycle(self):
        """Выполнение одного цикла обработки"""
        self.cycle_count += 1
        start_time = time.time()
        
        self.logger.info(f"Цикл #{self.cycle_count} начат")
        
        try:
            # 1. Захват капчи
            original_image = self.capture_screen_region()
            if original_image is None:
                self.logger.warning("Не удалось захватить изображение")
                return False
            
            # 2. Обработка изображения
            processed_image = self.enhance_image(original_image)
            
            # 3. Распознавание
            captcha_text = self.recognize_captcha(processed_image)
            
            if not captcha_text or len(captcha_text) < MIN_CAPTCHA_LENGTH:
                self.logger.warning(
                    f"Капча не распознана или слишком короткая: '{captcha_text}'"
                )
                return False
            
            self.logger.info(f"Распознано: '{captcha_text}' (длина: {len(captcha_text)})")
            
            # 4. Сохранение превью
            self.save_captcha_preview(original_image, processed_image, captcha_text)
            
            # 5. Ввод текста
            if not self.input_captcha_text(captcha_text):
                return False
            
            # 6. Нажатие кнопки
            if not self.click_submit_button():
                return False
            
            # 7. Подсчет статистики
            self.success_count += 1
            elapsed_time = time.time() - start_time
            
            self.logger.info(
                f"Цикл #{self.cycle_count} завершен за {elapsed_time:.2f} сек. "
                f"Успешность: {self.success_count}/{self.cycle_count} "
                f"({self.success_count/self.cycle_count*100:.1f}%)"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка в цикле #{self.cycle_count}: {e}")
            self.logger.debug(traceback.format_exc())
            return False
    
    def run(self):
        """Основной цикл работы бота"""
        self.logger.info("="*50)
        self.logger.info("CAPTCHA AUTOBOT ЗАПУЩЕН")
        self.logger.info("="*50)
        self.logger.info(f"Область капчи: {CAPTCHA_REGION}")
        self.logger.info(f"Поле ввода: {INPUT_COORDS}")
        self.logger.info(f"Кнопка: {BUTTON_COORDS}")
        self.logger.info(f"Интервал: {CHECK_INTERVAL} сек")
        self.logger.info("Для остановки нажмите Ctrl+C")
        self.logger.info("="*50)
        
        try:
            while True:
                success = self.run_cycle()
                
                if success:
                    self.logger.info(f"Ожидание {CHECK_INTERVAL} сек...")
                    time.sleep(CHECK_INTERVAL)
                else:
                    # При ошибке ждем меньше
                    self.logger.info("Ожидание 3 сек после ошибки...")
                    time.sleep(3)
                    
        except KeyboardInterrupt:
            self.logger.info("\n" + "="*50)
            self.logger.info("БОТ ОСТАНОВЛЕН ПОЛЬЗОВАТЕЛЕМ")
            self.logger.info("="*50)
            
            if self.cycle_count > 0:
                success_rate = (self.success_count / self.cycle_count) * 100
                self.logger.info(f"Итоговая статистика:")
                self.logger.info(f"  Всего циклов: {self.cycle_count}")
                self.logger.info(f"  Успешных: {self.success_count}")
                self.logger.info(f"  Успешность: {success_rate:.1f}%")
                
        except Exception as e:
            self.logger.error(f"Критическая ошибка: {e}")
            self.logger.debug(traceback.format_exc())


def main():
    """Точка входа"""
    try:
        bot = CaptchaAutoBot()
        bot.run()
    except Exception as e:
        print(f"Критическая ошибка при запуске: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
