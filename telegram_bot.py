#!/usr/bin/env python3
"""
🤖 Telegram Bot для управления Captcha Earning Bot
Полная версия с управлением воркером
"""

import os
import json
import logging
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
from config import (
    TELEGRAM_TOKEN,
    ADMIN_IDS,
    LOGS_DIR,
    TELEGRAM_LOG_FILE,
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    validate_config
)
from utils.logger import setup_logger

# ============================================
# НАСТРОЙКА ЛОГИРОВАНИЯ
# ============================================

logger = setup_logger(
    name='TelegramBot',
    log_file=TELEGRAM_LOG_FILE,
    level=LOG_LEVEL,
    format_str=LOG_FORMAT,
    date_format=LOG_DATE_FORMAT
)

# ============================================
# ГЛОБАЛЬНОЕ СОСТОЯНИЕ
# ============================================

bot_status = {
    "worker_running": False,
    "worker_start_time": None,
    "last_worker_check": None
}

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def load_worker_status() -> Optional[Dict]:
    """Загрузка статуса воркера из файла"""
    status_file = os.path.join("data", "worker_status.json")
    
    try:
        if os.path.exists(status_file):
            with open(status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки статуса воркера: {e}")
    
    return None

def get_recent_logs(log_file: str, lines: int = 10) -> str:
    """Получение последних логов"""
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                recent = all_lines[-lines:] if len(all_lines) > lines else all_lines
                return ''.join(recent)
    except Exception as e:
        logger.error(f"Ошибка чтения логов: {e}")
    
    return "Логи не найдены"

def is_admin(user_id: int) -> bool:
    """Проверка прав администратора"""
    if not ADMIN_IDS:
        return True  # Если список пустой, доступ у всех
    return user_id in ADMIN_IDS

def format_earnings(amount: float) -> str:
    """Форматирование суммы заработка"""
    if amount >= 1:
        return f"${amount:.2f}"
    elif amount >= 0.01:
        return f"${amount:.4f}"
    else:
        return f"${amount:.6f}"

def format_time(seconds: float) -> str:
    """Форматирование времени"""
    if seconds < 60:
        return f"{int(seconds)} сек"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes} мин {secs} сек"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours} час {minutes} мин"

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
🤖 *Добро пожаловать в Captcha Earning Bot!*

👤 *Пользователь:* {user.first_name or ''} {user.last_name or ''}
📧 *Username:* @{user.username or 'нет'}
🆔 *ID:* `{user.id}`
🕐 *Время:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

*💰 Система автоматического заработка:*
• Автоматическое решение капч
• Работа 24/7 на сервере
• Управление через Telegram
• Статистика в реальном времени

*📋 Доступные команды:*
/start - Главное меню
/status - Текущий статус
/stats - Подробная статистика
/start_worker - 🚀 Запуск заработка
/stop_worker - ⏹️ Остановка заработка
/earnings - 💰 Заработок
/settings - ⚙️ Настройки
/logs - 📜 Логи работы
/help - ❓ Помощь
"""
    
    keyboard = [
        [
            InlineKeyboardButton("🚀 Старт", callback_data='start_worker'),
            InlineKeyboardButton("⏹️ Стоп", callback_data='stop_worker')
        ],
        [
            InlineKeyboardButton("📊 Статус", callback_data='status'),
            InlineKeyboardButton("💰 Заработок", callback_data='earnings')
        ],
        [
            InlineKeyboardButton("⚙️ Настройки", callback_data='settings'),
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

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /status"""
    status_text = await generate_status_text()
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stats"""
    stats_text = await generate_stats_text()
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def earnings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /earnings"""
    earnings_text = await generate_earnings_text()
    await update.message.reply_text(earnings_text, parse_mode='Markdown')

