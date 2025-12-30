#!/usr/bin/env python3
"""
🎯 Основной воркер для решения капч и заработка
"""

import time
import random
import json
import logging
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict

import requests
from PIL import Image
import io

# Импорт модулей проекта
from config import (
    RUCAPTCHA_API_KEY,
    RUCAPTCHA_BASE_URL,
    WORK_CYCLE_DELAY_MIN,
    WORK_CYCLE_DELAY_MAX,
    BREAK_AFTER_CYCLES,
    BREAK_DURATION_MIN,
    BREAK_DURATION_MAX,
    CAPTCHA_LOG_FILE,
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    STATS_FILE,
    DATABASE_FILE
)
from rucaptcha_api import RucaptchaSolver
from database import save_captcha_result, get_daily_stats
from utils.logger import setup_logger

@dataclass
class WorkerStats:
    """Статистика воркера"""
    cycles_completed: int = 0
    captchas_solved: int = 0
    captchas_failed: int = 0
    total_earnings: float = 0.0
    session_start: str = ""
    last_captcha: str = ""
    status: str = "stopped"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class CaptchaWorker:
    """Основной класс воркера"""
    
    def __init__(self):
        self.running = False
        self.stats = WorkerStats()
        self.solver = RucaptchaSolver(RUCAPTCHA_API_KEY)
        self.logger = self.setup_logging()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Инициализация
        self.stats.session_start = datetime.now().isoformat()
        self.stats.status = "initialized"
        
        self.logger.info(f"🎯 Captcha Worker инициализирован (сессия: {self.session_id})")
    
    def setup_logging(self):
        """Настройка логирования"""
        logger = setup_logger(
            name='CaptchaWorker',
            log_file=CAPTCHA_LOG_FILE,
            level=LOG_LEVEL,
            format_str=LOG_FORMAT,
            date_format=LOG_DATE_FORMAT
        )
        return logger
    
    def load_stats(self):
        """Загрузка статистики"""
        try:
            if os.path.exists(STATS_FILE):
                with open(STATS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.stats.cycles_completed = data.get('cycles_completed', 0)
                    self.stats.captchas_solved = data.get('captchas_solved', 0)
                    self.stats.total_earnings = data.get('total_earnings', 0.0)
                    self.logger.info(f"Загружена статистика: {self.stats.captchas_solved} капч")
        except Exception as e:
            self.logger.warning(f"Не удалось загрузить статистику: {e}")
    
    def save_stats(self):
        """Сохранение статистики"""
        try:
            stats_data = self.stats.to_dict()
            stats_data['last_save'] = datetime.now().isoformat()
            
            with open(STATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Сохранена статистика: {self.stats.captchas_solved} капч")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения статистики: {e}")
    
    def get_new_captcha(self) -> Optional[Dict]:
        """Получение новой капчи от rucaptcha"""
        try:
            # Здесь в реальности нужно получать капчу от rucaptcha API
            # Это упрощенный пример
            captcha_data = {
                "id": f"cap_{int(time.time())}",
                "type": "ImageToTextTask",
                "image_url": None,  # URL изображения
                "image_base64": None,  # или base64
                "price": 0.0003,
                "created_at": datetime.now().isoformat()
            }
            
            return captcha_data
        except Exception as e:
            self.logger.error(f"Ошибка получения капчи: {e}")
            return None
    
    def solve_captcha_cycle(self) -> bool:
        """Один цикл решения капчи"""
        self.stats.cycles_completed += 1
        cycle_start = time.time()
        
        self.logger.info(f"🔄 Цикл #{self.stats.cycles_completed}")
        
        try:
            # 1. Получаем новую капчу
            captcha_data = self.get_new_captcha()
            if not captcha_data:
                self.logger.warning("Не удалось получить капчу")
                return False
            
            # 2. Решаем капчу
            self.logger.info(f"Решаем капчу #{captcha_data['id']}")
            
            # Имитация решения (в реальности используем solver.solve_captcha)
            time.sleep(random.uniform(2, 5))
            
            # 90% успешных решений для примера
            success = random.random() > 0.1
            
            if success:
                solution = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
                price = captcha_data['price']
                
                # 3. Сохраняем результат
                save_captcha_result(
                    captcha_id=captcha_data['id'],
                    captcha_type=captcha_data['type'],
                    solution=solution,
                    price=price,
                    success=True
                )
                
                # 4. Обновляем статистику
                self.stats.captchas_solved += 1
                self.stats.total_earnings += price
                self.stats.last_captcha = solution
                
                cycle_time = time.time() - cycle_start
                self.logger.info(f"✅ Решено: '{solution}' за {cycle_time:.1f} сек (+${price:.4f})")
                
                return True
            else:
                self.stats.captchas_failed += 1
                self.logger.warning("❌ Не удалось решить капчу")
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка в цикле: {e}")
            self.stats.captchas_failed += 1
            return False
    
    def get_delay(self) -> float:
        """Получение задержки между циклами"""
        base_delay = random.uniform(WORK_CYCLE_DELAY_MIN, WORK_CYCLE_DELAY_MAX)
        
        # Учет ошибок
        if self.stats.captchas_failed > 0:
            error_factor = 1.0 + (self.stats.captchas_failed * 0.1)
            base_delay *= error_factor
        
        # Перерыв после N циклов
        if self.stats.cycles_completed > 0 and self.stats.cycles_completed % BREAK_AFTER_CYCLES == 0:
            break_time = random.uniform(BREAK_DURATION_MIN, BREAK_DURATION_MAX)
            self.logger.info(f"⏸️ Перерыв после {BREAK_AFTER_CYCLES} циклов: {break_time:.0f} сек")
            base_delay += break_time
        
        return max(5, base_delay)
    
    def update_status_file(self):
        """Обновление файла статуса"""
        try:
            status = {
                "running": self.running,
                "stats": self.stats.to_dict(),
                "session_id": self.session_id,
                "last_update": datetime.now().isoformat(),
                "daily_stats": get_daily_stats(),
                "uptime_seconds": (datetime.now() - datetime.fromisoformat(self.stats.session_start)).total_seconds()
            }
            
            with open(f"data/worker_status.json", 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.debug(f"Не удалось обновить статус: {e}")
    
    def print_daily_stats(self):
        """Вывод дневной статистики"""
        stats = get_daily_stats()
        
        if stats['total_captchas'] > 0:
            self.logger.info("="*50)
            self.logger.info("📊 СЕГОДНЯШНЯЯ СТАТИСТИКА")
            self.logger.info(f"  Капч решено: {stats['total_captchas']}")
            self.logger.info(f"  Успешность: {stats['success_rate']:.1f}%")
            self.logger.info(f"  Заработано: ${stats['total_earnings']:.4f}")
            self.logger.info(f"  Скорость: {stats['captchas_per_hour']:.1f}/час")
            self.logger.info("="*50)
    
    def run(self):
        """Основной цикл работы"""
        self.running = True
        self.stats.status = "running"
        self.logger.info("🚀 Запуск основного цикла заработка")
        
        consecutive_failures = 0
        
        try:
            while self.running:
                # Задержка между циклами
                delay = self.get_delay()
                
                if consecutive_failures > 0:
                    delay *= (1.0 + consecutive_failures * 0.2)
                
                self.logger.info(f"⏳ Следующий цикл через: {delay:.1f} сек")
                time.sleep(delay)
                
                # Выполнение цикла
                success = self.solve_captcha_cycle()
                
                # Обновление счетчиков неудач
                if success:
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                
                # Длинный перерыв при многих неудачах
                if consecutive_failures >= 5:
                    long_break = random.uniform(300, 600)  # 5-10 минут
                    self.logger.warning(f"Много неудач, перерыв: {long_break:.1f} сек")
                    time.sleep(long_break)
                    consecutive_failures = 0
                
                # Обновление статуса
                self.update_status_file()
                
                # Периодическое сохранение
                if self.stats.cycles_completed % 10 == 0:
                    self.save_stats()
                
                # Ежечасная статистика
                if self.stats.cycles_completed % 20 == 0:
                    self.print_daily_stats()
                    
        except KeyboardInterrupt:
            self.logger.info("\n⏹️ Остановка по запросу")
        except Exception as e:
            self.logger.error(f"Критическая ошибка: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Остановка воркера"""
        self.running = False
        self.stats.status = "stopped"
        self.save_stats()
        
        self.logger.info("🛑 Воркер остановлен")
        self.logger.info(f"  Итог сессии: {self.stats.captchas_solved} капч, ${self.stats.total_earnings:.4f}")

# Функция для запуска в отдельном потоке
def run_worker():
    """Запуск воркера (для использования в потоках)"""
    worker = CaptchaWorker()
    worker.run()

if __name__ == "__main__":
    worker = CaptchaWorker()
    worker.run()
