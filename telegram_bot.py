#!/usr/bin/env python3
"""
🤖 Telegram Bot для управления Captcha AutoBot
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# Импорт конфигурации
try:
    from config import (
        TELEGRAM_TOKEN,
        ADMIN_IDS,
        DATA_DIR,
        LOGS_DIR,
        ACTIVITY_FILE,
        TELEGRAM_LOG_FILE,
        LOG_LEVEL,
        LOG_FORMAT,
        LOG_DATE_FORMAT,
        validate_config
    )
except ImportError as e:
    print(f"❌ Ошибка загрузки конфигурации: {e}")
    exit(1)

# ============================================
# НАСТРОЙКА ЛОГИРОВАНИЯ
# ============================================

def setup_logging():
    """Настройка логирования для Telegram бота"""
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    logger = logging.getLogger('TelegramBot')
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Форматтер
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    
    # Файловый handler
    file_handler = logging.FileHandler(TELEGRAM_LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Консольный handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

# ============================================
# ГЛОБАЛЬНОЕ СОСТОЯНИЕ
# ============================================

bot_status = {
    "running": False,
    "start_time": None,
    "cycles_completed": 0,
    "success_rate": 0.0,
    "last_captcha": None,
    "errors": 0
}

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def load_stats() -> Dict:
    """Загрузка статистики"""
    stats_file = os.path.join(DATA_DIR, "stats.json")
    
    try:
        if os.path.exists(stats_file):
            with open(stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки статистики: {e}")
    
    return {
        "total_cycles": 0,
        "total_success": 0,
        "total_errors": 0,
        "uptime_seconds": 0,
        "daily_stats": {},
        "last_update": datetime.now().isoformat()
    }

def save_stats(stats: Dict):
    """Сохранение статистики"""
    stats_file = os.path.join(DATA_DIR, "stats.json")
    
    try:
        stats["last_update"] = datetime.now().isoformat()
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Ошибка сохранения статистики: {e}")

def get_worker_status() -> Optional[Dict]:
    """Получение статуса воркера"""
    status_file = os.path.join(DATA_DIR, "worker_status.json")
    
    try:
        if os.path.exists(status_file):
            with open(status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    
    return None

def get_recent_logs(lines: int = 10) -> str:
    """Получение последних логов"""
    try:
        if os.path.exists(ACTIVITY_FILE):
            with open(ACTIVITY_FILE, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                recent = all_lines[-lines:] if len(all_lines) > lines else all_lines
                return ''.join(recent)
    except Exception as e:
        logger.error(f"Ошибка чтения логов: {e}")
    
    return "Логи не найдены"

def is_admin(user_id: int) -> bool:
    """Проверка прав администратора"""
    if not ADMIN_IDS:  # Если список пустой - доступ у всех
        return True
    return user_id in ADMIN_IDS

# ============================================
# ОБРАБОТЧИКИ КОМАНД
# ============================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text(
            "⛔ У вас нет доступа к этому боту.\n"
            "Обратитесь к администратору."
        )
        return
    
    welcome_text = f"""
🤖 *Добро пожаловать в Captcha AutoBot Control Panel!*

👤 *Пользователь:* {user.first_name or ''} (@{user.username or 'без username'})
🆔 *ID:* `{user.id}`
🕐 *Время:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

*📋 Доступные команды:*
/start - Главное меню
/status - Статус системы
/stats - Подробная статистика
/start_bot - 🚀 Запуск обработчика
/stop_bot - ⏹️ Остановка обработчика
/config - ⚙️ Конфигурация
/logs - 📜 Последние логи
/help - ❓ Помощь

