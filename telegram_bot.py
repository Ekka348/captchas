#!/usr/bin/env python3
"""
🤖 Telegram бот для управления Captcha AutoBot
Управляет автономным ботом, который сам находит и решает капчи
"""

import os
import json
import logging
import asyncio
import threading
from datetime import datetime
from typing import Optional, Dict

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    ContextTypes, MessageHandler, filters
)

from website_automator import WebsiteAutomator
from config import TELEGRAM_TOKEN, ADMIN_IDS
from rucaptcha_api import RucaptchaSolver
from database import init_db, save_earning, get_daily_stats

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TelegramAutoBot')

# Глобальные переменные
automator: Optional[WebsiteAutomator] = None
bot_thread: Optional[threading.Thread] = None
current_target_url: str = ""
is_bot_running = False

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def mask_api_key(api_key: str) -> str:
    """Маскировка API ключа"""
    if len(api_key) > 12:
        return f"{api_key[:8]}...{api_key[-4:]}"
    return "***"

def format_stats(stats: Dict) -> str:
    """Форматирование статистики"""
    if not stats:
        return "Статистика недоступна"
    
    text = "📊 *СТАТИСТИКА*\n\n"
    
    if 'captchas_solved' in stats:
        text += f"• Решено капч: `{stats['captchas_solved']}`\n"
    
    if 'total_earnings' in stats:
        text += f"• Заработано: `${stats['total_earnings']:.4f}`\n"
    
    if 'errors' in stats:
        text += f"• Ошибок: `{stats['errors']}`\n"
    
    if 'runtime' in stats:
        text += f"• Время работы: `{stats['runtime']}`\n"
    
    if 'current_site' in stats and stats['current_site']:
        text += f"• Текущий сайт: `{stats['current_site']}`\n"
    
    return text

async def check_balance() -> float:
    """Проверка баланса Rucaptcha"""
    try:
        from config import RUCAPTCHA_API_KEY
        solver = RucaptchaSolver(RUCAPTCHA_API_KEY)
        balance = solver.get_balance()
        return balance if balance else 0.0
    except:
        return 0.0

