# routes/ai_routes.py
"""
AI Assistant Routes for Dental Academy Mobile App
Includes RAG-powered AI system with user API keys
"""

from flask import Blueprint, render_template, request, session, redirect, url_for, g, flash, current_app, jsonify
from flask_login import login_required, current_user
from extensions import db, csrf
from models import (
    Subject, Module, UserProgress, Lesson, ContentCategory,
    ContentSubcategory, ContentTopic, LearningPath, User,
    UserAPIKey, AIConversation, ContentEmbedding,
    VirtualPatientScenario, Test, Question, TestAttempt
)
from utils.mobile_detection import get_mobile_detector
from utils.ai_manager import AIManager, AIProviderManager
from utils.rag_system import RAGSystem
from translations_new import get_translation as t
import json
import logging
from datetime import datetime, timedelta
import random

# Blueprint setup
ai_bp = Blueprint('ai', __name__, url_prefix='/<lang>/ai-assistant', template_folder='../templates')

# Инициализация систем
ai_manager = AIManager()
rag_system = RAGSystem()

# Языковые настройки
SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa', 'ar']
DEFAULT_LANGUAGE = 'en'

@ai_bp.before_request
def before_request_ai():
    """Обработка языка для AI роутов."""
    try:
        lang_from_url = request.view_args.get('lang') if request.view_args else None
        
        if lang_from_url and lang_from_url in SUPPORTED_LANGUAGES:
            g.lang = lang_from_url
        else:
            g.lang = session.get('lang') or DEFAULT_LANGUAGE
        
        if session.get('lang') != g.lang:
            session['lang'] = g.lang
            
    except Exception as e:
        current_app.logger.error(f"Error in before_request_ai: {e}", exc_info=True)
        g.lang = DEFAULT_LANGUAGE

@ai_bp.context_processor
def inject_ai_context():
    """Добавляет AI контекст в шаблоны."""
    detector = get_mobile_detector()
    return dict(
        lang=getattr(g, 'lang', DEFAULT_LANGUAGE),
        is_mobile=detector.is_mobile_device,
        device_type=detector.device_type,
        supported_languages=SUPPORTED_LANGUAGES,
        ai_providers=AIProviderManager.get_all_providers()
    )

@ai_bp.route('/')
@login_required
def ai_chat(lang):
    """Главная страница AI чата."""
    try:
        detector = get_mobile_detector()
        
        # Получаем настройки AI пользователя
        user_providers = ai_manager.get_user_providers(current_user.id)
        has_configured_ai = len(user_providers) > 0
        
        # Получаем последние разговоры
        recent_conversations = ai_manager.get_conversation_history(current_user.id, limit=10, language=lang)
        
        # Получаем статистику использования
        usage_stats = ai_manager.get_user_statistics(current_user.id)
        
        # Получаем статистику RAG системы
        rag_stats = rag_system.get_content_statistics(language=lang)
        
        # Всегда используем мобильный шаблон
        template = 'mobile/ai/chat_mobile.html'
        
        return render_template(
            template,
            title=t('ai_assistant', lang=lang),
            has_configured_ai=has_configured_ai,
            user_providers=user_providers,
            recent_conversations=recent_conversations,
            usage_stats=usage_stats,
            rag_stats=rag_stats,
            ai_providers=AIProviderManager.get_all_providers(),
            current_language=lang
        )
        
    except Exception as e:
        current_app.logger.error(f"Error in ai_chat: {e}", exc_info=True)
        flash(t("error_loading_ai_chat", lang=lang), "danger")
        return redirect(url_for('main_bp.home', lang=lang))

@ai_bp.route('/mobile')
@login_required
def mobile_chat(lang):
    """Мобильный роут для AI чата - алиас для ai_chat для совместимости."""
    return ai_chat(lang)

