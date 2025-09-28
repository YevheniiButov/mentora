#!/usr/bin/env python3
"""
Безопасная миграция IRT системы с rollback функциями
"""

import os
import sys
import json
import shutil
from datetime import datetime
import subprocess

class SafeMigration:
    def __init__(self):
        self.migration_log = []
        self.rollback_commands = []
        self.backup_path = None
        
    def log_step(self, step, message, success=True):
        """Логирует шаг миграции"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "step": step,
            "message": message,
            "success": success
        }
        self.migration_log.append(log_entry)
        
        status = "✅" if success else "❌"
        print(f"{status} Step {step}: {message}")
        
        if not success:
            print("🔄 Starting rollback...")
            self.rollback()
            sys.exit(1)
    
    def add_rollback_command(self, command, description):
        """Добавляет команду для rollback"""
        self.rollback_commands.append({
            "command": command,
            "description": description
        })
    
    def rollback(self):
        """Выполняет rollback всех изменений"""
        print("🔄 Executing rollback...")
        
        # Выполняем rollback команды в обратном порядке
        for rollback_cmd in reversed(self.rollback_commands):
            try:
                print(f"   Rolling back: {rollback_cmd['description']}")
                if rollback_cmd['command']:
                    subprocess.run(rollback_cmd['command'], shell=True, check=True)
            except Exception as e:
                print(f"   ❌ Rollback failed: {e}")
        
        print("🔄 Rollback completed")
    
    def step1_backup_database(self):
        """Шаг 1: Создание бэкапа базы данных"""
        self.log_step(1, "Creating database backup...")
        
        try:
            # Запускаем скрипт бэкапа
            result = subprocess.run([sys.executable, 'backup_production.py'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                # Ищем путь к бэкапу в выводе
                for line in result.stdout.split('\n'):
                    if 'Production backup:' in line:
                        self.backup_path = line.split(': ')[1].strip()
                        break
                
                self.add_rollback_command(
                    f"python3 restore_from_backup.py {self.backup_path}",
                    "Restore database from backup"
                )
                
                self.log_step(1, f"Database backup created: {self.backup_path}")
            else:
                self.log_step(1, f"Backup failed: {result.stderr}", False)
                
        except Exception as e:
            self.log_step(1, f"Backup exception: {e}", False)
    
    def step2_add_irt_models(self):
        """Шаг 2: Добавление IRT моделей"""
        self.log_step(2, "Adding IRT models to database...")
        
        try:
            # Проверяем, что модели уже добавлены в models.py
            with open('models.py', 'r') as f:
                content = f.read()
                
            if 'class IRTParameters' in content and 'class DiagnosticSession' in content:
                self.log_step(2, "IRT models already present in models.py")
            else:
                self.log_step(2, "IRT models not found in models.py", False)
            
            # Создаем миграцию для добавления таблиц
            migration_sql = """
            -- IRT Parameters table
            CREATE TABLE IF NOT EXISTS irt_parameters (
                id SERIAL PRIMARY KEY,
                question_id INTEGER NOT NULL UNIQUE,
                difficulty FLOAT NOT NULL,
                discrimination FLOAT NOT NULL,
                guessing FLOAT DEFAULT 0.25,
                calibration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                calibration_sample_size INTEGER,
                reliability FLOAT,
                se_difficulty FLOAT,
                se_discrimination FLOAT,
                se_guessing FLOAT,
                infit FLOAT,
                outfit FLOAT
            );
            
            -- Diagnostic Session table
            CREATE TABLE IF NOT EXISTS diagnostic_session (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                session_type VARCHAR(50) NOT NULL,
                test_length INTEGER,
                time_limit INTEGER,
                current_ability FLOAT DEFAULT 0.0,
                ability_se FLOAT DEFAULT 1.0,
                questions_answered INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0,
                current_question_id INTEGER,
                session_data TEXT,
                ability_history TEXT,
                status VARCHAR(20) DEFAULT 'active',
                termination_reason VARCHAR(50),
                ip_address VARCHAR(45),
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Diagnostic Response table
            CREATE TABLE IF NOT EXISTS diagnostic_response (
                id SERIAL PRIMARY KEY,
                session_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                selected_answer VARCHAR(255) NOT NULL,
                is_correct BOOLEAN NOT NULL,
                response_time FLOAT,
                confidence_level INTEGER,
                ability_before FLOAT,
                ability_after FLOAT,
                se_before FLOAT,
                se_after FLOAT,
                item_information FLOAT,
                expected_response FLOAT,
                responded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            # Сохраняем SQL миграцию
            with open('irt_migration.sql', 'w') as f:
                f.write(migration_sql)
            
            self.add_rollback_command(
                "python3 remove_irt_tables.py",
                "Remove IRT tables"
            )
            
            self.log_step(2, "IRT models migration prepared")
            
        except Exception as e:
            self.log_step(2, f"IRT models error: {e}", False)
    
    def step3_run_specialty_migration(self):
        """Шаг 3: Запуск миграции специальностей"""
        self.log_step(3, "Running specialty migration...")
        
        try:
            # Проверяем наличие скрипта миграции
            if not os.path.exists('specialty_migration.py'):
                self.log_step(3, "specialty_migration.py not found", False)
            
            # Запускаем миграцию
            result = subprocess.run([sys.executable, 'specialty_migration.py'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.add_rollback_command(
                    "python3 rollback_specialty_migration.py",
                    "Rollback specialty migration"
                )
                self.log_step(3, "Specialty migration completed")
            else:
                self.log_step(3, f"Specialty migration failed: {result.stderr}", False)
                
        except Exception as e:
            self.log_step(3, f"Specialty migration exception: {e}", False)
    
    def step4_enable_irt_features(self):
        """Шаг 4: Включение IRT функций"""
        self.log_step(4, "Enabling IRT features...")
        
        try:
            # Создаем feature flags
            feature_flags = {
                "irt_enabled": True,
                "irt_pilot_mode": True,
                "irt_dentists": True,
                "irt_general_practitioners": False,
                "irt_calibration": True,
                "irt_analytics": True
            }
            
            # Сохраняем feature flags
            with open('feature_flags.json', 'w') as f:
                json.dump(feature_flags, f, indent=2)
            
            self.add_rollback_command(
                "rm -f feature_flags.json",
                "Remove feature flags"
            )
            
            self.log_step(4, "IRT features enabled")
            
        except Exception as e:
            self.log_step(4, f"Feature enable error: {e}", False)
    
    def step5_test_system(self):
        """Шаг 5: Тестирование системы"""
        self.log_step(5, "Testing IRT system...")
        
        try:
            # Запускаем тесты
            result = subprocess.run([sys.executable, 'test_irt_staging.py'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_step(5, "IRT system tests passed")
            else:
                self.log_step(5, f"IRT system tests failed: {result.stderr}", False)
                
        except Exception as e:
            self.log_step(5, f"System test exception: {e}", False)
    
    def save_migration_log(self):
        """Сохраняет лог миграции"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"migration_log_{timestamp}.json"
        
        migration_data = {
            "timestamp": timestamp,
            "migration_log": self.migration_log,
            "rollback_commands": self.rollback_commands,
            "backup_path": self.backup_path
        }
        
        with open(log_filename, 'w') as f:
            json.dump(migration_data, f, indent=2)
        
        print(f"📝 Migration log saved: {log_filename}")
    
    def run_migration(self):
        """Запускает полную миграцию"""
        print("🚀 Starting safe IRT system migration...")
        print("=" * 60)
        
        try:
            # Выполняем все шаги
            self.step1_backup_database()
            self.step2_add_irt_models()
            self.step3_run_specialty_migration()
            self.step4_enable_irt_features()
            self.step5_test_system()
            
            # Сохраняем лог
            self.save_migration_log()
            
            print("=" * 60)
            print("🎉 Migration completed successfully!")
            print("✅ IRT system is ready for production")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            self.rollback()
            sys.exit(1)

def main():
    """Основная функция"""
    migration = SafeMigration()
    migration.run_migration()

if __name__ == "__main__":
    main()


