# routes/ai_assistant_routes.py
from flask import Blueprint, request, jsonify, g
from flask_login import login_required, current_user
import logging
import random
from models import db, DiagnosticSession

logger = logging.getLogger(__name__)

# Создаем blueprint с языковой поддержкой
ai_assistant_bp = Blueprint(
    'ai_assistant_bp',
    __name__,
    url_prefix='/<string:lang>/ai-assistant'
)

@ai_assistant_bp.before_request
def before_request():
    """Выполняется перед каждым запросом к AI Assistant"""
    # Устанавливаем язык из URL параметра
    from flask import request
    lang = request.view_args.get('lang', 'ru') if request.view_args else 'ru'
    
    # Проверяем валидность языка
    valid_languages = ['en', 'ru', 'nl', 'uk', 'fa', 'es', 'pt', 'tr', 'ar']
    if lang not in valid_languages:
        lang = 'ru'
    
    g.lang = lang

@ai_assistant_bp.route('/predict-exam', methods=['POST'])
@login_required
def predict_exam(lang):
    """Предсказание готовности к экзамену"""
    try:
        # Мок-данные для демонстрации
        # В реальном приложении здесь был бы AI анализ
        prediction = {
            'exam_readiness': round(random.uniform(65, 95), 1),
            'success_probability': round(random.uniform(70, 90), 1),
            'weak_areas': [
                'Эндодонтия - требует дополнительной практики',
                'Хирургия - изучить протоколы анестезии',
                'Протезирование - повторить материаловедение'
            ][:random.randint(1, 3)],
            'recommendations': [
                'Пройти дополнительные тесты по слабым темам',
                'Изучить клинические случаи',
                'Практиковать практические навыки'
            ][:random.randint(1, 3)],
            'confidence_level': random.choice(['high', 'medium', 'low'])
        }
        
        logger.info(f"AI Exam prediction generated for user {request.args.get('user_id', 'unknown')}")
        
        return jsonify({
            'success': True,
            'prediction': prediction
        })
        
    except Exception as e:
        logger.error(f"Error in predict_exam: {e}")
        return jsonify({
            'success': False,
            'error': 'Произошла ошибка при анализе готовности к экзамену'
        }), 500

@ai_assistant_bp.route('/recommend-content', methods=['POST'])
@login_required
def recommend_content(lang):
    """Рекомендации контента"""
    try:
        data = request.get_json() or {}
        limit = data.get('limit', 3)
        
        # Мок-рекомендации
        all_recommendations = [
            {
                'type': 'module',
                'title': 'Основы эндодонтии',
                'description': 'Изучите современные методы лечения корневых каналов',
                'url': f"/{g.lang}/learning-map",
                'priority': 'high'
            },
            {
                'type': 'lesson',
                'title': 'Анестезия в стоматологии',
                'description': 'Протоколы и техники местной анестезии',
                'url': f"/{g.lang}/learning-map",
                'priority': 'medium'
            },
            {
                'type': 'practice',
                'title': 'Клинические случаи',
                'description': 'Разбор сложных клинических ситуаций',
                'url': f"/{g.lang}/learning-map",
                'priority': 'high'
            },
            {
                'type': 'test',
                'title': 'Тест по материаловедению',
                'description': 'Проверьте знания современных материалов',
                'url': f"/{g.lang}/learning-map",
                'priority': 'low'
            }
        ]
        
        # Возвращаем случайные рекомендации в указанном количестве
        recommendations = random.sample(all_recommendations, min(limit, len(all_recommendations)))
        
        logger.info(f"AI Content recommendations generated: {len(recommendations)} items")
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
        
    except Exception as e:
        logger.error(f"Error in recommend_content: {e}")
        return jsonify({
            'success': False,
            'error': 'Произошла ошибка при подборе рекомендаций'
        }), 500

@ai_assistant_bp.route('/analyze-progress', methods=['POST'])
@login_required
def analyze_progress(lang):
    """Анализ прогресса обучения"""
    try:
        # Мок-данные анализа прогресса
        stats = {
            'completed_lessons': random.randint(15, 50),
            'total_lessons': 120,
            'average_score': round(random.uniform(75, 95), 1),
            'study_time': random.randint(25, 80),  # часы
            'streak_days': random.randint(3, 21),
            'weak_areas': [
                'Хирургия',
                'Протезирование',
                'Пародонтология'
            ][:random.randint(1, 3)],
            'strong_areas': [
                'Терапия',
                'Диагностика',
                'Профилактика'
            ][:random.randint(1, 3)]
        }
        
        logger.info("AI Progress analysis generated")
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error in analyze_progress: {e}")
        return jsonify({
            'success': False,
            'error': 'Произошла ошибка при анализе прогресса'
        }), 500

