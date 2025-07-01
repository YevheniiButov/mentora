# routes/content_editor_routes.py
"""
Content Editor API для интерактивного веб-редактора контента
Интегрирован с существующими моделями и системой аутентификации
"""

import json
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import (
    Blueprint, render_template, request, jsonify, redirect, url_for, 
    flash, g, current_app, session, abort, send_file
)
from flask_login import login_required, current_user
from sqlalchemy import and_, or_, desc
from models import (
    db, ContentPage, ContentPageVersion, ContentTemplate,
    User, Lesson, Module, Subject
)
from utils.decorators import admin_required
from extensions import csrf

# Создаем Blueprint для Content Editor
content_editor_bp = Blueprint(
    'content_editor',
    __name__,
    url_prefix='/<string:lang>/editor',
    template_folder='../templates'
)

# Поддерживаемые языки
SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa', 'ar']
DEFAULT_LANGUAGE = 'en'

# Настройки загрузки файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'mp4', 'webm', 'pdf', 'doc', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    """Проверка разрешенных расширений файлов"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@content_editor_bp.before_request
def before_request_editor():
    """Обработка языка для всех маршрутов редактора"""
    lang_from_url = request.view_args.get('lang') if request.view_args else None
    
    if lang_from_url and lang_from_url in SUPPORTED_LANGUAGES:
        g.lang = lang_from_url
    else:
        g.lang = session.get('lang') or DEFAULT_LANGUAGE
    
    if session.get('lang') != g.lang:
        session['lang'] = g.lang

@content_editor_bp.context_processor
def inject_lang_editor():
    """Добавляет lang в контекст шаблонов"""
    return dict(lang=getattr(g, 'lang', 'en'))

# ==================== ВИЗУАЛЬНЫЙ РЕДАКТОР ====================

@content_editor_bp.route('/')
@login_required
@admin_required
def editor_interface(lang):
    """Основной интерфейс визуального редактора"""
    try:
        # Получаем параметры для предзагрузки контента
        page_id = request.args.get('page_id', type=int)
        lesson_id = request.args.get('lesson_id', type=int)
        module_id = request.args.get('module_id', type=int)
        subject_id = request.args.get('subject_id', type=int)
        
        # Получаем доступные шаблоны
        templates = ContentTemplate.query.filter_by(is_active=True).all()
        
        # Получаем иерархию контента для навигации
        hierarchy = get_content_hierarchy()
        
        return render_template('content_editor/editor.html',
                             page_id=page_id,
                             lesson_id=lesson_id,
                             module_id=module_id,
                             subject_id=subject_id,
                             templates=templates,
                             hierarchy=hierarchy)
    
    except Exception as e:
        current_app.logger.error(f"Error loading editor interface: {e}")
        flash('Ошибка загрузки редактора', 'error')
        return redirect(url_for('admin_bp.dashboard', lang=lang))

# ==================== API ENDPOINTS ====================

