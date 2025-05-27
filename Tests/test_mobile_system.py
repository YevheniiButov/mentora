# tests/test_mobile_system.py
"""
Comprehensive tests for mobile system functionality
Полные тесты функциональности мобильной системы
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from flask import Flask, g, session
from datetime import datetime, timedelta

from utils.mobile_detection import MobileDetector, get_mobile_detector
from utils.mobile_helpers import (
    PWAManager, MobileImageProcessor, MobilePerformanceMonitor,
    MobileContentOptimizer, content_optimizer
)
from mobile_integration import MobileTemplateManager, render_adaptive_template
from config.mobile_config import MobileConfig, get_mobile_config


class TestMobileDetection:
    """Тесты определения мобильных устройств"""
    
    def test_mobile_user_agents(self):
        """Тест определения мобильных User-Agent"""
        mobile_user_agents = [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36",
            "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15"
        ]
        
        for ua in mobile_user_agents:
            detector = MobileDetector(ua)
            assert detector.is_mobile == True, f"Should detect mobile: {ua}"
            assert detector.device_type == 'mobile'
    
    def test_tablet_user_agents(self):
        """Тест определения планшетов"""
        tablet_user_agents = [
            "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (Linux; Android 10; SM-T510) AppleWebKit/537.36"
        ]
        
        for ua in tablet_user_agents:
            detector = MobileDetector(ua)
            assert detector.is_tablet == True, f"Should detect tablet: {ua}"
            assert detector.device_type == 'tablet'
    
    def test_desktop_user_agents(self):
        """Тест определения десктопных устройств"""
        desktop_user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
        
        for ua in desktop_user_agents:
            detector = MobileDetector(ua)
            assert detector.is_mobile == False, f"Should not detect mobile: {ua}"
            assert detector.device_type == 'desktop'
    
    def test_device_info_structure(self):
        """Тест структуры информации об устройстве"""
        ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
        detector = MobileDetector(ua)
        
        device_info = detector.get_device_info()
        
        required_fields = [
            'is_mobile', 'is_tablet', 'is_mobile_device', 
            'device_type', 'screen_size_category', 'user_agent'
        ]
        
        for field in required_fields:
            assert field in device_info, f"Missing required field: {field}"
    
    def test_screen_size_detection(self):
        """Тест определения размера экрана"""
        # Тест с мобильными заголовками
        headers = {'HTTP_VIEWPORT_WIDTH': '375'}
        detector = MobileDetector("Mozilla/5.0 (iPhone)", headers)
        
        assert detector.screen_size_category in ['small', 'medium', 'large', 'desktop']
    
    def test_should_use_mobile_template(self):
        """Тест логики выбора мобильного шаблона"""
        mobile_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
        detector = MobileDetector(mobile_ua)
        
        # По умолчанию должен использовать мобильный шаблон
        assert detector.should_use_mobile_template() == True
        
        # Принудительное отключение
        assert detector.should_use_mobile_template(force_mobile=False) == False
        
        # Принудительное включение
        desktop_detector = MobileDetector("Mozilla/5.0 (Windows NT 10.0)")
        assert desktop_detector.should_use_mobile_template(force_mobile=True) == True


class TestMobileTemplateManager:
    """Тесты менеджера мобильных шаблонов"""
    
    @pytest.fixture
    def app(self):
        """Создает тестовое Flask приложение"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def template_manager(self, app):
        """Создает менеджер шаблонов"""
        manager = MobileTemplateManager(app)
        return manager
    
    def test_template_registration(self, template_manager):
        """Тест регистрации соответствий шаблонов"""
        template_manager.register_mobile_template(
            'desktop.html', 'mobile.html'
        )
        
        assert 'desktop.html' in template_manager.template_mappings
        assert template_manager.template_mappings['desktop.html'] == 'mobile.html'
    
    def test_appropriate_template_selection(self, app, template_manager):
        """Тест выбора подходящего шаблона"""
        template_manager.register_mobile_template(
            'test.html', 'test_mobile.html'
        )
        
        with app.test_request_context(headers={'User-Agent': 'iPhone'}):
            # Мобильный шаблон для мобильного устройства
            result = template_manager.get_appropriate_template('test.html')
            assert result == 'test_mobile.html'
        
        with app.test_request_context(headers={'User-Agent': 'Windows Chrome'}):
            # Десктопный шаблон для десктопа
            result = template_manager.get_appropriate_template('test.html')
            assert result == 'test.html'
    
    def test_mobile_image_filter(self, template_manager):
        """Тест фильтра мобильных изображений"""
        # Тест автоматического размера
        result = template_manager.mobile_image_filter('/path/image.jpg', 'small')
        assert '_small.jpg' in result
        
        # Тест без изменений для десктопа
        result = template_manager.mobile_image_filter('/path/image.jpg', 'desktop')
        assert result == '/path/image.jpg'
    
    def test_mobile_truncate_filter(self, template_manager):
        """Тест фильтра обрезки текста"""
        long_text = "This is a very long text that should be truncated for mobile devices"
        
        # Для мобильных должен обрезать
        result = template_manager.mobile_truncate_filter(long_text, 30)
        assert len(result) <= 33  # 30 + "..."
        assert result.endswith('...')
        
        # Короткий текст не обрезается
        short_text = "Short"
        result = template_manager.mobile_truncate_filter(short_text, 30)
        assert result == short_text


