#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Learning Routes
Маршруты для простых систем обучения
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from extensions import db
from models import User, Question, UserProgress, PersonalLearningPlan
from utils.simple_spaced_repetition import SimpleSpacedRepetition, SimpleReviewScheduler
from utils.simple_weekly_adjustment import SimpleWeeklyAdjustment
from utils.simple_student_dashboard import SimpleStudentDashboard

# Создаем Blueprint
simple_learning_bp = Blueprint('simple_learning', __name__, url_prefix='/api/simple-learning')

# Инициализируем системы
spaced_repetition = SimpleSpacedRepetition()
review_scheduler = SimpleReviewScheduler(spaced_repetition)
weekly_adjustment = SimpleWeeklyAdjustment()
student_dashboard = SimpleStudentDashboard()

@simple_learning_bp.route('/spaced-repetition/calculate', methods=['POST'])
@login_required
def calculate_next_review():
    """Расчет следующего повторения для вопроса (SM-2 алгоритм)"""
    try:
        data = request.get_json()
        question_id = data.get('question_id')
        quality = data.get('quality', 3)  # Качество ответа (0-5)
        user_ability = data.get('user_ability')  # IRT способность (опционально)
        
        if not question_id:
            return jsonify({'error': 'question_id обязателен'}), 400
        
        # Валидация качества ответа
        if not isinstance(quality, int) or quality < 0 or quality > 5:
            return jsonify({'error': 'quality должен быть числом от 0 до 5'}), 400
        
        # Рассчитываем следующее повторение с SM-2
        result = spaced_repetition.calculate_next_review(
            user_id=current_user.id,
            question_id=question_id,
            quality=quality,
            user_ability=user_ability
        )
        
        return jsonify({
            'success': True,
            'next_review': result['next_review'].isoformat(),
            'interval': result['interval'],
            'ease_factor': result['ease_factor'],
            'repetitions': result['repetitions'],
            'quality': quality,
            'reason': result['reason'],
            'total_reviews': result['total_reviews'],
            'average_quality': result['average_quality']
        })
        
    except Exception as e:
        current_app.logger.error(f"Error calculating next review: {e}")
        return jsonify({'error': 'Ошибка расчета повторения'}), 500