# ============================================
# КОМАНДЫ УПРАВЛЕНИЯ
# ============================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - главное меню"""
    user_id = update.effective_user.id
    
    if ADMIN_IDS and user_id not in ADMIN_IDS:
        await update.message.reply_text(
            "⛔ У вас нет доступа к этому боту.\n"
            "Обратитесь к администратору."
        )
        return
    
    keyboard = [
        [
            InlineKeyboardButton("▶️ Запустить бота", callback_data='start_bot'),
            InlineKeyboardButton("⏹️ Остановить", callback_data='stop_bot')
        ],
        [
            InlineKeyboardButton("📊 Статистика", callback_data='stats'),
            InlineKeyboardButton("💰 Баланс", callback_data='balance')
        ],
        [
            InlineKeyboardButton("⚙️ Настройки", callback_data='settings'),
            InlineKeyboardButton("❓ Помощь", callback_data='help')
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 *CAPTCHA AUTO BOT*\n\n"
        f"*Статус:* {'🟢 Работает' if is_bot_running else '🔴 Остановлен'}\n"
        f"*Сайт:* `{current_target_url or 'Не установлен'}`\n\n"
        "Выберите действие:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help - помощь"""
    help_text = (
        "❓ *ПОМОЩЬ ПО АВТО-БОТУ*\n\n"
        "*Как работает:*\n"
        "1. Бот самостоятельно находит капчи на сайте\n"
        "2. Автоматически распознает текст\n"
        "3. Вводит решение и отправляет\n"
        "4. Переходит к следующей капче\n\n"
        
        "*Команды:*\n"
        "• /start - Главное меню\n"
        "• /site <url> - Установить целевой сайт\n"
        "• /stats - Статистика работы\n"
        "• /balance - Баланс Rucaptcha\n"
        "• /stop - Остановить бота\n"
        "• /help - Эта справка\n\n"
        
        "*Как начать:*\n"
        "1. Установите сайт: /site https://пример.com\n"
        "2. Запустите бота: /start_bot\n"
        "3. Бот начнет автоматическое решение\n\n"
        
        "*Требования:*\n"
        "• Аккаунт на rucaptcha.com\n"
        "• API ключ в config.py\n"
        "• Сайт с текстовыми капчами\n"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def set_site_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установка целевого сайта"""
    global current_target_url
    
    if not context.args:
        await update.message.reply_text(
            "Укажите URL сайта:\n"
            "`/site https://example.com`",
            parse_mode='Markdown'
        )
        return
    
    url = context.args[0]
    
    # Простая валидация URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    current_target_url = url
    
    await update.message.reply_text(
        f"✅ Сайт установлен:\n`{url}`\n\n"
        f"Теперь запустите бота командой /start_bot",
        parse_mode='Markdown'
    )

async def start_bot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запуск бота"""
    global automator, bot_thread, is_bot_running, current_target_url
    
    if is_bot_running:
        await update.message.reply_text(
            "⚠️ Бот уже запущен!\n"
            "Используйте /stop для остановки."
        )
        return
    
    if not current_target_url:
        await update.message.reply_text(
            "❌ Сначала установите целевой сайт:\n"
            "`/site https://example.com`",
            parse_mode='Markdown'
        )
        return
    
    # Создаем и запускаем автоматор в отдельном потоке
    automator = WebsiteAutomator()
    
    def run_bot():
        global is_bot_running
        is_bot_running = True
        try:
            automator.start(current_target_url)
        except Exception as e:
            logger.error(f"Ошибка в боте: {e}")
        finally:
            is_bot_running = False
    
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    await update.message.reply_text(
        "🚀 *Бот запущен!*\n\n"
        f"*Сайт:* `{current_target_url}`\n"
        "*Статус:* Автоматическое решение капч\n"
        "*Действие:* Находит → Распознает → Вводит\n\n"
        "Используйте /stats для статистики\n"
        "Используйте /stop для остановки",
        parse_mode='Markdown'
    )

async def stop_bot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Остановка бота"""
    global automator, is_bot_running
    
    if not is_bot_running:
        await update.message.reply_text("🤷 Бот не запущен")
        return
    
    if automator:
        automator.stop()
    
    is_bot_running = False
    
    await update.message.reply_text(
        "🛑 *Бот остановлен*\n\n"
        "Автоматизация завершена.\n"
        "Используйте /stats для итоговой статистики.",
        parse_mode='Markdown'
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика работы"""
    global automator
    
    if not automator:
        await update.message.reply_text("🤷 Бот еще не запускался")
        return
    
    # Получаем статистику
    stats = automator.get_stats()
    
    # Получаем ежедневную статистику из БД
    daily_stats = get_daily_stats()
    
    # Формируем сообщение
    message = "📈 *СТАТИСТИКА РАБОТЫ*\n\n"
    
    # Текущая сессия
    message += "*Текущая сессия:*\n"
    message += format_stats(stats)
    
    # Ежедневная статистика
    if daily_stats:
        message += "\n*За сегодня:*\n"
        message += f"• Капч решено: `{daily_stats.get('captchas_today', 0)}`\n"
        message += f"• Заработано: `${daily_stats.get('earnings_today', 0):.4f}`\n"
    
    # Баланс
    try:
        balance = await check_balance()
        message += f"\n*Баланс Rucaptcha:* `${balance:.4f}`\n"
    except:
        pass
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка баланса"""
    message = await update.message.reply_text(
        "🔄 *Проверка баланса...*",
        parse_mode='Markdown'
    )
    
    try:
        balance = await check_balance()
        
        await message.edit_text(
            f"💰 *БАЛАНС RUCAPTCHA*\n\n"
            f"• *Сумма:* `${balance:.4f}`\n"
            f"• *Статус:* {'🟢 Активен' if balance > 0 else '🔴 Нет средств'}\n"
            f"• *Минимум для вывода:* $0.30\n\n"
            f"_Проверено: {datetime.now().strftime('%H:%M:%S')}_",
            parse_mode='Markdown'
        )
    except Exception as e:
        await message.edit_text(
            f"❌ *ОШИБКА ПРОВЕРКИ*\n\n"
            f"*Причина:* {str(e)}\n\n"
            f"Проверьте:\n"
            f"1. Интернет соединение\n"
            f"2. API ключ в config.py\n"
            f"3. Баланс на rucaptcha.com",
            parse_mode='Markdown'
        )

# ============================================
# ОБРАБОТЧИКИ КНОПОК
# ============================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    
    if action == 'start_bot':
        await start_bot_command(query, context)
    elif action == 'stop_bot':
        await stop_bot_command(query, context)
    elif action == 'stats':
        await stats_command(query, context)
    elif action == 'balance':
        await balance_command(query, context)
    elif action == 'help':
        await help_command(query, context)

# ============================================
# ОСНОВНАЯ ФУНКЦИЯ
# ============================================

def main():
    """Запуск Telegram бота"""
    print("="*60)
    print("🤖 CAPTCHA AUTO BOT - TELEGRAM УПРАВЛЕНИЕ")
    print("="*60)
    
    if not TELEGRAM_TOKEN:
        print("❌ Ошибка: TELEGRAM_TOKEN не установлен!")
        print("Добавьте в Railway Variables:")
        print("TELEGRAM_TOKEN=ваш_токен_бота")
        return
    
    # Инициализация БД
    init_db()
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрируем команды
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("site", set_site_command))
    application.add_handler(CommandHandler("start_bot", start_bot_command))
    application.add_handler(CommandHandler("stop", stop_bot_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("balance", balance_command))
    
    # Регистрируем обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Запускаем бота
    print("✅ Бот запущен!")
    print("💬 Добавьте бота в Telegram")
    print("📱 Отправьте /start для начала")
    print("="*60)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
