# routes/admin/content_admin.py
# Управление образовательным контентом

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, g, current_app
from flask_login import current_user
from sqlalchemy import func, or_
from datetime import datetime
import json
import os
from werkzeug.utils import secure_filename
import re
import unicodedata

from models import db, LearningPath, Subject, Module, Lesson, Question, Test
from . import admin_required

# Создаем blueprint для контент админки
content_admin_bp = Blueprint('content_admin', __name__, url_prefix='/content')

def create_slug(text):
    """Создает URL-friendly slug из текста"""
    if not text:
        return ""
    
    # Удаляем HTML теги если есть
    text = re.sub(r'<[^>]+>', '', text)
    
    # Нормализуем unicode символы
    text = unicodedata.normalize('NFKD', text)
    
    # Конвертируем в нижний регистр
    text = text.lower()
    
    # Заменяем пробелы и специальные символы на дефисы
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    
    # Удаляем дефисы в начале и конце
    text = text.strip('-')
    
    return text[:50]  # Ограничиваем длину

# ================== DASHBOARD ==================

@content_admin_bp.route('/dashboard')
@admin_required(['content'])
def content_dashboard(lang):
    """Главная страница управления контентом"""
    
    # Статистика контента  
    stats = {
        'learning_paths': LearningPath.query.count(),
        'subjects': Subject.query.count(),
        'modules': Module.query.count(),
        'lessons': Lesson.query.count(),
        'questions': Question.query.count(),
        'tests': Test.query.count()
    }
    
    # Последние изменения
    recent_lessons = Lesson.query.order_by(Lesson.id.desc()).limit(10).all()
    
    # Модули без уроков 
    empty_modules = Module.query.outerjoin(Lesson).group_by(Module.id).having(func.count(Lesson.id) == 0).all()
    
    return render_template('admin/unified/content/dashboard.html',
                         stats=stats,
                         recent_lessons=recent_lessons,
                         empty_modules=empty_modules)

# ================== HIERARCHY MANAGEMENT ==================

@content_admin_bp.route('/hierarchy')
@admin_required(['content'])
def hierarchy_manager(lang):
    """Визуальное управление иерархией контента"""
    
    learning_paths = LearningPath.query.order_by(LearningPath.order).all()
    
    hierarchy_data = []
    for path in learning_paths:
        path_data = {
            'id': path.id,
            'type': 'path',
            'name': path.name,
            'order': path.order,
            'icon': path.icon,
            'children': []
        }
        
        for subject in path.subjects.order_by(Subject.order).all():
            subject_data = {
                'id': subject.id,
                'type': 'subject', 
                'name': subject.name,
                'order': subject.order,
                'icon': subject.icon,
                'children': []
            }
            
            for module in subject.module.order_by(Module.order).all():
                module_data = {
                    'id': module.id,
                    'type': 'module',
                    'name': module.title,
                    'order': module.order,
                    'icon': module.icon,
                    'is_premium': module.is_premium,
                    'lessons_count': module.lessons.count()
                }
                subject_data['children'].append(module_data)
            
            path_data['children'].append(subject_data)
        
        hierarchy_data.append(path_data)
    
    return render_template('admin/unified/content/hierarchy.html',
                         hierarchy_data=hierarchy_data)

# ================== LEARNING PATHS CRUD ==================

@content_admin_bp.route('/learning-paths')
@admin_required(['content'])
def learning_paths_list(lang):
    """Список категорий обучения"""
    paths = LearningPath.query.order_by(LearningPath.order).all()
    return render_template('admin/unified/content/learning_paths.html', paths=paths)

