#!/usr/bin/env python3
"""
🎯 Фоновый воркер для решения капч
С человеческим поведением и полной вариативностью
"""

import time
import random
import json
import math
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum

import pyautogui
import numpy as np

# Импорт конфигурации
try:
    from config import (
        CAPTCHA_REGION,
        INPUT_COORDS,
        BUTTON_COORDS,
        CYCLE_DELAY_MIN,
        CYCLE_DELAY_MAX,
        CYCLE_DELAY_DISTRIBUTION,
        TYPING_SPEED_BASE,
        TYPING_SPEED_VARIATION,
        MISTAKE_PROBABILITY,
        THINKING_PAUSE_PROB,
        CLICK_ACCURACY_FRESH,
        CLICK_ACCURACY_TIRED,
        MOUSE_SPEED_MIN,
        MOUSE_SPEED_MAX,
        MOUSE_CURVE_VARIATION,
        WORK_START_HOUR,
        WORK_END_HOUR,
        BREAK_PROBABILITY_DAY,
        BREAK_PROBABILITY_NIGHT,
        DATA_DIR,
        LOGS_DIR,
        STATS_FILE,
        ACTIVITY_FILE,
        WORKER_STATE_FILE,
        WORKER_STATUS_FILE,
        CAPTCHA_LOG_FILE,
        LOG_LEVEL,
        LOG_FORMAT,
        LOG_DATE_FORMAT
    )
except ImportError as e:
    print(f"❌ Ошибка загрузки конфигурации: {e}")
    print("Создайте файл config.py или запустите setup.py")
    sys.exit(1)

# ============================================
# КЛАССЫ ДЛЯ ВАРИАТИВНОСТИ
# ============================================

class HumanState(Enum):
    FRESH = "fresh"
    STEADY = "steady"
    TIRED = "tired"
    BREAK = "break"

@dataclass
class HumanMetrics:
    """Метрики человеческого состояния"""
    fatigue: float = 0.0  # 0.0-1.0
    concentration: float = 1.0  # 1.0-0.3
    mood: float = 0.8  # 0.0-1.0
    last_success: Optional[datetime] = None
    consecutive_errors: int = 0
    
    def update(self, success: bool, work_duration_minutes: float):
        """Обновление состояния"""
        # Усталость растет со временем
        self.fatigue = min(1.0, 0.25 * math.log(work_duration_minutes + 1))
        
        # Концентрация падает с усталостью
        self.concentration = max(0.3, 1.0 - self.fatigue * 0.7)
        
        # Настроение зависит от успехов
        if success:
            self.mood = min(1.0, self.mood + 0.05)
            self.consecutive_errors = 0
            self.last_success = datetime.now()
        else:
            self.mood = max(0.3, self.mood - 0.08)
            self.consecutive_errors += 1