@ai_assistant_bp.route('/chat', methods=['POST'])
@login_required
def ai_chat(lang):
    """Мини-чат с AI ассистентом"""
    try:
        data = request.get_json() or {}
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Сообщение не может быть пустым'
            }), 400
        
        # Простые ответы-заглушки
        responses = [
            "Я понимаю ваш вопрос. Для получения подробной информации рекомендую изучить соответствующий модуль.",
            "Это интересный вопрос! Попробуйте поискать ответ в разделе обучающих материалов.",
            "Для лучшего понимания темы рекомендую пройти дополнительные тесты.",
            "Ваш вопрос касается важной области стоматологии. Изучите клинические случаи для практического понимания."
        ]
        
        response = random.choice(responses)
        
        logger.info(f"AI Chat response generated for message: {message[:50]}...")
        
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        logger.error(f"Error in ai_chat: {e}")
        return jsonify({
            'success': False,
            'error': 'Произошла ошибка при обработке сообщения'
        }), 500

@ai_assistant_bp.route('/progress-stats', methods=['GET'])
@login_required
def progress_stats(lang):
    """Получение статистики прогресса пользователя"""
    try:
        # Мок-данные статистики
        stats = {
            'completed_lessons': random.randint(10, 45),
            'total_lessons': 120,
            'average_score': round(random.uniform(70, 95), 1),
            'study_time': random.randint(20, 80),  # часы
            'streak_days': random.randint(1, 15),
            'level': random.randint(1, 5),
            'experience_points': random.randint(100, 1500),
            'achievements': random.randint(0, 8)
        }
        
        logger.info("Progress stats generated")
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error in progress_stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Произошла ошибка при получении статистики'
        }), 500

@ai_assistant_bp.route('/diagnostic/end_session', methods=['POST'])
@login_required
def end_diagnostic_session(lang):
    """Завершение активной диагностической сессии"""
    try:
        # Находим активную сессию пользователя
        active_session = DiagnosticSession.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).first()
        
        if not active_session:
            return jsonify({
                'success': False,
                'error': 'Активная диагностическая сессия не найдена'
            }), 404
        
        # Завершаем сессию
        active_session.status = 'terminated'
        active_session.termination_reason = 'manual_exit'
        active_session.completed_at = db.func.now()
        db.session.commit()
        
        logger.info(f"Diagnostic session {active_session.id} ended for user {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': 'Диагностическая сессия успешно завершена'
        })
        
    except Exception as e:
        logger.error(f"Error ending diagnostic session: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Произошла ошибка при завершении сессии'
        }), 500

@ai_assistant_bp.route('/diagnostic/continue_session', methods=['GET'])
@login_required
def continue_diagnostic_session(lang):
    """Получение данных активной сессии для продолжения"""
    try:
        # Находим активную сессию пользователя
        active_session = DiagnosticSession.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).first()
        
        if not active_session:
            return jsonify({
                'success': False,
                'error': 'Активная диагностическая сессия не найдена'
            }), 404
        
        # Возвращаем данные сессии
        session_data = {
            'session_id': active_session.id,
            'current_ability': active_session.current_ability,
            'ability_se': active_session.ability_se,
            'questions_answered': active_session.questions_answered,
            'correct_answers': active_session.correct_answers,
            'session_type': active_session.session_type,
            'started_at': active_session.started_at.isoformat() if active_session.started_at else None
        }
        
        logger.info(f"Continuing diagnostic session {active_session.id} for user {current_user.id}")
        
        return jsonify({
            'success': True,
            'session': session_data
        })
        
    except Exception as e:
        logger.error(f"Error continuing diagnostic session: {e}")
        return jsonify({
            'success': False,
            'error': 'Произошла ошибка при получении данных сессии'
        }), 500

@ai_assistant_bp.route('/diagnostic/restart_session', methods=['POST'])
@login_required
def restart_diagnostic_session(lang):
    """Перезапуск диагностической сессии (завершает старую, создает новую)"""
    try:
        # Завершаем активную сессию, если есть
        active_session = DiagnosticSession.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).first()
        
        if active_session:
            active_session.status = 'terminated'
            active_session.termination_reason = 'restart'
            active_session.completed_at = db.func.now()
            logger.info(f"Terminated session {active_session.id} for restart")
        
        # Создаем новую сессию
        new_session = DiagnosticSession(
            user_id=current_user.id,
            session_type='diagnostic',
            test_length=20,  # 20 вопросов для BI-toets
            time_limit=120,  # 2 часа
            current_ability=0.0,
            ability_se=1.0,
            questions_answered=0,
            correct_answers=0,
            status='active'
        )
        
        db.session.add(new_session)
        db.session.commit()
        
        logger.info(f"Created new diagnostic session {new_session.id} for user {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': 'Новая диагностическая сессия создана',
            'session_id': new_session.id
        })
        
    except Exception as e:
        logger.error(f"Error restarting diagnostic session: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Произошла ошибка при перезапуске сессии'
        }), 500

@ai_assistant_bp.route('/health', methods=['GET'])
def health_check(lang):
    """Проверка здоровья AI системы"""
    from flask import jsonify
    return jsonify({
        'ai_system': 'operational',
        'status': 'healthy',
        'version': '1.0.0',
        'language': lang
    }) 