#!/usr/bin/env python3
"""
🎯 Основной решатель капч по фиксированным координатам
"""

import time
import json
import random
import logging
from datetime import datetime
from typing import Optional, Dict, Any

import pyautogui
from PIL import Image

from config import (
    load_coordinates, save_settings, load_settings,
    DELAY_BETWEEN_CAPTCHAS_MIN, DELAY_BETWEEN_CAPTCHAS_MAX,
    DELAY_TYPING_MIN, DELAY_TYPING_MAX,
    DELAY_CLICK_MIN, DELAY_CLICK_MAX,
    MOUSE_MOVE_DURATION_MIN, MOUSE_MOVE_DURATION_MAX,
    MOUSE_ACCURACY, DATA_DIR, STATS_FILE
)
from image_processor import ImageProcessor
from mouse_controller import MouseController

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/solver.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ScreenSolver')

class ScreenCaptchaSolver:
    """Основной класс для решения капч"""
    
    def __init__(self):
        self.is_running = False
        self.image_processor = ImageProcessor()
        self.mouse_controller = MouseController()
        
        # Загружаем конфигурацию
        self.coordinates = load_coordinates()
        self.settings = load_settings()
        
        # Статистика
        self.stats = self._load_stats()
        logger.info("✅ Решатель инициализирован")
    
    def _load_stats(self) -> Dict[str, Any]:
        """Загрузка статистики"""
        try:
            if os.path.exists(STATS_FILE):
                with open(STATS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        
        return {
            'total_solved': 0,
            'total_errors': 0,
            'session_solved': 0,
            'session_errors': 0,
            'last_solution': None,
            'last_error': None,
            'start_time': None,
            'sessions': []
        }
    
    def _save_stats(self):
        """Сохранение статистики"""
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(STATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Ошибка сохранения статистики: {e}")
    
    def capture_captcha(self) -> Optional[Image.Image]:
        """Сделать скриншот области с капчей"""
        try:
            region = self.coordinates['captcha_region']
            screenshot = pyautogui.screenshot(region=region)
            logger.debug(f"Скриншот сделан: {region}")
            return screenshot
        except Exception as e:
            logger.error(f"Ошибка скриншота: {e}")
            return None
    
    def solve_one_captcha(self) -> bool:
        """Решить одну капчу"""
        logger.info("🔄 Обработка капчи...")
        
        # 1. Скриншот
        captcha_image = self.capture_captcha()
        if not captcha_image:
            logger.error("❌ Не удалось сделать скриншот")
            self.stats['total_errors'] += 1
            self.stats['session_errors'] += 1
            self.stats['last_error'] = 'screenshot_failed'
            self._save_stats()
            return False
        
        # 2. Обработка и распознавание
        solution = self.image_processor.process_and_recognize(captcha_image)
        if not solution:
            logger.warning("⚠️ Не удалось распознать капчу")
            self.stats['total_errors'] += 1
            self.stats['session_errors'] += 1
            self.stats['last_error'] = 'recognition_failed'
            
            # Сохраняем скриншот для отладки
            if self.settings.get('save_screenshots', True):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                captcha_image.save(f"screenshots/error_{timestamp}.png")
            
            self._save_stats()
            return False
        
        logger.info(f"📝 Распознано: '{solution}'")
        
        # 3. Ввод текста
        input_coords = self.coordinates['input_coords']
        self.mouse_controller.click_with_variance(input_coords)
        time.sleep(random.uniform(0.2, 0.5))
        
        # Очистка поля
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(random.uniform(0.1, 0.3))
        pyautogui.press('delete')
        time.sleep(random.uniform(0.1, 0.3))
        
        # Ввод текста
        for char in solution:
            pyautogui.write(char)
            time.sleep(random.uniform(DELAY_TYPING_MIN, DELAY_TYPING_MAX))
        
        # 4. Клик по кнопке
        button_coords = self.coordinates['button_coords']
        self.mouse_controller.click_with_variance(button_coords)
        
        # 5. Обновление статистики
        self.stats['total_solved'] += 1
        self.stats['session_solved'] += 1
        self.stats['last_solution'] = solution
        self.stats['last_error'] = None
        
        # Сохраняем успешный скриншот
        if self.settings.get('save_screenshots', True):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            captcha_image.save(f"screenshots/success_{timestamp}_{solution}.png")
        
        logger.info(f"🎯 Капча решена! (#{self.stats['total_solved']})")
        self._save_stats()
        
        return True
    
    def run(self):
        """Основной цикл работы"""
        print("\n" + "="*60)
        print("🚀 ЗАПУСК АВТОМАТИЧЕСКОГО РЕШАТЕЛЯ")
        print("="*60)
        
        # Показываем текущие координаты
        print(f"\n📍 Текущие координаты:")
        print(f"  Капча: {self.coordinates['captcha_region']}")
        print(f"  Поле ввода: {self.coordinates['input_coords']}")
        print(f"  Кнопка: {self.coordinates['button_coords']}")
        print("\n" + "="*60)
        print("⚠️  Убедитесь, что окно с капчами активно!")
        print("⚠️  Для остановки нажмите Ctrl+C")
        print("="*60)
        print("\nНачинаю работу через 3 секунды...")
        time.sleep(3)
        
        self.is_running = True
        self.stats['start_time'] = datetime.now().isoformat()
        
        try:
            while self.is_running:
                success = self.solve_one_captcha()
                
                if success:
                    # Случайная пауза между капчами
                    delay = random.uniform(
                        DELAY_BETWEEN_CAPTCHAS_MIN,
                        DELAY_BETWEEN_CAPTCHAS_MAX
                    )
                    logger.info(f"⏳ Следующая через {delay:.1f} сек...")
                    
                    # Показываем прогресс каждые 10 капч
                    if self.stats['session_solved'] % 10 == 0:
                        self.show_progress()
                    
                    time.sleep(delay)
                else:
                    logger.warning("⏳ Ожидание 10 сек после ошибки...")
                    time.sleep(10)
                
                # Остановка после слишком многих ошибок
                if self.stats['session_errors'] > self.settings.get('max_errors_before_stop', 10):
                    logger.error(f"⚠️ Слишком много ошибок ({self.stats['session_errors']}). Остановка.")
                    break
                    
        except KeyboardInterrupt:
            logger.info("\n🛑 Остановка по запросу пользователя")
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
        finally:
            self.is_running = False
            self.show_final_stats()
    
    def show_progress(self):
        """Показать прогресс"""
        print("\n" + "="*40)
        print("📊 ПРОГРЕСС")
        print("="*40)
        print(f"Решено в этой сессии: {self.stats['session_solved']}")
        print(f"Ошибок в этой сессии: {self.stats['session_errors']}")
        print(f"Всего решено: {self.stats['total_solved']}")
        print(f"Последнее решение: {self.stats.get('last_solution', 'нет')}")
        print("="*40)
    
    def show_final_stats(self):
        """Показать итоговую статистику"""
        print("\n" + "="*60)
        print("📈 ИТОГОВАЯ СТАТИСТИКА")
        print("="*60)
        
        if self.stats['start_time']:
            try:
                start = datetime.fromisoformat(self.stats['start_time'])
                duration = datetime.now() - start
                hours = duration.total_seconds() / 3600
                
                print(f"Время работы: {hours:.2f} часов")
                if hours > 0:
                    captchas_per_hour = self.stats['session_solved'] / hours
                    print(f"Скорость: {captchas_per_hour:.1f} капч/час")
            except:
                pass
        
        print(f"Решено в сессии: {self.stats['session_solved']}")
        print(f"Ошибок в сессии: {self.stats['session_errors']}")
        print(f"Всего решено: {self.stats['total_solved']}")
        print(f"Всего ошибок: {self.stats['total_errors']}")
        
        if self.stats['session_solved'] > 0:
            success_rate = self.stats['session_solved'] / (
                self.stats['session_solved'] + self.stats['session_errors']
            ) * 100
            print(f"Успешность: {success_rate:.1f}%")
        
        print("="*60)
        
        # Сохраняем сессию
        self._save_session_stats()
    
    def _save_session_stats(self):
        """Сохранение статистики сессии"""
        try:
            session_data = {
                'start_time': self.stats['start_time'],
                'end_time': datetime.now().isoformat(),
                'solved': self.stats['session_solved'],
                'errors': self.stats['session_errors'],
                'last_solution': self.stats['last_solution']
            }
            
            if 'sessions' not in self.stats:
                self.stats['sessions'] = []
            
            self.stats['sessions'].append(session_data)
            self._save_stats()
            
        except Exception as e:
            logger.error(f"Ошибка сохранения сессии: {e}")

def load_stats() -> Optional[Dict[str, Any]]:
    """Загрузка статистики для просмотра"""
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return None

if __name__ == "__main__":
    import os
    solver = ScreenCaptchaSolver()
    solver.run()
