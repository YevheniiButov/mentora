#!/usr/bin/env python3
"""
Тестовый скрипт для проверки TemplateDeployer
Dental Academy Template Deployment System
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Добавляем корневую папку проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.template_deployer import TemplateDeployer, ValidationResult

class TemplateDeployerTester:
    def __init__(self):
        self.test_results = []
        self.temp_dir = None
        self.deployer = None
        
    def setup_test_environment(self):
        """Настройка тестового окружения"""
        print("🔧 Setting up test environment...")
        
        # Создание временной директории
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Создание структуры папок
        (self.temp_dir / 'templates').mkdir()
        (self.temp_dir / 'static' / 'css').mkdir(parents=True)
        (self.temp_dir / 'static' / 'js').mkdir(parents=True)
        (self.temp_dir / 'backups' / 'templates' / 'metadata').mkdir(parents=True)
        (self.temp_dir / 'backups' / 'templates' / 'files').mkdir(parents=True)
        
        # Создание тестовых файлов
        self._create_test_files()
        
        # Инициализация TemplateDeployer с явными путями
        self.deployer = TemplateDeployer(
            template_folder=self.temp_dir / 'templates',
            static_folder=self.temp_dir / 'static',
            backup_dir=self.temp_dir / 'backups' / 'templates'
        )
        
        print(f"✅ Test environment ready: {self.temp_dir}")
        
    def _create_test_files(self):
        """Создание тестовых файлов"""
        
        # Тестовый CSS файл
        css_content = """
:root {
    --primary-color: #3ECDC1;
    --secondary-color: #FF6B6B;
    --text-primary: #2d3748;
    --background-primary: #ffffff;
}
        """
        with open(self.temp_dir / 'static' / 'css' / 'test.css', 'w') as f:
            f.write(css_content)
        
        # Тестовый JS файл
        js_content = """
