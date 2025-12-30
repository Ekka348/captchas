#!/usr/bin/env python3
"""
🖱️ Контроллер мыши с человекоподобным поведением
"""

import time
import random
import math
import logging
from typing import Tuple

import pyautogui

from config import (
    MOUSE_MOVE_DURATION_MIN, MOUSE_MOVE_DURATION_MAX,
    MOUSE_ACCURACY
)

# Настройка безопасности pyautogui
pyautogui.FAILSAFE = True  # Прервать если мышь в углу экрана
pyautogui.PAUSE = 0.1  # Минимальная пауза между командами

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MouseController')

class MouseController:
    """Класс для человекоподобного управления мышью"""
    
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        logger.info(f"✅ Контроллер мыши инициализирован. Экран: {self.screen_width}x{self.screen_height}")
    
    def human_move_to(self, x: int, y: int) -> None:
        """
        Человекоподобное перемещение мыши с кривой Безье
        """
        try:
            # Текущая позиция мыши
            current_x, current_y = pyautogui.position()
            
            # Случайное отклонение для "дрожания руки"
            x += random.randint(-MOUSE_ACCURACY, MOUSE_ACCURACY)
            y += random.randint(-MOUSE_ACCURACY, MOUSE_ACCURACY)
            
            # Ограничиваем координаты экраном
            x = max(0, min(x, self.screen_width - 1))
            y = max(0, min(y, self.screen_height - 1))
            
            # Случайная продолжительность движения
            duration = random.uniform(
                MOUSE_MOVE_DURATION_MIN,
                MOUSE_MOVE_DURATION_MAX
            )
            
            # Параметры для кривой Безье
            control_points = []
            
            # Создаем контрольные точки для кривой
            distance = math.sqrt((x - current_x)**2 + (y - current_y)**2)
            
            if distance > 100:  # Только для длинных перемещений
                num_points = random.randint(1, 2)
                
                for i in range(num_points):
                    # Случайная точка на пути
                    t = (i + 1) / (num_points + 1)
                    mid_x = current_x + (x - current_x) * t
                    mid_y = current_y + (y - current_y) * t
                    
                    # Добавляем случайное отклонение
                    deviation = random.uniform(-0.3, 0.3) * distance / 5
                    angle = random.uniform(0, 2 * math.pi)
                    
                    control_points.append((
                        mid_x + deviation * math.cos(angle),
                        mid_y + deviation * math.sin(angle)
                    ))
            
            # Перемещение с человеческой скоростью
            if control_points:
                # Кривая Безье с контрольными точками
                points = self._generate_bezier_curve(
                    (current_x, current_y),
                    (x, y),
                    control_points,
                    steps=int(duration * 100)
                )
                
                # Плавное перемещение по точкам
                for point_x, point_y in points:
                    pyautogui.moveTo(point_x, point_y)
                    time.sleep(duration / len(points))
            else:
                # Прямое перемещение для коротких дистанций
                pyautogui.moveTo(x, y, duration=duration)
            
            logger.debug(f"Мышь перемещена в ({x}, {y}) за {duration:.2f} сек")
            
        except Exception as e:
            logger.error(f"Ошибка перемещения мыши: {e}")
            pyautogui.moveTo(x, y)  # Простое перемещение в случае ошибки
    
    def _generate_bezier_curve(self, start: Tuple[float, float], end: Tuple[float, float],
                               control_points: list, steps: int = 50) -> list:
        """Генерация кривой Безье"""
        points = []
        
        for i in range(steps + 1):
            t = i / steps
            points.append(self._bezier_point(t, start, end, control_points))
        
        return points
    
    def _bezier_point(self, t: float, start: Tuple[float, float], end: Tuple[float, float],
                      control_points: list) -> Tuple[float, float]:
        """Вычисление точки на кривой Безье"""
        # Кривая Безье высшего порядка
        all_points = [start] + control_points + [end]
        n = len(all_points) - 1
        
        x = 0.0
        y = 0.0
        
        for i, (point_x, point_y) in enumerate(all_points):
            # Коэффициент Бернштейна
            coeff = math.comb(n, i) * (t**i) * ((1 - t)**(n - i))
            x += coeff * point_x
            y += coeff * point_y
        
        return (x, y)
    
    def human_click(self, x: int, y: int, button: str = 'left') -> None:
        """Человекоподобный клик"""
        try:
            # Перемещение
            self.human_move_to(x, y)
            
            # Случайная задержка перед кликом
            time.sleep(random.uniform(0.1, 0.3))
            
            # Клик
            pyautogui.click(button=button)
            
            # Случайная задержка после клика
            time.sleep(random.uniform(0.05, 0.15))
            
            logger.debug(f"Клик в ({x}, {y}) кнопкой {button}")
            
        except Exception as e:
            logger.error(f"Ошибка клика: {e}")
    
    def click_with_variance(self, coords: Tuple[int, int]) -> None:
        """Клик со случайным отклонением"""
        x, y = coords
        
        # Случайное отклонение
        variance = MOUSE_ACCURACY
        x += random.randint(-variance, variance)
        y += random.randint(-variance, variance)
        
        self.human_click(x, y)
    
    def double_click(self, x: int, y: int) -> None:
        """Двойной клик"""
        try:
            self.human_move_to(x, y)
            time.sleep(random.uniform(0.1, 0.2))
            
            pyautogui.doubleClick()
            
            logger.debug(f"Двойной клик в ({x}, {y})")
            
        except Exception as e:
            logger.error(f"Ошибка двойного клика: {e}")
    
    def right_click(self, x: int, y: int) -> None:
        """Правый клик"""
        try:
            self.human_move_to(x, y)
            time.sleep(random.uniform(0.1, 0.3))
            
            pyautogui.rightClick()
            
            logger.debug(f"Правый клик в ({x}, {y})")
            
        except Exception as e:
            logger.error(f"Ошибка правого клика: {e}")
    
    def drag_to(self, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
        """Перетаскивание"""
        try:
            # Перемещение к начальной точке
            self.human_move_to(start_x, start_y)
            time.sleep(random.uniform(0.2, 0.4))
            
            # Нажатие и удержание
            pyautogui.mouseDown()
            time.sleep(random.uniform(0.1, 0.2))
            
            # Перетаскивание
            self.human_move_to(end_x, end_y)
            time.sleep(random.uniform(0.1, 0.2))
            
            # Отпускание
            pyautogui.mouseUp()
            
            logger.debug(f"Перетаскивание из ({start_x}, {start_y}) в ({end_x}, {end_y})")
            
        except Exception as e:
            logger.error(f"Ошибка перетаскивания: {e}")
            pyautogui.mouseUp()  # На всякий случай отпускаем
    
    def scroll(self, clicks: int, direction: str = 'down') -> None:
        """Прокрутка колесика"""
        try:
            # Определение направления
            if direction == 'up':
                clicks = abs(clicks)
            else:
                clicks = -abs(clicks)
            
            # Случайная скорость прокрутки
            for _ in range(abs(clicks)):
                pyautogui.scroll(clicks // abs(clicks))
                time.sleep(random.uniform(0.05, 0.15))
            
            logger.debug(f"Прокрутка {abs(clicks)} кликов {direction}")
            
        except Exception as e:
            logger.error(f"Ошибка прокрутки: {e}")
    
    def test_mouse(self):
        """Тестирование работы мыши"""
        print("\n" + "="*60)
        print("🖱️ ТЕСТИРОВАНИЕ МЫШИ")
        print("="*60)
        
        print("\n1. Тест перемещения")
        print("2. Тест кликов")
        print("3. Тест перетаскивания")
        print("4. Тест прокрутки")
        
        choice = input("\nВаш выбор (1-4): ").strip()
        
        if choice == "1":
            print("\n📏 Тест перемещения...")
            print("Мышь будет перемещаться по экрану")
            input("Нажмите Enter чтобы начать...")
            
            # Перемещение по углам экрана
            corners = [
                (100, 100),
                (self.screen_width - 100, 100),
                (self.screen_width - 100, self.screen_height - 100),
                (100, self.screen_height - 100)
            ]
            
            for x, y in corners:
                print(f"Перемещение в ({x}, {y})...")
                self.human_move_to(x, y)
                time.sleep(1)
            
            print("✅ Тест завершен")
            
        elif choice == "2":
            print("\n🖱️ Тест кликов...")
            current_x, current_y = pyautogui.position()
            print(f"Текущая позиция: ({current_x}, {current_y})")
            
            print("Левый клик...")
            self.human_click(current_x, current_y)
            time.sleep(1)
            
            print("Двойной клик...")
            self.double_click(current_x + 50, current_y)
            time.sleep(1)
            
            print("Правый клик...")
            self.right_click(current_x, current_y + 50)
            
            print("✅ Тест завершен")
            
        elif choice == "3":
            print("\n↔️ Тест перетаскивания...")
            current_x, current_y = pyautogui.position()
            
            print(f"Начинаю перетаскивание из ({current_x}, {current_y})")
            self.drag_to(current_x, current_y, current_x + 200, current_y + 200)
            
            print("✅ Тест завершен")
            
        elif choice == "4":
            print("\n🔄 Тест прокрутки...")
            
            print("Прокрутка вниз...")
            self.scroll(5, 'down')
            time.sleep(1)
            
            print("Прокрутка вверх...")
            self.scroll(5, 'up')
            
            print("✅ Тест завершен")
            
        else:
            print("❌ Неверный выбор")

if __name__ == "__main__":
    controller = MouseController()
    controller.test_mouse()
