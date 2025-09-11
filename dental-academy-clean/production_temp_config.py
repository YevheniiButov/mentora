# Production Configuration
# Этот файл содержит временные значения для восстановления работы сервера

import os

# Временные значения для production (НЕБЕЗОПАСНО - только для экстренного восстановления)
PRODUCTION_TEMP_CONFIG = {
    'SECRET_KEY': 'mentora-production-temp-key-2024',
    'MAIL_USERNAME': 'MS_uUzJtfkAxyPn@mentora.mlsender.net',
    'MAIL_PASSWORD': 'mssp.eTIPhpXlO2nu.e6t7xgcGA1kl.Bw3hiAB80JpM',
    'MAIL_DEFAULT_SENDER': 'Mentora <noreply@mentora.com>',
    'MAIL_SUPPRESS_SEND': True
}

def get_production_temp_config():
    """Возвращает временную конфигурацию для production"""
    return PRODUCTION_TEMP_CONFIG
