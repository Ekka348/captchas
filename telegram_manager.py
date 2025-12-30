#!/usr/bin/env python3
"""
🤖 Telegram бот для управления Captcha AutoBot
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

from config import (
    load_coordinates, load_settings, save_settings,
    print_config_summary, DATA_DIR, STATS_FILE
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/telegram.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('TelegramManager')

# Получаем токен из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")

class TelegramManager:
    """Класс для управления через Telegram"""
    
    def __init__(self):
        self.coordinates = load_coordinates()
        self.settings = load_settings()
        logger.info("✅ Telegram менеджер инициализирован")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start - главное меню"""
        keyboard = [
            [
                InlineKeyboardButton("🎯 Запустить решатель", callback_data='start_solver'),
                InlineKeyboardButton("⏹️ Остановить", callback_data='stop_solver')
            ],
            [
                InlineKeyboardButton("📍 Координаты", callback_data='coordinates'),
                InlineKeyboardButton("⚙️ Настройки", callback_data='settings')
            ],
            [
                InlineKeyboardButton("📊 Статистика", callback_data='stats'),
                InlineKeyboardButton("❓ Помощь", callback_data='help')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤖 *CAPTCHA AUTO BOT - УПРАВЛЕНИЕ*\n\n"
            "*Статус:* 🟢 Готов к работе\n"
            "*Режим:* Локальное распознавание\n"
            "*Хостинг:* Railway\n\n"
            "Выберите действие:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help - справка"""
        help_text = """
❓ *ПОМОЩЬ ПО CAPTCHA AUTO BOT*

*Как это работает:*
1. Бот делает скриншот области с капчей
2. Локально распознает текст через Tesseract OCR
3. Вводит текст в указанное поле
4. Нажимает кнопку "следующая"
5. Повторяет автоматически

*Требования:*
• Установленный Tesseract OCR
• Настроенные координаты областей
• Активное окно с капчами

*Команды управления:*
/start - Главное меню
/help - Эта справка
/stats - Статистика работы
/settings - Настройки
/coordinates - Просмотр координат

*Для запуска решателя:*
Нажмите кнопку "🎯 Запустить решатель" или отправьте /run

*Настройка координат:*
Запустите `python3 setup_coordinates.py` на компьютере
"""
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /stats - статистика"""
        try:
            if os.path.exists(STATS_FILE):
                with open(STATS_FILE, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                
                stats_text = "📊 *СТАТИСТИКА РАБОТЫ*\n\n"
                stats_text += f"• Всего решено: `{stats.get('total_solved', 0)}`\n"
                stats_text += f"• Всего ошибок: `{stats.get('total_errors', 0)}`\n"
                
                if stats.get('last_solution'):
                    stats_text += f"• Последнее решение: `{stats['last_solution']}`\n"
                
                if stats.get('sessions'):
                    total_sessions = len(stats['sessions'])
                    stats_text += f"• Всего сессий: `{total_sessions}`\n"
                    
                    # Последняя сессия
                    last_session = stats['sessions'][-1]
                    stats_text += f"• Последняя сессия:\n"
                    stats_text += f"  Решено: `{last_session.get('solved', 0)}`\n"
                    stats_text += f"  Ошибок: `{last_session.get('errors', 0)}`\n"
                
                await update.message.reply_text(stats_text, parse_mode='Markdown')
            else:
                await update.message.reply_text(
                    "📊 Статистика пока не собрана.\n"
                    "Запустите решатель для начала работы.",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"Ошибка загрузки статистики: {e}")
            await update.message.reply_text(
                "❌ Ошибка загрузки статистики",
                parse_mode='Markdown'
            )
    
    async def coordinates_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /coordinates - просмотр координат"""
        coords = self.coordinates
        
        coords_text = "📍 *ТЕКУЩИЕ КООРДИНАТЫ*\n\n"
        coords_text += f"*Область капчи:*\n`{coords.get('captcha_region')}`\n\n"
        coords_text += f"*Поле ввода:*\n`{coords.get('input_coords')}`\n\n"
        coords_text += f"*Кнопка:*\n`{coords.get('button_coords')}`\n\n"
        
        if coords.get('screen_size'):
            coords_text += f"*Размер экрана:*\n`{coords['screen_size']}`\n\n"
        
        if coords.get('created_at'):
            try:
                created = datetime.fromisoformat(coords['created_at'].replace('Z', '+00:00'))
                coords_text += f"*Создано:* `{created.strftime('%Y-%m-%d %H:%M')}`\n"
            except:
                pass
        
        coords_text += "\n*Для изменения:*\nЗапустите `python3 setup_coordinates.py` локально"
        
        await update.message.reply_text(coords_text, parse_mode='Markdown')
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /settings - настройки"""
        settings = self.settings
        
        keyboard = [
            [
                InlineKeyboardButton(
                    f"👤 Человекоподобно: {'✅' if settings.get('human_like', True) else '❌'}",
                    callback_data='toggle_human_like'
                )
            ],
            [
                InlineKeyboardButton(
                    f"🖼️ Сохранять скриншоты: {'✅' if settings.get('save_screenshots', True) else '❌'}",
                    callback_data='toggle_screenshots'
                )
            ],
            [
                InlineKeyboardButton(
                    f"🐛 Режим отладки: {'✅' if settings.get('debug_mode', False) else '❌'}",
                    callback_data='toggle_debug'
                )
            ],
            [
                InlineKeyboardButton("💾 Сохранить", callback_data='save_settings'),
                InlineKeyboardButton("↩️ Назад", callback_data='back_to_menu')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        settings_text = "⚙️ *НАСТРОЙКИ*\n\n"
        settings_text += "Измените параметры и нажмите 'Сохранить':\n"
        
        await update.message.reply_text(
            settings_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def run_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /run - запуск решателя"""
        # В реальном приложении здесь был бы запуск решателя
        # В Railway мы можем только управлять настройками
        
        await update.message.reply_text(
            "⚠️ *ЗАПУСК РЕШАТЕЛЯ*\n\n"
            "В режиме Railway автоматический решатель не может быть запущен,\n"
            "так как требует доступа к экрану и установленного Tesseract.\n\n"
            "*Для запуска:*\n"
            "1. Установите Tesseract OCR на свой компьютер\n"
            "2. Настройте координаты через `setup_coordinates.py`\n"
            "3. Запустите `python3 main.py` локально\n\n"
            "Этот бот предназначен только для управления настройками.",
            parse_mode='Markdown'
        )
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий кнопок"""
        query = update.callback_query
        await query.answer()
        
        action = query.data
        
        if action == 'start_solver':
            await self.run_command(query, context)
            
        elif action == 'stop_solver':
            await query.message.reply_text(
                "⏹️ *ОСТАНОВКА*\n\n"
                "В режиме Railway решатель не запущен.\n"
                "Для остановки локального решателя нажмите Ctrl+C.",
                parse_mode='Markdown'
            )
            
        elif action == 'coordinates':
            await self.coordinates_command(query, context)
            
        elif action == 'settings':
            await self.settings_command(query, context)
            
        elif action == 'stats':
            await self.stats_command(query, context)
            
        elif action == 'help':
            await self.help_command(query, context)
            
        elif action == 'toggle_human_like':
            self.settings['human_like'] = not self.settings.get('human_like', True)
            await self.settings_command(query, context)
            
        elif action == 'toggle_screenshots':
            self.settings['save_screenshots'] = not self.settings.get('save_screenshots', True)
            await self.settings_command(query, context)
            
        elif action == 'toggle_debug':
            self.settings['debug_mode'] = not self.settings.get('debug_mode', False)
            await self.settings_command(query, context)
            
        elif action == 'save_settings':
            save_settings(self.settings)
            await query.message.reply_text(
                "✅ Настройки сохранены!",
                parse_mode='Markdown'
            )
            
        elif action == 'back_to_menu':
            await self.start_command(query, context)

def main():
    """Запуск Telegram бота"""
    print("="*60)
    print("🤖 TELEGRAM УПРАВЛЕНИЕ CAPTCHA AUTOBOT")
    print("="*60)
    
    if not TELEGRAM_TOKEN:
        print("❌ ОШИБКА: TELEGRAM_TOKEN не установлен!")
        print("Добавьте в Railway Variables:")
        print("TELEGRAM_TOKEN=ваш_токен_бота")
        return
    
    print(f"✅ Токен: {TELEGRAM_TOKEN[:10]}...")
    print("✅ Конфигурация загружена")
    print("="*60)
    print("🚀 Запуск Telegram бота...")
    print("="*60)
    
    # Создаем менеджер
    manager = TelegramManager()
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрируем команды
    application.add_handler(CommandHandler("start", manager.start_command))
    application.add_handler(CommandHandler("help", manager.help_command))
    application.add_handler(CommandHandler("stats", manager.stats_command))
    application.add_handler(CommandHandler("settings", manager.settings_command))
    application.add_handler(CommandHandler("coordinates", manager.coordinates_command))
    application.add_handler(CommandHandler("run", manager.run_command))
    
    # Регистрируем обработчик кнопок
    application.add_handler(CallbackQueryHandler(manager.button_handler))
    
    # Запускаем бота
    print("✅ Бот запущен!")
    print("💬 Отправьте /start в Telegram")
    print("="*60)
    
    application.run_polling(allowed_updates=['message', 'callback_query'])

if __name__ == "__main__":
    main()
