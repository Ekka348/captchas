#!/usr/bin/env python3
"""
📝 Настройка логирования для проекта
"""

import logging
import sys
import os
from typing import Optional

def setup_logger(
    name: str,
    log_file: str,
    level: str = "INFO",
    format_str: Optional[str] = None,
    date_format: Optional[str] = None
) -> logging.Logger:
    """
    Настройка логгера с файловым и консольным выводом
    
    Args:
        name: Имя логгера
        log_file: Путь к файлу логов
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR)
        format_str: Формат строки лога
        date_format: Формат даты
        
    Returns:
        Настроенный логгер
    """
    # Создаем директорию для логов если нужно
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    # Создаем логгер
    logger = logging.getLogger(name)
    
    # Устанавливаем уровень
    logger.setLevel(getattr(logging, level.upper()))
    
    # Формат по умолчанию
    if format_str is None:
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    if date_format is None:
        date_format = "%Y-%m-%d %H:%M:%S"
    
    formatter = logging.Formatter(format_str, datefmt=date_format)
    
    # Файловый handler
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"❌ Ошибка создания файлового логгера: {e}")
    
    # Консольный handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Отключаем распространение на корневой логгер
    logger.propagate = False
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Получение логгера по имени
    
    Args:
        name: Имя логгера
        
    Returns:
        Существующий или новый логгер
    """
    return logging.getLogger(name)

def setup_rotating_logger(
    name: str,
    log_file: str,
    max_bytes: int = 10485760,  # 10 MB
    backup_count: int = 5,
    level: str = "INFO"
) -> logging.Logger:
    """
    Настройка логгера с ротацией файлов
    
    Args:
        name: Имя логгера
        log_file: Путь к файлу логов
        max_bytes: Максимальный размер файла перед ротацией
        backup_count: Количество backup файлов
        level: Уровень логирования
        
    Returns:
        Настроенный логгер с ротацией
    """
    import logging.handlers
    
    # Создаем директорию
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    # Создаем логгер
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Форматтер
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Rotating file handler
    try:
        rotating_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        rotating_handler.setFormatter(formatter)
        logger.addHandler(rotating_handler)
    except Exception as e:
        print(f"❌ Ошибка создания rotating логгера: {e}")
    
    # Консольный handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    logger.propagate = False
    
    return logger

def log_exception(logger: logging.Logger, exception: Exception, context: str = ""):
    """
    Логирование исключения с контекстом
    
    Args:
        logger: Логгер для записи
        exception: Исключение
        context: Контекст ошибки
    """
    if context:
        logger.error(f"{context}: {str(exception)}")
    else:
        logger.error(f"Exception: {str(exception)}")
    
    import traceback
    logger.error(f"Traceback:\n{traceback.format_exc()}")

# Пример использования
if __name__ == "__main__":
    # Тестирование логгера
    test_logger = setup_logger(
        name="TestLogger",
        log_file="logs/test.log",
        level="DEBUG"
    )
    
    test_logger.debug("Это debug сообщение")
    test_logger.info("Это info сообщение")
    test_logger.warning("Это warning сообщение")
    test_logger.error("Это error сообщение")
    
    print("✅ Логирование настроено и протестировано")