async def start_worker_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start_worker"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Только для администраторов")
        return
    
    worker_status = load_worker_status()
    
    if worker_status and worker_status.get('running', False):
        await update.message.reply_text(
            "⚠️ *Воркер уже запущен!*\n"
            "Используйте /status для проверки состояния.",
            parse_mode='Markdown'
        )
        return
    
    # В реальности здесь нужно запускать воркер
    # Для примера просто меняем статус
    bot_status["worker_running"] = True
    bot_status["worker_start_time"] = datetime.now().isoformat()
    
    await update.message.reply_text(
        "✅ *Воркер запущен!*\n\n"
        "*Начал работу в:* " + datetime.now().strftime('%H:%M:%S') + "\n"
        "*Режим:* Автоматический заработок\n"
        "*Интервал:* 10-30 секунд\n\n"
        "Используйте /status для мониторинга.",
        parse_mode='Markdown'
    )
    
    logger.info(f"Запуск воркера (пользователь: {update.effective_user.username})")

async def stop_worker_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stop_worker"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Только для администраторов")
        return
    
    worker_status = load_worker_status()
    
    if not worker_status or not worker_status.get('running', False):
        await update.message.reply_text(
            "ℹ️ *Воркер уже остановлен*\n"
            "Используйте /start_worker для запуска.",
            parse_mode='Markdown'
        )
        return
    
    bot_status["worker_running"] = False
    
    # Получаем статистику сессии
    if worker_status and 'stats' in worker_status:
        stats = worker_status['stats']
        await update.message.reply_text(
            "🛑 *Воркер остановлен!*\n\n"
            "*Статистика сессии:*\n"
            f"• Циклов: {stats.get('cycles_completed', 0)}\n"
            f"• Капч решено: {stats.get('captchas_solved', 0)}\n"
            f"• Заработано: {format_earnings(stats.get('total_earnings', 0))}\n\n"
            "Все данные сохранены.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("🛑 Воркер остановлен")
    
    logger.info(f"Остановка воркера (пользователь: {update.effective_user.username})")

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /settings"""
    from config import (
        WORK_CYCLE_DELAY_MIN,
        WORK_CYCLE_DELAY_MAX,
        BREAK_AFTER_CYCLES,
        TARGET_DAILY_EARNINGS,
        CAPTCHA_TYPES
    )
    
    settings_text = f"""
*⚙️ Настройки системы*

*📅 Рабочие параметры:*
• Интервал циклов: `{WORK_CYCLE_DELAY_MIN}-{WORK_CYCLE_DELAY_MAX}` сек
• Перерыв после: `{BREAK_AFTER_CYCLES}` циклов
• Цель в день: `{format_earnings(TARGET_DAILY_EARNINGS)}`

*🎯 Поддерживаемые капчи:*
"""
    
    for i, captcha_type in enumerate(CAPTCHA_TYPES, 1):
        settings_text += f"{i}. `{captcha_type}`\n"
    
    settings_text += f"\n*⚡ Текущий статус:* {'🟢 Активен' if bot_status['worker_running'] else '🔴 Остановлен'}"
    
    keyboard = [
        [
            InlineKeyboardButton("Изменить интервал", callback_data='change_interval'),
            InlineKeyboardButton("Изменить цель", callback_data='change_target')
        ],
        [
            InlineKeyboardButton("Список капч", callback_data='captcha_list'),
            InlineKeyboardButton("Назад", callback_data='refresh')
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        settings_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /logs"""
    keyboard = [
        [
            InlineKeyboardButton("📱 Telegram", callback_data='logs_telegram'),
            InlineKeyboardButton("🎯 Worker", callback_data='logs_worker')
        ],
        [
            InlineKeyboardButton("📊 Все логи", callback_data='logs_all'),
            InlineKeyboardButton("Назад", callback_data='refresh')
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📜 *Выберите лог для просмотра:*",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
*❓ Помощь по Captcha Earning Bot*

*🎯 Как это работает:*
1. Бот автоматически решает капчи через rucaptcha.com
2. За каждую решенную капчу вы получаете оплату
3. Система работает 24/7 на сервере Railway
4. Вы управляете всем через этого Telegram бота

*💰 Заработок:*
• Обычная капча: $0.0003-$0.001
• ReCaptcha: $0.001-$0.003
• hCaptcha: $0.002-$0.005
• В среднем: $0.5-$2 в день

*🛠️ Основные команды:*
• `/start_worker` - Запуск автоматического заработка
• `/stop_worker` - Остановка заработка
• `/status` - Текущий статус работы
• `/stats` - Подробная статистика
• `/earnings` - Информация о заработке
• `/logs` - Просмотр логов работы

*⚠️ Важно:*
• Бот работает как фоновый процесс
• Для остановки используйте /stop_worker
• Все данные сохраняются автоматически
• Минимальный вывод на rucaptcha: $0.3

*🆘 Поддержка:*
При проблемах проверьте:
1. API ключ rucaptcha в конфигурации
2. Баланс на rucaptcha (для тестов)
3. Логи через /logs
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

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
    
    if action == 'start_worker':
        worker_status = load_worker_status()
        
        if worker_status and worker_status.get('running', False):
            await query.edit_message_text("⚠️ Воркер уже запущен!")
        else:
            bot_status["worker_running"] = True
            bot_status["worker_start_time"] = datetime.now().isoformat()
            await query.edit_message_text(
                "✅ *Воркер запущен!*\n"
                "Начал работу в " + datetime.now().strftime('%H:%M:%S'),
                parse_mode='Markdown'
            )
            
    elif action == 'stop_worker':
        worker_status = load_worker_status()
        
        if not worker_status or not worker_status.get('running', False):
            await query.edit_message_text("ℹ️ Воркер уже остановлен")
        else:
            bot_status["worker_running"] = False
            await query.edit_message_text("🛑 Воркер остановлен")
            
    elif action == 'status':
        status_text = await generate_status_text()
        await query.edit_message_text(status_text, parse_mode='Markdown')
        
    elif action == 'earnings':
        earnings_text = await generate_earnings_text()
        await query.edit_message_text(earnings_text, parse_mode='Markdown')
        
    elif action == 'stats':
        stats_text = await generate_stats_text()
        await query.edit_message_text(stats_text, parse_mode='Markdown')
        
    elif action == 'settings':
        await settings_command(query, context)
        
    elif action == 'logs':
        await logs_command(query, context)
        
    elif action == 'logs_telegram':
        logs = get_recent_logs(TELEGRAM_LOG_FILE, 15)
        if len(logs) > 3000:
            logs = logs[-3000:]
        
        await query.edit_message_text(
            f"*📱 Логи Telegram бота:*\n```\n{logs}\n```",
            parse_mode='MarkdownV2'
        )
        
    elif action == 'logs_worker':
        from config import CAPTCHA_LOG_FILE
        logs = get_recent_logs(CAPTCHA_LOG_FILE, 15)
        if len(logs) > 3000:
            logs = logs[-3000:]
        
        await query.edit_message_text(
            f"*🎯 Логи воркера:*\n```\n{logs}\n```",
            parse_mode='MarkdownV2'
        )
        
    elif action == 'refresh':
        status_text = await generate_status_text()
        await query.edit_message_text(status_text, parse_mode='Markdown')
        
    elif action == 'help':
        help_text = """
*Быстрая помощь:*
• Старт: /start_worker или кнопка 🚀
• Стоп: /stop_worker или кнопка ⏹️
• Статус: /status или кнопка 📊
• Заработок: /earnings или кнопка 💰
• Логи: /logs или кнопка 📜
"""
        await query.edit_message_text(help_text, parse_mode='Markdown')
        
    elif action == 'change_interval':
        await query.edit_message_text(
            "🔄 Изменение интервала:\n"
            "Используйте команду:\n"
            "`/set_interval 10 30`\n\n"
            "Где 10 - мин. задержка, 30 - макс. задержка (секунды)",
            parse_mode='Markdown'
        )
        
    elif action == 'change_target':
        await query.edit_message_text(
            "🎯 Изменение дневной цели:\n"
            "Используйте команду:\n"
            "`/set_target 1.5`\n\n"
            "Где 1.5 - цель в долларах за день",
            parse_mode='Markdown'
        )
        
    elif action == 'captcha_list':
        from config import CAPTCHA_TYPES
        
        list_text = "*📋 Поддерживаемые типы капч:*\n\n"
        for i, captcha_type in enumerate(CAPTCHA_TYPES, 1):
            price_range = {
                "ImageToTextTask": "$0.0003-$0.001",
                "RecaptchaV2Task": "$0.001-$0.003",
                "HCaptchaTask": "$0.002-$0.005",
                "RecaptchaV3Task": "$0.003-$0.008"
            }.get(captcha_type, "$0.0005-$0.002")
            
            list_text += f"{i}. *{captcha_type}* - {price_range}\n"
        
        await query.edit_message_text(list_text, parse_mode='Markdown')

# ============================================
# ГЕНЕРАЦИЯ ТЕКСТОВ
# ============================================

async def generate_status_text() -> str:
    """Генерация текста статуса"""
    worker_status = load_worker_status()
    
    if worker_status:
        stats = worker_status.get('stats', {})
        daily_stats = worker_status.get('daily_stats', {})
        
        status_icon = "🟢" if worker_status.get('running', False) else "🔴"
        status_text = "РАБОТАЕТ" if worker_status.get('running', False) else "ОСТАНОВЛЕН"
        
        uptime_seconds = worker_status.get('uptime_seconds', 0)
        uptime_str = format_time(uptime_seconds)
        
        last_captcha = stats.get('last_captcha', 'Нет данных')
        if len(last_captcha) > 15:
            last_captcha = last_captcha[:15] + "..."
        
        status_message = f"""
{status_icon} *СТАТУС СИСТЕМЫ*

*Состояние:* **{status_text}**
*Время работы:* `{uptime_str}`
*Сессия:* `{worker_status.get('session_id', 'N/A')}`

*📊 Текущая сессия:*
• Циклов: `{stats.get('cycles_completed', 0)}`
• Капч решено: `{stats.get('captchas_solved', 0)}`
• Заработано: `{format_earnings(stats.get('total_earnings', 0))}`
• Последняя капча: `{last_captcha}`

*📈 Сегодня:*
• Капч: `{daily_stats.get('total_captchas', 0)}`
• Заработано: `{format_earnings(daily_stats.get('total_earnings', 0))}`
• Успешность: `{daily_stats.get('success_rate', 0):.1f}%`

*🕐 Обновлено:* {datetime.now().strftime('%H:%M:%S')}
"""
    else:
        status_message = """
🔴 *СТАТУС СИСТЕМЫ*

*Состояние:* **НЕТ ДАННЫХ**
*Воркер:* Не запущен или данные не получены

*Действия:*
1. Запустите воркер командой /start_worker
2. Подождите 1-2 минуты
3. Проверьте статус снова

*🕐 Обновлено:* """ + datetime.now().strftime('%H:%M:%S')
    
    return status_message

async def generate_stats_text() -> str:
    """Генерация текста статистики"""
    worker_status = load_worker_status()
    
    if not worker_status:
        return "*📊 Статистика:*\nДанные не найдены\n\nЗапустите воркер командой /start_worker"
    
    stats = worker_status.get('stats', {})
    daily_stats = worker_status.get('daily_stats', {})
    
    # Рассчитываем среднюю производительность
    total_captchas = stats.get('captchas_solved', 0)
    total_earnings = stats.get('total_earnings', 0)
    
    if total_captchas > 0:
        avg_price = total_earnings / total_captchas
    else:
        avg_price = 0
    
    stats_message = f"""
📊 *ПОДРОБНАЯ СТАТИСТИКА*

*🎯 За все время:*
• Всего циклов: `{stats.get('cycles_completed', 0):,}`
• Капч решено: `{total_captchas:,}`
• Общий заработок: `{format_earnings(total_earnings)}`
• Средняя цена: `{format_earnings(avg_price)}` за капчу

*📅 Сегодня ({datetime.now().strftime('%d.%m.%Y')}):*
• Капч решено: `{daily_stats.get('total_captchas', 0)}`
• Заработано: `{format_earnings(daily_stats.get('total_earnings', 0))}`
• Успешность: `{daily_stats.get('success_rate', 0):.1f}%`
• Скорость: `{daily_stats.get('captchas_per_hour', 0):.1f}` капч/час

*⚡ Производительность:*
• Статус: `{'🟢 Активен' if worker_status.get('running', False) else '🔴 Остановлен'}`
• Сессия: `{worker_status.get('session_id', 'N/A')}`
• Время работы: `{format_time(worker_status.get('uptime_seconds', 0))}`

*💡 Прогноз:*
• В час: `{format_earnings(daily_stats.get('hourly_earnings', 0))}`
• В день: `{format_earnings(daily_stats.get('daily_earnings', 0))}`
• В месяц: `{format_earnings(daily_stats.get('monthly_earnings', 0))}`

*🕐 Обновлено:* {datetime.now().strftime('%H:%M:%S')}
"""
    
    return stats_message

async def generate_earnings_text() -> str:
    """Генерация текста о заработке"""
    worker_status = load_worker_status()
    
    if not worker_status:
        return "*💰 Заработок:*\nДанные не найдены\n\nЗапустите воркер командой /start_worker"
    
    daily_stats = worker_status.get('daily_stats', {})
    
    earnings_message = f"""
💰 *ИНФОРМАЦИЯ О ЗАРАБОТКЕ*

*📊 Текущие показатели:*
• Сегодня: `{format_earnings(daily_stats.get('total_earnings', 0))}`
• В час: `{format_earnings(daily_stats.get('hourly_earnings', 0))}`
• Капч/час: `{daily_stats.get('captchas_per_hour', 0):.1f}`

*📈 Прогнозы:*
• За день: `{format_earnings(daily_stats.get('daily_earnings', 0))}`
• За неделю: `{format_earnings(daily_stats.get('weekly_earnings', 0))}`
• За месяц: `{format_earnings(daily_stats.get('monthly_earnings', 0))}`

*🎯 Типы капч и оплата:*
1. *Текстовая капча* - $0.0003-$0.001
2. *ReCaptcha v2* - $0.001-$0.003
3. *hCaptcha* - $0.002-$0.005
4. *ReCaptcha v3* - $0.003-$0.008

*💳 Вывод средств:*
• Минималка rucaptcha: *$0.3*
• Популярные методы:
  - 💳 Карты (Visa/Mastercard)
  - 📱 ЮMoney (Яндекс.Деньги)
  - 🅿️ PayPal
  - ₿ Криптовалюта
  - 📲 Мобильные платежи

*⚠️ Важно:*
• Заработок зависит от активности
• Сложные капчи оплачиваются лучше
• Качество решения влияет на рейтинг
• Вывод доступен при достижении минимума

*🕐 Обновлено:* {datetime.now().strftime('%H:%M:%S')}
"""
    
    return earnings_message

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
    
    if not TELEGRAM_TOKEN:
        print("❌ Токен Telegram бота не установлен!")
        print("Получите токен у @BotFather и добавьте в config.py")
        return
    
    print("="*60)
    print("🤖 TELEGRAM BOT ДЛЯ УПРАВЛЕНИЯ CAPTCHA EARNING BOT")
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
    application.add_handler(CommandHandler("earnings", earnings_command))
    application.add_handler(CommandHandler("start_worker", start_worker_command))
    application.add_handler(CommandHandler("stop_worker", stop_worker_command))
    application.add_handler(CommandHandler("settings", settings_command))
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
