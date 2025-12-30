#!/usr/bin/env python3
"""
❤️ Healthcheck endpoint для Railway
"""

from flask import Flask, jsonify
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)

@app.route('/health')
def health_check():
    """Проверка здоровья приложения"""
    checks = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'checks': {}
    }
    
    # Проверка директорий
    try:
        os.makedirs('data', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        checks['checks']['directories'] = 'ok'
    except:
        checks['checks']['directories'] = 'failed'
        checks['status'] = 'unhealthy'
    
    # Проверка базы данных
    try:
        conn = sqlite3.connect('data/captcha_bot.db')
        conn.execute('SELECT 1')
        conn.close()
        checks['checks']['database'] = 'ok'
    except:
        checks['checks']['database'] = 'failed'
        checks['status'] = 'unhealthy'
    
    # Проверка файлов конфигурации
    try:
        from config import validate_config
        is_valid, errors = validate_config()
        checks['checks']['config'] = 'ok' if is_valid else 'failed: ' + str(errors)
        if not is_valid:
            checks['status'] = 'unhealthy'
    except:
        checks['checks']['config'] = 'failed'
        checks['status'] = 'unhealthy'
    
    return jsonify(checks)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT', 8080))
