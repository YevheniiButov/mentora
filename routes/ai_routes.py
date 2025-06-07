# routes/ai_routes.py
"""
AI Assistant Routes for Dental Academy Mobile App
Includes RAG-powered AI system with user API keys
"""

from flask import Blueprint, render_template, request, session, redirect, url_for, g, flash, current_app, jsonify
from flask_login import login_required, current_user
from extensions import db
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