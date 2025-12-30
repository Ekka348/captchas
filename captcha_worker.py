#!/usr/bin/env python3
"""
🎯 Упрощенный воркер для сервера без GUI
"""

import time
import random
import json
import logging
from datetime import datetime
from typing import Optional

from rucaptcha_api import RucaptchaSolver
from database import save_captcha_result, get_daily_stats
from config import RUCAPTCHA_API_KEY

class CaptchaWorkerServer:
    """Версия воркера для сервера"""
    
    def __init__(self):
        self.running = False
        self.solver = RucaptchaSolver(RUCAPTCHA_API_KEY)
        self.logger = logging.getLogger('CaptchaWorkerServer')
        self.stats = {
            'cycles_completed': 0,
            'captchas_solved': 0,
            'captchas_failed': 0,
            'total_earnings': 0.0
        }
    
    def solve_captcha_cycle(self) -> bool:
        """Один цикл решения капчи"""
        self.stats['cycles_completed'] += 1
        
        try:
            # Получаем баланс для проверки подключения
            balance = self.solver.get_balance()
            
            # Имитация решения капчи (в реальности нужно получать реальные капчи)
            time.sleep(random.uniform(2, 5))
            
            # 90% успешных решений для примера
            success = random.random() > 0.1
            
            if success:
                captcha_id = f"cap_{int(time.time())}_{random.randint(1000, 9999)}"
                solution = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
                price = random.uniform(0.0003, 0.001)
                
                # Сохраняем результат
                save_captcha_result(
                    captcha_id=captcha_id,
                    captcha_type="ImageToTextTask",
                    solution=solution,
                    price=price,
                    success=True
                )
                
                # Обновляем статистику
                self.stats['captchas_solved'] += 1
                self.stats['total_earnings'] += price
                
                self.logger.info(f"✅ Решена капча: {solution} (+${price:.4f})")
                return True
            else:
                self.stats['captchas_failed'] += 1
                self.logger.warning("❌ Не удалось решить капчу")
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка в цикле: {e}")
            self.stats['captchas_failed'] += 1
            return False
    
    def update_status_file(self):
        """Обновление файла статуса"""
        try:
            status = {
                "running": self.running,
                "stats": self.stats,
                "last_update": datetime.now().isoformat(),
                "daily_stats": get_daily_stats(),
                "balance": self.solver.get_balance() or 0.0
            }
            
            with open("data/worker_status.json", "w", encoding="utf-8") as f:
                json.dump(status, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def run(self):
        """Основной цикл работы"""
        self.running = True
        self.logger.info("🚀 Запуск воркера на сервере")
        
        try:
            while self.running:
                # Задержка между циклами
                delay = random.uniform(10, 30)
                time.sleep(delay)
                
                # Выполнение цикла
                self.solve_captcha_cycle()
                
                # Обновление статуса
                self.update_status_file()
                
                # Периодическое логирование
                if self.stats['cycles_completed'] % 10 == 0:
                    self.logger.info(f"Статистика: {self.stats['captchas_solved']} капч, ${self.stats['total_earnings']:.4f}")
                    
        except KeyboardInterrupt:
            self.logger.info("⏹️ Остановка воркера")
        except Exception as e:
            self.logger.error(f"Критическая ошибка: {e}")
        finally:
            self.running = False
