#!/usr/bin/env python3
"""
🌐 Контроллер браузера для автоматизации работы с сайтами
"""

import time
import random
import logging
from typing import Optional, Tuple, Dict, Any
from datetime import datetime

import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config import (
    CHROME_HEADLESS,
    CHROME_WINDOW_SIZE,
    CHROME_USER_AGENT,
    PROXY_ENABLED,
    PROXY_SERVER,
    PROXY_USERNAME,
    PROXY_PASSWORD
)

class BrowserController:
    """Управление браузером для автоматизации"""
    
    def __init__(self, headless: bool = CHROME_HEADLESS):
        self.driver = None
        self.headless = headless
        self.logger = logging.getLogger('BrowserController')
        self.wait_timeout = 30
        
    def init_driver(self) -> bool:
        """Инициализация драйвера Chrome"""
        try:
            options = uc.ChromeOptions()
            
            # Базовые опции
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument(f'--window-size={CHROME_WINDOW_SIZE[0]},{CHROME_WINDOW_SIZE[1]}')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument(f'--user-agent={CHROME_USER_AGENT}')
            
            # Headless режим
            if self.headless:
                options.add_argument('--headless=new')
            
            # Прокси
            if PROXY_ENABLED and PROXY_SERVER:
                if PROXY_USERNAME and PROXY_PASSWORD:
                    proxy_auth = f"{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_SERVER}"
                else:
                    proxy_auth = PROXY_SERVER
                
                options.add_argument(f'--proxy-server={proxy_auth}')
                self.logger.info(f"Используется прокси: {PROXY_SERVER}")
            
            # Дополнительные опции
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Инициализация драйвера
            self.driver = uc.Chrome(
                options=options,
                headless=self.headless,
                version_main=119  # Укажите актуальную версию Chrome
            )
            
            # Убираем признаки автоматизации
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("✅ Браузер инициализирован")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации браузера: {e}")
            return False
    
    def open_url(self, url: str, wait_element: Optional[str] = None) -> bool:
        """Открытие URL и ожидание элемента"""
        try:
            if not self.driver:
                if not self.init_driver():
                    return False
            
            self.logger.info(f"🌐 Открываю URL: {url}")
            self.driver.get(url)
            
            # Ожидание загрузки
            if wait_element:
                self.wait_for_element(wait_element)
            
            # Случайная задержка для естественности
            time.sleep(random.uniform(2, 4))
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка открытия URL: {e}")
            return False
    
    def wait_for_element(self, selector: str, by: By = By.CSS_SELECTOR, timeout: int = None) -> Optional[Any]:
        """Ожидание элемента на странице"""
        try:
            wait = WebDriverWait(self.driver, timeout or self.wait_timeout)
            element = wait.until(
                EC.presence_of_element_located((by, selector))
            )
            return element
        except TimeoutException:
            self.logger.warning(f"Элемент не найден: {selector}")
            return None
    
    def find_element(self, selector: str, by: By = By.CSS_SELECTOR) -> Optional[Any]:
        """Поиск элемента"""
        try:
            return self.driver.find_element(by, selector)
        except NoSuchElementException:
            return None
    
    def find_elements(self, selector: str, by: By = By.CSS_SELECTOR) -> list:
        """Поиск нескольких элементов"""
        try:
            return self.driver.find_elements(by, selector)
        except:
            return []
    
    def click_element(self, selector: str, by: By = By.CSS_SELECTOR, human_delay: bool = True) -> bool:
        """Клик по элементу"""
        try:
            element = self.find_element(selector, by)
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
    
    def type_text(self, selector: str, text: str, by: By = By.CSS_SELECTOR, human_typing: bool = True) -> bool:
        """Ввод текста в поле"""
        try:
            element = self.find_element(selector, by)
            if element:
                if human_typing:
                    # Эмуляция человеческого ввода
                    element.click()
                    time.sleep(random.uniform(0.1, 0.3))
                    
                    for char in text:
                        element.send_keys(char)
                        time.sleep(random.uniform(0.05, 0.15))
                else:
                    # Быстрый ввод
                    element.send_keys(text)
                
                self.logger.debug(f"Введен текст: '{text}' в {selector}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка ввода текста: {e}")
            return False
    
    def get_screenshot(self, element_selector: Optional[str] = None, save_path: Optional[str] = None) -> Optional[bytes]:
        """Скриншот страницы или элемента"""
        try:
            if element_selector:
                element = self.find_element(element_selector)
                if element:
                    screenshot = element.screenshot_as_png
                else:
                    return None
            else:
                screenshot = self.driver.get_screenshot_as_png()
            
            if save_path:
                with open(save_path, 'wb') as f:
                    f.write(screenshot)
            
            return screenshot
            
        except Exception as e:
            self.logger.error(f"Ошибка скриншота: {e}")
            return None
    
    def execute_script(self, script: str, *args) -> Any:
        """Выполнение JavaScript"""
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            self.logger.error(f"Ошибка выполнения скрипта: {e}")
            return None
    
    def scroll_to_element(self, selector: str, by: By = By.CSS_SELECTOR) -> bool:
        """Прокрутка к элементу"""
        try:
            element = self.find_element(selector, by)
            if element:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(random.uniform(0.5, 1))
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка прокрутки: {e}")
            return False
    
    def switch_to_frame(self, selector: Optional[str] = None) -> bool:
        """Переключение на iframe"""
        try:
            if selector:
                frame = self.find_element(selector)
                if frame:
                    self.driver.switch_to.frame(frame)
            else:
                self.driver.switch_to.default_content()
            
            return True
        except Exception as e:
            self.logger.error(f"Ошибка переключения фрейма: {e}")
            return False
    
    def get_page_source(self) -> str:
        """Получение исходного кода страницы"""
        try:
            return self.driver.page_source
        except:
            return ""
    
    def get_current_url(self) -> str:
        """Получение текущего URL"""
        try:
            return self.driver.current_url
        except:
            return ""
    
    def refresh_page(self) -> bool:
        """Обновление страницы"""
        try:
            self.driver.refresh()
            time.sleep(random.uniform(2, 4))
            return True
        except Exception as e:
            self.logger.error(f"Ошибка обновления страницы: {e}")
            return False
    
    def close(self):
        """Закрытие браузера"""
        try:
            if self.driver:
                self.driver.quit()
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

# Пример использования
if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)
    
    with BrowserController(headless=True) as browser:
        if browser.open_url("https://rucaptcha.com"):
            print("✅ Страница загружена")
            
            # Делаем скриншот
            screenshot = browser.get_screenshot()
            if screenshot:
                with open("test_screenshot.png", "wb") as f:
                    f.write(screenshot)
                print("✅ Скриншот сохранен")
            
            print(f"Текущий URL: {browser.get_current_url()}")
        else:
            print("❌ Не удалось открыть страницу")