class HumanBehavior:
    """Эмулятор человеческого поведения"""
    
    def __init__(self):
        self.metrics = HumanMetrics()
        self.error_patterns = {
            'adjacent_swap': 0.40,      # Соседние буквы
            'double_letter': 0.20,      # Удвоение
            'missing_letter': 0.15,     # Пропуск
            'extra_letter': 0.10,       # Лишняя буква
            'case_error': 0.08,         # Регистр
            'homophone': 0.05,          # Омофон
            'keyboard_neighbor': 0.02   # Соседняя клавиша
        }
        
    def get_cycle_delay(self) -> float:
        """Получение задержки с учетом состояния"""
        # Базовое распределение
        if CYCLE_DELAY_DISTRIBUTION == "normal":
            mean = (CYCLE_DELAY_MIN + CYCLE_DELAY_MAX) / 2
            std = (CYCLE_DELAY_MAX - CYCLE_DELAY_MIN) / 4
            delay = np.random.normal(mean, std)
            delay = max(CYCLE_DELAY_MIN, min(CYCLE_DELAY_MAX, delay))
        else:
            delay = random.uniform(CYCLE_DELAY_MIN, CYCLE_DELAY_MAX)
        
        # Коррекция на состояние
        fatigue_factor = 1.0 + (self.metrics.fatigue * 0.4)
        mood_factor = 1.0 + ((1.0 - self.metrics.mood) * 0.2)
        error_factor = 1.0 + (self.metrics.consecutive_errors * 0.3)
        
        final_delay = delay * fatigue_factor * mood_factor * error_factor
        
        # Случайная вариация
        final_delay *= random.uniform(0.9, 1.1)
        
        # Проверка на перерыв
        current_hour = datetime.now().hour
        break_prob = BREAK_PROBABILITY_DAY if WORK_START_HOUR <= current_hour <= WORK_END_HOUR else BREAK_PROBABILITY_NIGHT
        
        if random.random() < break_prob:
            break_duration = random.uniform(30, 180)  # 30-180 секунд
            final_delay += break_duration
        
        return max(5, final_delay)  # Не меньше 5 секунд
    
    def human_click(self, target_x: int, target_y: int) -> Tuple[int, int]:
        """Человеческий клик"""
        # Точность зависит от состояния
        accuracy = CLICK_ACCURACY_TIRED if self.metrics.fatigue > 0.5 else CLICK_ACCURACY_FRESH
        accuracy *= (1.0 + (1.0 - self.metrics.concentration) * 0.5)
        
        # Случайное смещение
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, accuracy)
        offset_x = distance * math.cos(angle)
        offset_y = distance * math.sin(angle)
        
        click_x = int(target_x + offset_x)
        click_y = int(target_y + offset_y)
        
        # Естественное движение
        self._human_mouse_move(click_x, click_y)
        
        # Пауза перед кликом
        aim_time = random.uniform(0.1, 0.5) * (1.0 + self.metrics.fatigue)
        time.sleep(aim_time)
        
        # Клик
        pyautogui.click()
        
        # Пауза после
        time.sleep(random.uniform(0.05, 0.3))
        
        return click_x, click_y
    
    def _human_mouse_move(self, target_x: int, target_y: int):
        """Естественное движение мыши"""
        current_x, current_y = pyautogui.position()
        
        # Разбиваем на сегменты для извилистости
        distance = math.sqrt((target_x - current_x)**2 + (target_y - current_y)**2)
        num_segments = max(2, int(distance / 50))
        
        for i in range(num_segments):
            t = (i + 1) / num_segments
            segment_x = current_x + (target_x - current_x) * t
            segment_y = current_y + (target_y - current_y) * t
            
            # Добавляем извилистость
            if i < num_segments - 1:
                deviation = random.uniform(-MOUSE_CURVE_VARIATION * 20, MOUSE_CURVE_VARIATION * 20)
                angle = random.uniform(0, 2 * math.pi)
                segment_x += deviation * math.cos(angle)
                segment_y += deviation * math.sin(angle)
            
            # Скорость движения
            speed = random.uniform(MOUSE_SPEED_MIN, MOUSE_SPEED_MAX)
            speed *= (1.0 + self.metrics.fatigue * 0.3)  # Уставшие двигаются медленнее
            
            # Движение
            pyautogui.moveTo(int(segment_x), int(segment_y), 
                           duration=speed * (distance / num_segments / 500))
            
            # Случайные микропаузы
            if random.random() < 0.1:
                time.sleep(random.uniform(0.02, 0.1))
    
    def human_typing(self, text: str) -> str:
        """Человеческий ввод с ошибками"""
        if not text:
            return text
        
        result = []
        
        for i, char in enumerate(text):
            # Скорость печати
            base_speed = TYPING_SPEED_BASE
            speed_multiplier = 0.8 if i == 0 or i == len(text) - 1 else random.uniform(0.9, 1.1)
            
            # Влияние состояния
            fatigue_effect = 1.0 + (self.metrics.fatigue * 0.3)
            concentration_effect = 1.0 + ((1.0 - self.metrics.concentration) * 0.2)
            
            final_speed = (base_speed * speed_multiplier * 
                         fatigue_effect * concentration_effect * 
                         random.uniform(1 - TYPING_SPEED_VARIATION, 1 + TYPING_SPEED_VARIATION))
            
            # Проверка на ошибку
            char_to_type = char
            error_chance = MISTAKE_PROBABILITY * (1.0 + self.metrics.fatigue * 0.5)
            
            if random.random() < error_chance:
                char_to_type = self._make_typing_error(char)
            
            # Печать
            pyautogui.write(char_to_type, interval=final_speed)
            result.append(char_to_type)
            
            # Пауза для "мышления"
            if random.random() < THINKING_PAUSE_PROB:
                think_time = random.uniform(0.3, 1.2) * (1.0 + self.metrics.fatigue)
                time.sleep(think_time)
        
        return ''.join(result)
    
    def _make_typing_error(self, char: str) -> str:
        """Создание опечатки"""
        char_lower = char.lower()
        
        # Выбор типа ошибки
        error_type = random.choices(
            list(self.error_patterns.keys()),
            weights=list(self.error_patterns.values())
        )[0]
        
        # Применение ошибки
        if error_type == 'double_letter' and char.isalpha():
            return char * 2
            
        elif error_type == 'missing_letter':
            return ''
            
        elif error_type == 'case_error':
            return char.lower() if char.isupper() else char.upper()
            
        elif error_type == 'homophone':
            homophones = {'0': 'o', '1': 'i', '5': 's', '8': 'b', 'o': '0', 'i': '1'}
            return homophones.get(char_lower, char)
            
        elif error_type == 'keyboard_neighbor':
            neighbors = {
                'q': 'w', 'w': 'qe', 'e': 'wr', 'r': 'et', 't': 'ry',
                'y': 'tu', 'u': 'yi', 'i': 'uo', 'o': 'ip', 'p': 'o[',
                'a': 's', 's': 'ad', 'd': 'sf', 'f': 'dg', 'g': 'fh',
                'h': 'gj', 'j': 'hk', 'k': 'jl', 'l': 'k;',
                'z': 'x', 'x': 'zc', 'c': 'xv', 'v': 'cb', 'b': 'vn',
                'n': 'bm', 'm': 'n,'
            }
            return neighbors.get(char_lower, char)
        
        return char