@simple_learning_bp.route('/spaced-repetition/due-reviews', methods=['GET'])
@login_required
def get_due_reviews():
    """Получение вопросов, готовых к повторению"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        # Получаем вопросы для повторения
        due_reviews = spaced_repetition.get_due_reviews(
            user_id=current_user.id,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'due_reviews': due_reviews,
            'count': len(due_reviews)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting due reviews: {e}")
        return jsonify({'error': 'Ошибка получения повторений'}), 500

@simple_learning_bp.route('/spaced-repetition/schedule', methods=['POST'])
@login_required
def schedule_daily_reviews():
    """Планирование ежедневных повторений"""
    try:
        data = request.get_json()
        available_time = data.get('available_time', 30)  # минуты
        
        # Планируем повторения
        scheduled_reviews = review_scheduler.schedule_daily_reviews(
            user_id=current_user.id,
            available_time=available_time
        )
        
        return jsonify({
            'success': True,
            'scheduled_reviews': scheduled_reviews,
            'estimated_time': len(scheduled_reviews) * 2  # 2 минуты на вопрос
        })
        
    except Exception as e:
        current_app.logger.error(f"Error scheduling reviews: {e}")
        return jsonify({'error': 'Ошибка планирования повторений'}), 500

@simple_learning_bp.route('/spaced-repetition/statistics', methods=['GET'])
@login_required
def get_review_statistics():
    """Получение статистики повторений"""
    try:
        days = request.args.get('days', 30, type=int)
        
        # Получаем статистику
        stats = spaced_repetition.get_review_statistics(
            user_id=current_user.id,
            days=days
        )
        
        # Получаем статистику по доменам
        domain_stats = spaced_repetition.get_domain_statistics(
            user_id=current_user.id,
            days=days
        )
        
        # Получаем рекомендации
        recommendations = review_scheduler.get_review_recommendations(
            user_id=current_user.id
        )
        
        return jsonify({
            'success': True,
            'statistics': stats,
            'domain_statistics': domain_stats,
            'recommendations': recommendations
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting review statistics: {e}")
        return jsonify({'error': 'Ошибка получения статистики'}), 500

@simple_learning_bp.route('/weekly-adjustment/analyze', methods=['GET'])
@login_required
def analyze_weekly_progress():
    """Анализ еженедельного прогресса"""
    try:
        # Анализируем прогресс
        analysis = weekly_adjustment.analyze_weekly_progress(
            user_id=current_user.id
        )
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        current_app.logger.error(f"Error analyzing weekly progress: {e}")
        return jsonify({'error': 'Ошибка анализа прогресса'}), 500

@simple_learning_bp.route('/weekly-adjustment/adjust', methods=['POST'])
@login_required
def adjust_plan():
    """Корректировка плана обучения"""
    try:
        # Корректируем план
        result = weekly_adjustment.adjust_plan_if_needed(
            user_id=current_user.id
        )
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error adjusting plan: {e}")
        return jsonify({'error': 'Ошибка корректировки плана'}), 500

@simple_learning_bp.route('/weekly-adjustment/increase-questions', methods=['GET'])
@login_required
def increase_daily_questions():
    """Увеличение количества ежедневных вопросов"""
    try:
        # Получаем рекомендации по увеличению нагрузки
        result = weekly_adjustment.increase_daily_questions(
            user_id=current_user.id
        )
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error increasing questions: {e}")
        return jsonify({'error': 'Ошибка увеличения вопросов'}), 500

@simple_learning_bp.route('/weekly-adjustment/report', methods=['GET'])
@login_required
def get_weekly_report():
    """Получение еженедельного отчета"""
    try:
        # Получаем отчет
        report = weekly_adjustment.get_weekly_report(
            user_id=current_user.id
        )
        
        return jsonify({
            'success': True,
            'report': report
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting weekly report: {e}")
        return jsonify({'error': 'Ошибка получения отчета'}), 500

@simple_learning_bp.route('/dashboard', methods=['GET'])
@login_required
def get_dashboard():
    """Получение дашборда студента"""
    try:
        # Получаем дашборд
        dashboard = student_dashboard.get_dashboard(current_user.id)
        
        # Получаем информацию о серии обучения
        streak_info = student_dashboard.get_streak_info(current_user.id)
        
        return jsonify({
            'success': True,
            'dashboard': dashboard,
            'streak_info': streak_info
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting dashboard: {e}")
        return jsonify({'error': 'Ошибка получения дашборда'}), 500

@simple_learning_bp.route('/dashboard/progress-chart', methods=['GET'])
@login_required
def get_progress_chart():
    """Получение данных для графика прогресса"""
    try:
        days = request.args.get('days', 30, type=int)
        
        # Получаем данные для графика
        chart_data = student_dashboard.get_progress_chart(
            user_id=current_user.id,
            days=days
        )
        
        return jsonify({
            'success': True,
            'chart_data': chart_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting progress chart: {e}")
        return jsonify({'error': 'Ошибка получения графика'}), 500

@simple_learning_bp.route('/dashboard/domain-progress', methods=['GET'])
@login_required
def get_domain_progress():
    """Получение прогресса по доменам"""
    try:
        # Получаем прогресс по доменам
        domain_progress = student_dashboard.get_domain_progress(
            user_id=current_user.id
        )
        
        return jsonify({
            'success': True,
            'domain_progress': domain_progress
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting domain progress: {e}")
        return jsonify({'error': 'Ошибка получения прогресса по доменам'}), 500

# Тестовые маршруты для демонстрации
@simple_learning_bp.route('/test/spaced-repetition', methods=['GET'])
@login_required
def test_spaced_repetition():
    """Тестовый маршрут для демонстрации spaced repetition (SM-2)"""
    try:
        # Симулируем ответы на вопросы с разным качеством
        test_results = []
        
        # Тест 1: Правильный ответ (качество 5)
        result1 = spaced_repetition.calculate_next_review(
            user_id=current_user.id,
            question_id=1,
            quality=5
        )
        test_results.append({
            'test': 'Правильный ответ (качество 5)',
            'result': result1
        })
        
        # Тест 2: Частично правильный ответ (качество 3)
        result2 = spaced_repetition.calculate_next_review(
            user_id=current_user.id,
            question_id=2,
            quality=3
        )
        test_results.append({
            'test': 'Частично правильный ответ (качество 3)',
            'result': result2
        })
        
        # Тест 3: Неправильный ответ (качество 1)
        result3 = spaced_repetition.calculate_next_review(
            user_id=current_user.id,
            question_id=3,
            quality=1
        )
        test_results.append({
            'test': 'Неправильный ответ (качество 1)',
            'result': result3
        })
        
        return jsonify({
            'success': True,
            'test_results': test_results,
            'message': 'Тест SM-2 алгоритма выполнен успешно'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error testing spaced repetition: {e}")
        return jsonify({'error': 'Ошибка тестирования'}), 500

@simple_learning_bp.route('/test/weekly-adjustment', methods=['GET'])
@login_required
def test_weekly_adjustment():
    """Тестовый маршрут для демонстрации weekly adjustment"""
    try:
        # Анализируем прогресс
        analysis = weekly_adjustment.analyze_weekly_progress(
            user_id=current_user.id
        )
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'message': 'Тест weekly adjustment выполнен успешно'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error testing weekly adjustment: {e}")
        return jsonify({'error': 'Ошибка тестирования'}), 500

@simple_learning_bp.route('/test/dashboard', methods=['GET'])
@login_required
def test_dashboard():
    """Тестовый маршрут для демонстрации dashboard"""
    try:
        # Генерируем dashboard
        dashboard = student_dashboard.generate_dashboard(
            user_id=current_user.id
        )
        
        return jsonify({
            'success': True,
            'dashboard': dashboard,
            'message': 'Тест dashboard выполнен успешно'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error testing dashboard: {e}")
        return jsonify({'error': 'Ошибка тестирования'}), 500 