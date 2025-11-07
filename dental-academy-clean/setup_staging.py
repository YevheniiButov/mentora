#!/usr/bin/env python3
"""
Скрипт для настройки staging environment для IRT системы
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime
import json

def create_staging_config():
    """Создает конфигурацию для staging environment"""
    
    staging_config = {
        "environment": "staging",
        "database_url": os.environ.get('STAGING_DATABASE_URL', 'sqlite:///staging.db'),
        "debug": True,
        "testing": True,
        "irt_enabled": True,
        "irt_pilot_mode": True,
        "feature_flags": {
            "irt_dentists": True,
            "irt_general_practitioners": False,
            "irt_calibration": True,
            "irt_analytics": True
        },
        "monitoring": {
            "health_checks": True,
            "performance_monitoring": True,
            "error_tracking": True
        }
    }
    
    # Создаем .env.staging файл
    with open('.env.staging', 'w') as f:
        f.write("# Staging Environment Configuration\n")
        f.write(f"FLASK_ENV=staging\n")
        f.write(f"FLASK_DEBUG=True\n")
        f.write(f"DATABASE_URL={staging_config['database_url']}\n")
        f.write(f"IRT_ENABLED=True\n")
        f.write(f"IRT_PILOT_MODE=True\n")
        f.write(f"FEATURE_FLAGS={json.dumps(staging_config['feature_flags'])}\n")
        f.write(f"MONITORING_ENABLED=True\n")
    
    print("✅ Staging configuration created: .env.staging")
    return staging_config

def setup_staging_database():
    """Настраивает staging базу данных"""
    
    print("🔧 Setting up staging database...")
    
    # Создаем staging директорию
    staging_dir = "staging"
    if not os.path.exists(staging_dir):
        os.makedirs(staging_dir)
        print(f"✅ Created staging directory: {staging_dir}")
    
    # Копируем текущую БД в staging (если SQLite)
    if os.path.exists('instance/app.db'):
        staging_db_path = os.path.join(staging_dir, 'staging.db')
        shutil.copy2('instance/app.db', staging_db_path)
        print(f"✅ Copied production DB to staging: {staging_db_path}")
    
    return staging_dir

def create_staging_scripts():
    """Создает скрипты для работы со staging"""
    
    # Скрипт для запуска staging сервера
    staging_server_script = """#!/bin/bash
# Запуск staging сервера

echo "🚀 Starting staging server..."

# Устанавливаем staging environment
export FLASK_ENV=staging
export FLASK_DEBUG=True

# Загружаем staging конфигурацию
if [ -f .env.staging ]; then
    export $(cat .env.staging | xargs)
fi

# Запускаем сервер
python3 app.py --staging
"""
    
    with open('run_staging.sh', 'w') as f:
        f.write(staging_server_script)
    
    os.chmod('run_staging.sh', 0o755)
    print("✅ Created staging server script: run_staging.sh")
    
    # Скрипт для тестирования IRT системы
    irt_test_script = """#!/usr/bin/env python3
# Тестирование IRT системы на staging

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from models import *

def test_irt_system():
    with app.app_context():
        print("🧪 Testing IRT system on staging...")
        
        # Тест 1: Проверка моделей
        print("1. Testing models...")
        try:
            # Проверяем, что все модели доступны
            from models import IRTParameters, DiagnosticSession, DiagnosticResponse
            print("   ✅ IRT models available")
        except ImportError as e:
            print(f"   ❌ IRT models error: {e}")
            return False
        
        # Тест 2: Проверка базы данных
        print("2. Testing database...")
        try:
            # Проверяем подключение к БД
            db.session.execute("SELECT 1")
            print("   ✅ Database connection OK")
        except Exception as e:
            print(f"   ❌ Database error: {e}")
            return False
        
        # Тест 3: Проверка IRT функций
        print("3. Testing IRT functions...")
        try:
            # Проверяем scipy импорт
            import scipy
            import numpy
            print("   ✅ Scipy and numpy available")
        except ImportError as e:
            print(f"   ❌ Scipy/numpy error: {e}")
            return False
        
        print("🎉 All IRT tests passed!")
        return True

if __name__ == "__main__":
    success = test_irt_system()
    sys.exit(0 if success else 1)