# ============================================
# ОСНОВНОЙ КЛАСС ВОРКЕРА
# ============================================

class CaptchaWorker:
    """Основной класс воркера"""
    
    def __init__(self, headless: bool = False):
        self.running = False
        self.headless = headless
        self.human = HumanBehavior()
        
        # Статистика
        self.cycle_count = 0
        self.success_count = 0
        self.error_count = 0
        self.session_start = datetime.now()
        
        # Инициализация
        self._ensure_directories()
        self._setup_logging()
        self._load_state()
        
        self.logger.info("🎯 Captcha Worker инициализирован")
        
    def _ensure_directories(self):
        """Создание необходимых директорий"""
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(LOGS_DIR, exist_ok=True)
    
    def _setup_logging(self):
        """Настройка логирования"""
        logger = logging.getLogger('CaptchaWorker')
        logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # Форматтер
        formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        
        # Файловый handler
        file_handler = logging.FileHandler(CAPTCHA_LOG_FILE, encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        # Консольный handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        if not self.headless:
            logger.addHandler(console_handler)
        
        self.logger = logger
    
    def _load_state(self):
        """Загрузка состояния"""
        try:
            if os.path.exists(WORKER_STATE_FILE):
                with open(WORKER_STATE_FILE, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.cycle_count = state.get('cycle_count', 0)
                    self.success_count = state.get('success_count', 0)
                    self.error_count = state.get('error_count', 0)
                    self.logger.info(f"Загружено состояние: {self.cycle_count} циклов")
        except Exception as e:
            self.logger.warning(f"Не удалось загрузить состояние: {e}")
    
    def _save_state(self):
        """Сохранение состояния"""
        try:
            state = {
                'cycle_count': self.cycle_count,
                'success_count': self.success_count,
                'error_count': self.error_count,
                'last_save': datetime.now().isoformat(),
                'session_start': self.session_start.isoformat()
            }
            
            with open(WORKER_STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
                
            self.logger.debug(f"Сохранено состояние: {self.cycle_count} циклов")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения состояния: {e}")
    
    def _update_global_status(self, last_captcha: Optional[str] = None):
        """Обновление глобального статуса"""
        try:
            status = {
                'running': self.running,
                'cycle_count': self.cycle_count,
                'success_rate': self._calculate_success_rate(),
                'last_captcha': last_captcha,
                'error_count': self.error_count,
                'fatigue': self.human.metrics.fatigue,
                'concentration': self.human.metrics.concentration,
                'mood': self.human.metrics.mood,
                'last_update': datetime.now().isoformat()
            }
            
            with open(WORKER_STATUS_FILE, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def _calculate_success_rate(self) -> float:
        """Расчет процента успеха"""
        if self.cycle_count == 0:
            return 0.0
        return (self.success_count / self.cycle_count) * 100
    
    def _log_activity(self, message: str):
        """Логирование активности"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(ACTIVITY_FILE, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {message}\n")
        except:
            pass
    
    def _simulate_captcha_solution(self) -> Optional[str]:
        """
        Имитация решения капчи
        TODO: Замените на реальное распознавание
        """
        import string
        
        # Разная сложность
        complexity = random.choices(['easy', 'medium', 'hard'], weights=[0.5, 0.3, 0.2])[0]
        
        if complexity == 'easy':
            chars = string.digits
            length = random.randint(4, 6)
        elif complexity == 'medium':
            chars = string.ascii_uppercase + string.digits
            length = random.randint(5, 7)
        else:
            chars = string.ascii_letters + string.digits
            length = random.randint(6, 8)
        
        return ''.join(random.choice(chars) for _ in range(length))
    
    def solve_cycle(self) -> Optional[str]:
        """Выполнение одного цикла решения"""
        self.cycle_count += 1
        cycle_start = time.time()
        
        self.logger.info(f"🔄 Цикл #{self.cycle_count}")
        
        try:
            # 1. "Чтение" капчи
            read_time = random.uniform(1.0, 3.0) * (1.0 + self.human.metrics.fatigue)
            time.sleep(read_time)
            
            # 2. Распознавание
            captcha_text = self._simulate_captcha_solution()
            
            if not captcha_text or len(captcha_text) < 4:
                self.logger.warning("Не удалось распознать капчу")
                self.error_count += 1
                self.human.metrics.update(False, 0)
                time.sleep(random.uniform(2, 6))
                return None
            
            self.logger.info(f"Распознано: '{captcha_text}'")
            
            # 3. Клик в поле
            self.human.human_click(*INPUT_COORDS)
            
            # 4. Очистка поля (90% случаев)
            if random.random() < 0.9:
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(random.uniform(0.1, 0.3))
                pyautogui.press('delete')
                time.sleep(random.uniform(0.1, 0.2))
            
            # 5. Ввод текста
            typed_text = self.human.human_typing(captcha_text)
            
            # 6. Проверка
            if typed_text != captcha_text:
                self.logger.info(f"Введено с ошибками: '{typed_text}'")
            
            check_time = random.uniform(0.2, 1.0)
            time.sleep(check_time)
            
            # 7. Отправка
            self.human.human_click(*BUTTON_COORDS)
            
            # 8. Статистика
            cycle_time = time.time() - cycle_start
            self.success_count += 1
            
            # Обновление состояния
            work_duration = (datetime.now() - self.session_start).total_seconds() / 60
            self.human.metrics.update(True, work_duration)
            
            # Логирование
            self._log_activity(f"Цикл #{self.cycle_count}: '{captcha_text}' за {cycle_time:.1f} сек")
            self.logger.info(f"Завершено за {cycle_time:.1f} сек")
            
            return captcha_text
            
        except Exception as e:
            self.logger.error(f"Ошибка в цикле: {e}")
            self.error_count += 1
            
            work_duration = (datetime.now() - self.session_start).total_seconds() / 60
            self.human.metrics.update(False, work_duration)
            
            time.sleep(random.uniform(3, 10))
            return None
    
    def run(self):
        """Основной цикл работы"""
        self.running = True
        self.logger.info("🚀 Запуск основного цикла")
        self.logger.info(f"Координаты: капча={CAPTCHA_REGION}, поле={INPUT_COORDS}, кнопка={BUTTON_COORDS}")
        
        consecutive_failures = 0
        
        try:
            while self.running:
                # Получение задержки
                delay = self.human.get_cycle_delay()
                
                # Учет неудач
                if consecutive_failures > 0:
                    delay *= (1.0 + consecutive_failures * 0.3)
                
                self.logger.info(f"⏳ Следующий цикл через: {delay:.1f} сек")
                time.sleep(delay)
                
                # Выполнение цикла
                result = self.solve_cycle()
                
                # Обновление счетчиков
                if result:
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                
                # Много неудач - длинный перерыв
                if consecutive_failures >= 3:
                    long_break = random.uniform(60, 180)
                    self.logger.warning(f"Много неудач, перерыв: {long_break:.1f} сек")
                    time.sleep(long_break)
                    consecutive_failures = 0
                
                # Обновление глобального статуса
                self._update_global_status(result)
                
                # Периодическое сохранение
                if self.cycle_count % 10 == 0:
                    self._save_state()
                
                # Периодическая статистика
                if self.cycle_count % 20 == 0:
                    self.print_statistics()
                    
        except KeyboardInterrupt:
            self.logger.info("\n⏹️ Остановка по запросу пользователя")
        except Exception as e:
            self.logger.error(f"Критическая ошибка: {e}")
        finally:
            self.stop()
    
    def print_statistics(self):
        """Вывод статистики"""
        session_duration = datetime.now() - self.session_start
        hours = session_duration.total_seconds() / 3600
        
        if hours == 0:
            return
        
        success_rate = self._calculate_success_rate()
        cycles_per_hour = self.cycle_count / hours
        
        self.logger.info("="*50)
        self.logger.info("📊 СТАТИСТИКА")
        self.logger.info(f"  Циклов: {self.cycle_count}")
        self.logger.info(f"  Успешность: {success_rate:.1f}%")
        self.logger.info(f"  Ошибок: {self.error_count}")
        self.logger.info(f"  Время работы: {hours:.1f} часов")
        self.logger.info(f"  Скорость: {cycles_per_hour:.1f} циклов/час")
        self.logger.info(f"  Усталость: {self.human.metrics.fatigue:.2f}")
        self.logger.info("="*50)
    
    def stop(self):
        """Остановка воркера"""
        self.running = False
        self._save_state()
        
        success_rate = self._calculate_success_rate()
        
        self.logger.info("🛑 Воркер остановлен")
        self.logger.info(f"  Итог: {self.cycle_count} циклов, успешность {success_rate:.1f}%")

# ============================================
# ТОЧКА ВХОДА
# ============================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Captcha Worker')
    parser.add_argument('--headless', action='store_true', help='Режим без вывода в консоль')
    parser.add_argument('--test', action='store_true', help='Тестовый режим (5 циклов)')
    parser.add_argument('--cycles', type=int, default=0, help='Количество циклов для выполнения')
    
    args = parser.parse_args()
    
    print("="*60)
    print("🎯 CAPTCHA WORKER - РЕШЕНИЕ КАПЧ С ЧЕЛОВЕЧЕСКИМ ПОВЕДЕНИЕМ")
    print("="*60)
    
    # Проверка конфигурации
    from config import validate_config
    is_valid, errors = validate_config()
    
    if not is_valid:
        print("❌ Ошибки конфигурации:")
        for error in errors:
            print(f"  • {error}")
        print("\nИсправьте config.py перед запуском")
        return
    
    worker = CaptchaWorker(headless=args.headless)
    
    if args.test:
        print("🧪 Тестовый режим (5 циклов)")
        worker.running = True
        for i in range(5):
            worker.solve_cycle()
            time.sleep(2)
        worker.stop()
    elif args.cycles > 0:
        print(f"🔢 Режим с ограничением: {args.cycles} циклов")
        worker.running = True
        for i in range(args.cycles):
            if not worker.running:
                break
            worker.solve_cycle()
        worker.stop()
    else:
        print("🚀 Запуск в бесконечном режиме")
        print("   Для остановки нажмите Ctrl+C")
        print("="*60)
        worker.run()

if __name__ == "__main__":
    main()
