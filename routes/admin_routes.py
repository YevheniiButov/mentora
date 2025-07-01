# routes/admin_routes.py

import sys
from flask import (
    Blueprint, render_template, request, redirect, url_for, session, flash, g, current_app, jsonify, 
    make_response, send_file # Добавлены jsonify, make_response, send_file
    )
from flask_login import login_required, current_user
from models import db, User, Module, Lesson, LearningPath, Subject, Question # Убраны несуществующие модели
from werkzeug.utils import secure_filename # Добавлено для работы с xray_upload
import os
import json
from datetime import datetime, timedelta
from models import VirtualPatientScenario
from utils.decorators import admin_required

admin_bp = Blueprint(
    "admin_bp",
    __name__,
    url_prefix='/<string:lang>/admin', # Префикс для всех маршрутов блюпринта
    template_folder='../templates/admin' # Явно указываем папку шаблонов админки
    )

# --- Обработчик для проверки доступа к админке ---
# Выполняется перед каждым запросом к этому блюпринту
@admin_bp.before_request
def before_request_admin_check():
    """
    Проверяет, авторизован ли пользователь и является ли он админом.
    Язык уже должен быть установлен глобальным обработчиком в g.lang.
    """
    # Получаем язык из g (установлен в app.py)
    current_lang = getattr(g, 'lang', current_app.config['DEFAULT_LANGUAGE'])

    # Проверка авторизации
    if not current_user.is_authenticated:
        flash("Please log in to access this page.", "warning")
        # url_for здесь корректен
        login_url = url_for('auth_bp.login', lang=current_lang, next=request.url) # Используем request.url для next
        return redirect(login_url)

    # Проверка прав админа
    if not current_user.role == 'admin':
        flash("You do not have permission to access the admin area.", "danger")
        # url_for здесь корректен
        return redirect(url_for('main_bp.profile', lang=current_lang)) # Редирект на профиль

    # Если проверки пройдены, запрос продолжается к view-функции

# --- Контекстный процессор для админки ---
@admin_bp.context_processor
def inject_admin_context():
    """Добавляет lang и current_user в контекст шаблонов админки."""
    lang = getattr(g, 'lang', current_app.config['DEFAULT_LANGUAGE'])
    # Передаем current_user напрямую
    return dict(lang=lang, current_user=current_user)

# --- Маршруты админки ---

# Путь: /<lang>/admin/dashboard
@admin_bp.route("/dashboard")
def dashboard(lang):
    """Отображает главную панель админки с краткой статистикой."""
    g.lang = lang
    
    # Получаем статистику
    total_users = User.query.count()
    total_modules = Module.query.count()
    total_lessons = Lesson.query.count()
    total_questions = Question.query.count()
    total_learning_paths = LearningPath.query.count()
    total_subjects = Subject.query.count()
    virtual_patients = VirtualPatientScenario.query.count()
    achievements = 0  # Пока не реализовано
    
    # Статистика форума (пока заглушка)
    forum_topics = 0
    forum_posts = 0
    
    # Последние 5 зарегистрированных пользователей
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # Популярные модули (пока заглушка)
    popular_modules = []
    
    stats = {
        'total_users': total_users,
        'total_modules': total_modules,
        'total_lessons': total_lessons,
        'total_questions': total_questions,
        'total_learning_paths': total_learning_paths,
        'total_subjects': total_subjects,
        'virtual_patients': virtual_patients,
        'achievements': achievements,
        'forum_topics': forum_topics,
        'forum_posts': forum_posts
    }
    
    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_users=recent_users,
        popular_modules=popular_modules
    )

# Путь: /<lang>/admin/ai-analytics
@admin_bp.route("/ai-analytics")
@login_required
@admin_required
def ai_analytics_dashboard(lang):
    """Отображает дашборд аналитики ИИ системы."""
    return render_template("ai_analytics_dashboard.html")

@admin_bp.route('/api/import-scenarios', methods=['POST'])
@login_required
@admin_required
def import_scenarios(lang):
    g.lang = lang
    try:
        if 'scenarios_file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'Файл не найден в запросе'
            }), 400
            
        file = request.files['scenarios_file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'Файл не выбран'
            }), 400
            
        replace_existing = request.form.get('replace_existing') == 'true'
        
        # Чтение и парсинг JSON
        try:
            file_content = file.read().decode('utf-8')
            scenarios_data = json.loads(file_content)
            
            if not isinstance(scenarios_data, list):
                # Возможно, это один сценарий, а не список
                if isinstance(scenarios_data, dict):
                    scenarios_data = [scenarios_data]
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Некорректный формат JSON. Ожидается список сценариев или один сценарий.'
                    }), 400
                
        except json.JSONDecodeError:
            return jsonify({
                'success': False,
                'message': 'Некорректный JSON-файл'
            }), 400
            
        # Импорт сценариев
        imported_count = 0
        skipped_count = 0
        
        # Если выбрана замена существующих, удаляем все сценарии
        if replace_existing:
            VirtualPatientScenario.query.delete()
            db.session.commit()
        
        # Импорт сценариев
        for scenario_item in scenarios_data:
            # Проверяем, что элемент является словарем
            if not isinstance(scenario_item, dict):
                skipped_count += 1
                continue
                
            # Нормализация заголовка
            title = scenario_item.get('title', 'Безымянный сценарий')
            if isinstance(title, dict):
                # Если заголовок - словарь с переводами, берем английскую версию
                title_str = title.get('en', next(iter(title.values())))
            else:
                title_str = str(title)
            
            # Нормализация описания
            description = scenario_item.get('description', '')
            if isinstance(description, dict):
                description_str = description.get('en', next(iter(description.values()) if description else ''))
            else:
                description_str = str(description)
                
            # Проверяем существование сценария с таким заголовком
            existing_scenario = VirtualPatientScenario.query.filter_by(title=title_str).first()
            
            if existing_scenario and not replace_existing:
                # Пропускаем существующий сценарий
                skipped_count += 1
                continue
                
            # Получаем и нормализуем scenario_data
            scenario_data_obj = {}
            
            # Проверяем, есть ли ключ scenario_data в импортируемом сценарии
            if 'scenario_data' in scenario_item:
                raw_data = scenario_item['scenario_data']
                
                # Нормализация данных сценария
                if isinstance(raw_data, str):
                    try:
                        # Если это строка JSON, пытаемся ее распарсить
                        scenario_data_obj = json.loads(raw_data)
                    except json.JSONDecodeError:
                        # Если не удалось распарсить, создаем стандартную структуру
                        scenario_data_obj = {
                            "translations": {
                                "en": {
                                    "patient_info": {
                                        "name": title_str,
                                        "age": scenario_item.get('age', 30),
                                        "gender": scenario_item.get('gender', 'male'),
                                        "image": scenario_item.get('image', 'patient_default.jpg'),
                                        "medical_history": scenario_item.get('medical_history', 'Нет данных')
                                    },
                                    "initial_state": {
                                        "patient_statement": scenario_item.get('initial_statement', 'Здравствуйте, доктор'),
                                        "patient_emotion": scenario_item.get('emotion', 'neutral'),
                                        "notes": scenario_item.get('notes', 'Первичный прием')
                                    },
                                    "dialogue_nodes": scenario_item.get('dialogue_nodes', []),
                                    "outcomes": {
                                        "good": {
                                            "title": "Отличная диагностика!",
                                            "text": "Вы проявили отличные навыки диагностики."
                                        },
                                        "average": {
                                            "title": "Хорошая попытка",
                                            "text": "Есть аспекты, требующие улучшения."
                                        },
                                        "poor": {
                                            "title": "Требуется практика",
                                            "text": "Рекомендуется повторить материал."
                                        }
                                    }
                                }
                            }
                        }
                elif isinstance(raw_data, dict):
                    # Если это уже словарь, проверяем его структуру
                    if "translations" in raw_data and isinstance(raw_data["translations"], dict):
                        # Если уже в формате с переводами, используем как есть
                        scenario_data_obj = raw_data
                    else:
                        # Если это словарь, но без структуры переводов, оборачиваем его
                        scenario_data_obj = {
                            "translations": {
                                "en": raw_data
                            }
                        }
            else:
                # Если нет ключа scenario_data, создаем базовую структуру
                dialogue_nodes = []
                
                # Пытаемся извлечь узлы диалога из других полей
                if "dialogue_nodes" in scenario_item and isinstance(scenario_item["dialogue_nodes"], list):
                    dialogue_nodes = scenario_item["dialogue_nodes"]
                    
                # Создаем стандартную структуру
                scenario_data_obj = {
                    "translations": {
                        "en": {
                            "patient_info": {
                                "name": title_str,
                                "age": scenario_item.get('age', 30),
                                "gender": scenario_item.get('gender', 'male'),
                                "image": scenario_item.get('image', 'patient_default.jpg'),
                                "medical_history": scenario_item.get('medical_history', 'Нет данных')
                            },
                            "initial_state": {
                                "patient_statement": scenario_item.get('initial_statement', 'Здравствуйте, доктор'),
                                "patient_emotion": scenario_item.get('emotion', 'neutral'),
                                "notes": scenario_item.get('notes', 'Первичный прием')
                            },
                            "dialogue_nodes": dialogue_nodes,
                            "outcomes": {
                                "good": {
                                    "title": "Отличная диагностика!",
                                    "text": "Вы проявили отличные навыки диагностики."
                                },
                                "average": {
                                    "title": "Хорошая попытка",
                                    "text": "Есть аспекты, требующие улучшения."
                                },
                                "poor": {
                                    "title": "Требуется практика",
                                    "text": "Рекомендуется повторить материал."
                                }
                            }
                        }
                    }
                }
            
            # Создаем или обновляем сценарий
            if existing_scenario and replace_existing:
                existing_scenario.title = title_str
                existing_scenario.description = description_str
                existing_scenario.difficulty = scenario_item.get('difficulty', 'medium')
                existing_scenario.category = scenario_item.get('category', '')
                existing_scenario.timeframe = scenario_item.get('timeframe', 0)
                existing_scenario.max_score = scenario_item.get('max_score', 100)
                existing_scenario.is_premium = scenario_item.get('is_premium', False)
                existing_scenario.is_published = scenario_item.get('is_published', False)
                existing_scenario.scenario_data = json.dumps(scenario_data_obj)
                scenario = existing_scenario
            else:
                scenario = VirtualPatientScenario(
                    title=title_str,
                    description=description_str,
                    difficulty=scenario_item.get('difficulty', 'medium'),
                    category=scenario_item.get('category', ''),
                    timeframe=scenario_item.get('timeframe', 0),
                    max_score=scenario_item.get('max_score', 100),
                    is_premium=scenario_item.get('is_premium', False),
                    is_published=scenario_item.get('is_published', False),
                    scenario_data=json.dumps(scenario_data_obj)
                )
                db.session.add(scenario)
                
            # Увеличиваем счетчик импортированных сценариев
            imported_count += 1
            
        # Сохраняем изменения в базе данных
        db.session.commit()
        
        # Выводим отладочную информацию о последнем импортированном сценарии
        last_scenario = VirtualPatientScenario.query.order_by(VirtualPatientScenario.id.desc()).first()
        if last_scenario:
            print("="*50)
            print("Импортирован сценарий ID:", last_scenario.id)
            print("Заголовок:", last_scenario.title)
            print("Тип данных scenario_data:", type(last_scenario.scenario_data))
            print("Первые 200 символов данных:", str(last_scenario.scenario_data)[:200])
            print("="*50)
            
        return jsonify({
            'success': True,
            'imported_count': imported_count,
            'skipped_count': skipped_count
        })
    except Exception as e:
        db.session.rollback()
        # Добавляем детальную информацию об ошибке
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in import_scenarios: {error_details}")
        
        return jsonify({
            'success': False,
            'message': str(e),
            'details': error_details
        }), 500

