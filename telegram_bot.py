#!/usr/bin/env python3
"""
🤖 Telegram бот для УПРАВЛЕНИЯ Captcha Worker
Упрощенная версия БЕЗ healthcheck сервера
"""

import os
import json
import logging
import asyncio
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ============================================
# КОНФИГУРАЦИЯ
# ============================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
RUCAPTCHA_API_KEY = os.getenv("RUCAPTCHA_API_KEY", "99461b14be32f596e034e2459b05e645")

# ============================================
# ЛОГИРОВАНИЕ
# ============================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TelegramBotManager')

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

async def check_rucaptcha_balance(api_key: str):
    """Асинхронная проверка баланса Rucaptcha"""
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            url = "https://rucaptcha.com/res.php"
            params = {
                'key': api_key,
                'action': 'getbalance',
                'json': 1
            }
            
            async with session.get(url, params=params, timeout=10) as response:
                data = await response.json()
                return data
    except Exception as e:
        logger.error(f"Ошибка проверки баланса: {e}")
        return None

def mask_api_key(api_key: str) -> str:
    """Маскировка API ключа для логов"""
    if len(api_key) > 12:
        return f"{api_key[:8]}...{api_key[-4:]}"
    return "***"

# ============================================
# TELEGRAM КОМАНДЫ УПРАВЛЕНИЯ
# ============================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню управления"""
    keyboard = [
        [InlineKeyboardButton("📊 Статус", callback_data='status'),
         InlineKeyboardButton("💰 Баланс", callback_data='balance')],
        [InlineKeyboardButton("⚙️ Настройки", callback_data='settings'),
         InlineKeyboardButton("❓ Помощь", callback_data='help')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 *CAPTCHA EARNING BOT - УПРАВЛЕНИЕ*\n\n"
        "*Статус:* Система готова к работе\n"
        "*Роль:* Управление и мониторинг\n"
        "*Хостинг:* Railway\n\n"
        "Используйте кнопки ниже:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статус системы"""
    current_time = datetime.now().strftime("%H:%M:%S")
    
    status_text = (
        "📊 *СТАТУС СИСТЕМЫ*\n\n"
        "*Telegram Bot:*\n"
        "• Статус: ✅ Активен\n"
        "• Время: " + current_time + "\n"
        "• Хостинг: Railway\n\n"
        "*Rucaptcha:*\n"
        f"• Ключ: `{mask_api_key(RUCAPTCHA_API_KEY)}`\n"
        "• Статус: ⏳ Проверка...\n\n"
        "*Инструкция:*\n"
        "1. Запустите worker локально\n"
        "2. Используйте API ключ выше\n"
        "3. Зарабатывайте автоматически"
    )
    
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка баланса Rucaptcha"""
    # Отправляем сообщение о начале проверки
    message = await update.message.reply_text(
        "🔄 *Проверка баланса...*\n\n"
        f"Ключ: `{mask_api_key(RUCAPTCHA_API_KEY)}`",
        parse_mode='Markdown'
    )
    
    try:
        # Проверяем баланс
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            url = "https://rucaptcha.com/res.php"
            params = {
                'key': RUCAPTCHA_API_KEY,
                'action': 'getbalance',
                'json': 1
            }
            
            async with session.get(url, params=params, timeout=10) as response:
                data = await response.json()
                
                if data.get('status') == 1:
                    balance = float(data['request'])
                    
                    # Обновляем сообщение с результатом
                    await message.edit_text(
                        f"💰 *БАЛАНС RUCAPTCHA*\n\n"
                        f"• *Ключ:* `{mask_api_key(RUCAPTCHA_API_KEY)}`\n"
                        f"• *Баланс:* ${balance:.4f}\n"
                        f"• *Статус:* {'🟢 Активен' if balance > 0 else '🟡 Нет средств'}\n"
                        f"• *Минимум для вывода:* $0.30\n\n"
                        f"_Проверено в {datetime.now().strftime('%H:%M:%S')}_",
                        parse_mode='Markdown'
                    )
                else:
                    error_msg = data.get('request', 'Неизвестная ошибка')
                    await message.edit_text(
                        f"❌ *ОШИБКА ПРОВЕРКИ*\n\n"
                        f"• *Ошибка:* {error_msg}\n"
                        f"• *Ключ:* `{mask_api_key(RUCAPTCHA_API_KEY)}`\n\n"
                        f"_Проверьте API ключ_",
                        parse_mode='Markdown'
                    )
                    
    except Exception as e:
        await message.edit_text(
            f"❌ *ОШИБКА СОЕДИНЕНИЯ*\n\n"
            f"• *Причина:* {str(e)}\n"
            f"• *Действие:* Проверьте интернет\n\n"
            f"_Попробуйте позже_",
            parse_mode='Markdown'
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Справка"""
    help_text = (
        "❓ *ПОМОЩЬ ПО УПРАВЛЕНИЮ*\n\n"
        "*Команды:*\n"
        "• /start - Главное меню\n"
        "• /status - Статус системы\n"
        "• /balance - Проверка баланса\n"
        "• /help - Эта справка\n\n"
        "*Для заработка:*\n"
        "1. Скачайте `captcha_worker.py`\n"
        "2. Запустите на своем компьютере\n"
        "3. Используйте API ключ:\n"
        f"   `{RUCAPTCHA_API_KEY}`\n\n"
        "*Важно:* Этот бот только управляет!"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Настройки"""
    await update.message.reply_text(
        "⚙️ *НАСТРОЙКИ*\n\n"
        "*Текущая конфигурация:*\n"
        f"• API ключ: `{mask_api_key(RUCAPTCHA_API_KEY)}`\n"
        f"• Время: {datetime.now().strftime('%H:%M:%S')}\n"
        f"• Хостинг: Railway\n\n"
        "*Для изменения:*\n"
        "Измените переменные в Railway\n\n"
        "*Healthcheck:* Отключен (специально)",
        parse_mode='Markdown'
    )

# ============================================
# CALLBACK ОБРАБОТЧИКИ
# ============================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопок"""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    
    if action == 'status':
        await status_command(query, context)
    elif action == 'balance':
        await balance_command(query, context)
    elif action == 'settings':
        await settings_command(query, context)
    elif action == 'help':
        await help_command(query, context)

# ============================================
# ОСНОВНАЯ ФУНКЦИЯ (упрощенная)
# ============================================

def main():
    """Запуск бота управления - упрощенная версия"""
    print("="*60)
    print("🤖 TELEGRAM BOT MANAGER")
    print("="*60)
    
    if not TELEGRAM_TOKEN:
        print("❌ Ошибка: TELEGRAM_TOKEN не установлен!")
        print("Добавьте в Railway Variables:")
        print("TELEGRAM_TOKEN=ваш_токен_бота")
        return
    
    print(f"✅ Токен: {TELEGRAM_TOKEN[:10]}...")
    print(f"✅ API ключ: {mask_api_key(RUCAPTCHA_API_KEY)}")
    print("="*60)
    print("🚀 Запуск Telegram бота...")
    print("="*60)
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрируем команды
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("settings", settings_command))
    
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
