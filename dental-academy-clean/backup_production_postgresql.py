#!/usr/bin/env python3
"""
Скрипт для создания резервной копии продакшн PostgreSQL БД
"""
import os
import subprocess
import datetime
import json
from pathlib import Path

def create_backup_directory():
    """Создать директорию для бэкапов"""
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    return backup_dir

def get_production_db_config():
    """Получить конфигурацию продакшн БД из переменных окружения"""
    # Эти переменные должны быть установлены в продакшн среде
    db_host = os.environ.get('DATABASE_HOST', 'localhost')
    db_port = os.environ.get('DATABASE_PORT', '5432')
    db_name = os.environ.get('DATABASE_NAME', 'mentora_production')
    db_user = os.environ.get('DATABASE_USER', 'mentora_user')
    db_password = os.environ.get('DATABASE_PASSWORD')
    
    if not db_password:
        print("❌ DATABASE_PASSWORD не установлен в переменных окружения")
        return None
    
    return {
        'host': db_host,
        'port': db_port,
        'name': db_name,
        'user': db_user,
        'password': db_password
    }

def create_postgresql_backup(db_config, backup_dir):
    """Создать бэкап PostgreSQL БД"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"production_postgresql_backup_{timestamp}.sql"
    backup_path = backup_dir / backup_filename
    
    # Установить переменную окружения для пароля
    env = os.environ.copy()
    env['PGPASSWORD'] = db_config['password']
    
    # Команда pg_dump
    cmd = [
        'pg_dump',
        '-h', db_config['host'],
        '-p', str(db_config['port']),
        '-U', db_config['user'],
        '-d', db_config['name'],
        '--verbose',
        '--clean',
        '--create',
        '--if-exists',
        '--format=plain',
        '--file', str(backup_path)
    ]
    
    print(f"🔄 Создание бэкапа PostgreSQL БД...")
    print(f"📁 Файл: {backup_path}")
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)
        print("✅ Бэкап PostgreSQL создан успешно")
        return backup_path
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка создания бэкапа: {e}")
        print(f"stderr: {e.stderr}")
        return None
    except FileNotFoundError:
        print("❌ pg_dump не найден. Установите PostgreSQL client tools")
        return None

def create_backup_metadata(backup_path, db_config):
    """Создать метаданные бэкапа"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    metadata_filename = f"backup_metadata_{timestamp}.json"
    metadata_path = backup_path.parent / metadata_filename
    
    metadata = {
        'backup_type': 'postgresql',
        'created_at': datetime.datetime.now().isoformat(),
        'backup_file': backup_path.name,
        'database_config': {
            'host': db_config['host'],
            'port': db_config['port'],
            'name': db_config['name'],
            'user': db_config['user']
        },
        'backup_size_bytes': backup_path.stat().st_size if backup_path.exists() else 0,
        'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip(),
        'git_branch': subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode().strip()
    }
    
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Метаданные созданы: {metadata_path}")
    return metadata_path

def verify_backup(backup_path):
    """Проверить целостность бэкапа"""
    if not backup_path.exists():
        print("❌ Файл бэкапа не существует")
        return False
    
    file_size = backup_path.stat().st_size
    if file_size == 0:
        print("❌ Файл бэкапа пустой")
        return False
    
    print(f"✅ Размер бэкапа: {file_size:,} байт")
    
    # Проверить, что файл содержит SQL
    try:
        with open(backup_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if 'PostgreSQL database dump' in first_line or '--' in first_line:
                print("✅ Бэкап содержит валидный SQL")
                return True
            else:
                print("❌ Бэкап не содержит валидный SQL")
                return False
    except Exception as e:
        print(f"❌ Ошибка чтения бэкапа: {e}")
        return False

def main():
    """Основная функция"""
    print("💾 Создание резервной копии продакшн PostgreSQL БД...")
    print("=" * 50)
    
    # Создать директорию для бэкапов
    backup_dir = create_backup_directory()
    
    # Получить конфигурацию БД
    db_config = get_production_db_config()
    if not db_config:
        return False
    
    # Создать бэкап
    backup_path = create_postgresql_backup(db_config, backup_dir)
    if not backup_path:
        return False
    
    # Проверить бэкап
    if not verify_backup(backup_path):
        print("❌ Проверка бэкапа не пройдена")
        return False
    
    # Создать метаданные
    metadata_path = create_backup_metadata(backup_path, db_config)
    
    print("\n" + "=" * 50)
    print("✅ Резервная копия создана успешно!")
    print(f"📁 Бэкап: {backup_path}")
    print(f"📄 Метаданные: {metadata_path}")
    print(f"💾 Размер: {backup_path.stat().st_size:,} байт")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
