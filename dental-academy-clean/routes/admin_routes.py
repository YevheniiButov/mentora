"""
Административные роуты для управления системой
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, LearningPath, Subject, Module, Lesson, UserProgress, Question, QuestionCategory, VirtualPatientScenario, VirtualPatientAttempt
from datetime import datetime
import json

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Декоратор для проверки прав администратора"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Требуются права администратора', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/', methods=['GET', 'POST'])
@login_required
@admin_required
def index():
    """Главная страница админ панели"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'upload_scenario':
            return handle_upload_scenario()
        elif action == 'create_path':
            return handle_create_path()
        elif action == 'create_lesson':
            return handle_create_lesson()
        elif action == 'create_test':
            return handle_create_test()
        elif action == 'add_user':
            return handle_add_user()
    
    # Базовая статистика
    stats = {
        'users': User.query.count(),
        'scenarios': VirtualPatientScenario.query.count(),
        'attempts': VirtualPatientAttempt.query.count(),
        'lessons': Lesson.query.count(),
        'questions': Question.query.count()
    }
    
    return render_template('admin/dashboard.html', stats=stats)

def handle_upload_scenario():
    """Обработка загрузки сценария виртуального пациента"""
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        scenario_file = request.files.get('scenario_file')
        
        if not title or not scenario_file:
            flash('Заполните все обязательные поля', 'error')
            return redirect(url_for('admin.index'))
        
        # Проверяем, что файл JSON
        if not scenario_file.filename.endswith('.json'):
            flash('Файл должен быть в формате JSON', 'error')
            return redirect(url_for('admin.index'))
        
        # Читаем и парсим JSON
        try:
            scenario_data = json.loads(scenario_file.read().decode('utf-8'))
        except json.JSONDecodeError:
            flash('Неверный формат JSON файла', 'error')
            return redirect(url_for('admin.index'))
        
        # Создаем сценарий
        scenario = VirtualPatientScenario(
            title=title,
            description=description,
            scenario_data=scenario_data,
            created_by=current_user.id,
            is_published=False
        )
        
        db.session.add(scenario)
        db.session.commit()
        
        flash(f'Сценарий "{title}" успешно загружен', 'success')
        return redirect(url_for('admin.virtual_patients'))
        
    except Exception as e:
        flash(f'Ошибка при загрузке сценария: {str(e)}', 'error')
        return redirect(url_for('admin.index'))

def handle_create_path():
    """Обработка создания пути обучения"""
    try:
        path_name = request.form.get('path_name')
        path_description = request.form.get('path_description')
        
        if not path_name:
            flash('Введите название пути обучения', 'error')
            return redirect(url_for('admin.index'))
        
        # Создаем путь обучения
        learning_path = LearningPath(
            name=path_name,
            description=path_description,
            created_by=current_user.id
        )
        
        db.session.add(learning_path)
        db.session.commit()
        
        flash(f'Путь обучения "{path_name}" создан', 'success')
        return redirect(url_for('learning_map_bp.learning_map', lang='ru'))
        
    except Exception as e:
        flash(f'Ошибка при создании пути: {str(e)}', 'error')
        return redirect(url_for('admin.index'))

def handle_create_lesson():
    """Обработка создания урока"""
    try:
        lesson_title = request.form.get('lesson_title')
        lesson_content = request.form.get('lesson_content')
        
        if not lesson_title:
            flash('Введите название урока', 'error')
            return redirect(url_for('admin.index'))
        
        # Создаем урок
        lesson = Lesson(
            title=lesson_title,
            content=lesson_content,
            created_by=current_user.id
        )
        
        db.session.add(lesson)
        db.session.commit()
        
        flash(f'Урок "{lesson_title}" создан', 'success')
        return redirect(url_for('admin.index'))
        
    except Exception as e:
        flash(f'Ошибка при создании урока: {str(e)}', 'error')
        return redirect(url_for('admin.index'))