@admin_bp.route('/api/export-scenarios', methods=['GET'])
@login_required
@admin_required
def export_scenarios(lang):
    g.lang = lang
    try:
        export_option = request.args.get('option', 'all')
        
        # Определяем, какие сценарии экспортировать
        if export_option == 'published':
            scenarios = VirtualPatientScenario.query.filter_by(is_published=True).all()
        elif export_option == 'selected':
            selected_ids = request.args.get('ids', '').split(',')
            selected_ids = [int(id) for id in selected_ids if id.isdigit()]
            scenarios = VirtualPatientScenario.query.filter(VirtualPatientScenario.id.in_(selected_ids)).all()
        else:
            scenarios = VirtualPatientScenario.query.all()
            
        # Формируем данные для экспорта
        export_data = []
        for scenario in scenarios:
            # Формируем структуру данных для экспорта
            scenario_dict = {
                'id': scenario.id,
                'title': scenario.title,
                'description': scenario.description,
                'difficulty': scenario.difficulty,
                'category': scenario.category,
                'timeframe': scenario.timeframe,
                'max_score': scenario.max_score,
                'is_premium': scenario.is_premium,
                'is_published': scenario.is_published,
                'scenario_data': json.loads(scenario.scenario_data)
            }
            export_data.append(scenario_dict)
            
        # Создаем JSON-ответ для скачивания
        response = jsonify(export_data)
        response.headers['Content-Disposition'] = 'attachment; filename=scenarios_export.json'
        return response
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    
# --- УПРАВЛЕНИЕ ИЕРАРХИЕЙ КОНТЕНТА ---
@admin_bp.route("/hierarchy")
def hierarchy_manager(lang):
    """Отображает интерфейс управления иерархией контента."""
    # Получаем данные для иерархии
    learning_paths = LearningPath.query.order_by(LearningPath.order).all()
    subjects = Subject.query.order_by(Subject.order).all()
    modules = Module.query.order_by(Module.order).all()
    
    return render_template(
        'hierarchy_manager.html',
        learning_paths=learning_paths,
        subjects=subjects,
        modules=modules
    )

# --- API для управления иерархией ---
@admin_bp.route("/api/add-path", methods=["POST"])
def add_path(lang):
    """Добавление новой категории обучения (LearningPath)."""
    current_lang = g.lang
    try:
        name = request.form.get('name')
        description = request.form.get('description', '')
        order = int(request.form.get('order', 0))
        icon = request.form.get('icon', 'list-task')
        
        if not name:
            flash("Название категории обязательно", "danger")
            return redirect(url_for(".hierarchy_manager", lang=current_lang))
            
        new_path = LearningPath(
            name=name,
            description=description,
            order=order,
            icon=icon
        )
        db.session.add(new_path)
        db.session.commit()
        
        flash("Категория успешно добавлена", "success")
        return redirect(url_for('.hierarchy_manager', lang=current_lang))
    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при добавлении категории: {str(e)}", "danger")
        return redirect(url_for('.hierarchy_manager', lang=current_lang))

@admin_bp.route("/explorer")
def hierarchy_explorer(lang):
    """Отображает интерфейс проводника для управления иерархией контента."""
    # Получаем все данные для древовидной структуры
    learning_paths = LearningPath.query.order_by(LearningPath.order).all()
    subjects = Subject.query.order_by(Subject.order).all()
    modules = Module.query.order_by(Module.order).all()
    lessons = Lesson.query.order_by(Lesson.order).all()
    
    return render_template(
        'hierarchy_explorer.html',
        learning_paths=learning_paths,
        subjects=subjects,
        modules=modules,
        lessons=lessons
    )

@admin_bp.route("/api/update-path", methods=["POST"])
def update_path(lang):
    """Обновление категории обучения (LearningPath)."""
    current_lang = g.lang
    try:
        path_id = request.form.get('path_id')
        name = request.form.get('name')
        description = request.form.get('description', '')
        order = request.form.get('order')
        icon = request.form.get('icon')
        
        if not path_id or not name:
            flash("ID и название категории обязательны", "danger")
            return redirect(url_for(".hierarchy_manager", lang=current_lang))
            
        path = LearningPath.query.get(path_id)
        if not path:
            flash(f"Категория с ID {path_id} не найдена", "danger")
            return redirect(url_for(".hierarchy_manager", lang=current_lang))
            
        path.name = name
        path.description = description
        if order is not None:
            path.order = int(order)
        if icon:
            path.icon = icon
            
        db.session.commit()
        
        flash("Категория успешно обновлена", "success")
        return redirect(url_for('.hierarchy_manager', lang=current_lang))
    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при обновлении категории: {str(e)}", "danger")
        return redirect(url_for('.hierarchy_manager', lang=current_lang))

