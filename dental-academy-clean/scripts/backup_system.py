#!/usr/bin/env python3
"""
Система автоматических бэкапов для Mentora
Создает резервные копии базы данных и файлов
"""

import os
import sys
import json
import shutil
import gzip
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BackupSystem:
    """Система резервного копирования"""
    
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Создаем поддиректории
        (self.backup_dir / "database").mkdir(exist_ok=True)
        (self.backup_dir / "files").mkdir(exist_ok=True)
        (self.backup_dir / "logs").mkdir(exist_ok=True)
    
    def create_database_backup(self):
        """Создание резервной копии базы данных"""
        try:
            from app import app
            from models import db, User, Contact, Profession, CountryAnalytics, DeviceAnalytics
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / "database" / f"db_backup_{timestamp}.json"
            
            with app.app_context():
                backup_data = {
                    'metadata': {
                        'timestamp': timestamp,
                        'version': '1.0',
                        'created_by': 'backup_system'
                    },
                    'tables': {}
                }
                
                # Список моделей для резервного копирования
                models = [
                    ('users', User),
                    ('contacts', Contact),
                    ('professions', Profession),
                    ('country_analytics', CountryAnalytics),
                    ('device_analytics', DeviceAnalytics)
                ]
                
                for table_name, model in models:
                    try:
                        records = []
                        for record in model.query.all():
                            # Преобразуем в словарь
                            record_dict = {}
                            for column in model.__table__.columns:
                                value = getattr(record, column.name)
                                if isinstance(value, datetime):
                                    value = value.isoformat()
                                record_dict[column.name] = value
                            records.append(record_dict)
                        
                        backup_data['tables'][table_name] = {
                            'count': len(records),
                            'records': records
                        }
                        
                        logger.info(f"✅ Таблица {table_name}: {len(records)} записей")
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Ошибка резервного копирования таблицы {table_name}: {str(e)}")
                        backup_data['tables'][table_name] = {
                            'count': 0,
                            'records': [],
                            'error': str(e)
                        }
                
                # Сохраняем резервную копию
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, ensure_ascii=False, indent=2)
                
                # Сжимаем файл
                compressed_file = f"{backup_file}.gz"
                with open(backup_file, 'rb') as f_in:
                    with gzip.open(compressed_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Удаляем несжатый файл
                backup_file.unlink()
                
                logger.info(f"✅ Резервная копия БД создана: {compressed_file}")
                return str(compressed_file)
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания резервной копии БД: {str(e)}")
            return None
    
    def create_files_backup(self):
        """Создание резервной копии важных файлов"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / "files" / f"files_backup_{timestamp}.tar.gz"
            
            # Список файлов и директорий для резервного копирования
            important_paths = [
                'config.py',
                'models.py',
                'app.py',
                'requirements.txt',
                'render.yaml',
                'templates/',
                'static/',
                'translations/',
                'scripts/'
            ]
            
            # Создаем архив
            import tarfile
            
            with tarfile.open(backup_file, 'w:gz') as tar:
                for path in important_paths:
                    if os.path.exists(path):
                        tar.add(path, arcname=path)
                        logger.info(f"✅ Добавлен в архив: {path}")
                    else:
                        logger.warning(f"⚠️ Файл не найден: {path}")
            
            logger.info(f"✅ Резервная копия файлов создана: {backup_file}")
            return str(backup_file)
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания резервной копии файлов: {str(e)}")
            return None
    
    def restore_database_backup(self, backup_file):
        """Восстановление базы данных из резервной копии"""
        try:
            from app import app
            from models import db, User, Contact, Profession, CountryAnalytics, DeviceAnalytics
            
            # Проверяем, сжат ли файл
            if backup_file.endswith('.gz'):
                import gzip
                with gzip.open(backup_file, 'rt', encoding='utf-8') as f:
                    backup_data = json.load(f)
            else:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
            
            with app.app_context():
                # Очищаем существующие данные
                db.session.query(User).delete()
                db.session.query(Contact).delete()
                db.session.query(Profession).delete()
                db.session.query(CountryAnalytics).delete()
                db.session.query(DeviceAnalytics).delete()
                
                # Восстанавливаем данные
                models_map = {
                    'users': User,
                    'contacts': Contact,
                    'professions': Profession,
                    'country_analytics': CountryAnalytics,
                    'device_analytics': DeviceAnalytics
                }
                
                for table_name, model in models_map.items():
                    if table_name in backup_data['tables']:
                        table_data = backup_data['tables'][table_name]
                        if 'error' in table_data:
                            logger.warning(f"⚠️ Пропускаем таблицу {table_name} из-за ошибки: {table_data['error']}")
                            continue
                        
                        for record_data in table_data['records']:
                            try:
                                # Создаем объект модели
                                record = model()
                                for key, value in record_data.items():
                                    if hasattr(record, key):
                                        setattr(record, key, value)
                                
                                db.session.add(record)
                                
                            except Exception as e:
                                logger.warning(f"⚠️ Ошибка восстановления записи в {table_name}: {str(e)}")
                        
                        logger.info(f"✅ Восстановлено {len(table_data['records'])} записей в {table_name}")
                
                db.session.commit()
                logger.info("✅ Восстановление базы данных завершено")
                return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка восстановления БД: {str(e)}")
            return False
    
    def cleanup_old_backups(self, days_to_keep=30):
        """Очистка старых резервных копий"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            for backup_type in ['database', 'files']:
                backup_path = self.backup_dir / backup_type
                if not backup_path.exists():
                    continue
                
                for backup_file in backup_path.iterdir():
                    if backup_file.is_file():
                        file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                        if file_time < cutoff_date:
                            backup_file.unlink()
                            logger.info(f"🗑️ Удалена старая резервная копия: {backup_file.name}")
            
            logger.info(f"✅ Очистка резервных копий старше {days_to_keep} дней завершена")
            
        except Exception as e:
            logger.error(f"❌ Ошибка очистки старых копий: {str(e)}")
    
    def get_backup_status(self):
        """Получение статуса резервных копий"""
        try:
            status = {
                'database_backups': [],
                'files_backups': [],
                'total_size': 0
            }
            
            for backup_type in ['database', 'files']:
                backup_path = self.backup_dir / backup_type
                if backup_path.exists():
                    for backup_file in backup_path.iterdir():
                        if backup_file.is_file():
                            file_info = {
                                'name': backup_file.name,
                                'size': backup_file.stat().st_size,
                                'created': datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat()
                            }
                            status[f'{backup_type}_backups'].append(file_info)
                            status['total_size'] += file_info['size']
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статуса: {str(e)}")
            return None
    
    def schedule_backups(self):
        """Планирование автоматических резервных копий"""
        try:
            # Ежедневная резервная копия БД в 2:00
            schedule.every().day.at("02:00").do(self.create_database_backup)
            
            # Еженедельная резервная копия файлов в воскресенье в 3:00
            schedule.every().sunday.at("03:00").do(self.create_files_backup)
            
            # Еженедельная очистка старых копий в понедельник в 4:00
            schedule.every().monday.at("04:00").do(self.cleanup_old_backups)
            
            logger.info("✅ Планировщик резервных копий настроен")
            
            # Запускаем планировщик
            while True:
                schedule.run_pending()
                time.sleep(60)  # Проверяем каждую минуту
                
        except KeyboardInterrupt:
            logger.info("⏹️ Планировщик резервных копий остановлен")
        except Exception as e:
            logger.error(f"❌ Ошибка планировщика: {str(e)}")

def main():
    """Основная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Система резервного копирования Mentora')
    parser.add_argument('action', choices=['backup', 'restore', 'status', 'schedule', 'cleanup'],
                       help='Действие для выполнения')
    parser.add_argument('--file', help='Файл резервной копии для восстановления')
    parser.add_argument('--days', type=int, default=30, help='Количество дней для хранения копий')
    
    args = parser.parse_args()
    
    backup_system = BackupSystem()
    
    if args.action == 'backup':
        logger.info("🔄 Создание резервных копий...")
        db_backup = backup_system.create_database_backup()
        files_backup = backup_system.create_files_backup()
        
        if db_backup and files_backup:
            logger.info("✅ Все резервные копии созданы успешно")
        else:
            logger.error("❌ Ошибка создания резервных копий")
    
    elif args.action == 'restore':
        if not args.file:
            logger.error("❌ Необходимо указать файл резервной копии")
            return
        
        logger.info(f"🔄 Восстановление из {args.file}...")
        if backup_system.restore_database_backup(args.file):
            logger.info("✅ Восстановление завершено успешно")
        else:
            logger.error("❌ Ошибка восстановления")
    
    elif args.action == 'status':
        status = backup_system.get_backup_status()
        if status:
            print(json.dumps(status, indent=2, ensure_ascii=False))
        else:
            logger.error("❌ Ошибка получения статуса")
    
    elif args.action == 'schedule':
        logger.info("⏰ Запуск планировщика резервных копий...")
        backup_system.schedule_backups()
    
    elif args.action == 'cleanup':
        logger.info(f"🗑️ Очистка резервных копий старше {args.days} дней...")
        backup_system.cleanup_old_backups(args.days)

if __name__ == '__main__':
    main()
