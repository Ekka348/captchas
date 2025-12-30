#!/usr/bin/env python3
"""
🤖 Telegram бот для управления Captcha Worker
"""

import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TelegramBot')

# Получаем переменные окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
RUCAPTCHA_API_KEY = os.getenv("RUCAPTCHA_API_KEY", "99461b14be32f596e034e2459b05e645")

def mask_key(key: str) -> str:
    """Маскировка API ключа для безопасности"""
    if len(key) > 10:
        return f"{key[:5]}...{key[-5:]}"
    return "***"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    keyboard = [
        [InlineKeyboardButton("📊 Статус системы", callback_data='status')],
        [InlineKeyboardButton("💰 Проверить баланс", callback_data='balance')],
        [InlineKeyboardButton("❓ Помощь", callback_data='help')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 *CAPTCHA AUTO BOT*\n\n"
        "*Статус:* 🟢 Система работает\n"
        "*API ключ:* `" + mask_key(RUCAPTCHA_API_KEY) + "`\n"
        "*Хостинг:* Railway\n\n"
        "Выберите действие:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
❓ *ПОМОЩЬ ПО CAPTCHA BOT*

*Как начать заработок:*
1. Загрузите файл `captcha_worker.py` на свой компьютер
2. Запустите его: `python3 captcha_worker.py`
3. Используйте API ключ: `""" + RUCAPTCHA_API_KEY + """`

*Что делает бот:*
• Автоматически решает капчи
• Зарабатывает деньги 24/7
• Сохраняет статистику

*Команды управления:*
/start - Главное меню
/help - Эта справка
/status - Статус системы

*Примерный заработок:*
• 0.0003$ за капчу
• 10-30 капч в час
• 2-7$ в день
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /status"""
    status_text = """
📊 *СТАТУС СИСТЕМЫ*

*Telegram Bot:* 🟢 Работает
*API соединение:* ✅ Активно
*Баланс:* Используйте кнопку "Проверить баланс"
*Хостинг:* Railway

*Для запуска заработка:*
1. Скачайте `captcha_worker.py`
2. Запустите на своем компьютере
3. Начните зарабатывать автоматически
"""
    
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка баланса через Rucaptcha API"""
    import requests
    
    message = await update.message.reply_text(
        "🔄 *Проверяю баланс...*\n\n"
        "Подключаюсь к Rucaptcha API...",
        parse_mode='Markdown'
    )
    
    try:
        # Запрос баланса
        response = requests.get(
            "https://rucaptcha.com/res.php",
            params={
                'key': RUCAPTCHA_API_KEY,
                'action': 'getbalance',
                'json': 1
            },
            timeout=10
        )
        
        data = response.json()
        
        if data.get('status') == 1:
            balance = float(data['request'])
            
            await message.edit_text(
                f"💰 *БАЛАНС RUCAPTCHA*\n\n"
                f"*Сумма:* `${balance:.4f}`\n"
                f"*Статус:* {'🟢 Активен' if balance > 0 else '🔴 Пополните счет'}\n"
                f"*Минимум вывода:* $0.30\n\n"
                f"*API ключ:* `{mask_key(RUCAPTCHA_API_KEY)}`\n\n"
                f"_Для заработка запустите captcha_worker.py_",
                parse_mode='Markdown'
            )
        else:
            error_msg = data.get('request', 'Неизвестная ошибка')
            await message.edit_text(
                f"❌ *ОШИБКА ПРОВЕРКИ*\n\n"
                f"*Ошибка:* {error_msg}\n"
                f"*Ключ:* `{mask_key(RUCAPTCHA_API_KEY)}`\n\n"
                f"Проверьте:\n"
                f"1. Корректность API ключа\n"
                f"2. Баланс на rucaptcha.com\n"
                f"3. Интернет соединение",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        await message.edit_text(
            f"❌ *ОШИБКА СОЕДИНЕНИЯ*\n\n"
            f"*Причина:* {str(e)}\n\n"
            f"Попробуйте позже или проверьте:\n"
            f"1. Интернет соединение\n"
            f"2. Доступность rucaptcha.com",
            parse_mode='Markdown'
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    
    if action == 'status':
        await status_command(query, context)
    elif action == 'balance':
        await balance_command(query, context)
    elif action == 'help':
        await help_command(query, context)

def main():
    """Основная функция запуска бота"""
    print("=" * 50)
    print("🤖 CAPTCHA TELEGRAM BOT")
    print("=" * 50)
    
    if not TELEGRAM_TOKEN:
        print("❌ ОШИБКА: TELEGRAM_TOKEN не установлен!")
        print("Добавьте в Railway Variables:")
        print("TELEGRAM_TOKEN=ваш_токен_бота")
        return
    
    print(f"✅ Токен: {TELEGRAM_TOKEN[:10]}...")
    print(f"✅ API ключ: {mask_key(RUCAPTCHA_API_KEY)}")
    print("=" * 50)
    print("🚀 Запуск Telegram бота...")
    print("=" * 50)
    
    # Создаем и запускаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрируем команды
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("balance", balance_command))
    
    # Регистрируем обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Запускаем бота
    print("✅ Бот запущен!")
    print("💬 Отправьте /start в Telegram")
    print("=" * 50)
    
    # Запускаем polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
