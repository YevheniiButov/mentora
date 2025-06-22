# routes/admin/uploader_routes.py
"""
Универсальная система загрузки контента для админ-панели Dental Academy
Поддерживает загрузку учебных модулей и виртуальных пациентов
"""

import json
import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, render_template, g
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import (
    LearningPath, Subject, Module, Lesson, 
    VirtualPatientScenario, ContentCategory,
    ContentSubcategory, ContentTopic
)
from flask_login import login_required, current_user
from utils.decorators import admin_required

# Создаем Blueprint для универсального загрузчика
uploader_bp = Blueprint('uploader', __name__, url_prefix='/<string:lang>/admin/uploader')

# Конфигурация
ALLOWED_EXTENSIONS = {'json'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    """Проверка разрешенных расширений файлов"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_json_file(file):
    """Валидация JSON файла"""
    try:
        content = file.read()
        file.seek(0)  # Возвращаем указатель в начало
        
        if len(content) > MAX_FILE_SIZE:
            return False, "Файл слишком большой (максимум 16MB)"
        
        data = json.loads(content.decode('utf-8'))
        return True, data
    except json.JSONDecodeError as e:
        return False, f"Неверный формат JSON: {str(e)}"
    except UnicodeDecodeError:
        return False, "Неверная кодировка файла"
    except Exception as e:
        return False, f"Ошибка чтения файла: {str(e)}"

@uploader_bp.route('/')
@login_required
@admin_required
def uploader_page(lang):
    """Страница универсального загрузчика"""
    try:
        # Получаем данные для селекторов
        learning_paths = LearningPath.query.order_by(LearningPath.order).all()
        
        return render_template(
            'admin/content_uploader_universal.html',
            learning_paths=learning_paths
        )
    except Exception as e:
        current_app.logger.error(f"Error loading uploader page: {e}")
        return "Ошибка загрузки страницы", 500

@uploader_bp.route('/api/subjects/<int:path_id>')
@login_required
@admin_required
def get_subjects(lang, path_id):
    """Получение предметов для выбранной категории обучения"""
    try:
        subjects = Subject.query.filter_by(learning_path_id=path_id).order_by(Subject.order).all()
        return jsonify([{
            'id': subject.id,
            'name': subject.name,
            'description': subject.description
        } for subject in subjects])
    except Exception as e:
        current_app.logger.error(f"Error getting subjects: {e}")
        return jsonify({'error': 'Ошибка получения предметов'}), 500

@uploader_bp.route('/api/modules/<int:subject_id>')
@login_required
@admin_required
def get_modules(lang, subject_id):
    """Получение модулей для выбранного предмета"""
    try:
        modules = Module.query.filter_by(subject_id=subject_id).order_by(Module.order).all()
        return jsonify([{
            'id': module.id,
            'title': module.title,
            'description': module.description,
            'lessons_count': module.lessons.count() if hasattr(module, 'lessons') else 0
        } for module in modules])
    except Exception as e:
        current_app.logger.error(f"Error getting modules: {e}")
        return jsonify({'error': 'Ошибка получения модулей'}), 500

@uploader_bp.route('/api/preview-learning-content', methods=['POST'])
@login_required
@admin_required
def preview_learning_content(lang):
    """Предпросмотр учебного контента перед загрузкой"""
    try:
        result = {'success': True, 'data': {}}
        
        # Обработка файла карточек
        if 'theory' in request.files:
            theory_file = request.files['theory']
            if theory_file and allowed_file(theory_file.filename):
                valid, theory_data = validate_json_file(theory_file)
                if valid:
                    result['data']['theory'] = theory_data[:5]  # Первые 5 для предпросмотра
                else:
                    return jsonify({'success': False, 'message': f'Ошибка в файле карточек: {theory_data}'})
        
        # Обработка файла тестов
        if 'tests' in request.files:
            tests_file = request.files['tests']
            if tests_file and allowed_file(tests_file.filename):
                valid, tests_data = validate_json_file(tests_file)
                if valid:
                    result['data']['tests'] = tests_data[:5]  # Первые 5 для предпросмотра
                else:
                    return jsonify({'success': False, 'message': f'Ошибка в файле тестов: {tests_data}'})
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error previewing learning content: {e}")
        return jsonify({'success': False, 'message': 'Ошибка предпросмотра'}), 500

@uploader_bp.route('/api/upload-learning-content', methods=['POST'])
@login_required
@admin_required
def upload_learning_content(lang):
    """Загрузка учебного контента в выбранный модуль"""
    try:
        current_app.logger.info("=== Начало загрузки учебного контента ===")
        
        module_id = request.form.get('module_id')
        current_app.logger.info(f"Получен module_id: {module_id}")
        
        if not module_id:
            return jsonify({'success': False, 'message': 'Не указан модуль'})
        
        module = Module.query.get_or_404(module_id)
        current_app.logger.info(f"Найден модуль: {module.title} (ID: {module.id})")
        
        uploaded_counts = {'theory': 0, 'tests': 0}
        
        # Обработка карточек обучения
        if 'theory' in request.files:
            theory_file = request.files['theory']
            current_app.logger.info(f"Получен файл карточек: {theory_file.filename}")
            if theory_file and allowed_file(theory_file.filename):
                valid, theory_data = validate_json_file(theory_file)
                if valid:
                    current_app.logger.info(f"Файл карточек валиден, содержит {len(theory_data)} элементов")
                    uploaded_counts['theory'] = process_theory_cards(module, theory_data)
                    current_app.logger.info(f"Обработано карточек: {uploaded_counts['theory']}")
                else:
                    current_app.logger.error(f"Ошибка валидации файла карточек: {theory_data}")
                    return jsonify({'success': False, 'message': f'Ошибка в файле карточек: {theory_data}'})
        
        # Обработка тестов
        if 'tests' in request.files:
            tests_file = request.files['tests']
            current_app.logger.info(f"Получен файл тестов: {tests_file.filename}")
            if tests_file and allowed_file(tests_file.filename):
                valid, tests_data = validate_json_file(tests_file)
                if valid:
                    current_app.logger.info(f"Файл тестов валиден, содержит {len(tests_data)} элементов")
                    uploaded_counts['tests'] = process_test_questions(module, tests_data)
                    current_app.logger.info(f"Обработано тестов: {uploaded_counts['tests']}")
                else:
                    current_app.logger.error(f"Ошибка валидации файла тестов: {tests_data}")
                    return jsonify({'success': False, 'message': f'Ошибка в файле тестов: {tests_data}'})
        
        # Создаем уроки на основе загруженного контента
        current_app.logger.info("Создание структуры уроков...")
        create_lessons_from_content(module)
        
        current_app.logger.info("Сохранение в базу данных...")
        db.session.commit()
        
        current_app.logger.info(f"=== Загрузка завершена успешно: {uploaded_counts} ===")
        
        return jsonify({
            'success': True,
            'message': 'Контент успешно загружен',
            'uploaded': uploaded_counts
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error uploading learning content: {e}")
        return jsonify({'success': False, 'message': f'Ошибка загрузки: {str(e)}'}), 500

def process_theory_cards(module, theory_data):
    """Обработка карточек обучения"""
    count = 0
    
    for card_data in theory_data:
        try:
            # Формируем контент карточки в правильном формате
            card_content = {
                'cards': [card_data]  # Оборачиваем в структуру, ожидаемую системой
            }
            
            # Создаем урок для карточки
            lesson = Lesson(
                title=card_data.get('card_title', 'Карточка обучения'),
                content=json.dumps(card_content, ensure_ascii=False),
                content_type='learning_card',  # Используем стандартный тип
                module_id=module.id,
                order=count + 1
            )
            
            # Добавляем изображение если есть
            if 'image' in card_data:
                # Можно добавить обработку изображений в будущем
                pass
            
            db.session.add(lesson)
            count += 1
            
        except Exception as e:
            current_app.logger.error(f"Error processing theory card: {e}")
            continue
    
    return count

def process_test_questions(module, tests_data):
    """Обработка тестовых вопросов"""
    count = 0
    
    # Группируем вопросы по module_title для создания тестовых уроков
    tests_by_module = {}
    for test_data in tests_data:
        module_title = test_data.get('module_title', 'Тест')
        if module_title not in tests_by_module:
            tests_by_module[module_title] = []
        tests_by_module[module_title].append(test_data)
    
    # Создаем тестовые уроки
    for module_title, questions in tests_by_module.items():
        try:
            # Формируем контент теста в JSON формате
            test_content = {
                'questions': []
            }
            
            for question_data in questions:
                # Обрабатываем правильный ответ
                answer = question_data.get('answer', 'A')
                if isinstance(answer, str) and len(answer) == 1 and answer.isalpha():
                    # Конвертируем букву в индекс (A=0, B=1, C=2, D=3)
                    correct_answer = ord(answer.upper()) - ord('A')
                else:
                    correct_answer = 0
                
                test_content['questions'].append({
                    'question': question_data.get('question', ''),
                    'options': question_data.get('options', []),
                    'correct_answer': correct_answer,
                    'explanation': question_data.get('explanation', ''),
                    'card_id': question_data.get('card_id', ''),
                    'tags': question_data.get('tags', []),
                    'source_references': question_data.get('source_references', []),
                    'scope': question_data.get('scope', 'intermediate'),
                    'module_title': question_data.get('module_title', module_title)
                })
            
            # Создаем урок-тест
            lesson = Lesson(
                title=f"Тест: {module_title}",
                content=json.dumps(test_content, ensure_ascii=False),
                content_type='quiz',  # Используем стандартный тип
                module_id=module.id,
                order=1000 + count  # Тесты идут после карточек
            )
            
            db.session.add(lesson)
            count += len(questions)
            
        except Exception as e:
            current_app.logger.error(f"Error processing test questions: {e}")
            continue
    
    return count

def create_lessons_from_content(module):
    """Создание структуры уроков: карточки → тест → карточки → тест"""
    try:
        # Получаем все уроки модуля
        theory_lessons = Lesson.query.filter_by(
            module_id=module.id, 
            content_type='learning_card'
        ).order_by(Lesson.order).all()
        
        test_lessons = Lesson.query.filter_by(
            module_id=module.id, 
            content_type='quiz'
        ).order_by(Lesson.order).all()
        
        # Перераспределяем порядок: 2-3 карточки, потом тест
        new_order = 1
        theory_index = 0
        test_index = 0
        
        while theory_index < len(theory_lessons) or test_index < len(test_lessons):
            # Добавляем 2-3 карточки
            for _ in range(min(3, len(theory_lessons) - theory_index)):
                if theory_index < len(theory_lessons):
                    theory_lessons[theory_index].order = new_order
                    new_order += 1
                    theory_index += 1
            
            # Добавляем тест если есть
            if test_index < len(test_lessons):
                test_lessons[test_index].order = new_order
                new_order += 1
                test_index += 1
        
    except Exception as e:
        current_app.logger.error(f"Error creating lesson structure: {e}")

@uploader_bp.route('/api/preview-scenario', methods=['POST'])
@login_required
@admin_required
def preview_scenario(lang):
    """Предпросмотр сценария виртуального пациента"""
    try:
        if 'scenario' not in request.files:
            return jsonify({'success': False, 'message': 'Файл сценария не найден'})
        
        scenario_file = request.files['scenario']
        if not scenario_file or not allowed_file(scenario_file.filename):
            return jsonify({'success': False, 'message': 'Неверный файл сценария'})
        
        valid, scenario_data = validate_json_file(scenario_file)
        if not valid:
            return jsonify({'success': False, 'message': f'Ошибка в файле сценария: {scenario_data}'})
        
        # Валидация структуры сценария
        required_fields = ['title', 'description']
        for field in required_fields:
            if field not in scenario_data:
                return jsonify({'success': False, 'message': f'Отсутствует обязательное поле: {field}'})
        
        # Подготавливаем данные для предпросмотра
        preview_data = {
            'title': scenario_data['title'],
            'description': scenario_data['description'],
            'difficulty': scenario_data.get('difficulty', 'medium'),
            'category': scenario_data.get('category', 'general'),
            'dialogue_nodes': len(scenario_data.get('dialogue_nodes', []))
        }
        
        return jsonify({'success': True, 'data': preview_data})
        
    except Exception as e:
        current_app.logger.error(f"Error previewing scenario: {e}")
        return jsonify({'success': False, 'message': 'Ошибка предпросмотра сценария'}), 500

@uploader_bp.route('/api/upload-scenario', methods=['POST'])
@login_required
@admin_required
def upload_scenario(lang):
    """Загрузка сценария виртуального пациента"""
    try:
        if 'scenario' not in request.files:
            return jsonify({'success': False, 'message': 'Файл сценария не найден'})
        
        scenario_file = request.files['scenario']
        category = request.form.get('category', 'general')
        difficulty = request.form.get('difficulty', 'medium')
        
        if not scenario_file or not allowed_file(scenario_file.filename):
            return jsonify({'success': False, 'message': 'Неверный файл сценария'})
        
        valid, scenario_data = validate_json_file(scenario_file)
        if not valid:
            return jsonify({'success': False, 'message': f'Ошибка в файле сценария: {scenario_data}'})
        
        # Создаем новый сценарий
        scenario = VirtualPatientScenario(
            title=scenario_data['title'],
            description=scenario_data['description'],
            difficulty=difficulty,
            category=category,
            scenario_data=json.dumps(scenario_data, ensure_ascii=False),
            created_at=datetime.utcnow(),
            is_published=True
        )
        
        db.session.add(scenario)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Сценарий успешно загружен',
            'scenario_id': scenario.id
        })
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Сценарий с таким названием уже существует'}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error uploading scenario: {e}")
        return jsonify({'success': False, 'message': f'Ошибка загрузки сценария: {str(e)}'}), 500

@uploader_bp.route('/api/batch-upload', methods=['POST'])
@login_required
@admin_required
def batch_upload(lang):
    """Массовая загрузка файлов"""
    try:
        files = request.files.getlist('files')
        if not files:
            return jsonify({'success': False, 'message': 'Файлы не выбраны'})
        
        results = {
            'total': len(files),
            'success': 0,
            'errors': 0,
            'details': []
        }
        
        for file in files:
            if not allowed_file(file.filename):
                results['errors'] += 1
                results['details'].append({
                    'filename': file.filename,
                    'status': 'error',
                    'message': 'Неподдерживаемый формат файла'
                })
                continue
            
            valid, data = validate_json_file(file)
            if not valid:
                results['errors'] += 1
                results['details'].append({
                    'filename': file.filename,
                    'status': 'error',
                    'message': f'Ошибка JSON: {data}'
                })
                continue
            
            # Определяем тип файла по содержимому
            file_type = detect_file_type(data)
            
            try:
                if file_type == 'learning_module':
                    process_batch_learning_module(data, file.filename)
                elif file_type == 'virtual_patient':
                    process_batch_virtual_patient(data, file.filename)
                else:
                    results['errors'] += 1
                    results['details'].append({
                        'filename': file.filename,
                        'status': 'error',
                        'message': 'Неизвестный тип файла'
                    })
                    continue
                
                results['success'] += 1
                results['details'].append({
                    'filename': file.filename,
                    'status': 'success',
                    'type': file_type
                })
                
            except Exception as e:
                results['errors'] += 1
                results['details'].append({
                    'filename': file.filename,
                    'status': 'error',
                    'message': str(e)
                })
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in batch upload: {e}")
        return jsonify({'success': False, 'message': f'Ошибка массовой загрузки: {str(e)}'}), 500

def detect_file_type(data):
    """Определение типа файла по содержимому"""
    if isinstance(data, list) and len(data) > 0:
        first_item = data[0]
        if 'card_title' in first_item or 'question' in first_item or 'module_title' in first_item:
            return 'learning_module'
    elif isinstance(data, dict):
        if 'scenario_data' in data or ('title' in data and 'description' in data and 'dialogue_nodes' in data):
            return 'virtual_patient'
    
    return 'unknown'

def process_batch_learning_module(data, filename):
    """Обработка модуля обучения в пакетном режиме"""
    # Создаем временный модуль для пакетных загрузок
    module_title = f"Пакетная загрузка: {filename}"
    
    # Можно добавить логику для автоматического создания модуля
    # Пока что просто логируем
    current_app.logger.info(f"Processing learning module from {filename}")

def process_batch_virtual_patient(data, filename):
    """Обработка виртуального пациента в пакетном режиме"""
    scenario = VirtualPatientScenario(
        title=data.get('title', f'Сценарий из {filename}'),
        description=data.get('description', ''),
        difficulty=data.get('difficulty', 'medium'),
        category=data.get('category', 'general'),
        scenario_data=json.dumps(data, ensure_ascii=False),
        created_at=datetime.utcnow(),
        is_published=True
    )
    
    db.session.add(scenario)

@uploader_bp.route('/api/learning-structure')
@login_required
@admin_required
def get_learning_structure(lang):
    """Получение полной структуры обучения для админки"""
    try:
        paths = LearningPath.query.order_by(LearningPath.order).all()
        structure = []
        
        for path in paths:
            path_data = {
                'id': path.id,
                'name': path.name,
                'subjects': []
            }
            
            for subject in path.subjects:
                subject_data = {
                    'id': subject.id,
                    'name': subject.name,
                    'modules': []
                }
                
                modules = Module.query.filter_by(subject_id=subject.id).order_by(Module.order).all()
                for module in modules:
                    module_data = {
                        'id': module.id,
                        'title': module.title,
                        'lessons_count': module.lessons.count() if hasattr(module, 'lessons') else 0
                    }
                    subject_data['modules'].append(module_data)
                
                path_data['subjects'].append(subject_data)
            
            structure.append(path_data)
        
        return jsonify(structure)
        
    except Exception as e:
        current_app.logger.error(f"Error getting learning structure: {e}")
        return jsonify({'error': 'Ошибка получения структуры обучения'}), 500

# === API endpoints для создания новых элементов ===

@uploader_bp.route('/api/create-learning-path', methods=['POST'])
@login_required
@admin_required
def create_learning_path(lang):
    """Создание новой категории обучения"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        icon = data.get('icon', 'list-task').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'Название категории обязательно'})
        
        # Проверяем уникальность названия
        existing = LearningPath.query.filter_by(name=name).first()
        if existing:
            return jsonify({'success': False, 'message': 'Категория с таким названием уже существует'})
        
        # Определяем порядок (следующий после последнего)
        max_order = db.session.query(db.func.max(LearningPath.order)).scalar() or 0
        
        new_path = LearningPath(
            name=name,
            description=description,
            icon=icon,
            order=max_order + 1
        )
        
        db.session.add(new_path)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Категория успешно создана',
            'data': {
                'id': new_path.id,
                'name': new_path.name,
                'description': new_path.description,
                'icon': new_path.icon
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating learning path: {e}")
        return jsonify({'success': False, 'message': 'Ошибка создания категории'}), 500

@uploader_bp.route('/api/create-subject', methods=['POST'])
@login_required
@admin_required
def create_subject(lang):
    """Создание нового предмета"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        learning_path_id = data.get('learning_path_id')
        icon = data.get('icon', 'folder2-open').strip()
        
        if not name or not learning_path_id:
            return jsonify({'success': False, 'message': 'Название предмета и категория обязательны'})
        
        # Проверяем существование категории
        learning_path = LearningPath.query.get(learning_path_id)
        if not learning_path:
            return jsonify({'success': False, 'message': 'Выбранная категория не найдена'})
        
        # Проверяем уникальность названия в рамках категории
        existing = Subject.query.filter_by(name=name, learning_path_id=learning_path_id).first()
        if existing:
            return jsonify({'success': False, 'message': 'Предмет с таким названием уже существует в этой категории'})
        
        # Определяем порядок (следующий после последнего в категории)
        max_order = db.session.query(db.func.max(Subject.order)).filter_by(learning_path_id=learning_path_id).scalar() or 0
        
        new_subject = Subject(
            name=name,
            description=description,
            learning_path_id=learning_path_id,
            icon=icon,
            order=max_order + 1
        )
        
        db.session.add(new_subject)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Предмет успешно создан',
            'data': {
                'id': new_subject.id,
                'name': new_subject.name,
                'description': new_subject.description,
                'learning_path_id': new_subject.learning_path_id,
                'icon': new_subject.icon
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating subject: {e}")
        return jsonify({'success': False, 'message': 'Ошибка создания предмета'}), 500

@uploader_bp.route('/api/create-module', methods=['POST'])
@login_required
@admin_required
def create_module(lang):
    """Создание нового модуля"""
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        subject_id = data.get('subject_id')
        module_type = data.get('module_type', 'content').strip()
        icon = data.get('icon', 'file-earmark-text').strip()
        is_premium = data.get('is_premium', False)
        
        if not title or not subject_id:
            return jsonify({'success': False, 'message': 'Название модуля и предмет обязательны'})
        
        # Проверяем существование предмета
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'success': False, 'message': 'Выбранный предмет не найден'})
        
        # Проверяем уникальность названия в рамках предмета
        existing = Module.query.filter_by(title=title, subject_id=subject_id).first()
        if existing:
            return jsonify({'success': False, 'message': 'Модуль с таким названием уже существует в этом предмете'})
        
        # Определяем порядок (следующий после последнего в предмете)
        max_order = db.session.query(db.func.max(Module.order)).filter_by(subject_id=subject_id).scalar() or 0
        
        new_module = Module(
            title=title,
            description=description,
            subject_id=subject_id,
            module_type=module_type,
            icon=icon,
            is_premium=is_premium,
            order=max_order + 1
        )
        
        db.session.add(new_module)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Модуль успешно создан',
            'data': {
                'id': new_module.id,
                'title': new_module.title,
                'description': new_module.description,
                'subject_id': new_module.subject_id,
                'module_type': new_module.module_type,
                'icon': new_module.icon,
                'is_premium': new_module.is_premium
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating module: {e}")
        return jsonify({'success': False, 'message': 'Ошибка создания модуля'}), 500 