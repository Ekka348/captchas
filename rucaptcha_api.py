#!/usr/bin/env python3
"""
📡 API клиент для работы с Rucaptcha.com
"""

import time
import base64
import requests
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from config import (
    RUCAPTCHA_API_KEY,
    RUCAPTCHA_BASE_URL,
    CAPTCHA_TYPES
)

class RucaptchaSolver:
    """Класс для работы с API rucaptcha.com"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = RUCAPTCHA_BASE_URL
        self.logger = logging.getLogger('RucaptchaAPI')
        
        if not api_key:
            self.logger.warning("API ключ не установлен")
    
    def get_balance(self) -> Optional[float]:
        """Получение баланса аккаунта"""
        try:
            response = requests.get(
                f"{self.base_url}/res.php",
                params={
                    'key': self.api_key,
                    'action': 'getbalance',
                    'json': 1
                },
                timeout=30
            )
            
            data = response.json()
            if data.get('status') == 1:
                balance = float(data.get('request', 0))
                self.logger.info(f"Баланс: ${balance:.2f}")
                return balance
            else:
                self.logger.error(f"Ошибка получения баланса: {data.get('request', 'Unknown')}")
                return None
                
        except Exception as e:
            self.logger.error(f"Ошибка запроса баланса: {e}")
            return None
    
    def report_incorrect(self, captcha_id: str) -> bool:
        """Сообщение о неверном решении"""
        try:
            response = requests.get(
                f"{self.base_url}/res.php",
                params={
                    'key': self.api_key,
                    'action': 'reportbad',
                    'id': captcha_id,
                    'json': 1
                },
                timeout=30
            )
            
            data = response.json()
            if data.get('status') == 1:
                self.logger.info(f"Капча {captcha_id} отмечена как неверная")
                return True
            else:
                self.logger.warning(f"Не удалось отметить капчу как неверную: {data.get('request', 'Unknown')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка отправки жалобы: {e}")
            return False
    
    def solve_image_captcha(self, image_base64: str, **kwargs) -> Optional[str]:
        """Решение текстовой капчи (ImageToText)"""
        try:
            # Отправка капчи на решение
            response = requests.post(
                f"{self.base_url}/in.php",
                data={
                    'key': self.api_key,
                    'method': 'base64',
                    'body': image_base64,
                    'json': 1,
                    'phrase': kwargs.get('phrase', 0),
                    'regsense': kwargs.get('regsense', 0),
                    'numeric': kwargs.get('numeric', 0),
                    'min_len': kwargs.get('min_len', 0),
                    'max_len': kwargs.get('max_len', 0),
                    'language': kwargs.get('language', 0)
                },
                timeout=30
            )
            
            data = response.json()
            if data.get('status') != 1:
                self.logger.error(f"Ошибка отправки капчи: {data.get('request', 'Unknown')}")
                return None
            
            captcha_id = data.get('request')
            self.logger.info(f"Капча отправлена на решение, ID: {captcha_id}")
            
            # Ожидание решения
            return self._wait_for_solution(captcha_id)
            
        except Exception as e:
            self.logger.error(f"Ошибка решения текстовой капчи: {e}")
            return None
    
    def solve_recaptcha_v2(self, site_key: str, page_url: str, **kwargs) -> Optional[str]:
        """Решение Google ReCaptcha v2"""
        try:
            # Отправка параметров ReCaptcha
            response = requests.post(
                f"{self.base_url}/in.php",
                data={
                    'key': self.api_key,
                    'method': 'userrecaptcha',
                    'googlekey': site_key,
                    'pageurl': page_url,
                    'json': 1,
                    'invisible': kwargs.get('invisible', 0),
                    'enterprise': kwargs.get('enterprise', 0)
                },
                timeout=30
            )
            
            data = response.json()
            if data.get('status') != 1:
                self.logger.error(f"Ошибка отправки ReCaptcha: {data.get('request', 'Unknown')}")
                return None
            
            captcha_id = data.get('request')
            self.logger.info(f"ReCaptcha v2 отправлена на решение, ID: {captcha_id}")
            
            # Ожидание решения
            return self._wait_for_solution(captcha_id, wait_time=20)
            
        except Exception as e:
            self.logger.error(f"Ошибка решения ReCaptcha v2: {e}")
            return None
    
    def solve_hcaptcha(self, site_key: str, page_url: str, **kwargs) -> Optional[str]:
        """Решение hCaptcha"""
        try:
            response = requests.post(
                f"{self.base_url}/in.php",
                data={
                    'key': self.api_key,
                    'method': 'hcaptcha',
                    'sitekey': site_key,
                    'pageurl': page_url,
                    'json': 1
                },
                timeout=30
            )
            
            data = response.json()
            if data.get('status') != 1:
                self.logger.error(f"Ошибка отправки hCaptcha: {data.get('request', 'Unknown')}")
                return None
            
            captcha_id = data.get('request')
            self.logger.info(f"hCaptcha отправлена на решение, ID: {captcha_id}")
            
            # Ожидание решения
            return self._wait_for_solution(captcha_id, wait_time=20)
            
        except Exception as e:
            self.logger.error(f"Ошибка решения hCaptcha: {e}")
            return None
    
    def _wait_for_solution(self, captcha_id: str, wait_time: int = 5, max_attempts: int = 60) -> Optional[str]:
        """Ожидание решения капчи"""
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            
            try:
                # Запрос статуса
                response = requests.get(
                    f"{self.base_url}/res.php",
                    params={
                        'key': self.api_key,
                        'action': 'get',
                        'id': captcha_id,
                        'json': 1
                    },
                    timeout=30
                )
                
                data = response.json()
                
                if data.get('status') == 1:
                    # Решение готово
                    solution = data.get('request')
                    self.logger.info(f"Капча {captcha_id} решена за {attempt * wait_time} сек")
                    return solution
                    
                elif data.get('request') == 'CAPCHA_NOT_READY':
                    # Решение еще не готово
                    if attempt % 5 == 0:
                        self.logger.debug(f"Ожидание решения капчи {captcha_id}... ({attempt * wait_time} сек)")
                    time.sleep(wait_time)
                    
                else:
                    # Ошибка
                    self.logger.error(f"Ошибка при ожидании решения: {data.get('request', 'Unknown')}")
                    return None
                    
            except Exception as e:
                self.logger.error(f"Ошибка запроса статуса капчи: {e}")
                time.sleep(wait_time)
        
        self.logger.warning(f"Превышено время ожидания для капчи {captcha_id}")
        return None
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Получение статуса задачи"""
        try:
            response = requests.get(
                f"{self.base_url}/res.php",
                params={
                    'key': self.api_key,
                    'action': 'get2',
                    'id': task_id,
                    'json': 1
                },
                timeout=30
            )
            
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса задачи: {e}")
            return None
    
    def image_to_base64(self, image_path: str) -> Optional[str]:
        """Конвертация изображения в base64"""
        try:
            with open(image_path, 'rb') as image_file:
                encoded = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded
        except Exception as e:
            self.logger.error(f"Ошибка конвертации изображения: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Тестирование подключения к API"""
        try:
            balance = self.get_balance()
            if balance is not None:
                self.logger.info(f"✅ Подключение к API успешно. Баланс: ${balance:.2f}")
                return True
            else:
                self.logger.error("❌ Не удалось получить баланс")
                return False
        except Exception as e:
            self.logger.error(f"❌ Ошибка подключения к API: {e}")
            return False

# Пример использования
if __name__ == "__main__":
    import sys
    from config import RUCAPTCHA_API_KEY
    
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if not RUCAPTCHA_API_KEY:
        print("❌ API ключ не установлен в config.py")
        sys.exit(1)
    
    solver = RucaptchaSolver(RUCAPTCHA_API_KEY)
    
    # Тест подключения
    if solver.test_connection():
        print("✅ API подключение работает")
    else:
        print("❌ Проблемы с API подключением")
