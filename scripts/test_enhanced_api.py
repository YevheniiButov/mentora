#!/usr/bin/env python3
"""
Тестовый скрипт для проверки обновленных API endpoints
Dental Academy Content Editor API
"""

import requests
import json
import time
from datetime import datetime

class EnhancedAPITester:
    def __init__(self, base_url="http://127.0.0.1:8083", lang="en"):
        self.base_url = base_url
        self.lang = lang
        self.session = requests.Session()
        self.test_results = []
        
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
    
    def test_css_variables_get(self):
        """Тест получения CSS переменных"""
        try:
            url = f"{self.base_url}/{self.lang}/admin/content-editor/api/content-editor/css-variables"
            response = self.session.get(url)
            
            success = response.status_code == 200
            data = response.json() if success else None
            
            details = None
            if success:
                if 'css_variables' in data and 'success' in data:
                    details = f"Found {len(data['css_variables'])} variables"
                else:
                    success = False
                    details = "Invalid response format"
            else:
                details = f"Status code: {response.status_code}"
            
            self.log_test("CSS Variables GET", success, details)
            return success
            
        except Exception as e:
            self.log_test("CSS Variables GET", False, str(e))
            return False
    
    def test_css_variables_update(self):
        """Тест обновления CSS переменных"""
        try:
            url = f"{self.base_url}/{self.lang}/admin/content-editor/api/content-editor/css-variables"
            
            test_variables = {
                "--test-primary-color": "#FF0000",
                "--test-secondary-color": "#00FF00",
                "--test-text-color": "#0000FF"
            }
            
            data = {
                'variables': test_variables
            }
            
            response = self.session.post(url, json=data)
            
            success = response.status_code == 200
            response_data = response.json() if success else None
            
            details = None
            if success:
                if 'success' in response_data and response_data['success']:
                    details = f"Updated {len(test_variables)} variables"
                else:
                    success = False
                    details = "Update failed in response"
            else:
                details = f"Status code: {response.status_code}"
            
            self.log_test("CSS Variables UPDATE", success, details)
            return success
            
        except Exception as e:
            self.log_test("CSS Variables UPDATE", False, str(e))
            return False
    
    def test_template_load(self):
        """Тест загрузки шаблона с полным парсингом"""
        try:
            template_path = "learning/subject_view.html"
            url = f"{self.base_url}/{self.lang}/admin/content-editor/api/content-editor/template/{template_path}"
            
            response = self.session.get(url)
            
            success = response.status_code == 200
            data = response.json() if success else None
            
            details = None
            if success:
                if 'template' in data and 'success' in data:
                    template = data['template']
                    required_fields = ['template_path', 'grapesjs_data', 'css_variables', 'jinja_logic']
                    missing_fields = [field for field in required_fields if field not in template]
                    
                    if not missing_fields:
                        details = f"Template loaded: {template['name']}"
                    else:
                        success = False
                        details = f"Missing fields: {missing_fields}"
                else:
                    success = False
                    details = "Invalid response format"
            else:
                details = f"Status code: {response.status_code}"
            
            self.log_test("Template LOAD with Jinja2 parsing", success, details)
            return success
            
        except Exception as e:
            self.log_test("Template LOAD with Jinja2 parsing", False, str(e))
            return False
    
    def test_template_save(self):
        """Тест сохранения шаблона с конвертацией Jinja2"""
        try:
            url = f"{self.base_url}/{self.lang}/admin/content-editor/api/content-editor/save"
            
            test_data = {
                'template_path': 'test/template_test.html',
                'name': 'Test Template',
                'grapesjs_data': {
                    'components': [
                        {
                            'type': 'text',
                            'content': 'Test content',
                            'attributes': {'class': 'test-class'}
                        }
                    ]
                },
                'css_variables': {
                    '--test-color': '#FF0000'
                },
                'jinja_logic': {
                    'blocks': [],
                    'variables': [],
                    'macros': []
                },
                'metadata': {
                    'test': True,
                    'created_by': 'test_script'
                },
                'convert_to_jinja2': True
            }
            
            response = self.session.post(url, json=test_data)
            
            success = response.status_code == 200
            data = response.json() if success else None
            
            details = None
            if success:
                if 'success' in data and data['success']:
                    details = f"Template saved with ID: {data.get('template_id', 'N/A')}"
                else:
                    success = False
                    details = "Save failed in response"
            else:
                details = f"Status code: {response.status_code}"
            
            self.log_test("Template SAVE with Jinja2 conversion", success, details)
            return success
            
        except Exception as e:
            self.log_test("Template SAVE with Jinja2 conversion", False, str(e))
            return False
    
    def test_live_preview(self):
        """Тест генерации live preview"""
        try:
            url = f"{self.base_url}/{self.lang}/admin/content-editor/api/content-editor/live-preview"
            
            test_data = {
                'template_path': 'test/preview_test.html',
                'grapesjs_data': {
                    'components': [
                        {
                            'type': 'text',
                            'content': 'Preview test content',
                            'attributes': {'class': 'preview-class'}
                        }
                    ]
                },
                'css_variables': {
                    '--preview-color': '#00FF00'
                },
                'jinja_logic': {
                    'blocks': [],
                    'variables': [],
                    'macros': []
                }
            }
            
            response = self.session.post(url, json=test_data)
            
            success = response.status_code == 200
            data = response.json() if success else None
            
            details = None
            if success:
                if 'preview_html' in data and 'success' in data:
                    html_length = len(data['preview_html'])
                    details = f"Preview generated: {html_length} characters"
                else:
                    success = False
                    details = "Preview generation failed"
            else:
                details = f"Status code: {response.status_code}"
            
            self.log_test("Live PREVIEW generation", success, details)
            return success
            
        except Exception as e:
            self.log_test("Live PREVIEW generation", False, str(e))
            return False
    
    def test_template_deploy(self):
        """Тест деплоя шаблона"""
        try:
            url = f"{self.base_url}/{self.lang}/admin/content-editor/api/content-editor/deploy"
            
            test_data = {
                'template_path': 'test/deploy_test.html'
            }
            
            response = self.session.post(url, json=test_data)
            
            success = response.status_code == 200
            data = response.json() if success else None
            
            details = None
            if success:
                if 'success' in data and data['success']:
                    details = f"Template deployed: {data.get('backup_path', 'N/A')}"
                else:
                    success = False
                    details = "Deploy failed in response"
            else:
                details = f"Status code: {response.status_code}"
            
            self.log_test("Template DEPLOY", success, details)
            return success
            
        except Exception as e:
            self.log_test("Template DEPLOY", False, str(e))
            return False
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("🚀 Starting Enhanced API Tests")
        print("=" * 50)
        
        tests = [
            self.test_css_variables_get,
            self.test_css_variables_update,
            self.test_template_load,
            self.test_template_save,
            self.test_live_preview,
            self.test_template_deploy
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
        
        # Сохранение результатов
        results_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'passed': passed,
                    'total': total,
                    'timestamp': datetime.now().isoformat()
                },
                'results': self.test_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {results_file}")
        
        return passed == total

def main():
    """Основная функция"""
    print("🔧 Enhanced API Tester for Dental Academy")
    print("Testing updated content editor API endpoints")
    print()
    
    # Настройки
    base_url = "http://127.0.0.1:8083"
    lang = "en"
    
    # Создание тестера
    tester = EnhancedAPITester(base_url, lang)
    
    # Проверка доступности сервера
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code != 200:
            print(f"❌ Server not accessible at {base_url}")
            print(f"   Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server at {base_url}")
        print(f"   Error: {str(e)}")
        print("   Make sure the Flask app is running: python app.py")
        return False
    
    print(f"✅ Server accessible at {base_url}")
    print()
    
    # Запуск тестов
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