def handle_create_test():
    """Обработка создания теста"""
    try:
        test_title = request.form.get('test_title')
        test_description = request.form.get('test_description')
        
        if not test_title:
            flash('Введите название теста', 'error')
            return redirect(url_for('admin.index'))
        
        # Создаем категорию теста
        category = QuestionCategory(
            name=test_title,
            description=test_description,
            created_by=current_user.id
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash(f'Тест "{test_title}" создан', 'success')
        return redirect(url_for('admin.index'))
        
    except Exception as e:
        flash(f'Ошибка при создании теста: {str(e)}', 'error')
        return redirect(url_for('admin.index'))

def handle_add_user():
    """Обработка добавления пользователя"""
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not name or not email or not password:
            flash('Заполните все обязательные поля', 'error')
            return redirect(url_for('admin.index'))
        
        # Проверяем, что email уникален
        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует', 'error')
            return redirect(url_for('admin.index'))
        
        # Создаем пользователя
        user = User(
            username=email,
            email=email,
            first_name=name,
            is_active=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Пользователь "{name}" добавлен', 'success')
        return redirect(url_for('admin.users'))
        
    except Exception as e:
        flash(f'Ошибка при добавлении пользователя: {str(e)}', 'error')
        return redirect(url_for('admin.index'))

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Управление пользователями"""
    users = User.query.all()
    return render_template('admin/users_manager.html', users=users)

@admin_bp.route('/virtual-patients')
@login_required
@admin_required
def virtual_patients():
    """Управление виртуальными пациентами"""
    scenarios = VirtualPatientScenario.query.order_by(VirtualPatientScenario.created_at.desc()).all()
    
    # Добавляем статистику по каждому сценарию
    scenarios_with_stats = []
    for scenario in scenarios:
        attempts_count = VirtualPatientAttempt.query.filter_by(scenario_id=scenario.id).count()
        completed_count = VirtualPatientAttempt.query.filter_by(scenario_id=scenario.id, completed=True).count()
        avg_score = db.session.query(db.func.avg(VirtualPatientAttempt.score)).filter_by(
            scenario_id=scenario.id, completed=True
        ).scalar() or 0
        
        scenarios_with_stats.append({
            'scenario': scenario,
            'attempts_count': attempts_count,
            'completed_count': completed_count,
            'avg_score': round(avg_score, 1)
        })
    
    return render_template('admin/virtual_patients.html', scenarios=scenarios_with_stats)

@admin_bp.route('/virtual-patients/<int:scenario_id>')
@login_required
@admin_required
def virtual_patient_detail(scenario_id):
    """Детальная информация о сценарии"""
    scenario = VirtualPatientScenario.query.get_or_404(scenario_id)
    
    # Получаем статистику попыток
    attempts = VirtualPatientAttempt.query.filter_by(scenario_id=scenario_id).order_by(
        VirtualPatientAttempt.started_at.desc()
    ).limit(20).all()
    
    # Статистика по результатам
    total_attempts = VirtualPatientAttempt.query.filter_by(scenario_id=scenario_id).count()
    completed_attempts = VirtualPatientAttempt.query.filter_by(scenario_id=scenario_id, completed=True).count()
    
    # Распределение по результатам
    good_results = VirtualPatientAttempt.query.filter_by(scenario_id=scenario_id, completed=True).filter(
        VirtualPatientAttempt.score >= scenario.max_score * 0.8
    ).count()
    
    average_results = VirtualPatientAttempt.query.filter_by(scenario_id=scenario_id, completed=True).filter(
        VirtualPatientAttempt.score >= scenario.max_score * 0.6,
        VirtualPatientAttempt.score < scenario.max_score * 0.8
    ).count()
    
    poor_results = VirtualPatientAttempt.query.filter_by(scenario_id=scenario_id, completed=True).filter(
        VirtualPatientAttempt.score < scenario.max_score * 0.6
    ).count()
    
    stats = {
        'total_attempts': total_attempts,
        'completed_attempts': completed_attempts,
        'completion_rate': round((completed_attempts / total_attempts * 100) if total_attempts > 0 else 0, 1),
        'good_results': good_results,
        'average_results': average_results,
        'poor_results': poor_results
    }
    
    return render_template('admin/virtual_patient_detail.html', 
                         scenario=scenario, 
                         attempts=attempts, 
                         stats=stats)

@admin_bp.route('/virtual-patients/<int:scenario_id>/toggle-publish', methods=['POST'])
@login_required
@admin_required
def toggle_scenario_publish(scenario_id):
    """Переключить статус публикации сценария"""
    scenario = VirtualPatientScenario.query.get_or_404(scenario_id)
    scenario.is_published = not scenario.is_published
    db.session.commit()
    
    status = 'опубликован' if scenario.is_published else 'снят с публикации'
    flash(f'Сценарий "{scenario.title}" {status}', 'success')
    
    return redirect(url_for('admin.virtual_patients'))

@admin_bp.route('/virtual-patients/<int:scenario_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_scenario(scenario_id):
    """Удалить сценарий"""
    scenario = VirtualPatientScenario.query.get_or_404(scenario_id)
    title = scenario.title
    
    # Удаляем связанные попытки (если CASCADE не настроен)
    VirtualPatientAttempt.query.filter_by(scenario_id=scenario_id).delete()
    
    db.session.delete(scenario)
    db.session.commit()
    
    flash(f'Сценарий "{title}" удален', 'success')
    return redirect(url_for('admin.virtual_patients'))

@admin_bp.route('/api/stats')
@login_required
@admin_required
def api_stats():
    """API для получения статистики админ панели"""
    # Статистика пользователей
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    
    # Статистика виртуальных пациентов
    total_scenarios = VirtualPatientScenario.query.count()
    published_scenarios = VirtualPatientScenario.query.filter_by(is_published=True).count()
    total_attempts = VirtualPatientAttempt.query.count()
    completed_attempts = VirtualPatientAttempt.query.filter_by(completed=True).count()
    
    # Статистика по уровням сложности
    difficulty_stats = {}
    for difficulty in ['easy', 'medium', 'hard']:
        count = VirtualPatientScenario.query.filter_by(difficulty=difficulty, is_published=True).count()
        difficulty_stats[difficulty] = count
    
    return jsonify({
        'users': {
            'total': total_users,
            'active': active_users
        },
        'virtual_patients': {
            'total_scenarios': total_scenarios,
            'published_scenarios': published_scenarios,
            'total_attempts': total_attempts,
            'completed_attempts': completed_attempts,
            'completion_rate': round((completed_attempts / total_attempts * 100) if total_attempts > 0 else 0, 1)
        },
        'difficulty_stats': difficulty_stats
    }) 