*🎯 Быстрые действия через кнопки ниже:*
"""
    
    keyboard = [
        [
            InlineKeyboardButton("🚀 Запустить", callback_data='start_bot'),
            InlineKeyboardButton("⏹️ Остановить", callback_data='stop_bot')
        ],
        [
            InlineKeyboardButton("📊 Статус", callback_data='status'),
            InlineKeyboardButton("📈 Статистика", callback_data='stats')
        ],
        [
            InlineKeyboardButton("⚙️ Конфиг", callback_data='config'),
            InlineKeyboardButton("📜 Логи", callback_data='logs')
        ],
        [
            InlineKeyboardButton("🔄 Обновить", callback_data='refresh'),
            InlineKeyboardButton("❓ Помощь", callback_data='help')
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    
    logger.info(f"Пользователь {user.id} запустил бота")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
*❓ Помощь по Captcha AutoBot*

*Как это работает:*
1. Бот запускает фоновый процесс обработки капч
2. Процесс работает автономно по заданным координатам
3. Вы можете управлять процессом через Telegram

*🛠️ Основные команды:*
• `/start_bot` - Запуск обработчика капч
• `/stop_bot` - Остановка обработчика
• `/status` - Текущий статус работы
• `/stats` - Статистика за все время
• `/logs` - Последние логи работы

*🔧 Техническая информация:*
• Координаты фиксированы в конфигурации
• Интервал проверки: 10-29 секунд
• Логи сохраняются в файлы
• Статистика обновляется в реальном времени

*⚠️ Важно:*
• Бот работает как фоновый процесс
• Для остановки используйте /stop_bot
• Все данные сохраняются между перезапусками
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /status"""
    status_text = await generate_status_text()
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stats"""
    stats_text = await generate_stats_text()
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def start_bot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start_bot"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Только для администраторов")
        return
    
    if bot_status["running"]:
        await update.message.reply_text(
            "⚠️ *Обработчик уже запущен!*\n"
            "Используйте /status для проверки состояния.",
            parse_mode='Markdown'
        )
        return
    
    # Здесь в реальности нужно запускать воркер
    # Пока просто меняем статус
    bot_status["running"] = True
    bot_status["start_time"] = datetime.now().isoformat()
    bot_status["errors"] = 0
    
    await update.message.reply_text(
        "✅ *Обработчик капч запущен!*\n\n"
        "*Детали:*\n"
        "• Статус: Активен\n"
        "• Время запуска: " + datetime.now().strftime('%H:%M:%S') + "\n"
        "• Режим: Фоновый процесс\n"
        "• Проверка каждые 10-29 секунд\n\n"
        "Используйте /status для мониторинга.",
        parse_mode='Markdown'
    )
    
    logger.info(f"Запуск обработчика (пользователь: {update.effective_user.username})")

async def stop_bot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stop_bot"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Только для администраторов")
        return
    
    if not bot_status["running"]:
        await update.message.reply_text(
            "ℹ️ *Обработчик уже остановлен*\n"
            "Используйте /start_bot для запуска.",
            parse_mode='Markdown'
        )
        return
    
    bot_status["running"] = False
    
    # Обновляем статистику времени работы
    if bot_status["start_time"]:
        try:
            start_time = datetime.fromisoformat(bot_status["start_time"])
            uptime = datetime.now() - start_time
            
            stats = load_stats()
            stats["uptime_seconds"] = stats.get("uptime_seconds", 0) + int(uptime.total_seconds())
            save_stats(stats)
        except:
            pass
    
    await update.message.reply_text(
        "🛑 *Обработчик капч остановлен!*\n\n"
        "*Статистика сессии:*\n"
        f"• Циклов выполнено: {bot_status['cycles_completed']}\n"
        f"• Успешность: {bot_status['success_rate']:.1f}%\n"
        f"• Ошибок: {bot_status['errors']}\n\n"
        "Все данные сохранены.",
        parse_mode='Markdown'
    )
    
    logger.info(f"Остановка обработчика (пользователь: {update.effective_user.username})")

async def config_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /config"""
    from config import (
        CAPTCHA_REGION,
        INPUT_COORDS,
        BUTTON_COORDS,
        CYCLE_DELAY_MIN,
        CYCLE_DELAY_MAX,
        CYCLE_DELAY_DISTRIBUTION,
        MISTAKE_PROBABILITY
    )
    
    config_text = f"""
*⚙️ Конфигурация Captcha AutoBot*

*📐 Координаты обработки:*
• Область капчи: `{CAPTCHA_REGION}`
• Центр поля ввода: `{INPUT_COORDS}`
• Центр кнопки отправки: `{BUTTON_COORDS}`

*⚡ Настройки производительности:*
• Интервал проверки: `{CYCLE_DELAY_MIN}-{CYCLE_DELAY_MAX}` сек
• Распределение: `{CYCLE_DELAY_DISTRIBUTION}`
• Вероятность ошибок: `{MISTAKE_PROBABILITY*100:.1f}%`

*📊 Текущее состояние:*
• Статус: {'✅ Активен' if bot_status['running'] else '⏸️ Остановлен'}
• Запущен: `{bot_status['start_time'] or 'Не запущен'}`
• Циклов: `{bot_status['cycles_completed']}`
• Успешность: `{bot_status['success_rate']:.1f}%`
• Ошибок: `{bot_status['errors']}`
"""
    
    await update.message.reply_text(config_text, parse_mode='Markdown')