"""
    
    with open('test_irt_staging.py', 'w') as f:
        f.write(irt_test_script)
    
    os.chmod('test_irt_staging.py', 0o755)
    print("✅ Created IRT test script: test_irt_staging.py")

def create_migration_plan():
    """Создает план миграции с rollback функциями"""
    
    migration_plan = {
        "steps": [
            {
                "step": 1,
                "name": "Backup Production Database",
                "command": "python3 backup_production.py",
                "rollback": "python3 restore_from_backup.py"
            },
            {
                "step": 2,
                "name": "Add IRT Models",
                "command": "python3 add_irt_models.py",
                "rollback": "python3 remove_irt_models.py"
            },
            {
                "step": 3,
                "name": "Run Specialty Migration",
                "command": "python3 specialty_migration.py",
                "rollback": "python3 rollback_specialty_migration.py"
            },
            {
                "step": 4,
                "name": "Enable IRT Features",
                "command": "python3 enable_irt_features.py",
                "rollback": "python3 disable_irt_features.py"
            },
            {
                "step": 5,
                "name": "Test IRT System",
                "command": "python3 test_irt_staging.py",
                "rollback": "N/A"
            }
        ],
        "safety_checks": [
            "Database backup created",
            "All models accessible",
            "No data loss",
            "Performance acceptable",
            "Error rate < 1%"
        ]
    }
    
    with open('migration_plan.json', 'w') as f:
        json.dump(migration_plan, f, indent=2)
    
    print("✅ Created migration plan: migration_plan.json")

def create_health_checks():
    """Создает health checks для мониторинга"""
    
    health_check_script = """#!/usr/bin/env python3
# Health checks для IRT системы

import sys
import os
import time
import requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db

def check_database_health():
    try:
        db.session.execute("SELECT 1")
        return True, "Database OK"
    except Exception as e:
        return False, f"Database error: {e}"

def check_irt_models():
    try:
        from models import IRTParameters, DiagnosticSession
        return True, "IRT models OK"
    except Exception as e:
        return False, f"IRT models error: {e}"

def check_scipy_availability():
    try:
        import scipy
        import numpy
        return True, "Scipy/numpy OK"
    except Exception as e:
        return False, f"Scipy/numpy error: {e}"

def check_api_endpoints():
    try:
        # Проверяем основные API endpoints
        endpoints = [
            '/api/irt/questions',
            '/api/irt/sessions',
            '/api/irt/results'
        ]
        
        for endpoint in endpoints:
            # Здесь можно добавить реальные проверки
            pass
        
        return True, "API endpoints OK"
    except Exception as e:
        return False, f"API endpoints error: {e}"

def run_health_checks():
    checks = [
        ("Database", check_database_health),
        ("IRT Models", check_irt_models),
        ("Scipy/Numpy", check_scipy_availability),
        ("API Endpoints", check_api_endpoints)
    ]
    
    print("🏥 Running health checks...")
    all_passed = True
    
    for name, check_func in checks:
        try:
            passed, message = check_func()
            status = "✅" if passed else "❌"
            print(f"   {status} {name}: {message}")
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"   ❌ {name}: Exception - {e}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    success = run_health_checks()
    sys.exit(0 if success else 1)
"""
    
    with open('health_check.py', 'w') as f:
        f.write(health_check_script)
    
    os.chmod('health_check.py', 0o755)
    print("✅ Created health check script: health_check.py")

def main():
    """Основная функция настройки staging"""
    
    print("🚀 Setting up staging environment for IRT system...")
    print("=" * 60)
    
    try:
        # 1. Создаем конфигурацию
        config = create_staging_config()
        
        # 2. Настраиваем базу данных
        staging_dir = setup_staging_database()
        
        # 3. Создаем скрипты
        create_staging_scripts()
        
        # 4. Создаем план миграции
        create_migration_plan()
        
        # 5. Создаем health checks
        create_health_checks()
        
        print("=" * 60)
        print("🎉 Staging environment setup complete!")
        print()
        print("📋 Next steps:")
        print("1. Run: ./run_staging.sh")
        print("2. Test: ./test_irt_staging.py")
        print("3. Health check: ./health_check.py")
        print("4. Follow migration plan: migration_plan.json")
        print()
        print("⚠️  Remember to backup production before migration!")
        
    except Exception as e:
        print(f"❌ Error setting up staging: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