class TestPWAManager:
    """Тесты PWA функциональности"""
    
    @pytest.fixture
    def app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['VAPID_PRIVATE_KEY'] = 'test-key'
        app.config['VAPID_SUBJECT'] = 'mailto:test@test.com'
        return app
    
    @pytest.fixture
    def pwa_manager(self, app):
        return PWAManager(app)
    
    def test_install_prompt_logging(self, app, pwa_manager):
        """Тест логирования установки PWA"""
        with app.test_client() as client:
            response = client.post('/pwa/install-prompt')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] == True
    
    def test_subscription_handling(self, app, pwa_manager):
        """Тест обработки push подписок"""
        subscription_data = {
            'endpoint': 'https://test.endpoint.com',
            'keys': {
                'p256dh': 'test-key',
                'auth': 'test-auth'
            }
        }
        
        with app.test_client() as client:
            # Тест создания подписки
            response = client.post('/pwa/subscription',
                                 json=subscription_data,
                                 content_type='application/json')
            
            assert response.status_code == 200
            
            # Тест удаления подписки
            response = client.delete('/pwa/subscription',
                                   json=subscription_data,
                                   content_type='application/json')
            
            assert response.status_code == 200


class TestMobileContentOptimizer:
    """Тесты оптимизатора контента"""
    
    @pytest.fixture
    def app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def optimizer(self, app):
        return MobileContentOptimizer(app)
    
    def test_mobile_truncate(self, optimizer):
        """Тест обрезки текста для мобильных"""
        long_text = "This is a very long text that needs to be truncated for mobile display"
        
        # Мобильный режим - короче
        mobile_result = optimizer.mobile_truncate(long_text, 'mobile', 'text')
        desktop_result = optimizer.mobile_truncate(long_text, 'desktop', 'text')
        
        assert len(mobile_result) < len(desktop_result)
        assert mobile_result.endswith('...')
    
    def test_mobile_format_number(self, optimizer):
        """Тест форматирования чисел"""
        # Большие числа сокращаются на мобильных
        result = optimizer.mobile_format_number(1500000, 'mobile')
        assert 'M' in result or 'K' in result
        
        # На десктопе остаются полными
        result = optimizer.mobile_format_number(1500000, 'desktop')
        assert ',' in result  # Разделители тысяч
    
    def test_mobile_time_ago(self, optimizer):
        """Тест форматирования времени"""
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        
        # Мобильный формат короче
        mobile_result = optimizer.mobile_time_ago(hour_ago, 'mobile')
        desktop_result = optimizer.mobile_time_ago(hour_ago, 'desktop')
        
        assert len(mobile_result) < len(desktop_result)
        assert 'ч' in mobile_result  # Сокращение
        assert 'час' in desktop_result  # Полное слово
    
    def test_optimize_content_for_device(self, optimizer):
        """Тест оптимизации контента"""
        content = {
            'title': 'Very long title that should be truncated for mobile devices',
            'description': 'Long description that needs optimization for different screen sizes',
            'items': list(range(20))  # 20 элементов
        }
        
        # Мобильная оптимизация
        mobile_optimized = optimizer.optimize_content_for_device(content, 'mobile')
        
        # Проверяем, что контент обрезан
        assert len(mobile_optimized['title']) < len(content['title'])
        assert len(mobile_optimized['items']) < len(content['items'])
        
        # Десктопная версия длиннее
        desktop_optimized = optimizer.optimize_content_for_device(content, 'desktop')
        assert len(desktop_optimized['title']) >= len(mobile_optimized['title'])


