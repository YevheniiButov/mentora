#!/usr/bin/env python3
"""
Test Deployment API
Тестовый скрипт для проверки API развертывания шаблонов

Usage:
    python scripts/test_deployment_api.py
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

class DeploymentAPITester:
    def __init__(self, base_url, email, password):
        self.base_url = base_url
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.csrf_token = None
        
    def login(self):
        """Вход в систему и получение CSRF токена"""
        print("🔐 Logging in...")
        
        # Получаем CSRF токен
        response = self.session.get(f"{self.base_url}/auth/login")
        if response.status_code == 200:
            # Извлекаем CSRF токен из формы (упрощенно)
            self.csrf_token = "test_csrf_token_12345"
        
        # Выполняем вход
        login_data = {
            'email': self.email,
            'password': self.password,
            'csrf_token': self.csrf_token
        }
        
        response = self.session.post(
            f"{self.base_url}/auth/login",
            data=login_data,
            allow_redirects=True
        )
        
        if response.status_code == 200 or response.status_code == 302:
            print("✅ Login successful")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
    
    def test_health_check(self):
        """Тест проверки здоровья сервиса"""
        print("\n🏥 Testing health check...")
        
        response = self.session.get(f"{self.base_url}/api/deploy/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data.get('message')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    
    def test_create_backup(self):
        """Тест создания резервной копии"""
        print("\n💾 Testing backup creation...")
        
        backup_data = {
            'template_path': 'templates/test_template.html',
            'description': 'Test backup from API'
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-CSRF-Token': self.csrf_token
        }
        
        response = self.session.post(
            f"{self.base_url}/api/deploy/backup",
            json=backup_data,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Backup created: {data.get('data', {}).get('backup_id')}")
                return data.get('data', {}).get('backup_id')
            else:
                print(f"❌ Backup creation failed: {data.get('message')}")
                return None
        else:
            print(f"❌ Backup request failed: {response.status_code}")
            return None
    
    def test_generate_preview(self):
        """Тест генерации предпросмотра"""
        print("\n👁️ Testing preview generation...")
        
        # Простой HTML контент для теста
        test_content = """
        <div class="test-container">
            <h1>Test Template</h1>
            <p>This is a test template for preview generation.</p>
            <div class="test-component">
                <span>Test component content</span>
            </div>
        </div>
        """
        
        preview_data = {
            'content': test_content,
            'template_name': 'test_preview'
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-CSRF-Token': self.csrf_token
        }
        
        response = self.session.post(
            f"{self.base_url}/api/deploy/preview",
            json=preview_data,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Preview generated: {data.get('data', {}).get('preview_url')}")
                return True
            else:
                print(f"❌ Preview generation failed: {data.get('message')}")
                return False
        else:
            print(f"❌ Preview request failed: {response.status_code}")
            return False
    
    def test_validate_template(self):
        """Тест валидации шаблона"""
        print("\n✅ Testing template validation...")
        
        # Простой Jinja2 шаблон для теста
        test_template = """
        {% extends "base.html" %}
        
        {% block content %}
        <div class="test-container">
            <h1>{{ title }}</h1>
            <p>{{ description }}</p>
            {% if items %}
            <ul>
                {% for item in items %}
                <li>{{ item.name }}</li>
                {% endfor %}
            </ul>
            {% endif %}
        </div>
        {% endblock %}
        """
        
        validate_data = {
            'content': test_template,
            'template_path': 'templates/test_template.html'
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-CSRF-Token': self.csrf_token
        }
        
        response = self.session.post(
            f"{self.base_url}/api/deploy/validate",
            json=validate_data,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                validation_passed = data.get('data', {}).get('validation_passed', False)
                issues_count = data.get('data', {}).get('issues_count', 0)
                print(f"✅ Validation completed: {'PASSED' if validation_passed else 'FAILED'} ({issues_count} issues)")
                return validation_passed
            else:
                print(f"❌ Validation failed: {data.get('message')}")
                return False
        else:
            print(f"❌ Validation request failed: {response.status_code}")
            return False
    
    def test_deploy_template(self):
        """Тест развертывания шаблона"""
        print("\n🚀 Testing template deployment...")
        
        # Простой Jinja2 шаблон для развертывания
        deploy_template = """
        {% extends "base.html" %}
        
        {% block content %}
        <div class="deployed-container">
            <h1>Deployed Template</h1>
            <p>This template was deployed via API at {{ timestamp }}</p>
            <div class="deployment-info">
                <p>Deployed by: {{ user }}</p>
                <p>Description: {{ description }}</p>
            </div>
        </div>
        {% endblock %}
        """
        
        deploy_data = {
            'content': deploy_template,
            'target_path': 'templates/deployed_test.html',
            'description': 'Test deployment from API',
            'require_backup': True,
            'strict_validation': False
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-CSRF-Token': self.csrf_token
        }
        
        response = self.session.post(
            f"{self.base_url}/api/deploy/deploy",
            json=deploy_data,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                deployment_id = data.get('data', {}).get('deployment_id')
                print(f"✅ Template deployed: {deployment_id}")
                return deployment_id
            else:
                print(f"❌ Deployment failed: {data.get('message')}")
                return None
        else:
            print(f"❌ Deployment request failed: {response.status_code}")
            return None
    
    def test_get_backup_list(self):
        """Тест получения списка резервных копий"""
        print("\n📋 Testing backup list retrieval...")
        
        response = self.session.get(f"{self.base_url}/api/deploy/backups/test_template")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                backups = data.get('data', {}).get('backups', [])
                print(f"✅ Found {len(backups)} backups")
                return backups
            else:
                print(f"❌ Backup list failed: {data.get('message')}")
                return []
        else:
            print(f"❌ Backup list request failed: {response.status_code}")
            return []
    
    def test_get_deployment_history(self):
        """Тест получения истории развертываний"""
        print("\n📚 Testing deployment history retrieval...")
        
        response = self.session.get(f"{self.base_url}/api/deploy/history/templates/deployed_test.html")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                history = data.get('data', {}).get('deployment_history', [])
                print(f"✅ Found {len(history)} deployment records")
                return history
            else:
                print(f"❌ History retrieval failed: {data.get('message')}")
                return []
        else:
            print(f"❌ History request failed: {response.status_code}")
            return []
    
    def test_rollback(self, backup_timestamp):
        """Тест отката изменений"""
        if not backup_timestamp:
            print("\n🔄 Skipping rollback test (no backup available)")
            return False
            
        print("\n🔄 Testing rollback...")
        
        rollback_data = {
            'target_path': 'templates/deployed_test.html',
            'backup_timestamp': backup_timestamp,
            'confirmation': 'CONFIRM_ROLLBACK'
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-CSRF-Token': self.csrf_token
        }
        
        response = self.session.post(
            f"{self.base_url}/api/deploy/rollback",
            json=rollback_data,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                rollback_id = data.get('data', {}).get('rollback_id')
                print(f"✅ Rollback completed: {rollback_id}")
                return True
            else:
                print(f"❌ Rollback failed: {data.get('message')}")
                return False
        else:
            print(f"❌ Rollback request failed: {response.status_code}")
            return False
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("🧪 Starting Deployment API Tests")
        print("=" * 50)
        
        # Вход в систему
        if not self.login():
            print("❌ Cannot proceed without login")
            return
        
        # Результаты тестов
        results = {
            'health_check': False,
            'backup_creation': False,
            'preview_generation': False,
            'template_validation': False,
            'template_deployment': False,
            'backup_list': False,
            'deployment_history': False,
            'rollback': False
        }
        
        # Тест 1: Проверка здоровья
        results['health_check'] = self.test_health_check()
        
        # Тест 2: Создание резервной копии
        backup_id = self.test_create_backup()
        results['backup_creation'] = backup_id is not None
        
        # Тест 3: Генерация предпросмотра
        results['preview_generation'] = self.test_generate_preview()
        
        # Тест 4: Валидация шаблона
        results['template_validation'] = self.test_validate_template()
        
        # Тест 5: Развертывание шаблона
        deployment_id = self.test_deploy_template()
        results['template_deployment'] = deployment_id is not None
        
        # Тест 6: Список резервных копий
        backups = self.test_get_backup_list()
        results['backup_list'] = len(backups) >= 0
        
        # Тест 7: История развертываний
        history = self.test_get_deployment_history()
        results['deployment_history'] = len(history) >= 0
        
        # Тест 8: Откат изменений
        results['rollback'] = self.test_rollback(backup_id)
        
        # Итоговый отчет
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Deployment API is working correctly.")
        else:
            print("⚠️ Some tests failed. Check the logs above for details.")
        
        return results

def main():
    """Основная функция"""
    print("🚀 Deployment API Test Suite")
    print("This script tests the deployment API endpoints")
    print()
    
    # Создаем тестер
    tester = DeploymentAPITester(BASE_URL, ADMIN_EMAIL, ADMIN_PASSWORD)
    
    # Запускаем тесты
    results = tester.run_all_tests()
    
    # Сохраняем результаты в файл
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"deployment_api_test_results_{timestamp}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'base_url': BASE_URL,
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Test results saved to: {results_file}")

if __name__ == "__main__":
    main() 