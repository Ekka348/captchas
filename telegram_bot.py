#!/usr/bin/env python3
"""
🤖 Telegram бот для УПРАВЛЕНИЯ Captcha Worker
НЕ решает капчи, только управление!
"""

import os
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ============================================
# КОНФИГУРАЦИЯ
# ============================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
ADMIN_IDS = []
try:
    admin_ids_str = os.getenv("ADMIN_IDS", "")
    if admin_ids_str:
        ADMIN_IDS = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip()]
except:
    ADMIN_IDS = []

# ============================================
# ЛОГИРОВАНИЕ
# ============================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TelegramBotManager')

# ============================================
# HEALTHCHECK СЕРВЕР (для Railway)
# ============================================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'healthy',
                'service': 'Telegram Bot Manager',
                'telegram': 'connected' if TELEGRAM_TOKEN else 'disconnected',
                'role': 'management_only',
                'warning': 'Это бот управления, НЕ решает капчи!'
            }
            
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def start_health_server(port=8080):
    """Запуск HTTP сервера для Railway"""
    try:
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        logger.info(f"✅ Healthcheck сервер запущен на порту {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"❌ Ошибка сервера: {e}")

# ============================================
# TELEGRAM КОМАНДЫ УПРАВЛЕНИЯ
# ============================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню управления"""
    keyboard = [
        [InlineKeyboardButton("📊 Статус воркера", callback_data='worker_status')],
        [InlineKeyboardButton("💰 Баланс Rucaptcha", callback_data='check_balance')],
        [InlineKeyboardButton("⚙️ Настройки", callback_data='settings')],
        [InlineKeyboardButton("❓ Помощь", callback_data='help')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎮 *ЦЕНТР УПРАВЛЕНИЯ Captcha Earning Bot*\n\n"
        "*Этот бот:*\n"
        "• Управляет Captcha Worker\n"
        "• Мониторит статус\n"
        "• Проверяет баланс\n"
        "• НЕ решает капчи!\n\n"
        "*Captcha Worker:*\n"
        "• Решает капчи на rucaptcha\n"
        "• Работает отдельно\n"
        "• Зарабатывает деньги\n\n"
        "Используйте кнопки для управления:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статус системы"""
    await update.message.reply_text(
        "📊 *СТАТУС СИСТЕМЫ*\n\n"
        "*Telegram Bot Manager:*\n"
        "• Статус: ✅ Активен\n"
        "• Роль: Управление\n"
        "• Хостинг: Railway\n\n"
        "*Captcha Worker:*\n"
        "• Статус: ⚠️ Не запущен\n"
        "• Расположение: Локальная машина\n"
        "• Заработок: Не активен\n\n"
        "_Для запуска воркера используйте локальный скрипт_",
        parse_mode='Markdown'
    )

async def check_balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка баланса Rucaptcha"""
    # Запрос API ключа у пользователя
    await update.message.reply_text(
        "💰 *ПРОВЕРКА БАЛАНСА RUCAPTCHA*\n\n"
        "Для проверки баланса отправьте ваш API ключ Rucaptcha:\n\n"
        "Пример команды:\n"
        "`/balance 99461b14be32f596e034e2459b05e645`\n\n"
        "*Внимание:* Не делитесь ключом публично!",
        parse_mode='Markdown'
    )

async def balance_with_key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка баланса с API ключом"""
    if not context.args:
        await update.message.reply_text(
            "❌ Укажите API ключ!\n\n"
            "Пример: `/balance ваш_api_ключ`",
            parse_mode='Markdown'
        )
        return
    
    api_key = context.args[0].strip()
    
    try:
        import requests
        
        # Скрываем часть ключа в логах
        masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
        
        await update.message.reply_text(
            f"🔄 Проверяю баланс для ключа: `{masked_key}`...",
            parse_mode='Markdown'
        )
        
        response = requests.get(
            "https://rucaptcha.com/res.php",
            params={
                'key': api_key,
                'action': 'getbalance',
                'json': 1
            },
            timeout=10
        )
        
        data = response.json()
        
        if data.get('status') == 1:
            balance = float(data['request'])
            status = "🟢 Активен" if balance > 0 else "🟡 Нет средств"
            
            await update.message.reply_text(
                f"💰 *БАЛАНС RUCAPTCHA*\n\n"
                f"• *Ключ:* `{masked_key}`\n"
                f"• *Баланс:* ${balance:.4f}\n"
                f"• *Статус:* {status}\n"
                f"• *Минимум для вывода:* $0.30\n\n"
                f"_Баланс успешно проверен_",
                parse_mode='Markdown'
            )
        else:
            error_msg = data.get('request', 'Неизвестная ошибка')
            await update.message.reply_text(
                f"❌ *ОШИБКА ПРОВЕРКИ*\n\n"
                f"• *Ключ:* `{masked_key}`\n"
                f"• *Ошибка:* {error_msg}\n"
                f"• *Возможные причины:*\n"
                f"  - Неверный API ключ\n"
                f"  - Ключ заблокирован\n"
                f"  - Проблемы с API\n\n"
                f"_Проверьте ключ и попробуйте снова_",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        await update.message.reply_text(
            f"❌ *ОШИБКА СОЕДИНЕНИЯ*\n\n"
            f"• *Причина:* {str(e)}\n"
            f"• *Действие:* Проверьте интернет\n\n"
            f"_Попробуйте позже_",
            parse_mode='Markdown'
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Справка"""
    await update.message.reply_text(
        "❓ *ПОМОЩЬ ПО УПРАВЛЕНИЮ*\n\n"
        "*Архитектура системы:*\n"
        "1. 🤖 *Этот бот* (Railway) - Управление\n"
        "2. 🎯 *Captcha Worker* (Локально) - Заработок\n\n"
        "*Команды управления:*\n"
        "• `/start` - Главное меню\n"
        "• `/status` - Статус системы\n"
        "• `/balance API_КЛЮЧ` - Проверка баланса\n"
        "• `/help` - Эта справка\n\n"
        "*Для заработка:*\n"
        "1. Запустите `captcha_worker.py` локально\n"
        "2. Используйте API ключ rucaptcha\n"
        "3. Мониторьте через этого бота\n\n"
        "*Важно:* Этот бот НЕ решает капчи!",
        parse_mode='Markdown'
    )

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Настройки"""
    await update.message.reply_text(
        "⚙️ *НАСТРОЙКИ СИСТЕМЫ*\n\n"
        "*Telegram Bot Manager:*\n"
        f"• Админов: {len(ADMIN_IDS)}\n"
        f"• Хостинг: Railway\n"
        f"• Healthcheck: Активен\n\n"
        "*Для настройки заработка:*\n"
        "1. Скачайте `captcha_worker.py`\n"
        "2. Установите Python 3.8+\n"
        "3. Установите зависимости:\n"
        "   ```bash\n"
        "   pip install requests python-telegram-bot\n"
        "   ```\n"
        "4. Запустите воркер:\n"
        "   ```bash\n"
        "   python captcha_worker.py\n"
        "   ```\n\n"
        "*API ключ Rucaptcha:*\n"
        "`99461b14be32f596e034e2459b05e645`",
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
    
    if action == 'worker_status':
        await status_command(query, context)
    elif action == 'check_balance':
        await check_balance_command(query, context)
    elif action == 'settings':
        await settings_command(query, context)
    elif action == 'help':
        await help_command(query, context)

# ============================================
# ОСНОВНАЯ ФУНКЦИЯ
# ============================================

def main():
    """Запуск бота управления"""
    print("="*60)
    print("🤖 TELEGRAM BOT MANAGER - УПРАВЛЕНИЕ")
    print("="*60)
    
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN не установлен!")
        return
    
    print(f"✅ Токен: {TELEGRAM_TOKEN[:10]}...")
    print(f"✅ Админы: {len(ADMIN_IDS)}")
    print("="*60)
    
    # Запуск healthcheck сервера для Railway
    port = int(os.getenv('PORT', 8080))
    health_thread = Thread(target=start_health_server, args=(port,), daemon=True)
    health_thread.start()
    
    print(f"✅ Healthcheck: http://0.0.0.0:{port}/health")
    print("="*60)
    
    # Создаем Telegram приложение
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрируем команды
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("balance", balance_with_key_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("settings", settings_command))
    
    # Регистрируем обработчик кнопок
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Запускаем бота
    print("🤖 Бот управления запущен!")
    print("💬 Добавьте бота в Telegram и отправьте /start")
    print("="*60)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
