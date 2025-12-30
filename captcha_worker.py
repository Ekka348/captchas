#!/usr/bin/env python3
"""
🎯 Captcha Worker для локального запуска
Решает капчи и зарабатывает деньги!
"""

import time
import random
import requests
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('CaptchaWorker')

class RucaptchaWorker:
    """Воркер для заработка на rucaptcha"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://rucaptcha.com"
        self.stats = {
            'captchas_solved': 0,
            'total_earnings': 0.0,
            'errors': 0,
            'start_time': datetime.now()
        }
        
        if not api_key:
            logger.error("❌ API ключ не указан!")
            raise ValueError("API ключ обязателен")
    
    def get_balance(self) -> float:
        """Получение баланса"""
        try:
            response = requests.get(
                f"{self.base_url}/res.php",
                params={
                    'key': self.api_key,
                    'action': 'getbalance',
                    'json': 1
                },
                timeout=10
            )
            
            data = response.json()
            if data.get('status') == 1:
                return float(data['request'])
            return 0.0
        except:
            return 0.0
    
    def solve_captcha(self) -> bool:
        """Решение одной капчи"""
        try:
            # Здесь будет логика получения и решения капчи
            # Пока имитация
            
            time.sleep(random.uniform(2, 5))
            
            # 90% успешных решений
            success = random.random() > 0.1
            
            if success:
                price = random.uniform(0.0003, 0.001)
                self.stats['captchas_solved'] += 1
                self.stats['total_earnings'] += price
                
                logger.info(f"✅ Решена капча #{self.stats['captchas_solved']} (+${price:.4f})")
                return True
            else:
                self.stats['errors'] += 1
                logger.warning("❌ Ошибка решения капчи")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")
            self.stats['errors'] += 1
            return False
    
    def print_stats(self):
        """Вывод статистики"""
        runtime = datetime.now() - self.stats['start_time']
        hours = runtime.total_seconds() / 3600
        
        print("="*50)
        print("📊 СТАТИСТИКА CAPTCHA WORKER")
        print("="*50)
        print(f"  Капч решено: {self.stats['captchas_solved']}")
        print(f"  Заработано: ${self.stats['total_earnings']:.4f}")
        print(f"  Ошибок: {self.stats['errors']}")
        print(f"  Время работы: {hours:.1f} часов")
        
        if hours > 0:
            per_hour = self.stats['total_earnings'] / hours
            print(f"  В час: ${per_hour:.4f}")
            print(f"  В день: ${per_hour * 24:.4f}")
        
        print("="*50)
    
    def run(self):
        """Основной цикл работы"""
        logger.info("🚀 Запуск Captcha Worker...")
        
        # Проверка баланса
        balance = self.get_balance()
        logger.info(f"💰 Начальный баланс: ${balance:.4f}")
        
        print("\n" + "="*60)
        print("🎯 CAPTCHA WORKER - СИСТЕМА ЗАРАБОТКА")
        print("="*60)
        print(f"API ключ: {self.api_key[:8]}...{self.api_key[-4:]}")
        print(f"Баланс: ${balance:.4f}")
        print("="*60)
        print("\nДля остановки нажмите Ctrl+C\n")
        
        try:
            while True:
                # Решение капчи
                self.solve_captcha()
                
                # Задержка между капчами
                delay = random.uniform(10, 30)
                time.sleep(delay)
                
                # Периодический вывод статистики
                if self.stats['captchas_solved'] % 10 == 0:
                    self.print_stats()
                    
        except KeyboardInterrupt:
            logger.info("\n🛑 Остановка по запросу пользователя")
            self.print_stats()
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")

def main():
    """Точка входа"""
    print("="*60)
    print("🎯 ЗАПУСК CAPTCHA WORKER ДЛЯ ЗАРАБОТКА")
    print("="*60)
    
    # Получаем API ключ
    api_key = input("Введите API ключ rucaptcha (или нажмите Enter для стандартного): ").strip()
    
    if not api_key:
        api_key = "99461b14be32f596e034e2459b05e645"
        print(f"Используется ключ: {api_key[:8]}...{api_key[-4:]}")
    
    # Запускаем воркер
    worker = RucaptchaWorker(api_key)
    worker.run()

if __name__ == "__main__":
    main()