@admin_bp.route("/api/delete-path/<int:path_id>", methods=["DELETE"])
def delete_path(lang, path_id):
    """Удаление категории обучения (LearningPath)."""
    try:
        path = LearningPath.query.get(path_id)
        if not path:
            return jsonify({"success": False, "message": f"Категория с ID {path_id} не найдена"}), 404
            
        db.session.delete(path)
        db.session.commit()
        
        return jsonify({"success": True, "message": "Категория успешно удалена"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Ошибка при удалении категории: {str(e)}"}), 500

@admin_bp.route("/api/add-subject", methods=["POST"])
def add_subject(lang):
    """Добавление нового предмета (Subject)."""
    current_lang = g.lang
    try:
        name = request.form.get('name')
        description = request.form.get('description', '')
        learning_path_id = request.form.get('learning_path_id')
        order = int(request.form.get('order', 0))
        icon = request.form.get('icon', 'folder2-open')
        
        if not name or not learning_path_id:
            flash("Название предмета и категория обязательны", "danger")
            return redirect(url_for(".hierarchy_manager", lang=current_lang))
            
        # Проверка существования категории
        learning_path = LearningPath.query.get(learning_path_id)
        if not learning_path:
            flash(f"Категория с ID {learning_path_id} не найдена", "danger")
            return redirect(url_for(".hierarchy_manager", lang=current_lang))
            
        new_subject = Subject(
            name=name,
            description=description,
            learning_path_id=learning_path_id,
            order=order,
            icon=icon
        )
        db.session.add(new_subject)
        db.session.commit()
        
        flash("Предмет успешно добавлен", "success")
        return redirect(url_for('.hierarchy_manager', lang=current_lang))
    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при добавлении предмета: {str(e)}", "danger")
        return redirect(url_for('.hierarchy_manager', lang=current_lang))

@admin_bp.route("/api/update-subject", methods=["POST"])
def update_subject(lang):
    """Обновление предмета (Subject)."""
    current_lang = g.lang
    try:
        subject_id = request.form.get('subject_id')
        name = request.form.get('name')
        description = request.form.get('description', '')
        learning_path_id = request.form.get('learning_path_id')
        order = request.form.get('order')
        icon = request.form.get('icon')
        
        if not subject_id or not name or not learning_path_id:
            flash("ID, название предмета и категория обязательны", "danger")
            return redirect(url_for(".hierarchy_manager", lang=current_lang))
            
        subject = Subject.query.get(subject_id)
        if not subject:
            flash(f"Предмет с ID {subject_id} не найден", "danger")
            return redirect(url_for(".hierarchy_manager", lang=current_lang))
            
        subject.name = name
        subject.description = description
        subject.learning_path_id = learning_path_id
        if order is not None:
            subject.order = int(order)
        if icon:
            subject.icon = icon
            
        db.session.commit()
        
        flash("Предмет успешно обновлен", "success")
        return redirect(url_for('.hierarchy_manager', lang=current_lang))
    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при обновлении предмета: {str(e)}", "danger")
        return redirect(url_for('.hierarchy_manager', lang=current_lang))

@admin_bp.route("/api/delete-subject/<int:subject_id>", methods=["DELETE"])
def delete_subject(lang, subject_id):
    """Удаление предмета (Subject)."""
    try:
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({"success": False, "message": f"Предмет с ID {subject_id} не найден"}), 404
            
        db.session.delete(subject)
        db.session.commit()
        
        return jsonify({"success": True, "message": "Предмет успешно удален"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Ошибка при удалении предмета: {str(e)}"}), 500

@admin_bp.route("/api/add-module", methods=["POST"])
def add_module(lang):
    """Добавление нового модуля (Module)."""
    current_lang = g.lang
    try:
        title = request.form.get('title')
        description = request.form.get('description', '')
        subject_id = request.form.get('subject_id')
        module_type = request.form.get('module_type', 'content')
        order = int(request.form.get('order', 0))
        icon = request.form.get('icon', 'file-earmark-text')
        is_premium = request.form.get('is_premium') == 'on'
        is_final_test = request.form.get('is_final_test') == 'on'
        
        if not title or not subject_id:
            flash("Название модуля и предмет обязательны", "danger")
            return redirect(url_for(".hierarchy_manager", lang=current_lang))
            
        # Проверка существования предмета
        subject = Subject.query.get(subject_id)
        if not subject:
            flash(f"Предмет с ID {subject_id} не найден", "danger")
            return redirect(url_for(".hierarchy_manager", lang=current_lang))
            
        new_module = Module(
            title=title,
            description=description,
            subject_id=subject_id,
            module_type=module_type,
            order=order,
            icon=icon,
            is_premium=is_premium,
            is_final_test=is_final_test
        )
        db.session.add(new_module)
        db.session.commit()
        
        flash("Модуль успешно добавлен", "success")
        return redirect(url_for('.hierarchy_manager', lang=current_lang))
    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при добавлении модуля: {str(e)}", "danger")
        return redirect(url_for('.hierarchy_manager', lang=current_lang))

@admin_bp.route("/api/update-module", methods=["POST"])
def update_module(lang):
    """Обновление модуля (Module)."""
    current_lang = g.lang
    try:
        module_id = request.form.get('module_id')
        title = request.form.get('title')
        description = request.form.get('description', '')
        subject_id = request.form.get('subject_id')
        module_type = request.form.get('module_type')
        order = request.form.get('order')
        icon = request.form.get('icon')
        is_premium = request.form.get('is_premium') == 'on'
        is_final_test = request.form.get('is_final_test') == 'on'
        
        if not module_id or not title or not subject_id:
            flash("ID, название модуля и предмет обязательны", "danger")
            return redirect(url_for(".hierarchy_manager", lang=current_lang))
            
        module = Module.query.get(module_id)
        if not module:
            flash(f"Модуль с ID {module_id} не найден", "danger")
            return redirect(url_for(".hierarchy_manager", lang=current_lang))
            
        module.title = title
        module.description = description
        module.subject_id = subject_id
        if module_type:
            module.module_type = module_type
        if order is not None:
            module.order = int(order)
        if icon:
            module.icon = icon
        module.is_premium = is_premium
        module.is_final_test = is_final_test
            
        db.session.commit()
        
        flash("Модуль успешно обновлен", "success")
        return redirect(url_for('.hierarchy_manager', lang=current_lang))
    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при обновлении модуля: {str(e)}", "danger")
        return redirect(url_for('.hierarchy_manager', lang=current_lang))

@admin_bp.route("/api/delete-module/<int:module_id>", methods=["DELETE"])
def delete_module_api(lang, module_id):
    """Удаление модуля (Module) через API."""
    try:
        module = Module.query.get(module_id)
        if not module:
            return jsonify({"success": False, "message": f"Модуль с ID {module_id} не найден"}), 404
            
        db.session.delete(module)
        db.session.commit()
        
        return jsonify({"success": True, "message": "Модуль успешно удален"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Ошибка при удалении модуля: {str(e)}"}), 500

# --- Импорт/экспорт JSON ---
@admin_bp.route("/import-json", methods=["POST"])
def import_json(lang):
    """Импорт данных из JSON-файла."""
    current_lang = g.lang
    if 'json_file' not in request.files:
        flash("Файл не был предоставлен", "danger")
        return redirect(url_for('.hierarchy_manager', lang=current_lang))
    
    file = request.files['json_file']
    
    if file.filename == '':
        flash("Файл не выбран", "danger")
        return redirect(url_for('.hierarchy_manager', lang=current_lang))
    
    if not file.filename.endswith('.json'):
        flash("Файл должен быть в формате JSON", "danger")
        return redirect(url_for('.hierarchy_manager', lang=current_lang))
    
    try:
        # Чтение и парсинг JSON
        content = file.read()
        data = json.loads(content)
        
        import_type = request.form.get('import_type', 'all')
        replace_existing = 'replace_existing' in request.form
        
        # Проверяем формат данных
        if isinstance(data, list):
            # Если данные в формате списка, преобразуем в словарь
            formatted_data = {}
            
            # Определяем тип данных в списке
            if data and isinstance(data[0], dict):
                if 'name' in data[0] and 'icon' in data[0]:
                    formatted_data['learning_paths'] = data
                elif 'learning_path_id' in data[0]:
                    formatted_data['subjects'] = data
                elif 'subject_id' in data[0]:
                    formatted_data['modules'] = data
                elif 'module_id' in data[0]:
                    formatted_data['lessons'] = data
                else:
                    # Если не удалось определить тип
                    formatted_data[import_type + 's'] = data
            
            data = formatted_data
        
        # Обработка импорта в зависимости от типа
        if import_type == 'paths' or import_type == 'all':
            paths_data = data.get('learning_paths', []) if isinstance(data, dict) else []
            import_learning_paths(paths_data, replace_existing)
            
        if import_type == 'subjects' or import_type == 'all':
            subjects_data = data.get('subjects', []) if isinstance(data, dict) else []
            import_subjects(subjects_data, replace_existing)
            
        if import_type == 'modules' or import_type == 'all':
            modules_data = data.get('modules', []) if isinstance(data, dict) else []
            import_modules(modules_data, replace_existing)
            
        if import_type == 'lessons' or import_type == 'all':
            lessons_data = data.get('lessons', []) if isinstance(data, dict) else []
            import_lessons(lessons_data, replace_existing)
        
        flash(f"Импорт JSON успешно выполнен для типа: {import_type}", "success")
        return redirect(url_for('.hierarchy_manager', lang=current_lang))
    
    except json.JSONDecodeError:
        flash("Ошибка: Некорректный формат JSON", "danger")
        return redirect(url_for('.hierarchy_manager', lang=current_lang))
    
    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при импорте: {str(e)}", "danger")
        return redirect(url_for('.hierarchy_manager', lang=current_lang))

@admin_bp.route("/export-json", methods=["POST"])
def export_json(lang):
    """Экспорт данных в JSON-файл."""
    try:
        export_type = request.form.get('export_type', 'all')
        export_format = request.form.get('export_format', 'pretty')
        
        # Подготовка данных для экспорта
        export_data = {}
        
        if export_type == 'paths' or export_type == 'all':
            paths = LearningPath.query.all()
            export_data['learning_paths'] = [
                {
                    'id': path.id,
                    'name': path.name,
                    'description': path.description,
                    'order': path.order,
                    'icon': path.icon
                } for path in paths
            ]
            
        if export_type == 'subjects' or export_type == 'all':
            subjects = Subject.query.all()
            export_data['subjects'] = [
                {
                    'id': subject.id,
                    'name': subject.name,
                    'description': subject.description,
                    'order': subject.order,
                    'icon': subject.icon,
                    'learning_path_id': subject.learning_path_id
                } for subject in subjects
            ]
            
        if export_type == 'modules' or export_type == 'all':
            modules = Module.query.all()
            export_data['modules'] = [
                {
                    'id': module.id,
                    'title': module.title,
                    'description': module.description,
                    'order': module.order,
                    'icon': module.icon,
                    'module_type': module.module_type,
                    'is_premium': module.is_premium,
                    'is_final_test': module.is_final_test,
                    'subject_id': module.subject_id
                } for module in modules
            ]
            
        if export_type == 'lessons' or export_type == 'all':
            lessons = Lesson.query.all()
            export_data['lessons'] = [
                {
                    'id': lesson.id,
                    'title': lesson.title,
                    'content_type': lesson.content_type,
                    'content': lesson.content,
                    'order': lesson.order,
                    'module_id': lesson.module_id
                } for lesson in lessons
            ]
        
        # Форматирование JSON
        indent = 4 if export_format == 'pretty' else None
        json_data = json.dumps(export_data, indent=indent, ensure_ascii=False)
        
        # Создание файла для скачивания
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"export_{export_type}_{timestamp}.json"
        
        # Отправка ответа с файлом
        response = make_response(json_data)
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
        
    except Exception as e:
        flash(f"Ошибка при экспорте: {str(e)}", "danger")
        return redirect(url_for('.hierarchy_manager', lang=lang))

# Вспомогательные функции для импорта данных
def import_learning_paths(paths_data, replace_existing):
    for path_data in paths_data:
        path_id = path_data.get('id')
        
        if path_id:
            # Проверка существования
            existing_path = LearningPath.query.get(path_id)
            
            if existing_path:
                if replace_existing:
                    # Обновляем существующий
                    existing_path.name = path_data.get('name', existing_path.name)
                    existing_path.description = path_data.get('description', existing_path.description)
                    existing_path.order = path_data.get('order', existing_path.order)
                    existing_path.icon = path_data.get('icon', existing_path.icon)
            else:
                # Создаем новый с указанным ID
                new_path = LearningPath(
                    id=path_id,
                    name=path_data.get('name', ''),
                    description=path_data.get('description', ''),
                    order=path_data.get('order', 0),
                    icon=path_data.get('icon', 'list-task')
                )
                db.session.add(new_path)
        else:
            # Создаем новый без ID
            new_path = LearningPath(
                name=path_data.get('name', ''),
                description=path_data.get('description', ''),
                order=path_data.get('order', 0),
                icon=path_data.get('icon', 'list-task')
            )
            db.session.add(new_path)
    
    db.session.commit()

def import_subjects(subjects_data, replace_existing):
    for subject_data in subjects_data:
        subject_id = subject_data.get('id')
        
        if subject_id:
            # Проверка существования
            existing_subject = Subject.query.get(subject_id)
            
            if existing_subject:
                if replace_existing:
                    # Обновляем существующий
                    existing_subject.name = subject_data.get('name', existing_subject.name)
                    existing_subject.description = subject_data.get('description', existing_subject.description)
                    existing_subject.learning_path_id = subject_data.get('learning_path_id', existing_subject.learning_path_id)
                    existing_subject.order = subject_data.get('order', existing_subject.order)
                    existing_subject.icon = subject_data.get('icon', existing_subject.icon)
            else:
                # Создаем новый с указанным ID
                new_subject = Subject(
                    id=subject_id,
                    name=subject_data.get('name', ''),
                    description=subject_data.get('description', ''),
                    learning_path_id=subject_data.get('learning_path_id'),
                    order=subject_data.get('order', 0),
                    icon=subject_data.get('icon', 'folder2-open')
                )
                db.session.add(new_subject)
        else:
            # Создаем новый без ID
            new_subject = Subject(
                name=subject_data.get('name', ''),
                description=subject_data.get('description', ''),
                learning_path_id=subject_data.get('learning_path_id'),
                order=subject_data.get('order', 0),
                icon=subject_data.get('icon', 'folder2-open')
            )
            db.session.add(new_subject)
    
    db.session.commit()

def import_modules(modules_data, replace_existing):
    for module_data in modules_data:
        module_id = module_data.get('id')
        
        if module_id:
            # Проверка существования
            existing_module = Module.query.get(module_id)
            
            if existing_module:
                if replace_existing:
                    # Обновляем существующий
                    existing_module.title = module_data.get('title', existing_module.title)
                    existing_module.description = module_data.get('description', existing_module.description)
                    existing_module.subject_id = module_data.get('subject_id', existing_module.subject_id)
                    existing_module.module_type = module_data.get('module_type', existing_module.module_type)
                    existing_module.order = module_data.get('order', existing_module.order)
                    existing_module.icon = module_data.get('icon', existing_module.icon)
                    existing_module.is_premium = module_data.get('is_premium', existing_module.is_premium)
                    existing_module.is_final_test = module_data.get('is_final_test', existing_module.is_final_test)
            else:
                # Создаем новый с указанным ID
                new_module = Module(
                    id=module_id,
                    title=module_data.get('title', ''),
                    description=module_data.get('description', ''),
                    subject_id=module_data.get('subject_id'),
                    module_type=module_data.get('module_type', 'content'),
                    order=module_data.get('order', 0),
                    icon=module_data.get('icon', 'file-earmark-text'),
                    is_premium=module_data.get('is_premium', False),
                    is_final_test=module_data.get('is_final_test', False)
                )
                db.session.add(new_module)
        else:
            # Создаем новый без ID
            new_module = Module(
                title=module_data.get('title', ''),
                description=module_data.get('description', ''),
                subject_id=module_data.get('subject_id'),
                module_type=module_data.get('module_type', 'content'),
                order=module_data.get('order', 0),
                icon=module_data.get('icon', 'file-earmark-text'),
                is_premium=module_data.get('is_premium', False),
                is_final_test=module_data.get('is_final_test', False)
            )
            db.session.add(new_module)
    
    db.session.commit()

def import_lessons(lessons_data, replace_existing):
    for lesson_data in lessons_data:
        lesson_id = lesson_data.get('id')
        
        if lesson_id:
            # Проверка существования
            existing_lesson = Lesson.query.get(lesson_id)
            
            if existing_lesson:
                if replace_existing:
                    # Обновляем существующий
                    existing_lesson.title = lesson_data.get('title', existing_lesson.title)
                    existing_lesson.content_type = lesson_data.get('content_type', existing_lesson.content_type)
                    existing_lesson.content = lesson_data.get('content', existing_lesson.content)
                    existing_lesson.module_id = lesson_data.get('module_id', existing_lesson.module_id)
                    existing_lesson.order = lesson_data.get('order', existing_lesson.order)
            else:
                # Создаем новый с указанным ID
                new_lesson = Lesson(
                    id=lesson_id,
                    title=lesson_data.get('title', ''),
                    content_type=lesson_data.get('content_type', 'learning_card'),
                    content=lesson_data.get('content', ''),
                    module_id=lesson_data.get('module_id'),
                    order=lesson_data.get('order', 0)
                )
                db.session.add(new_lesson)
        else:
            # Создаем новый без ID
            new_lesson = Lesson(
                title=lesson_data.get('title', ''),
                content_type=lesson_data.get('content_type', 'learning_card'),
                content=lesson_data.get('content', ''),
                module_id=lesson_data.get('module_id'),
                order=lesson_data.get('order', 0)
            )
            db.session.add(new_lesson)
    
    db.session.commit()

# Маршруты для перетаскивания элементов (Drag and Drop)
@admin_bp.route("/api/move-path/<int:path_id>", methods=["POST"])
def move_path(lang, path_id):
    """Обработка перемещения категории обучения."""
    # Категории нельзя перемещать между собой, только менять порядок
    return jsonify({"success": False, "message": "Категории нельзя перемещать"}), 400

@admin_bp.route("/api/move-subject/<int:subject_id>", methods=["POST"])
def move_subject(lang, subject_id):
    """Обработка перемещения предмета в другую категорию."""
    try:
        data = request.get_json()
        target_type = data.get('target_type')
        target_id = data.get('target_id')
        
        if target_type != 'path':
            return jsonify({"success": False, "message": "Предмет можно перемещать только в категорию"}), 400
        
        # Проверяем существование цели
        target_path = LearningPath.query.get(target_id)
        if not target_path:
            return jsonify({"success": False, "message": f"Категория с ID {target_id} не найдена"}), 404
        
        # Проверяем существование предмета
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({"success": False, "message": f"Предмет с ID {subject_id} не найден"}), 404
        
        # Перемещаем предмет в новую категорию
        subject.learning_path_id = target_id
        db.session.commit()
        
        return jsonify({"success": True, "message": "Предмет успешно перемещен"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Ошибка при перемещении предмета: {str(e)}"}), 500

@admin_bp.route("/api/move-module/<int:module_id>", methods=["POST"])
def move_module(lang, module_id):
    """Обработка перемещения модуля в другой предмет."""
    try:
        data = request.get_json()
        target_type = data.get('target_type')
        target_id = data.get('target_id')
        
        if target_type != 'subject':
            return jsonify({"success": False, "message": "Модуль можно перемещать только в предмет"}), 400
        
        # Проверяем существование цели
        target_subject = Subject.query.get(target_id)
        if not target_subject:
            return jsonify({"success": False, "message": f"Предмет с ID {target_id} не найден"}), 404
        
        # Проверяем существование модуля
        module = Module.query.get(module_id)
        if not module:
            return jsonify({"success": False, "message": f"Модуль с ID {module_id} не найден"}), 404
        
        # Перемещаем модуль в новый предмет
        module.subject_id = target_id
        db.session.commit()
        
        return jsonify({"success": True, "message": "Модуль успешно перемещен"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Ошибка при перемещении модуля: {str(e)}"}), 500

@admin_bp.route("/api/reorder-path/<int:path_id>", methods=["POST"])
def reorder_path(lang, path_id):
    """Изменение порядка категорий обучения."""
    try:
        data = request.get_json()
        target_id = data.get('target_id')
        
        # Проверяем существование категорий
        path = LearningPath.query.get(path_id)
        target_path = LearningPath.query.get(target_id)
        
        if not path:
            return jsonify({"success": False, "message": f"Категория с ID {path_id} не найдена"}), 404
        if not target_path:
            return jsonify({"success": False, "message": f"Категория с ID {target_id} не найдена"}), 404
        
        # Меняем порядок категорий
        # Сохраняем текущий порядок
        current_order = path.order
        target_order = target_path.order
        
        # Обмениваем порядок
        path.order = target_order
        target_path.order = current_order
        
        db.session.commit()
        
        return jsonify({"success": True, "message": "Порядок категорий успешно изменен"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Ошибка при изменении порядка категорий: {str(e)}"}), 500

@admin_bp.route("/api/reorder-subject/<int:subject_id>", methods=["POST"])
def reorder_subject(lang, subject_id):
    """Изменение порядка предметов."""
    try:
        data = request.get_json()
        target_id = data.get('target_id')
        
        # Проверяем существование предметов
        subject = Subject.query.get(subject_id)
        target_subject = Subject.query.get(target_id)
        
        if not subject:
            return jsonify({"success": False, "message": f"Предмет с ID {subject_id} не найден"}), 404
        if not target_subject:
            return jsonify({"success": False, "message": f"Предмет с ID {target_id} не найден"}), 404
        
        # Проверяем, что предметы находятся в одной категории
        if subject.learning_path_id != target_subject.learning_path_id:
            return jsonify({"success": False, "message": "Предметы должны быть в одной категории"}), 400
        
        # Меняем порядок предметов
        # Сохраняем текущий порядок
        current_order = subject.order
        target_order = target_subject.order
        
        # Обмениваем порядок
        subject.order = target_order
        target_subject.order = current_order
        
        db.session.commit()
        
        return jsonify({"success": True, "message": "Порядок предметов успешно изменен"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Ошибка при изменении порядка предметов: {str(e)}"}), 500

@admin_bp.route("/api/reorder-module/<int:module_id>", methods=["POST"])
def reorder_module(lang, module_id):
    """Изменение порядка модулей."""
    try:
        data = request.get_json()
        target_id = data.get('target_id')
        
        # Проверяем существование модулей
        module = Module.query.get(module_id)
        target_module = Module.query.get(target_id)
        
        if not module:
            return jsonify({"success": False, "message": f"Модуль с ID {module_id} не найден"}), 404
        if not target_module:
            return jsonify({"success": False, "message": f"Модуль с ID {target_id} не найден"}), 404
        
        # Проверяем, что модули находятся в одном предмете
        if module.subject_id != target_module.subject_id:
            return jsonify({"success": False, "message": "Модули должны быть в одном предмете"}), 400
        
        # Меняем порядок модулей
        # Сохраняем текущий порядок
        current_order = module.order
        target_order = target_module.order
        
        # Обмениваем порядок
        module.order = target_order
        target_module.order = current_order
        
        db.session.commit()
        
        return jsonify({"success": True, "message": "Порядок модулей успешно изменен"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Ошибка при изменении порядка модулей: {str(e)}"}), 500    

# --- УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ---
# Путь: /<lang>/admin/users
@admin_bp.route("/users", methods=["GET", "POST"])
def users(lang):
    current_lang = g.lang
    
    # Проверка, является ли пользователь администратором
    if not current_user.role == 'admin':  # Изменено: проверка на роль
        flash("Access denied. Administrator privileges required.", "danger")
        return redirect(url_for("main_bp.home", lang=current_lang))
    
    # Обработка POST для сохранения изменений пользователя
    if request.method == "POST":
        form_user_id = request.form.get("user_id")
        action = request.form.get("action")
        target_user = db.session.get(User, form_user_id)
        
        if target_user and action == "save":
            try:
                # Обновляем данные пользователя из формы
                target_user.name = request.form.get("name", target_user.name)
                target_user.email = request.form.get("email", target_user.email)
                target_user.has_subscription = request.form.get("has_subscription") == 'on'
                
                # Доп. проверка: не позволяем снимать админ права с себя
                if target_user.id == current_user.id and not (request.form.get("is_admin") == 'on'):
                    flash("Cannot remove admin privileges from yourself.", "warning")
                else:
                    # Изменено: используем role вместо is_admin
                    if request.form.get("is_admin") == 'on':
                        target_user.role = 'admin'
                    else:
                        target_user.role = 'user'
                
                db.session.commit()
                flash(f"✅ User '{target_user.name}' updated successfully.", "success")
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error updating user {form_user_id}: {e}", exc_info=True)
                flash(f"❌ Error updating user '{target_user.name}': {e}", "danger")
        elif not target_user:
            flash(f"❌ Error: User with ID {form_user_id} not found.", "danger")
        
        # Редирект на список пользователей
        return redirect(url_for(".users", lang=current_lang))
    
    # GET запрос: отображение списка пользователей
    all_users = User.query.order_by(User.id).all()
    
    # Формируем данные для шаблона
    users_data = []
    for user in all_users:
        users_data.append({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'is_admin': user.role == 'admin',  # Добавляем для совместимости с формой
            'has_subscription': user.has_subscription
        })
    
    return render_template("admin/users.html", users=all_users)

# Путь: /<lang>/admin/users/<user_id>/delete
@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(lang, user_id): # Функция ПРИНИМАЕТ lang и user_id
    current_lang = g.lang
    user_to_delete = db.session.get(User, user_id)

    if user_to_delete:
        # Проверка безопасности: не позволяем админу удалить самого себя
        if user_to_delete.id == current_user.id:
             flash("❌ You cannot delete your own account.", "danger")
        else:
            try:
                user_name = user_to_delete.name # Сохраняем имя для сообщения
                db.session.delete(user_to_delete)
                db.session.commit()
                flash(f"🗑 User '{user_name}' deleted successfully.", "success")
                current_app.logger.info(f"Admin {current_user.email} deleted user {user_id} ({user_name}).")
            except Exception as e:
                 db.session.rollback()
                 current_app.logger.error(f"Error deleting user {user_id}: {e}", exc_info=True)
                 flash(f"❌ Error deleting user: {e}", "danger")
    else:
        flash(f"❌ Error: User with ID {user_id} not found.", "danger")

    # Редирект на список пользователей, url_for корректен
    return redirect(url_for(".users", lang=current_lang))


# --- УПРАВЛЕНИЕ МОДУЛЯМИ ---

# Путь: /<lang>/admin/modules
@admin_bp.route("/modules", methods=["GET", "POST"])
def modules(lang): # Функция ПРИНИМАЕТ lang
    current_lang = g.lang

    # Обработка POST запроса (для импорта)
    # Лучше разделить импорт и создание на разные маршруты или использовать разные формы
    if request.method == "POST" and 'import_form' in request.form: # Идентифицируем форму импорта
        file = request.files.get("json_file")
        if not file or file.filename == '':
            flash("No file selected for import.", "warning")
            return redirect(url_for(".modules", lang=current_lang))

        if file and file.filename.endswith('.json'):
            try:
                # Читаем файл безопасно
                file_content = file.read().decode('utf-8')
                data = json.loads(file_content)

                # Убедимся, что data это список
                if not isinstance(data, list):
                    flash("❌ Invalid JSON format: root element must be a list of modules.", "danger")
                    return redirect(url_for(".modules", lang=current_lang))

                imported_count = 0
                skipped_count = 0
                for mod_data in data:
                    if not isinstance(mod_data, dict):
                        flash(f"Skipping invalid module data item: {mod_data}", "warning")
                        skipped_count += 1
                        continue

                    title = mod_data.get("title")
                    if not title:
                        flash("Skipping module with no title.", "warning")
                        skipped_count += 1
                        continue

                    existing = Module.query.filter_by(title=title).first()
                    if existing:
                        flash(f"Module '{title}' already exists, skipping.", "info")
                        skipped_count += 1
                        continue

                    module = Module(
                        title=title,
                        description=mod_data.get("description", ""),
                        is_premium=mod_data.get("is_premium", True)
                    )
                    db.session.add(module)
                    # Важно! flush нужен, чтобы получить module.id для уроков ДО коммита
                    db.session.flush()
                    imported_count += 1

                    lessons_data = mod_data.get("lessons", [])
                    if not isinstance(lessons_data, list):
                        flash(f"Invalid 'lessons' format for module '{title}', skipping lessons.", "warning")
                        lessons_data = []

                    for lesson_data in lessons_data:
                         if not isinstance(lesson_data, dict):
                             flash(f"Skipping invalid lesson data in module '{title}': {lesson_data}", "warning")
                             continue

                         quiz_list = lesson_data.get("quiz", [])
                         if not isinstance(quiz_list, list):
                             flash(f"Invalid 'quiz' format for lesson '{lesson_data.get('title')}' in module '{title}', skipping quiz.", "warning")
                             quiz_list = []

                         new_lesson = Lesson(
                             module_id=module.id, # Используем ID после flush
                             title=lesson_data.get("title", "Untitled Lesson"),
                             content=lesson_data.get("content", ""),
                             quiz=quiz_list
                         )
                         db.session.add(new_lesson)

                # Коммитим все изменения разом в конце
                if imported_count > 0:
                     db.session.commit()
                     flash(f"✅ Successfully imported {imported_count} new module(s). Skipped {skipped_count} items.", "success")
                     current_app.logger.info(f"Admin {current_user.email} imported {imported_count} modules.")
                else:
                     # Откатываем, если ничего не импортировали, но могли добавить module в сессию
                     db.session.rollback()
                     flash(f"No new modules were imported. Skipped {skipped_count} items.", "info")

            except json.JSONDecodeError:
                flash("❌ Invalid JSON file format.", "danger")
                db.session.rollback() # Откатываем при ошибке JSON
            except Exception as e:
                db.session.rollback() # Откатываем при любой другой ошибке
                current_app.logger.error(f"Error importing modules: {e}", exc_info=True)
                flash(f"❌ Failed to import modules: {e}", "danger")

            # Редирект на список модулей, url_for корректен
            return redirect(url_for(".modules", lang=current_lang))
        else:
            flash("❌ Invalid file type. Please upload a .json file.", "danger")
            return redirect(url_for(".modules", lang=current_lang))

    # Отображение страницы для GET запроса
    all_modules = Module.query.order_by(Module.title).all()
    # lang и current_user доступны в шаблоне через context_processor
    # Нужен шаблон admin/modules.html
    return render_template("admin/modules.html", modules=all_modules)


# Путь: /<lang>/admin/modules/create
@admin_bp.route("/modules/create", methods=["GET", "POST"])
def create_module(lang): # Функция ПРИНИМАЕТ lang
     """Страница и обработка создания нового модуля."""
     current_lang = g.lang

     if request.method == "POST":
        # Получаем данные из формы
        title = request.form.get("title")
        description = request.form.get("description", "") # По умолчанию пустая строка
        is_premium = request.form.get("is_premium") == "on" # Чекбокс
        # Данные для первого урока (опционально)
        lesson_title = request.form.get("lesson_title")
        lesson_content = request.form.get("lesson_content", "") # По умолчанию пустая строка
        quiz_json = request.form.get("quiz_json") # Ожидаем JSON строку

        # Валидация
        if not title:
             flash("Module title is required.", "danger")
             # Передаем введенные данные обратно в форму для удобства пользователя
             return render_template("admin/create_module.html", form_data=request.form)

        try:
            # Создаем модуль
            module = Module(title=title, description=description, is_premium=is_premium)
            db.session.add(module)
            db.session.flush() # Получаем ID модуля для урока

            # Пытаемся добавить первый урок, если есть данные
            if lesson_title or lesson_content or quiz_json:
                 quiz_data = []
                 if quiz_json:
                     try:
                         # Парсим JSON, ожидаем список
                         quiz_data = json.loads(quiz_json)
                         if not isinstance(quiz_data, list):
                             raise ValueError("Quiz JSON must be a list of objects.")
                         # Доп. валидация структуры объектов в quiz_data, если нужно
                     except (json.JSONDecodeError, ValueError) as json_err:
                         # Сообщаем об ошибке, но продолжаем создание модуля без квиза
                         flash(f"Warning: Invalid format for Quiz JSON - {json_err}. Lesson created without quiz.", "warning")
                         quiz_data = [] # Сбрасываем в пустой список

                 # Создаем урок
                 new_lesson = Lesson(
                     module_id=module.id,
                     title=lesson_title if lesson_title else f"{title} - Lesson 1", # Дефолтное название урока
                     content=lesson_content,
                     quiz=quiz_data
                 )
                 db.session.add(new_lesson)

            # Коммитим все изменения
            db.session.commit()
            flash(f"✅ Module '{module.title}' created successfully.", "success")
            current_app.logger.info(f"Admin {current_user.email} created module '{module.title}' (ID: {module.id}).")
            # Редирект на список модулей, url_for корректен
            return redirect(url_for(".modules", lang=current_lang))

        except Exception as e:
            db.session.rollback() # Откатываем транзакцию
            current_app.logger.error(f"Error creating module '{title}': {e}", exc_info=True)
            flash(f"❌ Error creating module: {e}", "danger")
            # Возвращаем на форму с предзаполненными данными
            return render_template("admin/create_module.html", form_data=request.form)

     # Отображение формы для GET запроса
     # Нужен шаблон admin/create_module.html
     return render_template("admin/create_module.html")


# Путь: /<lang>/admin/modules/<module_id>/delete
@admin_bp.route("/modules/<int:module_id>/delete", methods=["POST"])
def delete_module(lang, module_id): # Функция ПРИНИМАЕТ lang и module_id
    """Удаление модуля и связанных уроков."""
    current_lang = g.lang
    module = db.session.get(Module, module_id)

    if module:
        try:
            module_title = module.title # Сохраняем для сообщения
            # SQLAlchemy `cascade="all, delete-orphan"` в модели Module.lessons
            # должен автоматически удалить связанные уроки при удалении модуля.
            # Явная очистка уроков не нужна, если cascade настроен правильно.
            # Lesson.query.filter_by(module_id=module.id).delete() # <-- Это не нужно при cascade

            db.session.delete(module) # Просто удаляем модуль
            db.session.commit()
            flash(f"🗑 Module '{module_title}' and its associated lessons deleted successfully.", "success")
            current_app.logger.info(f"Admin {current_user.email} deleted module ID {module_id} ('{module_title}').")
        except Exception as e:
             db.session.rollback()
             current_app.logger.error(f"Error deleting module ID {module_id}: {e}", exc_info=True)
             flash(f"❌ Error deleting module: {e}", "danger")
    else:
        flash(f"❌ Error: Module with ID {module_id} not found.", "danger")

    # Редирект на список модулей, url_for корректен
    return redirect(url_for(".modules", lang=current_lang))

# ========== Рентген (новое) ==========
@admin_bp.route('/xray-manager')
@login_required
def xray_manager(lang):
    xray_dir = os.path.join(current_app.static_folder, 'xray')
    annotation_file = os.path.join(current_app.static_folder, 'annotations', 'annotations.json')
    xray_files = []
    annotations = {}
    if os.path.exists(xray_dir):
        for f in os.listdir(xray_dir):
            if f.endswith('.jpg') or f.endswith('.jpeg'):
                path = os.path.join(xray_dir, f)
                xray_files.append({"filename": f, "size": os.path.getsize(path)})
    if os.path.exists(annotation_file):
        with open(annotation_file) as f:
            annotations = json.load(f).get("_via_img_metadata", {})
    return render_template("xray_manager.html", title="Рентген-менеджер", xray_files=xray_files, annotations=annotations)

@admin_bp.route('/xray-upload', methods=['POST'])
@login_required
def xray_upload(lang):
    file = request.files.get("file")
    if file and file.filename.endswith(('.jpg', '.jpeg')):
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.static_folder, 'xray', filename))
        flash("✅ Снимок загружен", "success")
    else:
        flash("❌ Неверный формат файла", "danger")
    return redirect(url_for("admin_bp.xray_manager", lang=lang))

@admin_bp.route('/xray-delete/<filename>', methods=['POST'])
@login_required
def xray_delete(lang, filename):
    filepath = os.path.join(current_app.static_folder, 'xray', filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        flash("🗑 Снимок удалён", "success")
    else:
        flash("❌ Файл не найден", "danger")
    return redirect(url_for("admin_bp.xray_manager", lang=lang))

@admin_bp.route('/xray-save-annotations', methods=['POST'])
@login_required
def xray_save_annotations(lang):
    data = request.get_json()
    output_path = os.path.join(current_app.static_folder, 'annotations', 'annotations.json')
    try:
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return {"success": True}, 200
    except Exception as e:
        return {"success": False, "message": str(e)}, 500
    
# Веб-редактор контента
@admin_bp.route('/content-editor')
@login_required
@admin_required
def content_editor(lang):
    """Веб-редактор для создания и редактирования контента."""
    g.lang = lang
    return render_template('admin/content_editor/grapesjs_builder.html', lang=lang)

# Раздел виртуальных пациентов
@admin_bp.route('/virtual-patients', methods=['GET'])
@login_required
@admin_required
def virtual_patient_manager(lang):
    g.lang = lang
    # Получаем все сценарии из базы данных
    scenarios = VirtualPatientScenario.query.all()
    
    return render_template(
        'admin/virtual_patient_manager.html',
        lang=lang,
        scenarios=scenarios
    )

@admin_bp.route('/admin/virtual-patients/edit/<int:scenario_id>', methods=['GET'])
@login_required
@admin_required
def edit_scenario(lang, scenario_id):
    g.lang = lang
    scenario = VirtualPatientScenario.query.get_or_404(scenario_id)
    
    try:
        # Загружаем данные сценария
        raw_data = json.loads(scenario.scenario_data)
        
        # Проверяем структуру с переводами
        if "translations" in raw_data and isinstance(raw_data["translations"], dict):
            # Определяем язык для отображения
            used_lang = lang if lang in raw_data["translations"] else "en"
            if used_lang not in raw_data["translations"] and "en" in raw_data["translations"]:
                used_lang = "en"
            elif used_lang not in raw_data["translations"] and raw_data["translations"]:
                used_lang = next(iter(raw_data["translations"].keys()))
            
            # Получаем данные выбранного языка
            lang_data = raw_data["translations"].get(used_lang, {})
            
            # Создаем новую структуру данных, избегая циклических ссылок
            scenario_data = {
                # Метаданные для JavaScript
                "current_language": used_lang,
                "available_languages": list(raw_data["translations"].keys()),
                
                # Базовые разделы
                "patient_info": lang_data.get("patient_info", {}),
                "initial_state": lang_data.get("initial_state", {}),
                "dialogue_nodes": lang_data.get("dialogue_nodes", []),
                "outcomes": lang_data.get("outcomes", {})
            }
            
            # Сохраняем raw_data для JavaScript
            scenario_data["raw_data_json"] = json.dumps(raw_data)
        else:
            # Если нет переводов, создаем структуру с переводами
            fallback_data = {
                "translations": {
                    "en": raw_data
                }
            }
            
            # Используем данные как есть для текущего языка
            scenario_data = raw_data.copy() if isinstance(raw_data, dict) else {}
            scenario_data["current_language"] = "en"
            scenario_data["available_languages"] = ["en"]
            scenario_data["raw_data_json"] = json.dumps(fallback_data)
    except (json.JSONDecodeError, TypeError, KeyError) as e:
        print(f"Ошибка при обработке данных сценария: {e}")
        # Создаем пустую структуру данных при ошибке
        scenario_data = {
            "current_language": "en",
            "available_languages": ["en"],
            "patient_info": {},
            "initial_state": {},
            "dialogue_nodes": [],
            "outcomes": {},
            "raw_data_json": "{}"
        }
    
    # Добавляем отсутствующие обязательные секции
    default_data = {
        "patient_info": {
            "name": "Пациент",
            "age": 30,
            "gender": "male",
            "image": "patient_default.jpg",
            "medical_history": "Нет данных"
        },
        "initial_state": {
            "patient_statement": "Здравствуйте, доктор",
            "patient_emotion": "neutral",
            "notes": "Первичный прием"
        },
        "dialogue_nodes": [],
        "outcomes": {
            "good": {"title": "Отличная диагностика!", "text": "Вы проявили отличные навыки диагностики."},
            "average": {"title": "Хорошая попытка", "text": "Есть аспекты, требующие улучшения."},
            "poor": {"title": "Требуется практика", "text": "Рекомендуется повторить материал."}
        }
    }
    
    # Заполняем отсутствующие секции
    for key, default_value in default_data.items():
        if key not in scenario_data:
            scenario_data[key] = default_value
        elif isinstance(default_value, dict) and isinstance(scenario_data[key], dict):
            for subkey, subvalue in default_value.items():
                if subkey not in scenario_data[key]:
                    scenario_data[key][subkey] = subvalue
    
    # Проверяем изображение пациента
    patient_image = scenario_data.get("patient_info", {}).get("image", "")
    if not patient_image or not os.path.exists(os.path.join(current_app.static_folder, 'images/virtual_patients', patient_image)):
        if "patient_info" not in scenario_data:
            scenario_data["patient_info"] = {}
        scenario_data["patient_info"]["image"] = "patient_default.jpg"
    
    # Обеспечиваем уникальные ID для узлов диалога
    if "dialogue_nodes" in scenario_data and isinstance(scenario_data["dialogue_nodes"], list):
        for i, node in enumerate(scenario_data["dialogue_nodes"]):
            if not node.get("id"):
                node["id"] = f"node_{i + 1}_{int(datetime.now().timestamp())}"
    
    return render_template(
        'admin/virtual_patient_editor.html',
        lang=lang,
        scenario=scenario,
        scenario_data=scenario_data,
        debug=True
    )

# API для создания, обновления и удаления сценариев
@admin_bp.route('/api/create-scenario', methods=['POST'])
@login_required
@admin_required
def create_scenario(lang):
    g.lang = lang
    try:
        data = request.json
        
        # Создаем новый сценарий
        scenario = VirtualPatientScenario(
            title=data.get('title', 'Новый сценарий'),
            description=data.get('description', ''),
            difficulty=data.get('difficulty', 'medium'),
            category=data.get('category', 'diagnosis'),
            timeframe=data.get('timeframe', 0),
            max_score=data.get('max_score', 100),
            is_premium=data.get('is_premium', False),
            is_published=data.get('is_published', False),
            scenario_data=data.get('scenario_data', '{}')
        )
        
        db.session.add(scenario)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'scenario_id': scenario.id,
            'redirect_url': url_for('admin_bp.edit_scenario', lang=lang, scenario_id=scenario.id)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@admin_bp.route('/api/update-scenario/<int:scenario_id>', methods=['POST'])
@login_required
@admin_required
def update_scenario(lang, scenario_id):
    g.lang = lang
    try:
        data = request.json
        scenario = VirtualPatientScenario.query.get_or_404(scenario_id)
        
        # Основные данные сценария
        scenario.title = data.get('title', scenario.title)
        scenario.description = data.get('description', scenario.description)
        scenario.difficulty = data.get('difficulty', scenario.difficulty)
        scenario.category = data.get('category', scenario.category)
        scenario.timeframe = data.get('timeframe', scenario.timeframe)
        scenario.max_score = data.get('max_score', scenario.max_score)
        scenario.is_premium = data.get('is_premium', scenario.is_premium)
        scenario.is_published = data.get('is_published', scenario.is_published)
        
        # Получаем и проверяем данные сценария
        scenario_data_str = data.get('scenario_data', '{}')
        try:
            scenario_data = json.loads(scenario_data_str)
            # Проверка на корректность
            if not isinstance(scenario_data, dict):
                raise ValueError("Ожидается словарь для scenario_data")
                
            # Сохраняем данные сценария как строку JSON
            scenario.scenario_data = json.dumps(scenario_data)
        except json.JSONDecodeError as e:
            print(f"Ошибка декодирования JSON: {e}")
            return jsonify({
                'success': False,
                'message': 'Некорректный формат JSON для scenario_data'
            }), 400
            
        db.session.commit()
        
        return jsonify({
            'success': True
        })
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при обновлении сценария: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@admin_bp.route('/api/delete-scenario/<int:scenario_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_scenario(lang, scenario_id):
    g.lang = lang
    try:
        scenario = VirtualPatientScenario.query.get_or_404(scenario_id)
        
        db.session.delete(scenario)
        db.session.commit()
        
        return jsonify({
            'success': True
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Исправление функции в admin_routes.py

# Проверьте и исправьте функцию toggle_publish_scenario
@admin_bp.route('/api/toggle-publish-scenario/<int:scenario_id>', methods=['POST'])
@login_required
@admin_required
def toggle_publish_scenario(lang, scenario_id):
    g.lang = lang
    try:
        scenario = VirtualPatientScenario.query.get_or_404(scenario_id)
        
        # Инвертируем статус публикации
        scenario.is_published = not scenario.is_published
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_published': scenario.is_published
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@admin_bp.route('/api/duplicate-scenario/<int:scenario_id>', methods=['POST'])
@login_required
@admin_required
def duplicate_scenario(lang, scenario_id):
    g.lang = lang
    try:
        original = VirtualPatientScenario.query.get_or_404(scenario_id)
        
        # Создаем копию сценария
        duplicate = VirtualPatientScenario(
            title=f"{original.title} - Копия",
            description=original.description,
            difficulty=original.difficulty,
            category=original.category,
            timeframe=original.timeframe,
            max_score=original.max_score,
            is_premium=original.is_premium,
            is_published=False,  # Всегда устанавливаем как неопубликованный
            scenario_data=original.scenario_data
        )
        
        db.session.add(duplicate)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'scenario_id': duplicate.id,
            'redirect_url': url_for('admin_bp.edit_scenario', lang=lang, scenario_id=duplicate.id)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500    

@admin_bp.route("/api/content-tree", methods=["GET"])
@login_required
@admin_required
def get_content_tree(lang):
    try:
        # Получаем категории (Learning Paths)
        learning_paths = LearningPath.query.order_by(LearningPath.order).all()
        tree_data = []
        
        # Формируем дерево
        for path in learning_paths:
            path_node = {
                'id': f'path_{path.id}',
                'name': path.name,
                'type': 'path',
                'icon': path.icon or 'diagram-3',
                'expanded': False,
                'children': []
            }
            
            # Добавляем предметы (Subjects)
            subjects = Subject.query.filter_by(learning_path_id=path.id).order_by(Subject.order).all()
            for subject in subjects:
                subject_node = {
                    'id': f'subject_{subject.id}',
                    'name': subject.name,
                    'type': 'subject',
                    'icon': subject.icon or 'folder2-open',
                    'expanded': False,
                    'children': []
                }
                
                # Добавляем модули (Modules)
                modules = Module.query.filter_by(subject_id=subject.id).order_by(Module.order).all()
                for module in modules:
                    module_node = {
                        'id': f'module_{module.id}',
                        'name': module.title,
                        'type': 'module',
                        'icon': module.icon or 'file-earmark-text',
                        'expanded': False,
                        'children': []
                    }
                    
                    # Добавляем уроки (Lessons)
                    lessons = Lesson.query.filter_by(module_id=module.id).order_by(Lesson.order).all()
                    for lesson in lessons:
                        lesson_node = {
                            'id': f'lesson_{lesson.id}',
                            'name': lesson.title,
                            'type': 'lesson',
                            'icon': 'journal-text',
                            'content_type': lesson.content_type
                        }
                        module_node['children'].append(lesson_node)
                    
                    subject_node['children'].append(module_node)
                
                path_node['children'].append(subject_node)
            
            tree_data.append(path_node)
        
        # Добавляем виртуальных пациентов в отдельную категорию
        vp_category = {
            'id': 'vp_category',
            'name': 'Виртуальные пациенты',
            'type': 'vp_category',
            'icon': 'people-fill',
            'expanded': False,
            'children': []
        }
        
        # Проверяем, есть ли модель VirtualPatient
        if hasattr(sys.modules['models'], 'VirtualPatient'):
            from models import VirtualPatient
            vpatients = VirtualPatient.query.all()
            for vp in vpatients:
                vp_node = {
                    'id': f'vp_{vp.id}',
                    'name': vp.title,
                    'type': 'virtual_patient',
                    'icon': 'person-fill'
                }
                vp_category['children'].append(vp_node)
        
        tree_data.append(vp_category)
        
        return jsonify({'success': True, 'data': tree_data})
    except Exception as e:
        current_app.logger.error(f"Error getting content tree: {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route("/api/get-item/<string:item_type>/<int:item_id>", methods=["GET"])
@login_required
@admin_required
def get_item(item_type, item_id):
    try:
        item_data = {}
        
        if item_type == 'path':
            item = LearningPath.query.get_or_404(item_id)
            item_data = {
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'icon': item.icon,
                'order': item.order
            }
        elif item_type == 'subject':
            item = Subject.query.get_or_404(item_id)
            item_data = {
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'learning_path_id': item.learning_path_id,
                'icon': item.icon,
                'order': item.order
            }
        elif item_type == 'module':
            item = Module.query.get_or_404(item_id)
            item_data = {
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'subject_id': item.subject_id,
                'module_type': item.module_type,
                'icon': item.icon,
                'order': item.order,
                'is_premium': item.is_premium,
                'is_final_test': item.is_final_test
            }
        elif item_type == 'lesson':
            lesson = Lesson.query.get_or_404(item_id)
            item_data = {
                'id': lesson.id,
                'title': lesson.title,
                'module_id': lesson.module_id,
                'content_type': lesson.content_type,
                'content': lesson.content,
                'order': lesson.order
            }
        elif item_type == 'virtual_patient':
            # Проверяем, есть ли модель VirtualPatient
            if hasattr(sys.modules['models'], 'VirtualPatientScenario'):
                from models import VirtualPatientScenario
                vp = VirtualPatientScenario.query.get_or_404(item_id)
                item_data = {
                    'id': vp.id,
                    'title': vp.title,
                    'description': vp.description,
                    'scenario_data': vp.scenario_data
                }
        
        return jsonify({'success': True, 'data': item_data})
    except Exception as e:
        current_app.logger.error(f"Error getting item: {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route("/api/save-item/<string:item_type>/<int:item_id>", methods=["POST"])
@login_required
@admin_required
def save_item(item_type, item_id):
    try:
        data = request.json
        
        # Логика сохранения для разных типов элементов
        if item_type == 'path':
            path = LearningPath.query.get_or_404(item_id)
            path.name = data.get('name', path.name)
            path.description = data.get('description', path.description)
            path.order = data.get('order', path.order)
            path.icon = data.get('icon', path.icon)
            db.session.commit()
        elif item_type == 'subject':
            subject = Subject.query.get_or_404(item_id)
            subject.name = data.get('name', subject.name)
            subject.description = data.get('description', subject.description)
            subject.learning_path_id = data.get('learning_path_id', subject.learning_path_id)
            subject.order = data.get('order', subject.order)
            subject.icon = data.get('icon', subject.icon)
            db.session.commit()
        elif item_type == 'module':
            module = Module.query.get_or_404(item_id)
            module.title = data.get('title', module.title)
            module.description = data.get('description', module.description)
            module.subject_id = data.get('subject_id', module.subject_id)
            module.module_type = data.get('module_type', module.module_type)
            module.order = data.get('order', module.order)
            module.icon = data.get('icon', module.icon)
            module.is_premium = data.get('is_premium', module.is_premium)
            module.is_final_test = data.get('is_final_test', module.is_final_test)
            db.session.commit()
        elif item_type == 'lesson':
            lesson = Lesson.query.get_or_404(item_id)
            lesson.title = data.get('title', lesson.title)
            lesson.content_type = data.get('content_type', lesson.content_type)
            lesson.content = data.get('content', lesson.content)
            lesson.order = data.get('order', lesson.order)
            db.session.commit()
        elif item_type == 'virtual_patient':
            # Предполагается, что у вас есть модель VirtualPatient
            if hasattr(sys.modules['models'], 'VirtualPatientScenario'):
                from models import VirtualPatientScenario
                vp = VirtualPatientScenario.query.get_or_404(item_id)
                vp.title = data.get('title', vp.title)
                vp.description = data.get('description', vp.description)
                vp.scenario_data = data.get('scenario_data', vp.scenario_data)
                db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving item: {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route("/content-explorer")
@login_required
@admin_required
def content_explorer(lang):
    """Отображает интерфейс проводника контента."""
    return render_template("admin/content_explorer.html")

@admin_bp.route("/content-uploader")
@login_required
@admin_required
def content_uploader(lang):
    """Страница загрузки контента по модулям."""
    return render_template("admin/content_uploader.html")

@admin_bp.route("/api/modules-structure", methods=["GET"])
@login_required
@admin_required
def get_modules_structure(lang):
    """API для получения структуры модулей и их статуса."""
    try:
        # Получаем структуру всех модулей
        paths = LearningPath.query.order_by(LearningPath.order).all()
        structure = []
        
        for path in paths:
            path_data = {
                'id': path.id,
                'name': path.name,
                'icon': path.icon or 'diagram-3',
                'subjects': []
            }
            
            subjects = Subject.query.filter_by(learning_path_id=path.id).order_by(Subject.order).all()
            for subject in subjects:
                subject_data = {
                    'id': subject.id,
                    'name': subject.name,
                    'icon': subject.icon or 'folder2-open',
                    'modules': []
                }
                
                modules = Module.query.filter_by(subject_id=subject.id).order_by(Module.order).all()
                for module in modules:
                    # Проверяем наличие контента
                    has_theory = False
                    has_tests = False
                    
                    # Проверяем наличие уроков с learning_card
                    theory_lessons = Lesson.query.filter_by(
                        module_id=module.id, 
                        content_type='learning_card'
                    ).count()
                    has_theory = theory_lessons > 0
                    
                    # Проверяем наличие уроков с тестами
                    test_lessons = Lesson.query.filter_by(
                        module_id=module.id, 
                        content_type='quiz'
                    ).count()
                    has_tests = test_lessons > 0
                    
                    module_data = {
                        'id': module.id,
                        'title': module.title,
                        'description': module.description,
                        'has_theory': has_theory,
                        'has_tests': has_tests
                    }
                    
                    subject_data['modules'].append(module_data)
                
                path_data['subjects'].append(subject_data)
            
            structure.append(path_data)
        
        return jsonify({'success': True, 'data': structure})
    except Exception as e:
        current_app.logger.error(f"Error getting modules structure: {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route("/api/upload-module-content", methods=["POST"])
@login_required
@admin_required
def upload_module_content(lang):
    """API для загрузки контента в модуль."""
    try:
        module_id = request.form.get('module_id')
        if not module_id:
            return jsonify({'success': False, 'message': 'Не указан ID модуля'}), 400
        
        module = Module.query.get_or_404(module_id)
        
        theory_file = request.files.get('theory_file')
        tests_file = request.files.get('tests_file')
        
        if not theory_file and not tests_file:
            return jsonify({'success': False, 'message': 'Не загружено ни одного файла'}), 400
        
        # Обработка файла с теорией
        if theory_file:
            # Читаем JSON-файл
            theory_content = json.load(theory_file)
            
            # Валидируем структуру (массив карточек)
            if not isinstance(theory_content, list):
                return jsonify({'success': False, 'message': 'Файл теории должен содержать массив карточек'}), 400

            # Импортируем функцию создания slug из utils
            from utils.subtopics import create_slug
            
            # Группируем карточки по подтемам (module_title)
            subtopics = {}
            for card in theory_content:
                if card.get('type') == 'learning':
                    # Получаем название подтемы (или используем заголовок модуля как дефолт)
                    module_title = card.get('module_title', module.title)
                    
                    # Создаем ключ для подтемы
                    if module_title not in subtopics:
                        subtopics[module_title] = []
                        
                    # Добавляем карточку в подтему
                    subtopics[module_title].append(card)
            
            # Удаляем существующие уроки с теорией для этого модуля
            Lesson.query.filter_by(module_id=module.id, content_type='learning_card').delete()
            
            # Создаем отдельный урок для каждой подтемы
            order_counter = 1
            for subtopic_name, cards in subtopics.items():
                # Создаем контент с карточками
                lesson_content = {
                    "cards": cards
                }
                
                # Создаем новый урок с теорией для подтемы
                lesson = Lesson(
                    title=f"{subtopic_name}",
                    module_id=module.id,
                    content_type='learning_card',
                    content=json.dumps(lesson_content, ensure_ascii=False),
                    order=order_counter,
                    subtopic=subtopic_name,
                    subtopic_slug=create_slug(subtopic_name)
                )
                db.session.add(lesson)
                order_counter += 1
                
            # Сохраняем изменения
            db.session.commit()
            
        # Обработка файла с тестами
        if tests_file:
            # Читаем JSON-файл
            tests_content = json.load(tests_file)
            
            # Валидируем структуру (массив вопросов)
            if not isinstance(tests_content, list):
                return jsonify({'success': False, 'message': 'Файл тестов должен содержать массив вопросов'}), 400
            
            # Проверяем, импортирована ли функция create_slug
            if 'create_slug' not in locals():
                from utils.subtopics import create_slug
            
            # Группируем вопросы по подтемам (module_title)
            subtopics = {}
            for question in tests_content:
                if question.get('type') == 'test':
                    # Получаем название подтемы (или используем заголовок модуля как дефолт)
                    module_title = question.get('module_title', module.title)
                    
                    # Создаем ключ для подтемы
                    if module_title not in subtopics:
                        subtopics[module_title] = []
                        
                    # Добавляем вопрос в подтему
                    subtopics[module_title].append(question)
            
            # Удаляем существующие уроки с тестами для этого модуля
            Lesson.query.filter_by(module_id=module.id, content_type='quiz').delete()
            
            # Создаем отдельный урок с тестами для каждой подтемы
            order_counter = 1000  # Начинаем с большого числа, чтобы тесты были после карточек
            for subtopic_name, questions in subtopics.items():
                # Преобразуем ответы
                processed_questions = []
                for question in questions:
                    answer_letter = question.get('answer', 'A')
                    correct_answer = ord(answer_letter) - ord('A')
                    
                    processed_question = {
                        "question": question.get('question', ''),
                        "options": question.get('options', []),
                        "correct_answer": correct_answer,
                        "explanation": question.get('explanation', ''),
                        "card_id": question.get('card_id', ''),
                        "tags": question.get('tags', []),
                        "source_references": question.get('source_references', []),
                        "scope": question.get('scope', 'intermediate'),
                        "module_title": question.get('module_title', module.title)
                    }
                    processed_questions.append(processed_question)
                
                # Создаем контент с вопросами
                quiz_content = {
                    "questions": processed_questions
                }
                
                # Создаем новый урок с тестами для подтемы
                lesson = Lesson(
                    title=f"{subtopic_name} - Тест",
                    module_id=module.id,
                    content_type='quiz',
                    content=json.dumps(quiz_content, ensure_ascii=False),
                    order=order_counter,
                    subtopic=subtopic_name,
                    subtopic_slug=create_slug(subtopic_name)
                )
                db.session.add(lesson)
                order_counter += 1
        
        # Сохраняем изменения
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error uploading module content: {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route("/api/preview-module/<int:module_id>", methods=["GET"])
@login_required
@admin_required
def preview_module_content(module_id, lang):
    """Предпросмотр содержимого модуля."""
    try:
        module = Module.query.get_or_404(module_id)
        lessons = Lesson.query.filter_by(module_id=module.id).all()
        
        return render_template("admin/module_preview.html", 
                             module=module, 
                             lessons=lessons)
    except Exception as e:
        current_app.logger.error(f"Error previewing module: {e}", exc_info=True)
        return "Ошибка при предпросмотре модуля", 500

# Путь: /<lang>/admin/ai-notifications
@admin_bp.route("/ai-notifications")
@login_required
@admin_required
def ai_notifications(lang):
    """Отображает страницу настроек уведомлений ИИ аналитики."""
    return render_template("notification_settings.html")

# API для управления настройками уведомлений
@admin_bp.route("/api/notification-settings", methods=["GET"])
@login_required
@admin_required
def get_notification_settings(lang):
    """Получает текущие настройки уведомлений."""
    try:
        from utils.ai_notifications import AINotificationManager
        
        notification_manager = AINotificationManager()
        settings = notification_manager.get_notification_settings()
        
        return jsonify({
            'success': True,
            'settings': settings
        })
    except Exception as e:
        current_app.logger.error(f"Ошибка при получении настроек уведомлений: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@admin_bp.route("/api/update-notification-settings", methods=["POST"])
@login_required
@admin_required
def update_notification_settings(lang):
    """Обновляет настройки уведомлений."""
    try:
        from utils.ai_notifications import AINotificationManager
        
        data = request.json
        thresholds = data.get('thresholds', {})
        
        notification_manager = AINotificationManager()
        success = notification_manager.update_thresholds(thresholds)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Настройки успешно обновлены'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Ошибка при обновлении настроек'
            }), 400
    except Exception as e:
        current_app.logger.error(f"Ошибка при обновлении настроек уведомлений: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@admin_bp.route("/api/test-notification", methods=["POST"])
@login_required
@admin_required
def test_notification(lang):
    """Отправляет тестовое уведомление администраторам."""
    try:
        from utils.ai_notifications import AINotificationManager
        from datetime import datetime
        
        notification_manager = AINotificationManager()
        admin_emails = notification_manager.get_admin_emails()
        
        if not admin_emails:
            return jsonify({
                'success': False,
                'message': 'Не найдены email адреса администраторов'
            }), 400
        
        # Создаем тестовый алерт
        test_alert = {
            'type': 'test',
            'severity': 'info',
            'title': 'ТЕСТ: Проверка системы уведомлений',
            'message': f'Это тестовое уведомление, отправленное администратором {current_user.name} в {datetime.now().strftime("%H:%M:%S")}',
            'timestamp': datetime.now(),
            'actions': ['Убедиться, что уведомления работают корректно']
        }
        
        # Отправляем тестовое уведомление
        success = notification_manager.send_email_notification(test_alert, admin_emails)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Тестовое уведомление отправлено на {len(admin_emails)} адресов'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Ошибка при отправке тестового уведомления. Проверьте настройки SMTP.'
            }), 400
    except Exception as e:
        current_app.logger.error(f"Ошибка при отправке тестового уведомления: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@admin_bp.route("/api/run-alert-check", methods=["POST"])
@login_required
@admin_required
def run_alert_check(lang):
    """Запускает ручную проверку алертов."""
    try:
        from utils.ai_notifications import AINotificationManager
        
        notification_manager = AINotificationManager()
        alerts = notification_manager.process_alerts(send_notifications=True)
        
        # Логируем действие администратора
        current_app.logger.info(f"Администратор {current_user.name} запустил проверку алертов. Найдено алертов: {len(alerts)}")
        
        alert_summary = []
        for alert in alerts:
            alert_summary.append({
                'type': alert['type'],
                'severity': alert['severity'],
                'title': alert['title']
            })
        
        return jsonify({
            'success': True,
            'alert_count': len(alerts),
            'alerts': alert_summary,
            'message': f'Проверка завершена. Обнаружено алертов: {len(alerts)}'
        })
    except Exception as e:
        current_app.logger.error(f"Ошибка при запуске проверки алертов: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@admin_bp.route("/api/alert-history", methods=["GET"])
@login_required
@admin_required
def get_alert_history(lang):
    """Получает историю алертов."""
    try:
        # Здесь можно добавить получение истории из базы данных
        # Пока возвращаем заглушку
        
        # В будущем здесь будет запрос к таблице alerts/notifications
        mock_alerts = [
            {
                'id': 1,
                'timestamp': datetime.now() - timedelta(hours=1),
                'type': 'error_rate',
                'severity': 'warning',
                'title': 'Повышенный процент ошибок ИИ',
                'message': 'Процент ошибок составляет 12%',
                'status': 'sent'
            },
            {
                'id': 2,
                'timestamp': datetime.now() - timedelta(hours=2),
                'type': 'satisfaction',
                'severity': 'critical',
                'title': 'Низкая удовлетворенность пользователей',
                'message': 'Удовлетворенность упала до 58%',
                'status': 'sent'
            }
        ]
        
        # Конвертируем datetime в строки для JSON
        for alert in mock_alerts:
            alert['timestamp'] = alert['timestamp'].isoformat()
        
        return jsonify({
            'success': True,
            'alerts': mock_alerts
        })
    except Exception as e:
        current_app.logger.error(f"Ошибка при получении истории алертов: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500