async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /logs"""
    logs = get_recent_logs(15)
    
    if len(logs) > 4000:
        logs = logs[-4000:]
    
    await update.message.reply_text(f"```\n{logs}\n```", parse_mode='MarkdownV2')

# ============================================
# ОБРАБОТЧИКИ CALLBACK КНОПОК
# ============================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback кнопок"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    if not is_admin(user.id):
        await query.edit_message_text("⛔ Только для администраторов")
        return
    
    action = query.data
    
    if action == 'start_bot':
        if bot_status["running"]:
            await query.edit_message_text("⚠️ Обработчик уже запущен!")
        else:
            bot_status["running"] = True
            bot_status["start_time"] = datetime.now().isoformat()
            await query.edit_message_text("✅ Обработчик запущен!\nИспользуйте /status для мониторинга.")
            
    elif action == 'stop_bot':
        if not bot_status["running"]:
            await query.edit_message_text("ℹ️ Обработчик уже остановлен")
        else:
            bot_status["running"] = False
            await query.edit_message_text("🛑 Обработчик остановлен")
            
    elif action == 'status':
        status_text = await generate_status_text()
        await query.edit_message_text(status_text, parse_mode='Markdown')
        
    elif action == 'stats':
        stats_text = await generate_stats_text()
        await query.edit_message_text(stats_text, parse_mode='Markdown')
        
    elif action == 'config':
        from config import CAPTCHA_REGION, INPUT_COORDS, BUTTON_COORDS
        
        config_text = f"""
*Текущая конфигурация:*
• Капча: `{CAPTCHA_REGION}`
• Поле: `{INPUT_COORDS}`
• Кнопка: `{BUTTON_COORDS}`
• Статус: {'🟢 Активен' if bot_status['running'] else '🔴 Остановлен'}
• Циклов: {bot_status['cycles_completed']}
"""
        await query.edit_message_text(config_text, parse_mode='Markdown')
        
    elif action == 'logs':
        logs = get_recent_logs(8)
        if logs.strip():
            await query.edit_message_text(f"```\n{logs}\n```", parse_mode='MarkdownV2')
        else:
            await query.edit_message_text("Логи пусты")
            
    elif action == 'refresh':
        status_text = await generate_status_text()
        await query.edit_message_text(status_text, parse_mode='Markdown')
        
    elif action == 'help':
        help_text = """
*Быстрая помощь:*
• Запуск: /start_bot или кнопка ▶️
• Остановка: /stop_bot или кнопка ⏹️
• Статус: /status или кнопка 📊
• Логи: /logs или кнопка 📜
"""
        await query.edit_message_text(help_text, parse_mode='Markdown')

# ============================================
# ГЕНЕРАЦИЯ ТЕКСТОВ
# ============================================

async def generate_status_text() -> str:
    """Генерация текста статуса"""
    worker_status = get_worker_status()
    
    if worker_status:
        bot_status.update({
            "cycles_completed": worker_status.get("cycle_count", 0),
            "success_rate": worker_status.get("success_rate", 0.0),
            "last_captcha": worker_status.get("last_captcha", None),
            "errors": worker_status.get("error_count", 0)
        })
    
    if bot_status["running"]:
        status_icon = "🟢"
        status_text = "АКТИВЕН"
        
        if bot_status["start_time"]:
            try:
                start_time = datetime.fromisoformat(bot_status["start_time"])
                uptime = datetime.now() - start_time
                hours, remainder = divmod(int(uptime.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            except:
                uptime_str = "N/A"
        else:
            uptime_str = "00:00:00"
    else:
        status_icon = "🔴"
        status_text = "ОСТАНОВЛЕН"
        uptime_str = "00:00:00"
    
    last_captcha = bot_status["last_captcha"] or "Нет данных"
    if len(last_captcha) > 20:
        last_captcha = last_captcha[:20] + "..."
    
    return f"""
{status_icon} *СТАТУС СИСТЕМЫ*