@content_admin_bp.route('/api/learning-paths', methods=['POST'])
@admin_required(['content'])
def create_learning_path(lang):
    """Создание новой категории обучения"""
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'success': False, 'message': 'Название обязательно'})
        
        max_order = db.session.query(func.max(LearningPath.order)).scalar() or 0
        
        new_path = LearningPath(
            name=data['name'],
            description=data.get('description', ''),
            icon=data.get('icon', 'list-task'),
            order=max_order + 1,
            exam_phase=data.get('exam_phase', 1)
        )
        
        db.session.add(new_path)
        db.session.commit()
        
        current_app.logger.info(f"Admin {current_user.email} created learning path: {new_path.name}")
        
        return jsonify({
            'success': True,
            'message': 'Категория обучения успешно создана',
            'path': {
                'id': new_path.id,
                'name': new_path.name,
                'description': new_path.description,
                'order': new_path.order
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating learning path: {e}")
        return jsonify({'success': False, 'message': str(e)})

@content_admin_bp.route('/api/learning-paths/<int:path_id>', methods=['PUT'])
@admin_required(['content'])
def update_learning_path(lang, path_id):
    """Обновление категории обучения"""
    try:
        path = LearningPath.query.get_or_404(path_id)
        data = request.get_json()
        
        # Обновляем поля
        if 'name' in data:
            path.name = data['name']
        if 'description' in data:
            path.description = data['description']
        if 'icon' in data:
            path.icon = data['icon']
        if 'exam_phase' in data:
            path.exam_phase = data['exam_phase']
            
        db.session.commit()
        
        current_app.logger.info(f"Admin {current_user.email} updated learning path: {path.name}")
        
        return jsonify({
            'success': True,
            'message': 'Категория обучения обновлена'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating learning path {path_id}: {e}")
        return jsonify({'success': False, 'message': str(e)})

@content_admin_bp.route('/api/learning-paths/<int:path_id>', methods=['DELETE'])
@admin_required(['content'])
def delete_learning_path(lang, path_id):
    """Удаление категории обучения"""
    try:
        path = LearningPath.query.get_or_404(path_id)
        
        # Проверяем, есть ли связанные предметы
        if path.subjects.count() > 0:
            return jsonify({
                'success': False, 
                'message': 'Нельзя удалить категорию, содержащую предметы'
            })
        
        path_name = path.name
        db.session.delete(path)
        db.session.commit()
        
        current_app.logger.info(f"Admin {current_user.email} deleted learning path: {path_name}")
        
        return jsonify({
            'success': True,
            'message': 'Категория обучения удалена'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting learning path {path_id}: {e}")
        return jsonify({'success': False, 'message': str(e)})

# ================== SUBJECTS CRUD ==================

@content_admin_bp.route('/subjects')
@admin_required(['content'])
def subjects_list(lang):
    """Список предметов"""
    subjects = Subject.query.join(LearningPath).order_by(LearningPath.order, Subject.order).all()
    paths = LearningPath.query.order_by(LearningPath.order).all()
    return render_template('admin/unified/content/subjects.html', subjects=subjects, paths=paths)

@content_admin_bp.route('/api/subjects', methods=['POST'])
@admin_required(['content'])
def create_subject(lang):
    """Создание нового предмета"""
    try:
        data = request.get_json()
        
        # Валидация
        if not data.get('name') or not data.get('learning_path_id'):
            return jsonify({'success': False, 'message': 'Название и категория обязательны'})
        
        # Проверяем существование пути обучения
        learning_path = LearningPath.query.get(data['learning_path_id'])
        if not learning_path:
            return jsonify({'success': False, 'message': 'Категория обучения не найдена'})
        
        # Определяем порядок внутри пути
        max_order = db.session.query(func.max(Subject.order)).filter_by(
            learning_path_id=data['learning_path_id']
        ).scalar() or 0
        
        new_subject = Subject(
            name=data['name'],
            description=data.get('description', ''),
            icon=data.get('icon', 'folder2-open'),
            learning_path_id=data['learning_path_id'],
            order=max_order + 1
        )
        
        db.session.add(new_subject)
        db.session.commit()
        
        current_app.logger.info(f"Admin {current_user.email} created subject: {new_subject.name}")
        
        return jsonify({
            'success': True,
            'message': 'Предмет успешно создан',
            'subject': {
                'id': new_subject.id,
                'name': new_subject.name,
                'description': new_subject.description,
                'learning_path_name': learning_path.name
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating subject: {e}")
        return jsonify({'success': False, 'message': str(e)})

# ================== MODULES CRUD ==================

@content_admin_bp.route('/modules')
@admin_required(['content'])
def modules_list(lang):
    """Список модулей с фильтрацией"""
    
    # Параметры фильтрации
    search = request.args.get('search', '')
    subject_id = request.args.get('subject_id', type=int)
    module_type = request.args.get('type', '')
    is_premium = request.args.get('premium', '')
    
    # Базовый запрос
    query = Module.query.join(Subject).join(LearningPath)
    
    # Применяем фильтры
    if search:
        query = query.filter(or_(
            Module.title.ilike(f'%{search}%'),
            Module.description.ilike(f'%{search}%')
        ))
    
    if subject_id:
        query = query.filter(Module.subject_id == subject_id)
    
    if module_type:
        query = query.filter(Module.module_type == module_type)
    
    if is_premium == 'true':
        query = query.filter(Module.is_premium == True)
    elif is_premium == 'false':
        query = query.filter(Module.is_premium == False)
    
    # Сортировка и пагинация
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    modules = query.order_by(LearningPath.order, Subject.order, Module.order).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Данные для фильтров
    subjects = Subject.query.join(LearningPath).order_by(LearningPath.order, Subject.order).all()
    
    return render_template('admin/unified/content/modules.html',
                         modules=modules,
                         subjects=subjects,
                         current_filters={
                             'search': search,
                             'subject_id': subject_id,
                             'type': module_type,
                             'premium': is_premium
                         })

@content_admin_bp.route('/modules/<int:module_id>/editor')
@admin_required(['content'])
def module_editor(lang, module_id):
    """Редактор модуля с WYSIWYG"""
    module = Module.query.get_or_404(module_id)
    lessons = module.lessons.order_by(Lesson.order).all()
    
    return render_template('admin/unified/content/module_editor.html',
                         module=module,
                         lessons=lessons)

# ================== WYSIWYG CONTENT EDITOR ==================

@content_admin_bp.route('/lessons/<int:lesson_id>/editor')
@admin_required(['content'])
def lesson_editor(lang, lesson_id):
    """WYSIWYG редактор урока"""
    lesson = Lesson.query.get_or_404(lesson_id)
    
    content_data = {}
    if lesson.content:
        try:
            content_data = json.loads(lesson.content)
        except json.JSONDecodeError:
            content_data = {'type': 'text', 'content': lesson.content}
    
    return render_template('admin/unified/content/lesson_editor.html',
                         lesson=lesson,
                         content_data=content_data)

@content_admin_bp.route('/api/lessons/<int:lesson_id>/content', methods=['POST'])
@admin_required(['content'])
def save_lesson_content(lang, lesson_id):
    """Сохранение контента урока"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        data = request.get_json()
        
        if not data.get('type'):
            return jsonify({'success': False, 'message': 'Тип контента обязателен'})
        
        lesson.content = json.dumps(data, ensure_ascii=False)
        lesson.content_type = data['type']
        
        db.session.commit()
        
        current_app.logger.info(f"Admin {current_user.email} updated lesson content: {lesson.title}")
        
        return jsonify({
            'success': True,
            'message': 'Контент урока сохранен'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving lesson content {lesson_id}: {e}")
        return jsonify({'success': False, 'message': str(e)})

# ================== FILE MANAGEMENT ==================

@content_admin_bp.route('/media')
@admin_required(['content'])
def media_manager(lang):
    """Файловый менеджер для медиа"""
    
    # Получаем структуру папок
    upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    
    return render_template('admin/unified/content/media_manager.html',
                         upload_dir=upload_dir)

@content_admin_bp.route('/api/upload', methods=['POST'])
@admin_required(['content'])
def upload_file(lang):
    """Загрузка файлов"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'Файл не выбран'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Файл не выбран'})
        
        # Проверка типа файла
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'mp4', 'webm', 'mp3', 'wav'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'success': False, 'message': 'Недопустимый тип файла'})
        
        # Сохранение файла
        filename = secure_filename(file.filename)
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        current_app.logger.info(f"Admin {current_user.email} uploaded file: {filename}")
        
        return jsonify({
            'success': True,
            'message': 'Файл успешно загружен',
            'filename': filename,
            'url': f'/uploads/{filename}'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error uploading file: {e}")
        return jsonify({'success': False, 'message': str(e)})

# ================== BULK OPERATIONS ==================

@content_admin_bp.route('/bulk')
@admin_required(['content'])
def bulk_operations(lang):
    """Массовые операции над контентом"""
    return render_template('admin/unified/content/bulk_operations.html')

@content_admin_bp.route('/api/bulk/modules', methods=['POST'])
@admin_required(['content'])
def bulk_update_modules(lang):
    """Массовое обновление модулей"""
    try:
        data = request.get_json()
        module_ids = data.get('module_ids', [])
        updates = data.get('updates', {})
        
        if not module_ids:
            return jsonify({'success': False, 'message': 'Модули не выбраны'})
        
        updated_count = 0
        for module_id in module_ids:
            module = Module.query.get(module_id)
            if module:
                # Применяем обновления
                if 'is_premium' in updates:
                    module.is_premium = updates['is_premium']
                if 'module_type' in updates:
                    module.module_type = updates['module_type']
                
                updated_count += 1
        
        db.session.commit()
        
        current_app.logger.info(f"Admin {current_user.email} bulk updated {updated_count} modules")
        
        return jsonify({
            'success': True,
            'message': f'Обновлено модулей: {updated_count}'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in bulk update: {e}")
        return jsonify({'success': False, 'message': str(e)})

# ================== CONTENT CATEGORIES CRUD ==================

@content_admin_bp.route('/api/content-categories', methods=['POST'])
@admin_required(['content'])
def create_content_category(lang):
    """Создание новой категории контента"""
    try:
        from models import ContentCategory
        
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'success': False, 'message': 'Название обязательно'})
        
        # Автоматически генерируем slug
        slug = create_slug(data['name'])
        
        # Проверяем уникальность slug
        existing = ContentCategory.query.filter_by(slug=slug).first()
        if existing:
            slug = f"{slug}-{ContentCategory.query.count() + 1}"
        
        max_order = db.session.query(func.max(ContentCategory.order)).scalar() or 0
        
        new_category = ContentCategory(
            name=data['name'],
            slug=slug,
            icon=data.get('icon', 'folder'),
            order=max_order + 1
        )
        
        db.session.add(new_category)
        db.session.commit()
        
        current_app.logger.info(f"Admin {current_user.email} created content category: {new_category.name}")
        
        return jsonify({
            'success': True,
            'message': 'Категория успешно создана',
            'category': {
                'id': new_category.id,
                'name': new_category.name,
                'slug': new_category.slug,
                'order': new_category.order,
                'url': url_for('content_nav.view_category', lang=lang, category_slug=new_category.slug)
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating content category: {e}")
        return jsonify({'success': False, 'message': str(e)})

@content_admin_bp.route('/api/content-subcategories', methods=['POST'])
@admin_required(['content'])
def create_content_subcategory(lang):
    """Создание новой подкатегории контента"""
    try:
        from models import ContentCategory, ContentSubcategory
        
        data = request.get_json()
        
        if not data.get('name') or not data.get('category_id'):
            return jsonify({'success': False, 'message': 'Название и категория обязательны'})
        
        # Проверяем существование категории
        category = ContentCategory.query.get(data['category_id'])
        if not category:
            return jsonify({'success': False, 'message': 'Категория не найдена'})
        
        # Автоматически генерируем slug
        slug = create_slug(data['name'])
        
        # Проверяем уникальность slug в рамках категории
        existing = ContentSubcategory.query.filter_by(
            slug=slug, 
            category_id=data['category_id']
        ).first()
        if existing:
            count = ContentSubcategory.query.filter_by(category_id=data['category_id']).count()
            slug = f"{slug}-{count + 1}"
        
        max_order = db.session.query(func.max(ContentSubcategory.order)).filter_by(
            category_id=data['category_id']
        ).scalar() or 0
        
        new_subcategory = ContentSubcategory(
            name=data['name'],
            slug=slug,
            category_id=data['category_id'],
            icon=data.get('icon', 'bookmark'),
            order=max_order + 1
        )
        
        db.session.add(new_subcategory)
        db.session.commit()
        
        current_app.logger.info(f"Admin {current_user.email} created content subcategory: {new_subcategory.name}")
        
        return jsonify({
            'success': True,
            'message': 'Подкатегория успешно создана',
            'subcategory': {
                'id': new_subcategory.id,
                'name': new_subcategory.name,
                'slug': new_subcategory.slug,
                'order': new_subcategory.order,
                'url': url_for('content_nav.view_subcategory', lang=lang, 
                              category_slug=category.slug, subcategory_slug=new_subcategory.slug)
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating content subcategory: {e}")
        return jsonify({'success': False, 'message': str(e)})

@content_admin_bp.route('/api/content-topics', methods=['POST'])
@admin_required(['content'])
def create_content_topic(lang):
    """Создание новой темы контента"""
    try:
        from models import ContentCategory, ContentSubcategory, ContentTopic
        
        data = request.get_json()
        
        if not data.get('name') or not data.get('subcategory_id'):
            return jsonify({'success': False, 'message': 'Название и подкатегория обязательны'})
        
        # Проверяем существование подкатегории
        subcategory = ContentSubcategory.query.get(data['subcategory_id'])
        if not subcategory:
            return jsonify({'success': False, 'message': 'Подкатегория не найдена'})
        
        # Автоматически генерируем slug
        slug = create_slug(data['name'])
        
        # Проверяем уникальность slug в рамках подкатегории
        existing = ContentTopic.query.filter_by(
            slug=slug, 
            subcategory_id=data['subcategory_id']
        ).first()
        if existing:
            count = ContentTopic.query.filter_by(subcategory_id=data['subcategory_id']).count()
            slug = f"{slug}-{count + 1}"
        
        max_order = db.session.query(func.max(ContentTopic.order)).filter_by(
            subcategory_id=data['subcategory_id']
        ).scalar() or 0
        
        new_topic = ContentTopic(
            name=data['name'],
            slug=slug,
            subcategory_id=data['subcategory_id'],
            description=data.get('description', ''),
            order=max_order + 1
        )
        
        db.session.add(new_topic)
        db.session.commit()
        
        current_app.logger.info(f"Admin {current_user.email} created content topic: {new_topic.name}")
        
        category = subcategory.content_category
        
        return jsonify({
            'success': True,
            'message': 'Тема успешно создана',
            'topic': {
                'id': new_topic.id,
                'name': new_topic.name,
                'slug': new_topic.slug,
                'order': new_topic.order,
                'url': url_for('content_nav.view_topic', lang=lang, 
                              category_slug=category.slug, 
                              subcategory_slug=subcategory.slug, 
                              topic_slug=new_topic.slug)
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating content topic: {e}")
        return jsonify({'success': False, 'message': str(e)}) 