@content_editor_bp.route('/api/save', methods=['POST'])
@login_required
@admin_required
def save_content(lang):
    """Сохранение контента страницы"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'Нет данных для сохранения'}), 400
        
        # Валидация обязательных полей
        required_fields = ['title', 'content_data']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'message': f'Поле {field} обязательно'}), 400
        
        page_id = data.get('page_id')
        
        if page_id:
            # Обновление существующей страницы
            page = ContentPage.query.get_or_404(page_id)
            page.title = data['title']
            page.content_data = json.dumps(data['content_data'], ensure_ascii=False)
            page.page_metadata = json.dumps(data.get('metadata', {}), ensure_ascii=False)
            page.status = data.get('status', 'draft')
            page.updated_at = datetime.utcnow()
            page.updated_by = current_user.id
            
            # Создаем версию при изменении
            if data.get('create_version', False):
                page.create_version(current_user.id, data.get('version_notes'))
        
        else:
            # Создание новой страницы
            page = ContentPage(
                title=data['title'],
                slug=generate_slug(data['title']),
                content_data=json.dumps(data['content_data'], ensure_ascii=False),
                page_metadata=json.dumps(data.get('metadata', {}), ensure_ascii=False),
                status=data.get('status', 'draft'),
                language=g.lang,
                created_by=current_user.id,
                lesson_id=data.get('lesson_id'),
                module_id=data.get('module_id'),
                subject_id=data.get('subject_id'),
                template_id=data.get('template_id')
            )
            db.session.add(page)
        
        db.session.commit()
        
        current_app.logger.info(f"Content saved by user {current_user.id}: page_id={page.id}")
        
        return jsonify({
            'success': True,
            'page_id': page.id,
            'message': 'Контент успешно сохранен'
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving content: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@content_editor_bp.route('/api/publish', methods=['POST'])
@login_required
@admin_required
def publish_content(lang):
    """Публикация контента"""
    try:
        data = request.get_json()
        page_id = data.get('page_id')
        
        if not page_id:
            return jsonify({'success': False, 'message': 'ID страницы обязателен'}), 400
        
        page = ContentPage.query.get_or_404(page_id)
        
        # Проверяем, что контент готов к публикации
        if not page.content_data:
            return jsonify({'success': False, 'message': 'Контент не может быть пустым'}), 400
        
        page.status = 'published'
        page.is_published = True
        page.published_at = datetime.utcnow()
        page.updated_at = datetime.utcnow()
        page.updated_by = current_user.id
        
        db.session.commit()
        
        current_app.logger.info(f"Content published by user {current_user.id}: page_id={page.id}")
        
        return jsonify({
            'success': True,
            'message': 'Контент успешно опубликован'
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error publishing content: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@content_editor_bp.route('/api/preview')
@login_required
@admin_required
def preview_content(lang):
    """Предпросмотр контента"""
    try:
        page_id = request.args.get('page_id', type=int)
        content_data = request.args.get('content_data')
        
        if not page_id and not content_data:
            return jsonify({'success': False, 'message': 'Необходим ID страницы или данные контента'}), 400
        
        if page_id:
            page = ContentPage.query.get_or_404(page_id)
            content = json.loads(page.content_data) if page.content_data else {}
        else:
            content = json.loads(content_data) if content_data else {}
        
        # Здесь можно добавить дополнительную обработку контента для предпросмотра
        preview_html = render_preview_content(content)
        
        return jsonify({
            'success': True,
            'preview_html': preview_html
        })
    
    except Exception as e:
        current_app.logger.error(f"Error generating preview: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@content_editor_bp.route('/api/upload-media', methods=['POST'])
@login_required
@admin_required
def upload_media(lang):
    """Загрузка медиафайлов"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'Файл не найден'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Файл не выбран'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Неподдерживаемый тип файла'}), 400
        
        # Проверяем размер файла
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'success': False, 'message': 'Файл слишком большой'}), 400
        
        # Генерируем безопасное имя файла
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Создаем папку для загрузок, если её нет
        upload_folder = os.path.join(current_app.static_folder, 'uploads', 'editor')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Сохраняем файл
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Возвращаем URL файла
        file_url = f"/static/uploads/editor/{unique_filename}"
        
        current_app.logger.info(f"Media uploaded by user {current_user.id}: {filename}")
        
        return jsonify({
            'success': True,
            'file_url': file_url,
            'filename': filename,
            'message': 'Файл успешно загружен'
        })
    
    except Exception as e:
        current_app.logger.error(f"Error uploading media: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@content_editor_bp.route('/api/hierarchy')
@login_required
@admin_required
def get_hierarchy(lang):
    """Получение иерархии контента"""
    try:
        hierarchy = get_content_hierarchy()
        
        return jsonify({
            'success': True,
            'hierarchy': hierarchy
        })
    
    except Exception as e:
        current_app.logger.error(f"Error getting hierarchy: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@content_editor_bp.route('/api/autosave', methods=['POST'])
@login_required
@admin_required
def autosave_content(lang):
    """Автосохранение контента"""
    try:
        data = request.get_json()
        
        if not data or 'content_data' not in data:
            return jsonify({'success': False, 'message': 'Нет данных для автосохранения'}), 400
        
        page_id = data.get('page_id')
        
        if not page_id:
            return jsonify({'success': False, 'message': 'ID страницы обязателен для автосохранения'}), 400
        
        page = ContentPage.query.get(page_id)
        
        if not page:
            return jsonify({'success': False, 'message': 'Страница не найдена'}), 404
        
        # Обновляем только контент и метаданные
        page.content_data = json.dumps(data['content_data'], ensure_ascii=False)
        if 'metadata' in data:
            page.page_metadata = json.dumps(data['metadata'], ensure_ascii=False)
        page.updated_at = datetime.utcnow()
        page.updated_by = current_user.id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'autosaved_at': page.updated_at.isoformat(),
            'message': 'Автосохранение выполнено'
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error autosaving content: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def get_content_hierarchy():
    """Получение иерархии контента для навигации"""
    try:
        hierarchy = {
            'subjects': [],
            'modules': [],
            'lessons': [],
            'pages': []
        }
        
        # Получаем предметы
        subjects = Subject.query.all()
        for subject in subjects:
            subject_data = {
                'id': subject.id,
                'name': subject.name,
                'modules': []
            }
            
            # Получаем модули для предмета
            modules = Module.query.filter_by(subject_id=subject.id).all()
            for module in modules:
                module_data = {
                    'id': module.id,
                    'title': module.title,
                    'lessons': []
                }
                
                # Получаем уроки для модуля
                lessons = Lesson.query.filter_by(module_id=module.id).all()
                for lesson in lessons:
                    lesson_data = {
                        'id': lesson.id,
                        'title': lesson.title,
                        'pages': []
                    }
                    
                    # Получаем страницы для урока
                    pages = ContentPage.query.filter_by(lesson_id=lesson.id).all()
                    for page in pages:
                        page_data = {
                            'id': page.id,
                            'title': page.title,
                            'status': page.status,
                            'updated_at': page.updated_at.isoformat() if page.updated_at else None
                        }
                        lesson_data['pages'].append(page_data)
                    
                    module_data['lessons'].append(lesson_data)
                
                subject_data['modules'].append(module_data)
            
            hierarchy['subjects'].append(subject_data)
        
        return hierarchy
    
    except Exception as e:
        current_app.logger.error(f"Error getting content hierarchy: {e}")
        return {'subjects': [], 'modules': [], 'lessons': [], 'pages': []}

def generate_slug(title):
    """Генерация URL-friendly slug из заголовка"""
    import re
    import unicodedata
    
    # Нормализуем unicode символы
    title = unicodedata.normalize('NFKD', title)
    
    # Конвертируем в нижний регистр
    title = title.lower()
    
    # Заменяем пробелы и специальные символы на дефисы
    title = re.sub(r'[^\w\s-]', '', title)
    title = re.sub(r'[-\s]+', '-', title)
    
    # Удаляем дефисы в начале и конце
    title = title.strip('-')
    
    # Ограничиваем длину
    return title[:50]

def render_preview_content(content):
    """Рендеринг контента для предпросмотра"""
    try:
        # Здесь можно добавить логику рендеринга контента
        # Например, обработка markdown, HTML и т.д.
        
        if isinstance(content, dict):
            # Если контент в формате JSON
            return f"<div class='preview-content'>{content.get('html', '')}</div>"
        else:
            # Если контент в виде строки
            return f"<div class='preview-content'>{content}</div>"
    
    except Exception as e:
        current_app.logger.error(f"Error rendering preview: {e}")
        return "<div class='preview-content'>Ошибка рендеринга</div>"

# ==================== ДОПОЛНИТЕЛЬНЫЕ ENDPOINTS ====================

@content_editor_bp.route('/api/templates')
@login_required
@admin_required
def get_templates(lang):
    """Получение доступных шаблонов"""
    try:
        templates = ContentTemplate.query.filter_by(is_active=True).all()
        
        template_list = []
        for template in templates:
            template_list.append({
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'template_type': template.template_type,
                'template_structure': json.loads(template.template_structure) if template.template_structure else {}
            })
        
        return jsonify({
            'success': True,
            'templates': template_list
        })
    
    except Exception as e:
        current_app.logger.error(f"Error getting templates: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@content_editor_bp.route('/api/versions/<int:page_id>')
@login_required
@admin_required
def get_page_versions(lang, page_id):
    """Получение версий страницы"""
    try:
        page = ContentPage.query.get_or_404(page_id)
        versions = ContentPageVersion.query.filter_by(content_page_id=page_id).order_by(desc(ContentPageVersion.version_number)).all()
        
        version_list = []
        for version in versions:
            version_list.append({
                'id': version.id,
                'version_number': version.version_number,
                'title': version.title,
                'version_notes': version.version_notes,
                'created_at': version.created_at.isoformat(),
                'created_by': version.created_by
            })
        
        return jsonify({
            'success': True,
            'versions': version_list
        })
    
    except Exception as e:
        current_app.logger.error(f"Error getting page versions: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@content_editor_bp.route('/api/restore-version/<int:version_id>', methods=['POST'])
@login_required
@admin_required
def restore_version(lang, version_id):
    """Восстановление версии страницы"""
    try:
        version = ContentPageVersion.query.get_or_404(version_id)
        
        # Восстанавливаем контент из версии
        version.restore_to_page()
        
        db.session.commit()
        
        current_app.logger.info(f"Version restored by user {current_user.id}: version_id={version_id}")
        
        return jsonify({
            'success': True,
            'message': 'Версия успешно восстановлена'
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error restoring version: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500 