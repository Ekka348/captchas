#!/usr/bin/env python3
"""
🌐 Контроллер браузера для автоматизации работы с сайтами с использованием Playwright
"""

import time
import random
import logging
from typing import Optional, Tuple, Dict, Any
from playwright.sync_api import sync_playwright, Page, Browser

from config import (
    CHROME_HEADLESS,
    CHROME_WINDOW_SIZE,
    PROXY_ENABLED,
    PROXY_SERVER,
    PROXY_USERNAME,
    PROXY_PASSWORD
)

class BrowserController:
    """Управление браузером для автоматизации с Playwright"""
    
    def __init__(self, headless: bool = CHROME_HEADLESS):
        self.playwright = None
        self.browser = None
        self.page = None
        self.headless = headless
        self.logger = logging.getLogger('BrowserController')
        self.wait_timeout = 30000  # миллисекунды для Playwright
        
    def init_driver(self) -> bool:
        """Инициализация браузера через Playwright"""
        try:
            self.playwright = sync_playwright().start()
            
            # Настройки запуска браузера
            launch_options = {
                'headless': self.headless,
                'args': [
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    f'--window-size={CHROME_WINDOW_SIZE[0]},{CHROME_WINDOW_SIZE[1]}',
                    '--disable-blink-features=AutomationControlled'
                ]
            }
            
            # Настройка прокси
            if PROXY_ENABLED and PROXY_SERVER:
                if PROXY_USERNAME and PROXY_PASSWORD:
                    proxy_settings = {
                        'server': PROXY_SERVER,
                        'username': PROXY_USERNAME,
                        'password': PROXY_PASSWORD
                    }
                else:
                    proxy_settings = {'server': PROXY_SERVER}
                
                launch_options['proxy'] = proxy_settings
                self.logger.info(f"Используется прокси: {PROXY_SERVER}")
            
            # Запускаем браузер
            self.browser = self.playwright.chromium.launch(**launch_options)
            
            # Создаем контекст и страницу
            context = self.browser.new_context(
                viewport={'width': CHROME_WINDOW_SIZE[0], 'height': CHROME_WINDOW_SIZE[1]},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            self.page = context.new_page()
            
            # Скрываем WebDriver признаки
            self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            self.logger.info("✅ Браузер инициализирован с Playwright")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации браузера: {e}")
            return False
    
    def open_url(self, url: str, wait_element: Optional[str] = None) -> bool:
        """Открытие URL и ожидание элемента"""
        try:
            if not self.page:
                if not self.init_driver():
                    return False
            
            self.logger.info(f"🌐 Открываю URL: {url}")
            self.page.goto(url, wait_until="networkidle")
            
            # Ожидание элемента если указан
            if wait_element:
                self.wait_for_element(wait_element)
            
            # Случайная задержка для естественности
            time.sleep(random.uniform(2, 4))
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка открытия URL: {e}")
            return False
    
    def wait_for_element(self, selector: str, timeout: int = None) -> Optional[Any]:
        """Ожидание элемента на странице"""
        try:
            timeout_ms = timeout or self.wait_timeout
            element = self.page.wait_for_selector(selector, timeout=timeout_ms)
            return element
        except Exception:
            self.logger.warning(f"Элемент не найден: {selector}")
            return None
    
    def find_element(self, selector: str) -> Optional[Any]:
        """Поиск элемента"""
        try:
            return self.page.query_selector(selector)
        except Exception:
            return None
    
    def find_elements(self, selector: str) -> list:
        """Поиск нескольких элементов"""
        try:
            return self.page.query_selector_all(selector)
        except Exception:
            return []
    
    def click_element(self, selector: str, human_delay: bool = True) -> bool:
        """Клик по элементу"""
        try:
            element = self.find_element(selector)
            if element:
                if human_delay:
                    time.sleep(random.uniform(0.5, 1.5))
                
                element.click()
                self.logger.debug(f"Клик по элементу: {selector}")
                
                if human_delay:
                    time.sleep(random.uniform(0.2, 0.5))
                
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка клика: {e}")
            return False
    
    def type_text(self, selector: str, text: str, human_typing: bool = True) -> bool:
        """Ввод текста в поле"""
        try:
            element = self.find_element(selector)
            if element:
                if human_typing:
                    # Кликаем
                    element.click()
                    time.sleep(random.uniform(0.1, 0.3))
                    
                    # Вводим посимвольно
                    element.fill('')  # Очищаем поле
                    for char in text:
                        element.type(char, delay=random.uniform(50, 150))
                else:
                    # Быстрый ввод
                    element.fill(text)
                
                self.logger.debug(f"Введен текст: '{text}' в {selector}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка ввода текста: {e}")
            return False
    
    def get_screenshot(self, selector: Optional[str] = None, save_path: Optional[str] = None) -> Optional[bytes]:
        """Скриншот страницы или элемента"""
        try:
            if selector:
                element = self.find_element(selector)
                if element:
                    screenshot = element.screenshot()
                else:
                    return None
            else:
                screenshot = self.page.screenshot(full_page=True)
            
            if save_path:
                with open(save_path, 'wb') as f:
                    f.write(screenshot)
            
            return screenshot
            
        except Exception as e:
            self.logger.error(f"Ошибка скриншота: {e}")
            return None
    
    def get_page_source(self) -> str:
        """Получение исходного кода страницы"""
        try:
            return self.page.content()
        except:
            return ""
    
    def get_current_url(self) -> str:
        """Получение текущего URL"""
        try:
            return self.page.url
        except:
            return ""
    
    def refresh_page(self) -> bool:
        """Обновление страницы"""
        try:
            self.page.reload(wait_until="networkidle")
            time.sleep(random.uniform(2, 4))
            return True
        except Exception as e:
            self.logger.error(f"Ошибка обновления страницы: {e}")
            return False
    
    def close(self):
        """Закрытие браузера"""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            self.logger.info("Браузер закрыт")
        except:
            pass
    
    def __enter__(self):
        """Контекстный менеджер"""
        self.init_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер"""
        self.close()