console.log('Test JS file loaded');
        """
        with open(self.temp_dir / 'static' / 'js' / 'test.js', 'w') as f:
            f.write(js_content)
        
        # Оригинальный тестовый шаблон
        original_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Test Template</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/test.css') }}">
</head>
<body>
    <div class="container">
        <h1>{{ _('Welcome') }}</h1>
        <p>This is a test template</p>
    </div>
    <script src="{{ url_for('static', filename='js/test.js') }}"></script>
</body>
</html>
        """
        with open(self.temp_dir / 'templates' / 'test_template.html', 'w') as f:
            f.write(original_template)
    
    def log_test(self, test_name, success, details=None):
        """Логирование результатов теста"""
        result = {
            'test': test_name,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_validation_valid_template(self):
        """Тест валидации корректного шаблона"""
        try:
            valid_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Valid Template</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/test.css') }}">
</head>
<body>
    <div class="container">
        <h1>{{ _('Welcome') }}</h1>
        <p>Valid content</p>
    </div>
</body>
</html>
            """
            
            validation = self.deployer.validate_template(valid_content, 'test/valid.html')
            
            success = validation.is_valid and len(validation.errors) == 0
            details = f"Valid: {validation.is_valid}, Errors: {len(validation.errors)}, Warnings: {len(validation.warnings)}"
            
            self.log_test("Validation - Valid Template", success, details)
            return success
            
        except Exception as e:
            self.log_test("Validation - Valid Template", False, str(e))
            return False
    
    def test_validation_invalid_template(self):
        """Тест валидации некорректного шаблона"""
        try:
            invalid_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Invalid Template</title>
</head>
<body>
    <div class="container">
        <h1>{{ _('Welcome') }}</h1>
        <p>Invalid content with {{ unclosed_variable
    </div>
</body>
</html>
            """
            
            validation = self.deployer.validate_template(invalid_content, 'test/invalid.html')
            
            success = not validation.is_valid and len(validation.errors) > 0
            details = f"Valid: {validation.is_valid}, Errors: {len(validation.errors)}"
            
            self.log_test("Validation - Invalid Template", success, details)
            return success
            
        except Exception as e:
            self.log_test("Validation - Invalid Template", False, str(e))
            return False
    
    def test_validation_missing_files(self):
        """Тест валидации с отсутствующими файлами"""
        try:
            content_with_missing_files = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Missing Files</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/missing.css') }}">
    <script src="{{ url_for('static', filename='js/missing.js') }}"></script>
</head>
<body>
    <div class="container">
        <h1>Test</h1>
    </div>
</body>
</html>
            """
            
            validation = self.deployer.validate_template(content_with_missing_files, 'test/missing_files.html')
            
            success = len(validation.errors) > 0
            details = f"Errors: {len(validation.errors)}, Warnings: {len(validation.warnings)}"
            
            self.log_test("Validation - Missing Files", success, details)
            return success
            
        except Exception as e:
            self.log_test("Validation - Missing Files", False, str(e))
            return False
    
    def test_backup_creation(self):
        """Тест создания резервной копии"""
        try:
            template_path = 'test_template.html'
            user_id = 1
            notes = 'Test backup creation'
            
            # Создаем тестовый файл для бэкапа
            test_file = self.temp_dir / 'templates' / template_path
            test_file.parent.mkdir(parents=True, exist_ok=True)
            with open(test_file, 'w') as f:
                f.write("Test content for backup")
            
            backup_id = self.deployer.create_backup(template_path, user_id, notes)
            
            success = backup_id is not None and len(backup_id) > 0
            details = f"Backup ID: {backup_id}"
            
            self.log_test("Backup Creation", success, details)
            return success, backup_id
            
        except Exception as e:
            self.log_test("Backup Creation", False, str(e))
            return False, None
    
    def test_template_deployment(self):
        """Тест деплоя шаблона"""
        try:
            template_path = 'test_template.html'
            new_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Updated Test Template</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/test.css') }}">
</head>
<body>
    <div class="container">
        <h1>{{ _('Updated Welcome') }}</h1>
        <p>This is an updated test template</p>
    </div>
</body>
</html>
            """
            user_id = 1
            notes = 'Test deployment'
            
            # Создаем тестовый файл для деплоя
            test_file = self.temp_dir / 'templates' / template_path
            test_file.parent.mkdir(parents=True, exist_ok=True)
            with open(test_file, 'w') as f:
                f.write("Original content")
            
            result = self.deployer.deploy_template(
                template_path=template_path,
                new_content=new_content,
                user_id=user_id,
                notes=notes
            )
            
            success = result['success']
            details = f"Backup ID: {result.get('backup_id', 'N/A')}"
            
            self.log_test("Template Deployment", success, details)
            return success, result.get('backup_id')
            
        except Exception as e:
            self.log_test("Template Deployment", False, str(e))
            return False, None
    
    def test_backup_restoration(self):
        """Тест восстановления из резервной копии"""
        try:
            # Сначала создаем бэкап
            success, backup_id = self.test_backup_creation()
            if not success:
                return False
            
            template_path = 'test_template.html'
            
            # Восстанавливаем из бэкапа
            restore_success = self.deployer.rollback_template(template_path, backup_id)
            
            details = f"Backup ID: {backup_id}"
            
            self.log_test("Backup Restoration", restore_success, details)
            return restore_success
            
        except Exception as e:
            self.log_test("Backup Restoration", False, str(e))
            return False
    
    def test_backup_management(self):
        """Тест управления резервными копиями"""
        try:
            # Получение списка бэкапов
            backups = self.deployer.get_backup_list()
            
            success = isinstance(backups, list)
            details = f"Found {len(backups)} backups"
            
            self.log_test("Backup Management - List", success, details)
            
            # Получение статистики
            stats = self.deployer.get_deployment_stats()
            
            stats_success = isinstance(stats, dict)
            stats_details = f"Stats: {stats}"
            
            self.log_test("Backup Management - Stats", stats_success, stats_details)
            
            return success and stats_success
            
        except Exception as e:
            self.log_test("Backup Management", False, str(e))
            return False
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("🚀 Starting TemplateDeployer Tests")
        print("=" * 50)
        
        try:
            self.setup_test_environment()
            
            tests = [
                self.test_validation_valid_template,
                self.test_validation_invalid_template,
                self.test_validation_missing_files,
                self.test_backup_creation,
                self.test_template_deployment,
                self.test_backup_restoration,
                self.test_backup_management
            ]
            
            passed = 0
            total = len(tests)
            
            for test in tests:
                try:
                    if test():
                        passed += 1
                except Exception as e:
                    self.log_test(test.__name__, False, f"Test exception: {str(e)}")
            
            print("=" * 50)
            print(f"📊 Test Results: {passed}/{total} passed")
            
            return passed == total
            
        finally:
            # Очистка тестового окружения
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                print(f"🧹 Cleaned up test environment: {self.temp_dir}")

def main():
    """Основная функция"""
    print("🔧 TemplateDeployer Tester for Dental Academy")
    print("Testing template deployment system")
    print()
    
    tester = TemplateDeployerTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the results above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 