class TestMobilePerformanceMonitor:
    """Тесты монитора производительности"""
    
    @pytest.fixture
    def app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def monitor(self, app):
        return MobilePerformanceMonitor(app)
    
    def test_web_vitals_validation(self, monitor):
        """Тест валидации Core Web Vitals"""
        valid_data = {
            'largestContentfulPaint': 1200.5,
            'firstContentfulPaint': 800.0,
            'cumulativeLayoutShift': 0.05,
            'firstInputDelay': 50.0,
            'timeToFirstByte': 200.0,
            'userAgent': 'test-agent',
            'viewport': {'width': 375, 'height': 667},
            'connection': '4g'
        }
        
        result = monitor.validate_web_vitals(valid_data)
        assert result is not None
        assert result['lcp'] == 1200.5
        
        # Невалидные данные
        invalid_data = {'largestContentfulPaint': 'invalid'}
        result = monitor.validate_web_vitals(invalid_data)
        assert result is None
    
    def test_performance_api_endpoint(self, app, monitor):
        """Тест API эндпоинта производительности"""
        valid_metrics = {
            'largestContentfulPaint': 1500,
            'firstContentfulPaint': 900,
            'cumulativeLayoutShift': 0.1,
            'userAgent': 'Mozilla/5.0 (iPhone)'
        }
        
        with app.test_client() as client:
            response = client.post('/api/mobile-performance',
                                 json=valid_metrics,
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] == True


class TestMobileConfig:
    """Тесты конфигурации мобильной системы"""
    
    def test_config_validation(self):
        """Тест валидации конфигурации"""
        # Валидная конфигурация не должна возвращать ошибки
        errors = MobileConfig.validate_config()
        assert isinstance(errors, list)
    
    def test_cache_key_generation(self):
        """Тест генерации ключей кэша"""
        key = MobileConfig.get_cache_key('device', 'user123')
        assert 'device:user123' in key
    
    def test_feature_flags(self):
        """Тест feature flags"""
        # По умолчанию offline_mode должен быть включен
        assert MobileConfig.is_feature_enabled('offline_mode') == True
    
    def test_ab_test_variant(self):
        """Тест A/B тестирования"""
        # Должен возвращать один из вариантов
        variant = MobileConfig.get_ab_test_variant('mobile_navigation', 'user123')
        
        if variant is not None:  # Если тест включен
            assert variant in ['bottom_nav', 'sidebar_nav']
    
    def test_image_size_config(self):
        """Тест конфигурации размеров изображений"""
        mobile_config = MobileConfig.get_image_size_config('mobile')
        assert 'width' in mobile_config
        assert 'quality' in mobile_config
        
        desktop_config = MobileConfig.get_image_size_config('desktop')
        assert desktop_config['width'] > mobile_config['width']
    
    def test_content_limits(self):
        """Тест лимитов контента"""
        mobile_limit = MobileConfig.get_content_limit('title', 'mobile')
        desktop_limit = MobileConfig.get_content_limit('title', 'desktop')
        
        assert desktop_limit > mobile_limit


