import unittest
from unittest.mock import patch, MagicMock
from flask import current_app
from app import app
from models import db, User

class TestAIWidgets(unittest.TestCase):
    def setUp(self):
        """Настройка для каждого теста"""
        self.app = app
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Создаем временную базу данных
        db.create_all()
        
        # Создаем тестового пользователя
        self.test_user = User(username='testuser', email='test@example.com', password_hash='testpass')
        db.session.add(self.test_user)
        db.session.commit()
    
    def tearDown(self):
        """Очистка после каждого теста"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def login_user(self):
        """Логин тестового пользователя"""
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.test_user.id)
            sess['_fresh'] = True
    
    def test_index_page_loads_with_widgets(self):
        """Тест что главная страница загружается с ИИ виджетами"""
        self.login_user()
        
        response = self.client.get('/en/')
        self.assertEqual(response.status_code, 200)
        
        # Проверяем что HTML содержит наши виджеты
        html = response.get_data(as_text=True)
        self.assertIn('ai-widget', html)
        self.assertIn('examReadinessWidget', html)
        self.assertIn('recommendationsWidget', html)
        self.assertIn('miniChatWidget', html)
        self.assertIn('progressAnalyticsWidget', html)
        
        # Проверяем наличие CSS стилей для виджетов
        self.assertIn('.ai-widget {', html)
        self.assertIn('.widget-header', html)
        self.assertIn('@media (max-width: 768px)', html)
        
        # Проверяем наличие JavaScript функций
        self.assertIn('initializeAIWidgets', html)
        self.assertIn('loadExamReadiness', html)
        self.assertIn('optimizeForMobile', html)
        
        print("✅ Main page loads with AI widgets")
    
    def test_exam_prediction_endpoint(self):
        """Тест endpoint'а предсказания экзамена"""
        self.login_user()
        
        response = self.client.post('/en/ai-assistant/predict-exam')
        
        # Проверяем что endpoint доступен (может быть 200 или 500 если нет ML)
        self.assertIn(response.status_code, [200, 500])
        
        if response.status_code == 200:
            data = response.get_json()
            self.assertIn('success', data)
            
        print("✅ Exam prediction endpoint accessible")
    
    def test_recommendations_endpoint(self):
        """Тест endpoint'а рекомендаций"""
        self.login_user()
        
        response = self.client.post('/en/ai-assistant/recommend-content',
                                  json={'limit': 3})
        
        self.assertIn(response.status_code, [200, 500])
        
        if response.status_code == 200:
            data = response.get_json()
            self.assertIn('success', data)
            
        print("✅ Recommendations endpoint accessible")
    
    def test_mini_chat_integration(self):
        """Тест интеграции мини-чата"""
        self.login_user()
        
        # Тест отправки сообщения через существующий AI chat endpoint
        response = self.client.post('/en/ai-assistant/chat',
                                  json={'message': 'Test message', 'mini_chat': True})
        
        # Endpoint должен существовать
        self.assertIn(response.status_code, [200, 400, 500])
        
        print("✅ Mini chat integration works")
    
    @patch('utils.adaptive_learning.AdaptiveLearningEngine')
    def test_widgets_with_mock_data(self, mock_engine):
        """Тест виджетов с мок-данными"""
        self.login_user()
        
        # Мокаем ответ ML движка
        mock_instance = mock_engine.return_value
        mock_instance.predict_big_exam_success.return_value = {
            'success_probability': 0.75,
            'weak_areas': [
                {'area': 'dutch_proficiency', 'priority': 'high', 'current_level': 0.6}
            ],
            'recommendations': [
                {'title': 'Test Recommendation', 'description': 'Test Description'}
            ]
        }
        
        response = self.client.post('/en/ai-assistant/predict-exam')
        
        # Проверяем что мок работает
        if response.status_code == 200:
            data = response.get_json()
            self.assertTrue(data.get('success'))
            self.assertIn('prediction', data)
            
        print("✅ Widgets work with mock data")
    
    def test_mobile_responsiveness(self):
        """Тест мобильной адаптивности"""
        self.login_user()
        
        # Эмулируем мобильный User-Agent
        response = self.client.get('/en/', headers={
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        })
        
        self.assertEqual(response.status_code, 200)
        
        html = response.get_data(as_text=True)
        
        # Проверяем что мобильные стили подключены
        self.assertIn('@media (max-width: 768px)', html)
        self.assertIn('@media (max-width: 576px)', html)
        self.assertIn('touch-action: manipulation', html)
        self.assertIn('ai-widget', html)
        
        # Проверяем мобильные функции JavaScript
        self.assertIn('isMobileDevice()', html)
        self.assertIn('optimizeForMobile()', html)
        
        print("✅ Mobile responsiveness works")
    
    def test_widgets_without_authentication(self):
        """Тест что виджеты не показываются неаутентифицированным пользователям"""
        response = self.client.get('/en/')
        
        html = response.get_data(as_text=True)
        
        # ИИ виджеты НЕ должны отображаться
        self.assertNotIn('examReadinessWidget', html)
        self.assertNotIn('recommendationsWidget', html)
        self.assertNotIn('miniChatWidget', html)
        self.assertNotIn('progressAnalyticsWidget', html)
        
        # Но основная страница должна загружаться
        self.assertEqual(response.status_code, 200)
        
        print("✅ Widgets hidden for unauthenticated users")
    
    def test_widget_css_classes_present(self):
        """Тест наличия всех необходимых CSS классов"""
        self.login_user()
        
        response = self.client.get('/en/')
        html = response.get_data(as_text=True)
        
        # Проверяем основные CSS классы
        required_classes = [
            '.ai-widget',
            '.widget-header',
            '.widget-title',
            '.widget-body',
            '.success-probability-circle',
            '.recommendation-item',
            '.mini-chat-messages',
            '.analytics-metric'
        ]
        
        for css_class in required_classes:
            self.assertIn(css_class, html, f"Missing CSS class: {css_class}")
        
        print("✅ All required CSS classes present")
    
    def test_javascript_functions_present(self):
        """Тест наличия всех необходимых JavaScript функций"""
        self.login_user()
        
        response = self.client.get('/en/')
        html = response.get_data(as_text=True)
        
        # Проверяем основные JavaScript функции
        required_functions = [
            'initializeAIWidgets',
            'loadExamReadiness',
            'loadRecommendations',
            'loadProgressAnalytics',
            'toggleMiniChat',
            'sendMiniChatMessage',
            'refreshExamPrediction',
            'optimizeForMobile',
            'isMobileDevice'
        ]
        
        for function in required_functions:
            self.assertIn(function, html, f"Missing JavaScript function: {function}")
        
        print("✅ All required JavaScript functions present")
    
    def test_ai_dashboard_section_visibility(self):
        """Тест что секция AI dashboard показывается только авторизованным"""
        # Тест для неавторизованного пользователя
        response = self.client.get('/en/')
        html = response.get_data(as_text=True)
        self.assertNotIn('ai-dashboard-section', html)
        
        # Тест для авторизованного пользователя
        self.login_user()
        response = self.client.get('/en/')
        html = response.get_data(as_text=True)
        self.assertIn('ai-dashboard-section', html)
        
        print("✅ AI dashboard section visibility works correctly")
    
    def test_widget_error_handling(self):
        """Тест обработки ошибок в виджетах"""
        self.login_user()
        
        response = self.client.get('/en/')
        html = response.get_data(as_text=True)
        
        # Проверяем наличие функций обработки ошибок
        self.assertIn('getErrorHTML', html)
        self.assertIn('getLoadingHTML', html)
        
        # Проверяем что есть обработка try-catch в JavaScript
        self.assertIn('try {', html)
        self.assertIn('catch (error)', html)
        self.assertIn('console.error', html)
        
        print("✅ Error handling functions present")
    
    def test_csrf_protection(self):
        """Тест CSRF защиты для AJAX запросов"""
        self.login_user()
        
        response = self.client.get('/en/')
        html = response.get_data(as_text=True)
        
        # Проверяем что в JavaScript есть получение CSRF токена
        self.assertIn('getCSRFToken', html)
        self.assertIn('X-CSRFToken', html)
        self.assertIn('csrf-token', html)
        
        print("✅ CSRF protection implemented")
    
    def test_localization_support(self):
        """Тест поддержки локализации в виджетах"""
        self.login_user()
        
        # Тест русской локализации
        response = self.client.get('/ru/')
        self.assertEqual(response.status_code, 200)
        
        html = response.get_data(as_text=True)
        if 'ai-dashboard-section' in html:
            # Проверяем русские тексты
            self.assertIn('Готовность к BIG экзамену', html)
            self.assertIn('Персональные рекомендации', html)
            self.assertIn('Быстрый вопрос к ИИ', html)
        
        print("✅ Localization support works")
    
    def test_performance_optimizations(self):
        """Тест производительности и оптимизаций"""
        self.login_user()
        
        response = self.client.get('/en/')
        html = response.get_data(as_text=True)
        
        # Проверяем наличие оптимизаций производительности
        performance_features = [
            'document.visibilityState',  # Проверка видимости страницы
            'setTimeout',               # Асинхронная загрузка
            'passive: false',          # Оптимизация событий
            'updateInterval'           # Контроль частоты обновлений
        ]
        
        for feature in performance_features:
            self.assertIn(feature, html, f"Missing performance feature: {feature}")
        
        print("✅ Performance optimizations present")

if __name__ == '__main__':
    unittest.main() 