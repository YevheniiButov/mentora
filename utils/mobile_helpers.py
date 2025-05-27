# utils/mobile_helpers.py
"""
Mobile helpers and utilities for Dental Academy
Дополнительные утилиты для мобильной системы
"""

import os
import json
import hashlib
import base64
from datetime import datetime, timedelta
from flask import request, session, current_app, g, url_for
from PIL import Image, ImageOps
from io import BytesIO
import requests
from typing import Dict, List, Optional, Tuple, Union


class PWAManager:
    """Менеджер PWA функций"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Инициализация PWA для Flask приложения"""
        self.app = app
        
        # Регистрируем маршруты PWA
        app.add_url_rule('/pwa/install-prompt', 'pwa_install_prompt', 
                        self.install_prompt, methods=['POST'])
        app.add_url_rule('/pwa/subscription', 'pwa_subscription', 
                        self.handle_subscription, methods=['POST', 'DELETE'])
        app.add_url_rule('/pwa/send-notification', 'pwa_send_notification',
                        self.send_notification, methods=['POST'])
    
    def install_prompt(self):
        """Обработка запроса на установку PWA"""
        from flask import jsonify
        
        # Логируем установку PWA
        user_agent = request.headers.get('User-Agent', '')
        ip_address = request.remote_addr
        
        current_app.logger.info(f"PWA install prompt: UA={user_agent}, IP={ip_address}")
        
        # Сохраняем статистику установок
        self.track_install_event()
        
        return jsonify({
            'success': True,
            'message': 'Install prompt logged'
        })
    
    def handle_subscription(self):
        """Обработка push подписок"""
        from flask import jsonify
        
        if request.method == 'POST':
            # Новая подписка
            subscription_data = request.get_json()
            
            if not subscription_data:
                return jsonify({'error': 'No subscription data'}), 400
            
            # Сохраняем подписку в базе данных
            success = self.save_push_subscription(subscription_data)
            
            if success:
                return jsonify({'success': True})
            else:
                return jsonify({'error': 'Failed to save subscription'}), 500
        
        elif request.method == 'DELETE':
            # Отписка
            subscription_data = request.get_json()
            success = self.remove_push_subscription(subscription_data)
            
            return jsonify({'success': success})
    
    def send_notification(self):
        """Отправка push уведомления"""
        from flask import jsonify
        from pywebpush import webpush, WebPushException
        
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message required'}), 400
        
        # Получаем подписки пользователей
        subscriptions = self.get_push_subscriptions(data.get('user_ids', []))
        
        success_count = 0
        error_count = 0
        
        for subscription in subscriptions:
            try:
                webpush(
                    subscription_info=subscription['subscription'],
                    data=json.dumps(data['message']),
                    vapid_private_key=current_app.config.get('VAPID_PRIVATE_KEY'),
                    vapid_claims={
                        'sub': current_app.config.get('VAPID_SUBJECT')
                    }
                )
                success_count += 1
            except WebPushException as e:
                current_app.logger.error(f"Push notification failed: {e}")
                error_count += 1
                
                # Удаляем недействительные подписки
                if e.response and e.response.status_code in [410, 413, 429]:
                    self.remove_push_subscription(subscription['subscription'])
        
        return jsonify({
            'success': True,
            'sent': success_count,
            'failed': error_count
        })
    
    def save_push_subscription(self, subscription_data):
        """Сохраняет push подписку в базе данных"""
        try:
            # Здесь должна быть логика сохранения в БД
            # Пример структуры данных:
            subscription_record = {
                'user_id': getattr(g, 'user', {}).get('id'),
                'endpoint': subscription_data.get('endpoint'),
                'keys': subscription_data.get('keys', {}),
                'created_at': datetime.utcnow(),
                'user_agent': request.headers.get('User-Agent'),
                'ip_address': request.remote_addr
            }
            
            # TODO: Сохранить в БД
            current_app.logger.info(f"Push subscription saved: {subscription_record}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Failed to save push subscription: {e}")
            return False
    
    def remove_push_subscription(self, subscription_data):
        """Удаляет push подписку"""
        try:
            endpoint = subscription_data.get('endpoint')
            # TODO: Удалить из БД по endpoint
            current_app.logger.info(f"Push subscription removed: {endpoint}")
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to remove push subscription: {e}")
            return False
    
    def get_push_subscriptions(self, user_ids=None):
        """Получает push подписки пользователей"""
        # TODO: Получить из БД
        # Пример структуры:
        return [
            {
                'user_id': 1,
                'subscription': {
                    'endpoint': 'https://example.com/endpoint',
                    'keys': {
                        'p256dh': 'key1',
                        'auth': 'key2'
                    }
                }
            }
        ]
    
    def track_install_event(self):
        """Отслеживает события установки PWA"""
        install_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_agent': request.headers.get('User-Agent'),
            'referrer': request.headers.get('Referer'),
            'ip_address': request.remote_addr,
            'user_id': getattr(g, 'user', {}).get('id')
        }
        
        # Сохраняем в аналитику
        current_app.logger.info(f"PWA install tracked: {install_data}")


