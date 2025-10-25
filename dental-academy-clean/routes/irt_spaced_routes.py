#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IRT + Spaced Repetition Integration Routes
API роуты для работы с интегрированной системой IRT + Spaced Repetition
"""

import logging
from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify, current_app, g
from flask_login import login_required, current_user
from sqlalchemy import and_

from extensions import db
from models import User, Question, SpacedRepetitionItem, DiagnosticSession
from utils.irt_spaced_integration import get_irt_spaced_integration
from utils.metrics import record_error, record_fallback_usage
from utils.serializers import safe_jsonify
from utils.helpers import get_user_profession_code

logger = logging.getLogger(__name__)

# Создаем blueprint
irt_spaced_bp = Blueprint('irt_spaced', __name__, url_prefix='/irt-spaced')

@irt_spaced_bp.route('/review-schedule', methods=['GET'])
@login_required
def get_review_schedule():
    """
    Получает оптимальное расписание повторений с учетом IRT
    
    Query parameters:
    - domain: домен (опционально)
    - max_items: максимальное количество элементов (по умолчанию 20)
    """
    try:
        user_id = current_user.id
        domain = request.args.get('domain')
        max_items = int(request.args.get('max_items', 20))
        
        # Получаем расписание повторений
        irt_spaced_integration = get_irt_spaced_integration()
        review_items = irt_spaced_integration.get_optimal_review_schedule(
            user_id, domain, max_items
        )
        
        # Форматируем ответ
        formatted_items = []
        for item in review_items:
            # Получаем информацию о вопросе
            user_profession = get_user_profession_code(current_user)
            question = Question.query.filter_by(
                id=item.question_id,
                profession=user_profession
            ).first()
            if not question:
                continue
            
            formatted_items.append({
                'id': item.question_id,
                'question_text': question.text[:100] + '...' if len(question.text) > 100 else question.text,
                'domain': item.domain,
                'irt_difficulty': item.irt_difficulty,
                'user_ability': item.user_ability,
                'confidence_level': item.confidence_level,
                'learning_rate': item.learning_rate,
                'repetitions': item.repetitions,
                'quality': item.quality,
                'next_review': item.next_review.isoformat() if item.next_review else None,
                'last_review': item.last_review.isoformat() if item.last_review else None,
                'estimated_time': 3,  # 3 минуты на повторение
                'priority_score': irt_spaced_integration._calculate_priority_score(item)
            })
        
        return safe_jsonify({
            'success': True,
            'review_items': formatted_items,
            'total_count': len(formatted_items),
            'domain': domain,
            'max_items': max_items
        })
        
    except Exception as e:
        logger.error(f"Error getting review schedule: {e}")
        record_error("irt_spaced_routes", f"get_review_schedule failed: {e}")
        return safe_jsonify({
            'success': False,
            'error': str(e)
        }), 500

@irt_spaced_bp.route('/process-review', methods=['POST'])
@login_required
def process_review():
    """
    Обрабатывает ответ пользователя на повторение
    
    Request body:
    {
        "question_id": 123,
        "quality": 4,  // 0-5
        "response_time": 15.5  // в секундах (опционально)
    }
    """
    try:
        user_id = current_user.id
        data = request.get_json()
        
        if not data:
            return safe_jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        question_id = data.get('question_id')
        quality = data.get('quality')
        response_time = data.get('response_time')
        
        if question_id is None or quality is None:
            return safe_jsonify({
                'success': False,
                'error': 'question_id and quality are required'
            }), 400
        
        if not (0 <= quality <= 5):
            return safe_jsonify({
                'success': False,
                'error': 'quality must be between 0 and 5'
            }), 400
        
        # Создаем интегрированный элемент
        irt_spaced_integration = get_irt_spaced_integration()
        integrated_item = irt_spaced_integration.create_integrated_item(
            question_id, user_id
        )
        
        # Обрабатываем ответ
        result = irt_spaced_integration.process_review_response(
            integrated_item, quality, response_time
        )
        
        if result['success']:
            return safe_jsonify({
                'success': True,
                'result': result,
                'message': 'Review processed successfully'
            })
        else:
            return safe_jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }), 500
        
    except Exception as e:
        logger.error(f"Error processing review: {e}")
        record_error("irt_spaced_routes", f"process_review failed: {e}")
        return safe_jsonify({
            'success': False,
            'error': str(e)
        }), 500

@irt_spaced_bp.route('/adaptive-plan', methods=['GET'])
@login_required
def get_adaptive_plan():
    """
    Получает адаптивный ежедневный план с интеграцией IRT + SR
    
    Query parameters:
    - target_minutes: целевое время в минутах (по умолчанию 30)
    """
    try:
        user_id = current_user.id
        target_minutes = int(request.args.get('target_minutes', 30))
        
        # Генерируем адаптивный план
        irt_spaced_integration = get_irt_spaced_integration()
        plan = irt_spaced_integration.generate_adaptive_daily_plan(
            user_id, target_minutes
        )
        
        if not plan.get('success', True):
            return safe_jsonify(plan), 500
        
        return safe_jsonify(plan)
        
    except Exception as e:
        logger.error(f"Error getting adaptive plan: {e}")
        record_error("irt_spaced_routes", f"get_adaptive_plan failed: {e}")
        return safe_jsonify({
            'success': False,
            'error': str(e)
        }), 500

@irt_spaced_bp.route('/user-insights', methods=['GET'])
@login_required
def get_user_insights():
    """
    Получает IRT инсайты для пользователя
    """
    try:
        user_id = current_user.id
        
        # Получаем текущие способности
        irt_spaced_integration = get_irt_spaced_integration()
        current_abilities = irt_spaced_integration._get_current_abilities(user_id)
        
        # Генерируем инсайты
        insights = irt_spaced_integration._generate_irt_insights(
            user_id, current_abilities
        )
        
        # Получаем статистику повторений
        review_stats = _get_review_statistics(user_id)
        
        return safe_jsonify({
            'success': True,
            'insights': insights,
            'current_abilities': current_abilities,
            'review_statistics': review_stats
        })
        
    except Exception as e:
        logger.error(f"Error getting user insights: {e}")
        record_error("irt_spaced_routes", f"get_user_insights failed: {e}")
        return safe_jsonify({
            'success': False,
            'error': str(e)
        }), 500

@irt_spaced_bp.route('/batch-process', methods=['POST'])
@login_required
def batch_process_reviews():
    """
    Обрабатывает несколько ответов пользователя за раз
    
    Request body:
    {
        "reviews": [
            {
                "question_id": 123,
                "quality": 4,
                "response_time": 15.5
            },
            ...
        ]
    }
    """
    try:
        user_id = current_user.id
        data = request.get_json()
        
        if not data or 'reviews' not in data:
            return safe_jsonify({
                'success': False,
                'error': 'No reviews data provided'
            }), 400
        
        reviews = data['reviews']
        results = []
        
        for review in reviews:
            try:
                question_id = review.get('question_id')
                quality = review.get('quality')
                response_time = review.get('response_time')
                
                if question_id is None or quality is None:
                    results.append({
                        'question_id': question_id,
                        'success': False,
                        'error': 'question_id and quality are required'
                    })
                    continue
                
                if not (0 <= quality <= 5):
                    results.append({
                        'question_id': question_id,
                        'success': False,
                        'error': 'quality must be between 0 and 5'
                    })
                    continue
                
                # Создаем интегрированный элемент
                irt_spaced_integration = get_irt_spaced_integration()
                integrated_item = irt_spaced_integration.create_integrated_item(
                    question_id, user_id
                )
                
                # Обрабатываем ответ
                result = irt_spaced_integration.process_review_response(
                    integrated_item, quality, response_time
                )
                
                results.append({
                    'question_id': question_id,
                    'success': result['success'],
                    'result': result if result['success'] else None,
                    'error': result.get('error') if not result['success'] else None
                })
                
            except Exception as e:
                results.append({
                    'question_id': review.get('question_id'),
                    'success': False,
                    'error': str(e)
                })
        
        return safe_jsonify({
            'success': True,
            'results': results,
            'total_processed': len(results),
            'successful': len([r for r in results if r['success']]),
            'failed': len([r for r in results if not r['success']])
        })
        
    except Exception as e:
        logger.error(f"Error in batch process: {e}")
        record_error("irt_spaced_routes", f"batch_process_reviews failed: {e}")
        return safe_jsonify({
            'success': False,
            'error': str(e)
        }), 500

@irt_spaced_bp.route('/create-item', methods=['POST'])
@login_required
def create_integrated_item():
    """
    Создает интегрированный элемент IRT + Spaced Repetition
    
    Request body:
    {
        "question_id": 123,
        "user_ability": 0.5  // опционально
    }
    """
    try:
        user_id = current_user.id
        data = request.get_json()
        
        if not data:
            return safe_jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        question_id = data.get('question_id')
        user_ability = data.get('user_ability')
        
        if question_id is None:
            return safe_jsonify({
                'success': False,
                'error': 'question_id is required'
            }), 400
        
        # Создаем интегрированный элемент
        irt_spaced_integration = get_irt_spaced_integration()
        integrated_item = irt_spaced_integration.create_integrated_item(
            question_id, user_id, user_ability
        )
        
        return safe_jsonify({
            'success': True,
            'item': {
                'question_id': integrated_item.question_id,
                'domain': integrated_item.domain,
                'irt_difficulty': integrated_item.irt_difficulty,
                'user_ability': integrated_item.user_ability,
                'confidence_level': integrated_item.confidence_level,
                'learning_rate': integrated_item.learning_rate,
                'ease_factor': integrated_item.ease_factor,
                'interval': integrated_item.interval,
                'repetitions': integrated_item.repetitions,
                'next_review': integrated_item.next_review.isoformat() if integrated_item.next_review else None
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating integrated item: {e}")
        record_error("irt_spaced_routes", f"create_integrated_item failed: {e}")
        return safe_jsonify({
            'success': False,
            'error': str(e)
        }), 500

@irt_spaced_bp.route('/statistics', methods=['GET'])
@login_required
def get_statistics():
    """
    Получает статистику по интегрированной системе для пользователя
    """
    try:
        user_id = current_user.id
        
        # Получаем статистику повторений
        review_stats = _get_review_statistics(user_id)
        
        # Получаем IRT статистику
        irt_stats = _get_irt_statistics(user_id)
        
        # Получаем общую статистику
        overall_stats = _get_overall_statistics(user_id)
        
        return safe_jsonify({
            'success': True,
            'review_statistics': review_stats,
            'irt_statistics': irt_stats,
            'overall_statistics': overall_stats
        })
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        record_error("irt_spaced_routes", f"get_statistics failed: {e}")
        return safe_jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Вспомогательные функции

def _get_review_statistics(user_id: int) -> dict:
    """Получает статистику повторений для пользователя"""
    try:
        # Общее количество элементов
        total_items = SpacedRepetitionItem.query.filter_by(
            user_id=user_id, is_active=True
        ).count()
        
        # Готовые к повторению
        due_items = SpacedRepetitionItem.query.filter(
            and_(
                SpacedRepetitionItem.user_id == user_id,
                SpacedRepetitionItem.is_active == True,
                SpacedRepetitionItem.next_review <= datetime.now(timezone.utc)
            )
        ).count()
        
        # Просроченные
        overdue_items = SpacedRepetitionItem.query.filter(
            and_(
                SpacedRepetitionItem.user_id == user_id,
                SpacedRepetitionItem.is_active == True,
                SpacedRepetitionItem.next_review < datetime.now(timezone.utc) - timedelta(days=1)
            )
        ).count()
        
        # Статистика по доменам
        domain_stats = db.session.query(
            SpacedRepetitionItem.domain,
            db.func.count(SpacedRepetitionItem.id).label('count'),
            db.func.avg(SpacedRepetitionItem.quality).label('avg_quality'),
            db.func.avg(SpacedRepetitionItem.repetitions).label('avg_repetitions')
        ).filter(
            SpacedRepetitionItem.user_id == user_id,
            SpacedRepetitionItem.is_active == True
        ).group_by(SpacedRepetitionItem.domain).all()
        
        return {
            'total_items': total_items,
            'due_items': due_items,
            'overdue_items': overdue_items,
            'domain_statistics': [
                {
                    'domain': stat.domain,
                    'count': stat.count,
                    'avg_quality': float(stat.avg_quality) if stat.avg_quality else 0.0,
                    'avg_repetitions': float(stat.avg_repetitions) if stat.avg_repetitions else 0.0
                }
                for stat in domain_stats
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting review statistics: {e}")
        return {}

def _get_irt_statistics(user_id: int) -> dict:
    """Получает IRT статистику для пользователя"""
    try:
        # Получаем последнюю диагностическую сессию
        session = DiagnosticSession.query.filter_by(
            user_id=user_id
        ).order_by(DiagnosticSession.id.desc()).first()
        
        if not session or not session.session_data:
            return {}
        
        domain_abilities = session.session_data.get('domain_abilities', {})
        
        if not domain_abilities:
            return {}
        
        # Рассчитываем статистику
        abilities_list = list(domain_abilities.values())
        
        return {
            'overall_ability': sum(abilities_list) / len(abilities_list),
            'min_ability': min(abilities_list),
            'max_ability': max(abilities_list),
            'domain_count': len(domain_abilities),
            'strongest_domain': max(domain_abilities.items(), key=lambda x: x[1])[0] if domain_abilities else None,
            'weakest_domain': min(domain_abilities.items(), key=lambda x: x[1])[0] if domain_abilities else None,
            'domain_abilities': domain_abilities
        }
        
    except Exception as e:
        logger.error(f"Error getting IRT statistics: {e}")
        return {}

def _get_overall_statistics(user_id: int) -> dict:
    """Получает общую статистику для пользователя"""
    try:
        # Получаем статистику повторений
        review_stats = _get_review_statistics(user_id)
        
        # Получаем IRT статистику
        irt_stats = _get_irt_statistics(user_id)
        
        # Рассчитываем общие метрики
        total_items = review_stats.get('total_items', 0)
        due_items = review_stats.get('due_items', 0)
        overall_ability = irt_stats.get('overall_ability', 0.0)
        
        # Рекомендации
        recommendations = []
        
        if due_items > 10:
            recommendations.append("У вас много элементов готовых к повторению. Рекомендуется уделить время повторению.")
        
        if overall_ability < 0.3:
            recommendations.append("Ваш общий уровень знаний низкий. Рекомендуется больше практики.")
        elif overall_ability > 0.7:
            recommendations.append("Отличный прогресс! Можно переходить к более сложным темам.")
        
        return {
            'total_items': total_items,
            'due_items': due_items,
            'overall_ability': overall_ability,
            'recommendations': recommendations,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting overall statistics: {e}")
        return {} 