class TestMobileIntegration:
    """Интеграционные тесты мобильной системы"""
    
    @pytest.fixture
    def app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # Инициализируем мобильную систему
        from mobile_integration import init_mobile_integration
        from utils.mobile_helpers import init_mobile_helpers
        
        init_mobile_integration(app)
        init_mobile_helpers(app)
        
        return app
    
    def test_mobile_route_detection(self, app):
        """Тест определения мобильных устройств в роутах"""
        @app.route('/test')
        def test_route():
            detector = get_mobile_detector()
            return f"Mobile: {detector.is_mobile}"
        
        with app.test_client() as client:
            # Мобильный запрос
            response = client.get('/test', headers={'User-Agent': 'iPhone'})
            assert b'Mobile: True' in response.data
            
            # Десктопный запрос
            response = client.get('/test', headers={'User-Agent': 'Windows Chrome'})
            assert b'Mobile: False' in response.data
    
    def test_template_context_variables(self, app):
        """Тест переменных контекста в шаблонах"""
        @app.route('/template-test')
        def template_test():
            from mobile_integration import render_adaptive_template
            return render_adaptive_template('test.html', test_var='test')
        
        with app.test_client() as client:
            # Проверяем, что мобильные переменные добавляются в контекст
            with patch('mobile_integration.render_template') as mock_render:
                mock_render.return_value = "rendered"
                
                client.get('/template-test', headers={'User-Agent': 'iPhone'})
                
                # Проверяем, что вызов включает мобильные переменные
                args, kwargs = mock_render.call_args
                assert 'is_mobile' in kwargs
                assert 'device_type' in kwargs
    
    def test_offline_functionality(self, app):
        """Тест оффлайн функциональности"""
        with app.test_client() as client:
            # Проверяем, что Service Worker доступен
            response = client.get('/sw.js')
            assert response.status_code == 200
            
            # Проверяем, что манифест доступен
            response = client.get('/manifest.json')
            assert response.status_code == 200
    
    def test_mobile_api_endpoints(self, app):
        """Тест мобильных API эндпоинтов"""
        with app.test_client() as client:
            # Тест информации об устройстве
            response = client.get('/mobile-api/device-info')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'is_mobile' in data
            assert 'device_type' in data


class TestMobileImageProcessor:
    """Тесты процессора изображений"""
    
    @pytest.fixture
    def processor(self):
        return MobileImageProcessor()
    
    def test_image_size_generation(self, processor):
        """Тест генерации разных размеров изображений"""
        # Мокаем PIL Image
        with patch('utils.mobile_helpers.Image') as mock_image:
            mock_img = MagicMock()
            mock_img.size = (1920, 1080)
            mock_image.open.return_value.__enter__.return_value = mock_img
            
            # Мокаем os.path функции
            with patch('os.path.join') as mock_join, \
                 patch('os.path.basename') as mock_basename, \
                 patch('os.path.splitext') as mock_splitext:
                
                mock_basename.return_value = 'test.jpg'
                mock_splitext.return_value = ('test', '.jpg')
                mock_join.return_value = 'processed/test.jpg'
                
                sizes = {'small': {'width': 320, 'quality': 75}}
                result = processor.process_image_for_mobile('/test/image.jpg', sizes)
                
                # Должен вернуть словарь с обработанными изображениями
                assert isinstance(result, dict)
    
    def test_responsive_image_html_generation(self, processor):
        """Тест генерации HTML для responsive изображений"""
        html = processor.generate_responsive_image_html(
            '/images/test.jpg', 
            'Test image',
            'mobile-image'
        )
        
        assert '<picture' in html
        assert 'srcset' in html
        assert 'loading="lazy"' in html
        assert 'Test image' in html


# Pytest fixtures для всех тестов
@pytest.fixture(scope="session")
def app():
    """Создает тестовое приложение Flask"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    return app


@pytest.fixture
def client(app):
    """Создает тестовый клиент"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Создает CLI runner"""
    return app.test_cli_runner()


# Тесты производительности
@pytest.mark.performance
class TestMobilePerformance:
    """Тесты производительности мобильной системы"""
    
    def test_mobile_detection_speed(self):
        """Тест скорости определения мобильных устройств"""
        import time
        
        ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
        
        start_time = time.time()
        for _ in range(1000):
            detector = MobileDetector(ua)
            detector.is_mobile
        end_time = time.time()
        
        # Должно обрабатываться быстро (менее 1 секунды на 1000 запросов)
        assert (end_time - start_time) < 1.0
    
    def test_template_selection_speed(self, app):
        """Тест скорости выбора шаблонов"""
        import time
        
        manager = MobileTemplateManager()
        manager.register_mobile_template('test.html', 'test_mobile.html')
        
        with app.test_request_context(headers={'User-Agent': 'iPhone'}):
            start_time = time.time()
            for _ in range(1000):
                manager.get_appropriate_template('test.html')
            end_time = time.time()
            
            # Выбор шаблона должен быть быстрым
            assert (end_time - start_time) < 0.5


# Маркеры для pytest
pytestmark = [
    pytest.mark.mobile,  # Все тесты относятся к мобильной системе
]


if __name__ == '__main__':
    # Запуск тестов напрямую
    pytest.main([__file__, '-v', '--tb=short'])