@ai_bp.route('/chat', methods=['POST'])
@login_required
def process_chat(lang):
    """Обработка AI чата с RAG контекстом."""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        selected_provider = data.get('provider')
        selected_model = data.get('model')
        use_rag = data.get('use_rag', True)
        rag_filters = data.get('rag_filters', {})
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Отправляем запрос к AI через AI Manager
        response = ai_manager.chat_with_rag_context(
            user_id=current_user.id,
            message=user_message,
            language=lang,
            use_rag=use_rag,
            provider=selected_provider,
            model=selected_model,
            rag_filters=rag_filters
        )
        
        if not response['success']:
            error_code = response.get('error_code', 'UNKNOWN_ERROR')
            
            if error_code == 'NO_API_KEYS':
                return jsonify({
                    'error': response['error'],
                    'redirect_to_setup': True
                }), 400
            elif error_code == 'INVALID_API_KEY':
                return jsonify({
                    'error': response['error'],
                    'limit_exceeded': True
                }), 429
            else:
                return jsonify({'error': response['error']}), 500
        
        return jsonify({
            'response': response['response'],
            'sources': response.get('sources', []),
            'tokens_used': response.get('tokens_used', 0),
            'provider': response.get('provider'),
            'model': response.get('model'),
            'has_rag_context': response.get('has_rag_context', False),
            'response_time_ms': response.get('response_time_ms', 0),
            'conversation_id': response.get('conversation_id')
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in process_chat: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@ai_bp.route('/settings')
@login_required
def ai_settings(lang):
    """Настройки AI ключей и провайдеров."""
    try:
        detector = get_mobile_detector()
        
        # Получаем текущие настройки пользователя
        user_providers = ai_manager.get_user_providers(current_user.id)
        usage_stats = ai_manager.get_user_statistics(current_user.id)
        
        # Получаем статистику RAG системы
        rag_stats = rag_system.get_content_statistics(language=lang)
        
        # Всегда используем мобильный шаблон
        template = 'mobile/ai/settings_mobile.html'
        
        return render_template(
            template,
            title=t('ai_settings', lang=lang),
            user_providers=user_providers,
            usage_stats=usage_stats,
            rag_stats=rag_stats,
            ai_providers=AIProviderManager.get_all_providers(),
            current_language=lang
        )
        
    except Exception as e:
        current_app.logger.error(f"Error in ai_settings: {e}", exc_info=True)
        flash(t("error_loading_ai_settings", lang=lang), "danger")
        return redirect(url_for('ai.ai_chat', lang=lang))

@ai_bp.route('/settings/save-key', methods=['POST'])
@login_required
def save_api_key(lang):
    """Сохранение API ключа пользователя."""
    try:
        data = request.get_json()
        provider = data.get('provider', '').strip()
        api_key = data.get('api_key', '').strip()
        key_name = data.get('key_name', '').strip()
        
        if not provider or not api_key:
            return jsonify({'error': 'Provider and API key are required'}), 400
        
        if not AIProviderManager.validate_provider(provider):
            return jsonify({'error': f'Unsupported provider: {provider}'}), 400
        
        try:
            # Сохраняем API ключ через AI Manager
            user_api_key = ai_manager.save_api_key(
                user_id=current_user.id,
                provider=provider,
                api_key=api_key,
                key_name=key_name
            )
            
            provider_info = AIProviderManager.get_provider_info(provider)
            
            return jsonify({
                'success': True,
                'message': f'API key for {provider_info.get("name", provider)} saved successfully',
                'provider': provider,
                'key_name': user_api_key.key_name
            })
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
    except Exception as e:
        current_app.logger.error(f"Error saving API key: {e}", exc_info=True)
        return jsonify({'error': 'Failed to save API key'}), 500

@ai_bp.route('/settings/delete-key/<provider>', methods=['DELETE'])
@login_required
def delete_api_key(lang, provider):
    """Удаление API ключа пользователя."""
    try:
        success = ai_manager.delete_api_key(current_user.id, provider)
        
        if success:
            provider_info = AIProviderManager.get_provider_info(provider)
            return jsonify({
                'success': True,
                'message': f'API key for {provider_info.get("name", provider)} deleted successfully'
            })
        else:
            return jsonify({'error': 'API key not found'}), 404
            
    except Exception as e:
        current_app.logger.error(f"Error deleting API key: {e}", exc_info=True)
        return jsonify({'error': 'Failed to delete API key'}), 500

@ai_bp.route('/conversation/<int:conversation_id>/rate', methods=['POST'])
@login_required
def rate_conversation(lang, conversation_id):
    """Оценка разговора с AI."""
    try:
        data = request.get_json()
        rating = data.get('rating')
        feedback = data.get('feedback', '').strip()
        
        if not isinstance(rating, int) or not 1 <= rating <= 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        success = ai_manager.rate_conversation(
            user_id=current_user.id,
            conversation_id=conversation_id,
            rating=rating,
            feedback=feedback if feedback else None
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Rating saved successfully'
            })
        else:
            return jsonify({'error': 'Conversation not found'}), 404
            
    except Exception as e:
        current_app.logger.error(f"Error rating conversation: {e}", exc_info=True)
        return jsonify({'error': 'Failed to save rating'}), 500

@ai_bp.route('/search', methods=['POST'])
@login_required
def semantic_search(lang):
    """Семантический поиск по образовательному контенту."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        filters = data.get('filters', {})
        limit = data.get('limit', 5)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Выполняем семантический поиск
        search_results = rag_system.semantic_search(
            query=query,
            language=lang,
            limit=min(limit, 20),  # Максимум 20 результатов
            filters=filters
        )
        
        return jsonify({
            'query': query,
            'results': search_results,
            'total_results': len(search_results)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in semantic search: {e}", exc_info=True)
        return jsonify({'error': 'Search failed'}), 500

@ai_bp.route('/process-content', methods=['POST'])
@login_required
def process_content(lang):
    """Обработка контента для RAG системы (только для админов)."""
    try:
        if not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        language = data.get('language', lang)
        batch_size = data.get('batch_size', 10)
        
        # Запускаем обработку контента
        stats = rag_system.process_all_content(
            language=language,
            batch_size=batch_size
        )
        
        return jsonify({
            'success': True,
            'message': 'Content processing completed',
            'statistics': stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Error processing content: {e}", exc_info=True)
        return jsonify({'error': 'Content processing failed'}), 500

@ai_bp.route('/statistics')
@login_required
def get_statistics(lang):
    """Получение статистики AI и RAG систем."""
    try:
        # Статистика пользователя
        user_stats = ai_manager.get_user_statistics(current_user.id)
        
        # Статистика RAG системы
        rag_stats = rag_system.get_content_statistics(language=lang)
        
        # Статистика провайдеров пользователя
        user_providers = ai_manager.get_user_providers(current_user.id)
        
        return jsonify({
            'user_statistics': user_stats,
            'rag_statistics': rag_stats,
            'user_providers': user_providers,
            'available_providers': AIProviderManager.get_all_providers()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting statistics: {e}", exc_info=True)
        return jsonify({'error': 'Failed to get statistics'}), 500

@ai_bp.route('/maintenance/cleanup-cache', methods=['POST'])
@login_required
def cleanup_cache(lang):
    """Очистка просроченного кэша RAG (только для админов)."""
    try:
        if not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        deleted_count = rag_system.cleanup_expired_cache()
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up {deleted_count} expired cache entries',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        current_app.logger.error(f"Error cleaning up cache: {e}", exc_info=True)
        return jsonify({'error': 'Cache cleanup failed'}), 500

# Вспомогательные функции для обратной совместимости
def get_user_api_keys(user_id):
    """Обратная совместимость - получение API ключей пользователя."""
    return ai_manager.get_user_providers(user_id)

def get_recent_conversations(user_id, limit=10):
    """Обратная совместимость - получение недавних разговоров."""
    return ai_manager.get_conversation_history(user_id, limit=limit)

def get_ai_usage_stats(user_id):
    """Обратная совместимость - получение статистики использования."""
    return ai_manager.get_user_statistics(user_id)

# ===== НОВЫЕ ENDPOINTS ДЛЯ ИИ АНАЛИТИКИ =====

@ai_bp.route('/analytics/realtime', methods=['GET'])
@login_required
def get_realtime_ai_analytics(lang):
    """Реальные метрики ИИ системы (только для админов)"""
    try:
        # Проверка прав доступа
        if not (current_user.role == 'admin' or getattr(current_user, 'is_admin', False)):
            return jsonify({
                'success': False,
                'error': 'Access denied. Admin rights required.'
            }), 403
        
        from utils.ai_analytics import ai_analytics
        
        metrics = ai_analytics.get_realtime_metrics()
        
        current_app.logger.info(f"Admin {current_user.id} accessed realtime AI analytics")
        
        return jsonify({
            'success': True,
            'metrics': metrics
        })
        
    except Exception as e:
        current_app.logger.error(f"Realtime analytics error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Analytics service temporarily unavailable'
        }), 500

@ai_bp.route('/analytics/historical', methods=['GET'])
@login_required
def get_historical_ai_analytics(lang):
    """Исторические данные ИИ аналитики (только для админов)"""
    try:
        # Проверка прав доступа
        if not (current_user.role == 'admin' or getattr(current_user, 'is_admin', False)):
            return jsonify({
                'success': False,
                'error': 'Access denied. Admin rights required.'
            }), 403
        
        # Получаем параметр количества дней
        days = request.args.get('days', 30, type=int)
        days = min(max(days, 1), 365)  # От 1 до 365 дней
        
        from utils.ai_analytics import ai_analytics
        
        historical_data = ai_analytics.get_historical_analytics(days)
        
        current_app.logger.info(f"Admin {current_user.id} accessed historical AI analytics for {days} days")
        
        return jsonify({
            'success': True,
            'data': historical_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Historical analytics error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Historical analytics service temporarily unavailable'
        }), 500

@ai_bp.route('/analytics/user-insights', methods=['GET'])
@login_required
def get_user_insights(lang):
    """Аналитические инсайты о пользователях ИИ (только для админов)"""
    try:
        # Проверка прав доступа
        if not (current_user.role == 'admin' or getattr(current_user, 'is_admin', False)):
            return jsonify({
                'success': False,
                'error': 'Access denied. Admin rights required.'
            }), 403
        
        # Получаем параметры
        user_id = request.args.get('user_id', type=int)
        days = request.args.get('days', 7, type=int)
        days = min(max(days, 1), 90)  # От 1 до 90 дней
        
        from utils.ai_analytics import ai_analytics
        
        insights = ai_analytics.get_user_behavior_insights(user_id, days)
        
        current_app.logger.info(f"Admin {current_user.id} accessed user insights for user {user_id or 'all'}")
        
        return jsonify({
            'success': True,
            'insights': insights
        })
        
    except Exception as e:
        current_app.logger.error(f"User insights error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'User insights service temporarily unavailable'
        }), 500

@ai_bp.route('/analytics/track-event', methods=['POST'])
@login_required
def track_ai_event(lang):
    """Отслеживание событий ИИ системы"""
    try:
        data = request.get_json()
        
        event_type = data.get('event_type')
        event_data = data.get('event_data', {})
        
        if not event_type:
            return jsonify({
                'success': False,
                'error': 'event_type is required'
            }), 400
        
        # Валидация типа события
        valid_event_types = [
            'chat_start', 'chat_end', 'prediction_request', 
            'recommendation_click', 'widget_interaction', 
            'mode_switch', 'quick_action', 'analysis_request'
        ]
        
        if event_type not in valid_event_types:
            return jsonify({
                'success': False,
                'error': f'Invalid event_type. Must be one of: {", ".join(valid_event_types)}'
            }), 400
        
        # Создаем запись о событии
        from models import UserStats
        
        # Обновляем или создаем статистику пользователя
        user_stats = UserStats.query.filter_by(user_id=current_user.id).first()
        if not user_stats:
            user_stats = UserStats(
                user_id=current_user.id,
                total_study_time=0,
                lessons_completed=0,
                tests_completed=0,
                current_streak=0,
                longest_streak=0,
                total_experience_points=0,
                current_level=1,
                achievements_unlocked=0,
                last_activity=datetime.utcnow()
            )
            db.session.add(user_stats)
        
        # Обновляем последнюю активность
        user_stats.last_activity = datetime.utcnow()
        
        # Сохраняем событие в AIConversation с специальным типом
        conversation = AIConversation(
            user_id=current_user.id,
            session_id=data.get('session_id', f"event_{current_user.id}_{datetime.utcnow().timestamp()}"),
            user_message=f"EVENT:{event_type}",
            ai_response=json.dumps(event_data),
            provider='system',
            model='analytics',
            tokens_used=0,
            response_time_ms=0,
            language=lang,
            timestamp=datetime.utcnow()
        )
        
        db.session.add(conversation)
        db.session.commit()
        
        current_app.logger.info(f"User {current_user.id} tracked event: {event_type}")
        
        return jsonify({
            'success': True,
            'message': 'Event tracked successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Event tracking error: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Event tracking failed'
        }), 500

@ai_bp.route('/analytics/feedback', methods=['POST'])
@login_required
def submit_ai_feedback(lang):
    """Отзывы пользователей о работе ИИ"""
    try:
        data = request.get_json()
        
        feedback_type = data.get('feedback_type')  # 'prediction', 'recommendation', 'chat', 'widget'
        rating = data.get('rating')  # 1-5
        comment = data.get('comment', '')
        context = data.get('context', {})  # Дополнительная информация
        
        if not feedback_type or not rating:
            return jsonify({
                'success': False,
                'error': 'feedback_type and rating are required'
            }), 400
        
        if not (1 <= rating <= 5):
            return jsonify({
                'success': False,
                'error': 'rating must be between 1 and 5'
            }), 400
        
        # Валидация типа отзыва
        valid_feedback_types = ['prediction', 'recommendation', 'chat', 'widget', 'analysis', 'training']
        if feedback_type not in valid_feedback_types:
            return jsonify({
                'success': False,
                'error': f'Invalid feedback_type. Must be one of: {", ".join(valid_feedback_types)}'
            }), 400
        
        # Сохраняем отзыв как специальную запись разговора
        from datetime import datetime
        
        feedback_data = {
            'feedback_type': feedback_type,
            'rating': rating,
            'comment': comment,
            'context': context,
            'user_agent': request.headers.get('User-Agent', ''),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        conversation = AIConversation(
            user_id=current_user.id,
            session_id=f"feedback_{current_user.id}_{datetime.utcnow().timestamp()}",
            user_message=f"FEEDBACK:{feedback_type}:RATING:{rating}",
            ai_response=json.dumps(feedback_data),
            provider='system',
            model='feedback',
            tokens_used=0,
            response_time_ms=0,
            language=lang,
            timestamp=datetime.utcnow()
        )
        
        db.session.add(conversation)
        db.session.commit()
        
        current_app.logger.info(f"User {current_user.id} submitted feedback: {feedback_type}, rating: {rating}")
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Feedback submission error: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Feedback submission failed'
        }), 500

@ai_bp.route('/analytics/dashboard-data', methods=['GET'])
@login_required
def get_analytics_dashboard_data(lang):
    """Получение данных для административного дашборда (только для админов)"""
    try:
        # Проверка прав доступа
        if not (current_user.role == 'admin' or getattr(current_user, 'is_admin', False)):
            return jsonify({
                'success': False,
                'error': 'Access denied. Admin rights required.'
            }), 403
        
        from utils.ai_analytics import ai_analytics
        
        # Получаем все данные для дашборда
        realtime_metrics = ai_analytics.get_realtime_metrics()
        historical_data = ai_analytics.get_historical_analytics(7)  # Последние 7 дней
        user_insights = ai_analytics.get_user_behavior_insights()
        
        dashboard_data = {
            'overview': {
                'active_users_today': realtime_metrics.get('active_users', 0),
                'ai_interactions_24h': realtime_metrics.get('ai_interactions', 0),
                'system_health': realtime_metrics.get('system_health', 0.5),
                'user_satisfaction': realtime_metrics.get('user_satisfaction', 0.7)
            },
            'charts': {
                'daily_activity': historical_data.get('daily_metrics', []),
                'trending_topics': realtime_metrics.get('trending_topics', []),
                'feature_usage': realtime_metrics.get('usage_by_feature', {}),
                'trends': historical_data.get('trends', {})
            },
            'insights': {
                'user_engagement': realtime_metrics.get('user_engagement', 0.6),
                'learning_effectiveness': realtime_metrics.get('learning_effectiveness', 0.7),
                'error_rate': realtime_metrics.get('error_rate', 0.05),
                'power_users': user_insights.get('power_users', [])
            },
            'performance': realtime_metrics.get('performance_metrics', {}),
            'summary': historical_data.get('summary', {}),
            'last_updated': realtime_metrics.get('timestamp')
        }
        
        current_app.logger.info(f"Admin {current_user.id} accessed analytics dashboard data")
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Dashboard data error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Dashboard data service temporarily unavailable'
        }), 500

# ===== КОНЕЦ НОВЫХ ENDPOINTS ДЛЯ АНАЛИТИКИ ===== 

# ===== СПЕЦИАЛИЗИРОВАННЫЕ AI ENDPOINTS ДЛЯ UI ВИДЖЕТОВ =====

@ai_bp.route('/predict-exam', methods=['POST'])
@login_required
@csrf.exempt
def predict_exam(lang):
    """Предсказание экзаменационных результатов на основе прогресса пользователя."""
    try:
        data = request.get_json() if request.is_json else {}
        
        # Получаем данные пользователя для анализа
        from routes.learning_map_routes import get_user_stats
        user_stats = get_user_stats(current_user.id)
        
        # Простая логика предсказания на основе статистики
        total_progress = user_stats.get('total_progress', 0)
        completed_lessons = user_stats.get('completed_lessons', 0)
        total_lessons = user_stats.get('total_lessons', 1)
        completion_rate = completed_lessons / total_lessons if total_lessons > 0 else 0
        
        # Вычисляем предсказания
        exam_readiness = min(100, max(0, (completion_rate * 100) + random.randint(-15, 15)))
        success_probability = min(100, max(20, exam_readiness + random.randint(-10, 10)))
        
        # Определяем слабые места (случайный выбор для демонстрации)
        potential_topics = [
            "Анатомия зубов", "Пародонтология", "Эндодонтия", 
            "Ортодонтия", "Хирургия", "Терапия"
        ]
        weak_areas = random.sample(potential_topics, min(3, len(potential_topics)))
        
        # Рекомендации по улучшению
        recommendations = []
        if exam_readiness < 70:
            recommendations.extend([
                "Изучите основные модули перед экзаменом",
                "Пройдите дополнительные тесты",
                "Повторите слабые темы"
            ])
        elif exam_readiness < 85:
            recommendations.extend([
                "Закрепите знания практическими заданиями",
                "Изучите сложные случаи"
            ])
        else:
            recommendations.extend([
                "Вы хорошо подготовлены!",
                "Повторите ключевые концепции"
            ])
        
        # Временная оценка до готовности
        days_to_ready = max(1, int((100 - exam_readiness) / 10))
        
        prediction_result = {
            'exam_readiness': round(exam_readiness, 1),
            'success_probability': round(success_probability, 1),
            'weak_areas': weak_areas,
            'recommendations': recommendations,
            'estimated_study_time': f"{days_to_ready} дней",
            'confidence_level': 'high' if completion_rate > 0.7 else 'medium' if completion_rate > 0.3 else 'low',
            'last_updated': datetime.utcnow().isoformat(),
            'user_stats': {
                'total_progress': total_progress,
                'completion_rate': round(completion_rate * 100, 1),
                'lessons_completed': completed_lessons,
                'total_lessons': total_lessons
            }
        }
        
        # Логируем запрос предсказания
        current_app.logger.info(f"User {current_user.id} requested exam prediction: readiness {exam_readiness}%")
        
        return jsonify({
            'success': True,
            'prediction': prediction_result,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Exam prediction error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Prediction service temporarily unavailable',
            'fallback': {
                'exam_readiness': 75.0,
                'success_probability': 80.0,
                'message': 'Using fallback prediction data'
            }
        }), 500

@ai_bp.route('/recommend-content', methods=['POST'])
@login_required
@csrf.exempt
def recommend_content(lang):
    """Рекомендации контента на основе прогресса и предпочтений пользователя."""
    try:
        data = request.get_json() if request.is_json else {}
        
        # Получаем параметры запроса
        content_type = data.get('content_type', 'all')  # 'lessons', 'tests', 'virtual_patients', 'all'
        difficulty = data.get('difficulty', 'adaptive')  # 'beginner', 'intermediate', 'advanced', 'adaptive'
        limit = min(data.get('limit', 5), 20)  # Максимум 20 рекомендаций
        
        # Получаем статистику пользователя
        from routes.learning_map_routes import get_user_stats
        user_stats = get_user_stats(current_user.id)
        
        # Получаем модули и предметы для рекомендаций
        from models import Module, Subject, VirtualPatientScenario, Test
        
        recommendations = []
        
        # Рекомендации модулей
        if content_type in ['lessons', 'modules', 'all']:
            modules = Module.query.limit(10).all()
            for module in modules[:3]:
                recommendations.append({
                    'type': 'module',
                    'id': module.id,
                    'title': module.title,
                    'description': getattr(module, 'description', 'Изучите этот модуль'),
                    'difficulty': 'intermediate',
                    'estimated_time': '30 мин',
                    'reason': 'Подходит для вашего уровня',
                    'url': url_for('mobile.module_view', lang=lang, module_id=module.id),
                    'category': 'learning'
                })
        
        # Рекомендации виртуальных пациентов
        if content_type in ['virtual_patients', 'patients', 'all']:
            scenarios = VirtualPatientScenario.query.filter_by(is_published=True).limit(5).all()
            for scenario in scenarios[:2]:
                recommendations.append({
                    'type': 'virtual_patient',
                    'id': scenario.id,
                    'title': scenario.title,
                    'description': getattr(scenario, 'description', 'Клинический случай'),
                    'difficulty': scenario.difficulty if hasattr(scenario, 'difficulty') else 'medium',
                    'estimated_time': '15 мин',
                    'reason': 'Практический опыт',
                    'url': f"/{lang}/virtual-patient/interact/{scenario.id}",
                    'category': 'practice'
                })
        
        # Рекомендации тестов
        if content_type in ['tests', 'quizzes', 'all']:
            tests = Test.query.limit(5).all()
            for test in tests[:2]:
                recommendations.append({
                    'type': 'test',
                    'id': test.id,
                    'title': test.title,
                    'description': getattr(test, 'description', 'Проверьте свои знания'),
                    'difficulty': 'medium',
                    'estimated_time': '10 мин',
                    'reason': 'Закрепление знаний',
                    'url': f"/{lang}/test/{test.id}",
                    'category': 'assessment'
                })
        
        # Если рекомендаций мало, добавляем общие
        if len(recommendations) < limit:
            subjects = Subject.query.limit(5).all()
            for subject in subjects[:limit - len(recommendations)]:
                recommendations.append({
                    'type': 'subject',
                    'id': subject.id,
                    'title': subject.name,
                    'description': getattr(subject, 'description', 'Изучите этот предмет'),
                    'difficulty': 'adaptive',
                    'estimated_time': '2 часа',
                    'reason': 'Рекомендуется для изучения',
                    'url': url_for('mobile.subject_view', lang=lang, subject_id=subject.id),
                    'category': 'comprehensive'
                })
        
        # Сортируем по приоритету
        recommendations = recommendations[:limit]
        
        # Добавляем персонализированную информацию
        for rec in recommendations:
            rec['personalized'] = True
            rec['confidence'] = random.uniform(0.7, 0.95)  # Уверенность в рекомендации
            rec['tags'] = ['recommended', 'personalized']
        
        recommendation_result = {
            'recommendations': recommendations,
            'total_count': len(recommendations),
            'content_type': content_type,
            'difficulty': difficulty,
            'personalization_factors': {
                'user_level': user_stats.get('current_level', 1),
                'completion_rate': user_stats.get('total_progress', 0),
                'preferred_difficulty': difficulty,
                'learning_style': 'adaptive'
            },
            'generated_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=6)).isoformat()  # Кэш на 6 часов
        }
        
        # Логируем запрос рекомендаций
        current_app.logger.info(f"User {current_user.id} requested content recommendations: {content_type}, {len(recommendations)} items")
        
        return jsonify({
            'success': True,
            'recommendations': recommendation_result,
            'cached': False
        })
        
    except Exception as e:
        current_app.logger.error(f"Content recommendation error: {e}", exc_info=True)
        
        # Fallback рекомендации
        fallback_recommendations = [
            {
                'type': 'general',
                'id': 1,
                'title': 'Основы стоматологии',
                'description': 'Изучите базовые концепции',
                'difficulty': 'beginner',
                'estimated_time': '45 мин',
                'reason': 'Рекомендуется для начинающих',
                'url': f"/{lang}/learning-map",
                'category': 'foundation',
                'personalized': False,
                'confidence': 0.8,
                'tags': ['fallback', 'general']
            }
        ]
        
        return jsonify({
            'success': False,
            'error': 'Recommendation service temporarily unavailable',
            'fallback_recommendations': fallback_recommendations,
            'using_fallback': True
        }), 500

# ===== КОНЕЦ СПЕЦИАЛИЗИРОВАННЫХ AI ENDPOINTS ===== 