class MobileImageProcessor:
    """Процессор изображений для мобильных устройств"""
    
    def __init__(self, app=None):
        self.app = app
        self.upload_folder = None
        self.allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        self.upload_folder = app.config.get('UPLOAD_FOLDER', 'static/uploads')
        
        # Создаем директории для разных размеров
        for size in ['small', 'medium', 'large']:
            os.makedirs(os.path.join(self.upload_folder, size), exist_ok=True)
    
    def process_image_for_mobile(self, image_path: str, 
                               sizes: Dict[str, Dict] = None) -> Dict[str, str]:
        """
        Обрабатывает изображение для разных размеров экранов
        
        Args:
            image_path: Путь к исходному изображению
            sizes: Словарь с размерами {size_name: {width, height, quality}}
            
        Returns:
            Словарь с путями к обработанным изображениям
        """
        if sizes is None:
            sizes = {
                'small': {'width': 320, 'quality': 75},
                'medium': {'width': 768, 'quality': 80},
                'large': {'width': 1024, 'quality': 85}
            }
        
        processed_images = {}
        
        try:
            with Image.open(image_path) as img:
                # Исправляем ориентацию на основе EXIF
                img = ImageOps.exif_transpose(img)
                
                # Конвертируем в RGB если нужно
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                original_width, original_height = img.size
                
                for size_name, config in sizes.items():
                    target_width = config['width']
                    quality = config.get('quality', 80)
                    
                    # Вычисляем пропорциональную высоту
                    aspect_ratio = original_height / original_width
                    target_height = int(target_width * aspect_ratio)
                    
                    # Изменяем размер
                    resized_img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                    
                    # Генерируем имя файла
                    base_name = os.path.splitext(os.path.basename(image_path))[0]
                    output_filename = f"{base_name}_{size_name}.jpg"
                    output_path = os.path.join(self.upload_folder, size_name, output_filename)
                    
                    # Сохраняем с оптимизацией
                    resized_img.save(output_path, 'JPEG', 
                                   quality=quality, 
                                   optimize=True,
                                   progressive=True)
                    
                    # Добавляем в результат
                    processed_images[size_name] = url_for('static', 
                                                        filename=f'uploads/{size_name}/{output_filename}')
                
        except Exception as e:
            current_app.logger.error(f"Image processing failed: {e}")
            
        return processed_images
    
    def create_webp_versions(self, image_path: str) -> str:
        """Создает WebP версию изображения"""
        try:
            with Image.open(image_path) as img:
                img = ImageOps.exif_transpose(img)
                
                # WebP путь
                base_name = os.path.splitext(image_path)[0]
                webp_path = f"{base_name}.webp"
                
                # Сохраняем в WebP с высоким качеством
                img.save(webp_path, 'WebP', quality=85, method=6)
                
                return webp_path
                
        except Exception as e:
            current_app.logger.error(f"WebP conversion failed: {e}")
            return image_path
    
    def generate_responsive_image_html(self, base_image_url: str, 
                                     alt_text: str = '',
                                     css_classes: str = '') -> str:
        """Генерирует HTML для responsive изображения"""
        sizes_config = "(max-width: 480px) 320px, (max-width: 768px) 768px, 1024px"
        
        # Генерируем srcset
        srcset_parts = []
        for size in ['small', 'medium', 'large']:
            size_url = base_image_url.replace('.jpg', f'_{size}.jpg')
            width = {'small': 320, 'medium': 768, 'large': 1024}[size]
            srcset_parts.append(f"{size_url} {width}w")
        
        srcset = ', '.join(srcset_parts)
        
        return f'''
        <picture class="{css_classes}">
            <source srcset="{base_image_url.replace('.jpg', '.webp')}" type="image/webp">
            <img src="{base_image_url}" 
                 srcset="{srcset}"
                 sizes="{sizes_config}"
                 alt="{alt_text}"
                 loading="lazy"
                 decoding="async">
        </picture>
        '''


