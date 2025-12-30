#!/usr/bin/env python3
"""
🤖 Telegram бот с встроенным healthcheck для Railway
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# ============================================
# НАСТРОЙКИ
# ============================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
ADMIN_IDS = []
try:
    admin_ids_str = os.getenv("ADMIN_IDS", "")
    if admin_ids_str:
        ADMIN_IDS = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip()]
except:
    ADMIN_IDS = []

RUCAPTCHA_API_KEY = os.getenv("RUCAPTCHA_API_KEY", "")

# ============================================
# ЛОГИРОВАНИЕ
# ============================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TelegramBot')

# ============================================
# HEALTHCHECK СЕРВЕР
# ============================================

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Обработчик healthcheck запросов"""
    
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'healthy',
                'service': 'Captcha Earning Bot',
                'bot_status': 'running',
                'timestamp': datetime.now().isoformat(),
                'telegram': 'connected' if TELEGRAM_TOKEN else 'no_token',
                'rucaptcha': 'configured' if RUCAPTCHA_API_KEY else 'no_key'
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Отключаем логирование HTTP запросов
        pass

def start_health_server(port: int = 8080):
    """Запуск HTTP сервера для healthcheck"""
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        logger.info(f"🌐 Healthcheck сервер запущен на порту {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"❌ Ошибка healthcheck сервера: {e}")

# ============================================
# TELEGRAM КОМАНДЫ
# ============================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user = update.effective_user
    
    # Проверка админа (если указаны ADMIN_IDS)
    if ADMIN_IDS and user.id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Доступ запрещен")
        return
    
    keyboard = [
        [InlineKeyboardButton("📊 Статус", callback_data='status'),
         InlineKeyboardButton("🩺 Health", callback_data='health')],
        [InlineKeyboardButton("💰 Баланс", callback_data='balance'),
         InlineKeyboardButton("⚙️ Настройки", callback_data='settings')],
        [InlineKeyboardButton("❓ Помощь", callback_data='help')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🤖 *Добро пожаловать, {user.first_name}!*\n\n"
        "*Captcha Earning Bot* запущен и готов к работе.\n\n"
        "Используйте кнопки ниже для управления:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /health - проверка состояния системы"""
    health_status = await get_health_status()
    
    status_text = (
        f"🩺 *HEALTH CHECK*\n\n"
        f"• *Бот:* {health_status['bot']}\n"
        f"• *Telegram:* {health_status['telegram']}\n"
        f"• *Rucaptcha:* {health_status['rucaptcha']}\n"
        f"• *Время:* {health_status['time']}\n"
        f"• *Статус:* {health_status['status']}\n\n"
        f"_Проверка Railway: /health endpoint активен_"
    )
    
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /status - статус работы"""
    status_text = (
        "📊 *СТАТУС СИСТЕМЫ*\n\n"
        "• *Бот:* Активен ✅\n"
        "• *Хостинг:* Railway 🚂\n"
        "• *Режим:* Автономный\n"
        "• *Время работы:* С момента запуска\n\n"
        "*Доступные функции:*\n"
        "✓ Healthcheck endpoint\n"
        "✓ Управление через Telegram\n"
        "✓ Мониторинг состояния\n\n"
        "_Используйте /health для детальной проверки_"
    )
    
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /balance - проверка баланса rucaptcha"""
    if not RUCAPTCHA_API_KEY:
        await update.message.reply_text(
            "❌ *API ключ rucaptcha не настроен*\n\n"
            "Добавьте RUCAPTCHA_API_KEY в переменные Railway",
            parse_mode='Markdown'
        )
        return
    
    try:
        import requests
        
        # Запрос баланса через API rucaptcha
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
            await update.message.reply_text(
                f"💰 *БАЛАНС RUCAPTCHA*\n\n"
                f"• *Сумма:* ${balance:.2f}\n"
                f"• *Минимум для вывода:* $0.30\n"
                f"• *Статус:* Активен ✅\n\n"
                f"_Баланс обновлен_",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"⚠️ *Ошибка проверки баланса*\n\n"
                f"• *Ответ API:* {data.get('request', 'Unknown')}\n"
                f"• *Проверьте:* API ключ\n"
                f"• *Действие:* Перезапустите бота",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        await update.message.reply_text(
            f"❌ *Ошибка соединения*\n\n"
            f"• *Причина:* {str(e)}\n"
            f"• *Проверьте:* Интернет соединение\n"
            f"• *Действие:* Попробуйте позже",
            parse_mode='Markdown'
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    help_text = (
        "❓ *ПОМОЩЬ ПО CAPTCHA EARNING BOT*\n\n"
        "*Основные команды:*\n"
        "• /start - Главное меню\n"
        "• /health - Проверка состояния\n"
        "• /status - Статус работы\n"
        "• /balance - Баланс rucaptcha\n"
        "• /help - Эта справка\n\n"
        "*Для Railway:*\n"
        "• Healthcheck: `https://ваш-проект.up.railway.app/health`\n"
        "• Порт: 8080 (автоматически)\n\n"
        "*Настройка:*\n"
        "1. TELEGRAM_TOKEN - токен бота\n"
        "2. RUCAPTCHA_API_KEY - ключ rucaptcha\n"
        "3. ADMIN_IDS - ID администраторов\n\n"
        "_Бот работает 24/7 на Railway_"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ============================================
# CALLBACK ОБРАБОТЧИКИ
# ============================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback кнопок"""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    
    if action == 'health':
        await health_command(query, context)
    elif action == 'status':
        await status_command(query, context)
    elif action == 'balance':
        await balance_command(query, context)
    elif action == 'settings':
        await query.edit_message_text(
            "⚙️ *НАСТРОЙКИ*\n\n"
            "Текущая конфигурация:\n"
            f"• Telegram: {'✅' if TELEGRAM_TOKEN else '❌'}\n"
            f"• Rucaptcha: {'✅' if RUCAPTCHA_API_KEY else '❌'}\n"
            f"• Админы: {len(ADMIN_IDS)}\n\n"
            "_Настройте переменные в Railway_",
            parse_mode='Markdown'
        )
    elif action == 'help':
        await help_command(query, context)

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

async def get_health_status() -> Dict:
    """Получение статуса здоровья системы"""
    return {
        'bot': 'running',
        'telegram': 'connected' if TELEGRAM_TOKEN else 'no_token',
        'rucaptcha': 'configured' if RUCAPTCHA_API_KEY else 'no_key',
        'time': datetime.now().strftime('%H:%M:%S'),
        'status': 'healthy' if TELEGRAM_TOKEN else 'unhealthy',
        'railway': True,
        'port': os.getenv('PORT', '8080')
    }

def check_environment() -> bool:
    """Проверка окружения"""
    errors = []
    
    if not TELEGRAM_TOKEN:
        errors.append("TELEGRAM_TOKEN не установлен")
    
    if not RUCAPTCHA_API_KEY:
        errors.append("RUCAPTCHA_API_KEY не установлен")
    
    if errors:
        logger.error("❌ Ошибки конфигурации:")
        for error in errors:
            logger.error(f"  • {error}")
        return False
    
    return True

# ============================================
# ОСНОВНАЯ ФУНКЦИЯ
# ============================================

def main():
    """Основная функция запуска"""
    print("="*60)
    print("🤖 CAPTCHA EARNING BOT - RAILWAY EDITION")
    print("="*60)
    
    # Проверка окружения
    if not check_environment():
        print("\n❌ Исправьте ошибки и перезапустите")
        return
    
    print(f"✅ Конфигурация корректна")
    print(f"📱 Telegram: {TELEGRAM_TOKEN[:10]}...{TELEGRAM_TOKEN[-10:]}")
    print(f"🎯 Rucaptcha: {RUCAPTCHA_API_KEY[:5]}...{RUCAPTCHA_API_KEY[-5:]}")
    print(f"👑 Админы: {len(ADMIN_IDS)}")
    print("="*60)
    
    # Получаем порт из переменной Railway
    port = int(os.getenv('PORT', 8080))
    
    # Запускаем healthcheck сервер в отдельном потоке
    health_thread = Thread(target=start_health_server, args=(port,), daemon=True)
    health_thread.start()
    
    print(f"🌐 Healthcheck сервер запущен на порту {port}")
    print(f"🔗 Endpoint: http://0.0.0.0:{port}/health")
    print("="*60)
    
    # Создаем Telegram приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрируем команды
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("health", health_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Регистрируем обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Запускаем бота
    print("🤖 Запуск Telegram бота...")
    print("💬 Добавьте бота в Telegram и отправьте /start")
    print("⏳ Ожидание команд...")
    print("="*60)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