*Состояние:* **{status_text}**
*Время работы:* `{uptime_str}`
*Циклов выполнено:* `{bot_status['cycles_completed']}`
*Точность распознавания:* `{bot_status['success_rate']:.1f}%`
*Ошибок в сессии:* `{bot_status['errors']}`

*Последняя капча:* `{last_captcha}`

*Обновлено:* {datetime.now().strftime('%H:%M:%S')}
"""

async def generate_stats_text() -> str:
    """Генерация текста статистики"""
    stats = load_stats()
    worker_status = get_worker_status()
    
    total_time = timedelta(seconds=stats.get("uptime_seconds", 0))
    
    # Рассчитываем среднюю производительность
    total_cycles = stats.get("total_cycles", 0)
    if total_cycles > 0 and total_time.total_seconds() > 0:
        cycles_per_hour = total_cycles / (total_time.total_seconds() / 3600)
    else:
        cycles_per_hour = 0
    
    # Текущая сессия из статуса воркера
    if worker_status:
        current_cycles = worker_status.get("cycle_count", 0)
        current_success_rate = worker_status.get("success_rate", 0.0)
        current_errors = worker_status.get("error_count", 0)
        fatigue = worker_status.get("fatigue", 0.0)
        mood = worker_status.get("mood", 0.0)
    else:
        current_cycles = 0
        current_success_rate = 0.0
        current_errors = 0
        fatigue = 0.0
        mood = 0.0
    
    return f"""
📊 *ОБЩАЯ СТАТИСТИКА*

*За все время:*
• Всего циклов: `{total_cycles:,}`
• Общее время работы: `{str(total_time).split('.')[0]}`
• Средняя скорость: `{cycles_per_hour:.1f}` циклов/час

*Текущая сессия:*
• Циклов: `{current_cycles}`
• Успешность: `{current_success_rate:.1f}%`
• Ошибок: `{current_errors}`
• Усталость: `{fatigue:.2f}`
• Настроение: `{mood:.2f}`

*Обновлено:* {stats.get('last_update', 'N/A')}
"""

# ============================================
# ОБРАБОТЧИК ОШИБОК
# ============================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка в обработчике: {context.error}", exc_info=context.error)
    
    if update and update.effective_chat:
        try:
            await update.effective_chat.send_message(
                "⚠️ Произошла ошибка в обработке команды.\n"
                "Попробуйте еще раз или обратитесь к администратору."
            )
        except:
            pass

# ============================================
# ОСНОВНАЯ ФУНКЦИЯ
# ============================================

def main():
    """Основная функция запуска бота"""
    # Проверка конфигурации
    is_valid, errors = validate_config()
    
    if not is_valid:
        print("❌ Ошибки конфигурации:")
        for error in errors:
            print(f"  • {error}")
        print("\nИсправьте config.py перед запуском")
        return
    
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("❌ Токен Telegram бота не установлен!")
        print("Получите токен у @BotFather и добавьте в config.py")
        return
    
    print("="*60)
    print("🤖 TELEGRAM BOT ДЛЯ УПРАВЛЕНИЯ CAPTCHA AUTOBOT")
    print("="*60)
    print(f"Токен: {TELEGRAM_TOKEN[:10]}...{TELEGRAM_TOKEN[-10:]}")
    print(f"Админы: {len(ADMIN_IDS)} пользователей")
    print("="*60)
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("start_bot", start_bot_command))
    application.add_handler(CommandHandler("stop_bot", stop_bot_command))
    application.add_handler(CommandHandler("config", config_command))
    application.add_handler(CommandHandler("logs", logs_command))
    
    # Регистрируем обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Регистрируем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    logger.info("Запуск Telegram бота...")
    print("✅ Бот запущен и готов к работе!")
    print("💬 Добавьте бота в Telegram и отправьте /start")
    print("⏳ Ожидание команд...")
    print("="*60)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