class MobilePerformanceMonitor:
    """Монитор производительности для мобильных устройств"""
    
    def __init__(self, app=None):
        self.app = app
        self.metrics_storage = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        
        # Добавляем middleware для измерения времени ответа
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Регистрируем API для получения метрик
        app.add_url_rule('/api/mobile-performance', 'mobile_performance',
                        self.handle_performance_data, methods=['POST'])
    
    def before_request(self):
        """Вызывается перед каждым запросом"""
        g.start_time = datetime.utcnow()
        g.request_id = self.generate_request_id()
    
    def after_request(self, response):
        """Вызывается после каждого запроса"""
        if hasattr(g, 'start_time'):
            response_time = (datetime.utcnow() - g.start_time).total_seconds() * 1000
            
            # Сохраняем метрики только для мобильных устройств
            from utils.mobile_detection import get_mobile_detector
            detector = get_mobile_detector()
            
            if detector.is_mobile_device:
                self.record_request_metrics({
                    'request_id': getattr(g, 'request_id', ''),
                    'response_time': response_time,
                    'status_code': response.status_code,
                    'path': request.path,
                    'method': request.method,
                    'device_type': detector.device_type,
                    'user_agent': request.headers.get('User-Agent', ''),
                    'timestamp': g.start_time.isoformat()
                })
        
        return response
    
    def handle_performance_data(self):
        """Обрабатывает данные о производительности от клиента"""
        from flask import jsonify
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Валидируем Core Web Vitals
        metrics = self.validate_web_vitals(data)
        
        if metrics:
            self.record_client_metrics(metrics)
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Invalid metrics data'}), 400
    
    def validate_web_vitals(self, data: Dict) -> Optional[Dict]:
        """Валидирует метрики Core Web Vitals"""
        try:
            metrics = {
                'lcp': float(data.get('largestContentfulPaint', 0)),
                'fcp': float(data.get('firstContentfulPaint', 0)),
                'cls': float(data.get('cumulativeLayoutShift', 0)),
                'fid': float(data.get('firstInputDelay', 0)),
                'ttfb': float(data.get('timeToFirstByte', 0)),
                'user_agent': data.get('userAgent', ''),
                'viewport': data.get('viewport', {}),
                'connection': data.get('connection', ''),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Проверяем разумные границы
            if 0 <= metrics['lcp'] <= 10000 and 0 <= metrics['cls'] <= 1:
                return metrics
            
        except (ValueError, TypeError):
            pass
        
        return None
    
    def record_request_metrics(self, metrics: Dict):
        """Записывает метрики запроса"""
        current_app.logger.info(f"Mobile request metrics: {metrics}")
        
        # В реальном приложении здесь была бы отправка в аналитику
        # Например, в InfluxDB, CloudWatch, или другую систему мониторинга
    
    def record_client_metrics(self, metrics: Dict):
        """Записывает клиентские метрики"""
        current_app.logger.info(f"Mobile client metrics: {metrics}")
    
    def generate_request_id(self) -> str:
        """Генерирует уникальный ID запроса"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def get_performance_summary(self, time_period: timedelta = None) -> Dict:
        """Возвращает сводку по производительности"""
        if time_period is None:
            time_period = timedelta(hours=24)
        
        # В реальном приложении здесь был бы запрос к БД/аналитике
        return {
            'avg_response_time': 250.5,
            'p95_response_time': 450.0,
            'error_rate': 0.02,
            'avg_lcp': 1200.0,
            'avg_fcp': 800.0,
            'avg_cls': 0.05,
            'mobile_traffic_percentage': 65.3,
            'period': f"Last {time_period.total_seconds() / 3600:.0f} hours"
        }


class MobileContentOptimizer:
    """Оптимизатор контента для мобильных устройств"""
    
    def __init__(self, app=None):
        self.app = app
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        
        # Регистрируем Jinja2 фильтры
        app.jinja_env.filters['mobile_truncate'] = self.mobile_truncate
        app.jinja_env.filters['mobile_format_number'] = self.mobile_format_number
        app.jinja_env.filters['mobile_time_ago'] = self.mobile_time_ago
    
    def mobile_truncate(self, text: str, device_type: str = None, 
                       content_type: str = 'text') -> str:
        """
        Обрезает текст в зависимости от типа устройства
        
        Args:
            text: Исходный текст
            device_type: Тип устройства ('mobile', 'tablet', 'desktop')
            content_type: Тип контента ('title', 'description', 'text')
        """
        if not text:
            return text
        
        if device_type is None:
            from utils.mobile_detection import get_mobile_detector
            device_type = get_mobile_detector().device_type
        
        # Лимиты символов для разных типов контента и устройств
        limits = {
            'mobile': {'title': 30, 'description': 80, 'text': 150},
            'tablet': {'title': 45, 'description': 120, 'text': 200},
            'desktop': {'title': 80, 'description': 200, 'text': 400}
        }
        
        limit = limits.get(device_type, limits['mobile']).get(content_type, 150)
        
        if len(text) <= limit:
            return text
        
        # Обрезаем по словам, а не по символам
        words = text.split()
        truncated = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > limit - 3:  # -3 для "..."
                break
            truncated.append(word)
            current_length += len(word) + 1
        
        return ' '.join(truncated) + '...' if truncated else text[:limit-3] + '...'
    
    def mobile_format_number(self, number: Union[int, float], 
                           device_type: str = None) -> str:
        """Форматирует числа для мобильных устройств"""
        if not isinstance(number, (int, float)):
            return str(number)
        
        if device_type is None:
            from utils.mobile_detection import get_mobile_detector
            device_type = get_mobile_detector().device_type
        
        # На мобильных используем сокращения
        if device_type == 'mobile':
            if number >= 1000000:
                return f"{number/1000000:.1f}M"
            elif number >= 1000:
                return f"{number/1000:.1f}K"
        
        return f"{number:,}"
    
    def mobile_time_ago(self, timestamp: datetime, 
                       device_type: str = None) -> str:
        """Форматирует время в удобном для мобильных формате"""
        if not isinstance(timestamp, datetime):
            return str(timestamp)
        
        now = datetime.utcnow()
        diff = now - timestamp
        
        if device_type == 'mobile':
            # Короткие форматы для мобильных
            if diff.days > 7:
                return timestamp.strftime('%d.%m')
            elif diff.days > 0:
                return f"{diff.days}д"
            elif diff.seconds > 3600:
                return f"{diff.seconds // 3600}ч"
            elif diff.seconds > 60:
                return f"{diff.seconds // 60}м"
            else:
                return "сейчас"
        else:
            # Полные форматы для больших экранов
            if diff.days > 7:
                return timestamp.strftime('%d %B %Y')
            elif diff.days > 0:
                return f"{diff.days} дней назад"
            elif diff.seconds > 3600:
                return f"{diff.seconds // 3600} часов назад"
            elif diff.seconds > 60:
                return f"{diff.seconds // 60} минут назад"
            else:
                return "только что"
    
    def optimize_content_for_device(self, content: Dict, 
                                  device_type: str = None) -> Dict:
        """Оптимизирует весь контент для устройства"""
        if device_type is None:
            from utils.mobile_detection import get_mobile_detector
            device_type = get_mobile_detector().device_type
        
        optimized = content.copy()
        
        # Оптимизируем текстовые поля
        text_fields = ['title', 'description', 'content', 'summary']
        for field in text_fields:
            if field in optimized:
                content_type = 'title' if field == 'title' else 'text'
                optimized[field] = self.mobile_truncate(
                    optimized[field], device_type, content_type
                )
        
        # Оптимизируем списки (ограничиваем количество элементов)
        list_limits = {'mobile': 3, 'tablet': 5, 'desktop': 10}
        limit = list_limits.get(device_type, 5)
        
        list_fields = ['items', 'options', 'recommendations', 'features']
        for field in list_fields:
            if field in optimized and isinstance(optimized[field], list):
                optimized[field] = optimized[field][:limit]
        
        return optimized


class MobileSecurityHelper:
    """Помощник безопасности для мобильных устройств"""
    
    @staticmethod
    def generate_csp_header(device_type: str = None) -> str:
        """Генерирует Content Security Policy для мобильных"""
        from config.mobile_config import MobileConfig
        
        if device_type == 'mobile':
            # Более строгая политика для мобильных
            policy_parts = []
            for directive, value in MobileConfig.MOBILE_CSP_POLICY.items():
                policy_parts.append(f"{directive} {value}")
            
            return '; '.join(policy_parts)
        
        # Стандартная политика для других устройств
        return "default-src 'self'; script-src 'self' 'unsafe-inline'"
    
    @staticmethod
    def validate_mobile_request() -> bool:
        """Валидирует мобильный запрос на безопасность"""
        # Проверяем подозрительные заголовки
        suspicious_headers = [
            'X-Forwarded-Host',
            'X-Original-URL',
            'X-Rewrite-URL'
        ]
        
        for header in suspicious_headers:
            if header in request.headers:
                current_app.logger.warning(f"Suspicious header detected: {header}")
                return False
        
        # Проверяем User-Agent на подозрительные паттерны
        user_agent = request.headers.get('User-Agent', '')
        suspicious_patterns = ['bot', 'crawler', 'spider', 'scraper']
        
        if any(pattern in user_agent.lower() for pattern in suspicious_patterns):
            return False
        
        return True
    
    @staticmethod
    def rate_limit_key(prefix: str = 'mobile') -> str:
        """Генерирует ключ для rate limiting"""
        user_id = getattr(g, 'user', {}).get('id', 'anonymous')
        ip_address = request.remote_addr
        
        # Используем комбинацию user_id и IP для более точного ограничения
        key_data = f"{prefix}:{user_id}:{ip_address}"
        return hashlib.md5(key_data.encode()).hexdigest()


# Глобальные экземпляры
pwa_manager = PWAManager()
image_processor = MobileImageProcessor()
performance_monitor = MobilePerformanceMonitor()
content_optimizer = MobileContentOptimizer()


def init_mobile_helpers(app):
    """Инициализирует все мобильные хелперы"""
    pwa_manager.init_app(app)
    image_processor.init_app(app)
    performance_monitor.init_app(app)
    content_optimizer.init_app(app)
    
    app.logger.info("Mobile helpers initialized successfully")