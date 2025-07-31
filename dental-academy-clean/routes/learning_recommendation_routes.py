#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Learning Recommendation Routes
Маршруты для системы рекомендаций обучения
"""

from flask import Blueprint, request, jsonify, render_template, session
from flask_login import login_required, current_user
import json
import os
from datetime import datetime
from typing import Dict, List

# Импорт движка рекомендаций
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from learning_recommendation_engine import LearningRecommendationEngine, TestResult

learning_recommendation_bp = Blueprint('learning_recommendation', __name__)

@learning_recommendation_bp.route('/learning-recommendations', methods=['GET'])
@login_required
def learning_recommendations_page():
    """Страница с рекомендациями обучения"""
    return render_template('learning/recommendations.html')

@learning_recommendation_bp.route('/api/generate-recommendations', methods=['POST'])
@login_required
def generate_recommendations():
    """
    Генерация персонализированных рекомендаций обучения
    
    Ожидаемый формат данных:
    {
        "test_results": [
            {
                "domain": "Praktische vaardigheden",
                "score": 45.0,
                "total_questions": 20,
                "correct_answers": 9,
                "time_spent": 30
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'test_results' not in data:
            return jsonify({
                'success': False,
                'error': 'Отсутствуют данные о результатах тестирования'
            }), 400
        
        # Создание движка рекомендаций
        engine = LearningRecommendationEngine()
        
        # Преобразование данных в объекты TestResult
        test_results = []
        for result_data in data['test_results']:
            test_result = TestResult(
                domain=result_data['domain'],
                score=float(result_data['score']),
                total_questions=int(result_data['total_questions']),
                correct_answers=int(result_data['correct_answers']),
                time_spent=float(result_data['time_spent'])
            )
            test_results.append(test_result)
        
        # Генерация персонализированного отчета
        report = engine.generate_personalized_report(test_results)
        
        # Сохранение отчета в сессии пользователя
        session['learning_report'] = report
        session['report_generated_at'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'report': report
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка при генерации рекомендаций: {str(e)}'
        }), 500

@learning_recommendation_bp.route('/api/get-recommendations', methods=['GET'])
@login_required
def get_recommendations():
    """Получение сохраненных рекомендаций"""
    try:
        if 'learning_report' not in session:
            return jsonify({
                'success': False,
                'error': 'Рекомендации не найдены. Сначала пройдите тестирование.'
            }), 404
        
        report = session['learning_report']
        generated_at = session.get('report_generated_at', 'Неизвестно')
        
        return jsonify({
            'success': True,
            'report': report,
            'generated_at': generated_at
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка при получении рекомендаций: {str(e)}'
        }), 500

@learning_recommendation_bp.route('/api/export-learning-plan', methods=['POST'])
@login_required
def export_learning_plan():
    """Экспорт плана обучения в файл"""
    try:
        if 'learning_report' not in session:
            return jsonify({
                'success': False,
                'error': 'Рекомендации не найдены'
            }), 404
        
        data = request.get_json()
        format_type = data.get('format', 'json')  # json, pdf, csv
        
        report = session['learning_report']
        
        # Создание имени файла
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"learning_plan_{current_user.id}_{timestamp}"
        
        if format_type == 'json':
            file_path = f"static/exports/{filename}.json"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            download_url = f"/static/exports/{filename}.json"
            
        else:
            return jsonify({
                'success': False,
                'error': f'Неподдерживаемый формат: {format_type}'
            }), 400
        
        return jsonify({
            'success': True,
            'download_url': download_url,
            'filename': f"{filename}.{format_type}"
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка при экспорте: {str(e)}'
        }), 500

@learning_recommendation_bp.route('/api/domain-cards/<domain>', methods=['GET'])
@login_required
def get_domain_cards(domain):
    """Получение карточек для конкретного домена"""
    try:
        # Создание движка рекомендаций
        engine = LearningRecommendationEngine()
        
        # Загрузка маппинга доменов
        domain_mapping = engine.domain_mapping
        
        if domain not in domain_mapping.get('domain_mapping', {}):
            return jsonify({
                'success': False,
                'error': f'Домен {domain} не найден'
            }), 404
        
        domain_info = domain_mapping['domain_mapping'][domain]
        card_sources = domain_info.get('card_sources', {})
        
        # Сбор информации о карточках
        cards_info = {
            'domain': domain,
            'description': domain_info.get('description', ''),
            'weight': domain_info.get('weight', 0),
            'priority': domain_info.get('priority', 'low'),
            'sources': {}
        }
        
        for source_name, source_info in card_sources.items():
            cards_info['sources'][source_name] = {
                'files': source_info.get('files', []),
                'topics': source_info.get('topics', []),
                'card_count': source_info.get('card_count', 0),
                'relevant_tags': source_info.get('relevant_tags', [])
            }
        
        return jsonify({
            'success': True,
            'cards_info': cards_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка при получении карточек домена: {str(e)}'
        }), 500

@learning_recommendation_bp.route('/api/available-domains', methods=['GET'])
@login_required
def get_available_domains():
    """Получение списка доступных доменов"""
    try:
        # Создание движка рекомендаций
        engine = LearningRecommendationEngine()
        
        # Загрузка маппинга доменов
        domain_mapping = engine.domain_mapping
        
        domains = []
        for domain_name, domain_info in domain_mapping.get('domain_mapping', {}).items():
            domains.append({
                'name': domain_name,
                'description': domain_info.get('description', ''),
                'weight': domain_info.get('weight', 0),
                'priority': domain_info.get('priority', 'low'),
                'card_sources_count': len(domain_info.get('card_sources', {}))
            })
        
        # Сортировка по приоритету и весу
        domains.sort(key=lambda x: (
            {'high': 3, 'medium': 2, 'low': 1}[x['priority']], 
            x['weight']
        ), reverse=True)
        
        return jsonify({
            'success': True,
            'domains': domains
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка при получении доменов: {str(e)}'
        }), 500

@learning_recommendation_bp.route('/api/learning-progress', methods=['POST'])
@login_required
def update_learning_progress():
    """Обновление прогресса обучения"""
    try:
        data = request.get_json()
        
        if not data or 'domain' not in data or 'cards_completed' not in data:
            return jsonify({
                'success': False,
                'error': 'Отсутствуют данные о прогрессе'
            }), 400
        
        domain = data['domain']
        cards_completed = int(data['cards_completed'])
        time_spent = data.get('time_spent', 0)
        
        # Здесь можно добавить логику сохранения прогресса в базу данных
        # Пока просто возвращаем подтверждение
        
        return jsonify({
            'success': True,
            'message': f'Прогресс по домену {domain} обновлен',
            'cards_completed': cards_completed,
            'time_spent': time_spent
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка при обновлении прогресса: {str(e)}'
        }), 500

@learning_recommendation_bp.route('/api/learning-stats', methods=['GET'])
@login_required
def get_learning_stats():
    """Получение статистики обучения пользователя"""
    try:
        # Здесь можно добавить логику получения статистики из базы данных
        # Пока возвращаем заглушку
        
        stats = {
            'total_domains_studied': 0,
            'total_cards_completed': 0,
            'total_time_spent': 0,
            'average_score': 0,
            'streak_days': 0,
            'last_study_date': None
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка при получении статистики: {str(e)}'
        }), 500

@learning_recommendation_bp.route('/api/simulate-test-results', methods=['GET'])
@login_required
def simulate_test_results():
    """Симуляция результатов тестирования для демонстрации"""
    try:
        # Создание движка рекомендаций
        engine = LearningRecommendationEngine()
        
        # Симуляция результатов тестирования
        simulated_results = [
            TestResult("Praktische vaardigheden", 45.0, 20, 9, 30),
            TestResult("Behandelplanning", 75.0, 15, 11, 25),
            TestResult("Mondziekten en kaakchirurgie", 85.0, 12, 10, 20),
            TestResult("Farmacologie", 30.0, 18, 5, 35),
            TestResult("Ethiek en recht", 90.0, 10, 9, 15),
            TestResult("Systemische aandoeningen", 65.0, 16, 10, 28),
            TestResult("Complexe diagnostiek", 55.0, 14, 8, 22),
            TestResult("Spoedeisende hulp", 80.0, 12, 10, 18)
        ]
        
        # Генерация отчета
        report = engine.generate_personalized_report(simulated_results)
        
        # Сохранение в сессии
        session['learning_report'] = report
        session['report_generated_at'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'message': 'Симуляция результатов тестирования выполнена',
            'report': report
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка при симуляции: {str(e)}'
        }), 500 