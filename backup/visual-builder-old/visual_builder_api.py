from flask import Blueprint, request, jsonify, render_template, current_app, make_response
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import json, os, uuid
from datetime import datetime
from models import db, User, VisualBuilderPage, VisualBuilderTemplate, VisualBuilderMedia, VisualBuilderVersion

visual_builder_bp = Blueprint('visual_builder', __name__)

# === ОСНОВНЫЕ СТРАНИЦЫ ===

@visual_builder_bp.route('/visual-builder')
@login_required
def visual_builder():
    """Главная страница Visual Builder"""
    return render_template('admin/content_editor/visual_builder.html')

@visual_builder_bp.route('/visual-builder/page/<int:page_id>')
@login_required  
def edit_page(page_id):
    """Редактирование существующей страницы"""
    page = VisualBuilderPage.query.get_or_404(page_id)
    return render_template('admin/content_editor/visual_builder.html', page=page)

# === API ЭНДПОИНТЫ ===

@visual_builder_bp.route('/api/visual-builder/save', methods=['POST'])
@login_required
def save_page():
    """Сохранение страницы"""
    try:
        data = request.json
        
        page_id = data.get('page_id')
        content = data.get('content', '')
        title = data.get('title', 'Новая страница')
        description = data.get('description', '')
        settings = data.get('settings', {})
        
        if page_id:
            # Обновление существующей страницы
            page = VisualBuilderPage.query.get(page_id)
            if not page:
                return jsonify({'error': 'Страница не найдена'}), 404
            page.content_data = json.dumps(content)
            page.title = title
            page.description = description
            page.page_settings = json.dumps(settings)
            page.updated_at = datetime.utcnow()
            page.updated_by = current_user.id
        else:
            # Создание новой страницы
            slug = f"page-{uuid.uuid4().hex[:8]}"
            page = VisualBuilderPage(
                title=title,
                slug=slug,
                description=description,
                content_data=json.dumps(content),
                page_settings=json.dumps(settings),
                created_by=current_user.id,
                updated_by=current_user.id
            )
            db.session.add(page)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'page_id': page.id,
            'message': 'Страница сохранена'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@visual_builder_bp.route('/api/visual-builder/load/<int:page_id>')
@login_required
def load_page(page_id):
    """Загрузка страницы"""
    page = VisualBuilderPage.query.get_or_404(page_id)
    
    return jsonify({
        'id': page.id,
        'title': page.title,
        'description': page.description,
        'content': json.loads(page.content_data) if page.content_data else {},
        'settings': json.loads(page.page_settings) if page.page_settings else {},
        'created_at': page.created_at.isoformat(),
        'updated_at': page.updated_at.isoformat()
    })

@visual_builder_bp.route('/api/visual-builder/pages')
@login_required
def list_pages():
    """Список страниц пользователя"""
    pages = VisualBuilderPage.query.filter_by(created_by=current_user.id).all()
    
    return jsonify([{
        'id': page.id,
        'title': page.title,
        'description': page.description,
        'status': page.status,
        'is_published': page.is_published,
        'created_at': page.created_at.isoformat(),
        'updated_at': page.updated_at.isoformat()
    } for page in pages])

@visual_builder_bp.route('/api/visual-builder/delete/<int:page_id>', methods=['DELETE'])
@login_required
def delete_page(page_id):
    """Удаление страницы"""
    try:
        page = VisualBuilderPage.query.get_or_404(page_id)
        
        # Проверяем права доступа
        if page.created_by != current_user.id:
            return jsonify({'error': 'Нет прав для удаления'}), 403
        
        db.session.delete(page)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Страница удалена'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# === ШАБЛОНЫ ===

@visual_builder_bp.route('/api/templates')
@login_required
def get_templates():
    """Получение списка шаблонов"""
    templates = VisualBuilderTemplate.query.filter(
        (VisualBuilderTemplate.created_by == current_user.id) | 
        (VisualBuilderTemplate.is_public == True)
    ).all()
    
    return jsonify([{
        'id': t.id,
        'name': t.name,
        'description': t.description,
        'category': t.category,
        'icon': t.icon,
        'is_public': t.is_public,
        'usage_count': t.usage_count,
        'rating': t.rating,
        'created_at': t.created_at.isoformat()
    } for t in templates])

@visual_builder_bp.route('/api/templates', methods=['POST'])
@login_required
def create_template():
    """Создание нового шаблона"""
    try:
        data = request.json
        
        template = VisualBuilderTemplate(
            name=data['name'],
            description=data.get('description', ''),
            category=data.get('category', 'custom'),
            icon=data.get('icon', 'file-earmark'),
            template_structure=json.dumps(data['structure']),
            template_settings=json.dumps(data.get('settings', {})),
            is_public=data.get('is_public', False),
            created_by=current_user.id
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'template_id': template.id,
            'message': 'Шаблон создан'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@visual_builder_bp.route('/api/templates/<int:template_id>')
@login_required
def get_template(template_id):
    """Получение шаблона по ID"""
    template = VisualBuilderTemplate.query.get_or_404(template_id)
    
    # Проверяем права доступа
    if not template.is_public and template.created_by != current_user.id:
        return jsonify({'error': 'Нет прав доступа'}), 403
    
    return jsonify({
        'id': template.id,
        'name': template.name,
        'description': template.description,
        'category': template.category,
        'icon': template.icon,
        'structure': json.loads(template.template_structure) if template.template_structure else {},
        'settings': json.loads(template.template_settings) if template.template_settings else {},
        'created_at': template.created_at.isoformat()
    })

# === МЕДИА ===

@visual_builder_bp.route('/api/media/upload', methods=['POST'])
@login_required
def upload_media():
    """Загрузка медиа файлов"""
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не найден'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Создаем папку если не существует
        upload_folder = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'static/uploads'), 'visual-builder')
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Определяем тип файла
        file_type = get_file_type(file.content_type)
        
        # Сохраняем в БД
        media = VisualBuilderMedia(
            filename=unique_filename,
            original_filename=filename,
            file_path=file_path,
            file_url=f"/static/uploads/visual-builder/{unique_filename}",
            file_type=file_type,
            mime_type=file.content_type,
            file_size=os.path.getsize(file_path),
            uploaded_by=current_user.id
        )
        
        db.session.add(media)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'file_id': media.id,
            'filename': unique_filename,
            'url': media.file_url,
            'size': media.file_size,
            'type': media.file_type
        })
    
    return jsonify({'error': 'Недопустимый тип файла'}), 400

@visual_builder_bp.route('/api/media')
@login_required
def list_media():
    """Список медиа файлов пользователя"""
    media_files = VisualBuilderMedia.query.filter_by(uploaded_by=current_user.id).all()
    
    return jsonify([{
        'id': m.id,
        'filename': m.filename,
        'original_filename': m.original_filename,
        'url': m.file_url,
        'size': m.file_size,
        'type': m.file_type,
        'mime_type': m.mime_type,
        'uploaded_at': m.uploaded_at.isoformat()
    } for m in media_files])

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'webm', 'mp3', 'wav', 'pdf', 'doc', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(mime_type):
    """Определяет тип файла по MIME типу"""
    if mime_type.startswith('image/'):
        return 'image'
    elif mime_type.startswith('video/'):
        return 'video'
    elif mime_type.startswith('audio/'):
        return 'audio'
    else:
        return 'document'

# === ЭКСПОРТ ===

@visual_builder_bp.route('/api/export/<format>', methods=['POST'])
@login_required
def export_page(format):
    """Экспорт страницы в различных форматах"""
    try:
        data = request.json
        content = data.get('content', '')
        title = data.get('title', 'Экспортированная страница')
        
        if format == 'html':
            return export_as_html(content, title)
        elif format == 'json':
            return export_as_json(content, title)
        else:
            return jsonify({'error': 'Неподдерживаемый формат'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def export_as_html(content, title):
    """Экспорт как HTML"""
    html_template = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; }}
            .page-element {{ margin: 1rem 0; }}
        </style>
    </head>
    <body>
        <div class="container-fluid">
            {content}
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    response = make_response(html_template)
    response.headers['Content-Type'] = 'text/html'
    response.headers['Content-Disposition'] = f'attachment; filename="{title}.html"'
    return response

def export_as_json(content, title):
    """Экспорт как JSON"""
    export_data = {
        'title': title,
        'content': content,
        'exported_at': datetime.utcnow().isoformat(),
        'version': '1.0'
    }
    
    response = make_response(json.dumps(export_data, ensure_ascii=False, indent=2))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = f'attachment; filename="{title}.json"'
    return response

# === ВЕРСИОНИРОВАНИЕ ===

@visual_builder_bp.route('/api/visual-builder/versions/<int:page_id>')
@login_required
def get_page_versions(page_id):
    """Получение версий страницы"""
    page = VisualBuilderPage.query.get_or_404(page_id)
    
    if page.created_by != current_user.id:
        return jsonify({'error': 'Нет прав доступа'}), 403
    
    versions = VisualBuilderVersion.query.filter_by(vb_page_id=page_id).order_by(VisualBuilderVersion.version_number.desc()).all()
    
    return jsonify([{
        'id': v.id,
        'version_number': v.version_number,
        'title': v.title,
        'version_notes': v.version_notes,
        'created_at': v.created_at.isoformat(),
        'created_by': v.created_by
    } for v in versions])

@visual_builder_bp.route('/api/visual-builder/versions/<int:page_id>/<int:version_id>')
@login_required
def get_version_content(page_id, version_id):
    """Получение контента конкретной версии"""
    version = VisualBuilderVersion.query.get_or_404(version_id)
    
    if version.vb_page_id != page_id:
        return jsonify({'error': 'Версия не принадлежит странице'}), 400
    
    return jsonify({
        'id': version.id,
        'version_number': version.version_number,
        'title': version.title,
        'content': json.loads(version.content_data) if version.content_data else {},
        'settings': json.loads(version.page_settings) if version.page_settings else {},
        'version_notes': version.version_notes,
        'created_at': version.created_at.isoformat()
    })

# === СТАТИСТИКА ===

@visual_builder_bp.route('/api/visual-builder/stats')
@login_required
def get_stats():
    """Получение статистики пользователя"""
    try:
        pages_count = VisualBuilderPage.query.filter_by(created_by=current_user.id).count()
        templates_count = VisualBuilderTemplate.query.filter_by(created_by=current_user.id).count()
        media_count = VisualBuilderMedia.query.filter_by(uploaded_by=current_user.id).count()
        
        # Подсчет размера медиа файлов
        media_files = VisualBuilderMedia.query.filter_by(uploaded_by=current_user.id).all()
        total_size = sum(m.file_size for m in media_files)
        
        return jsonify({
            'pages_count': pages_count,
            'templates_count': templates_count,
            'media_count': media_count,
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === УТИЛИТЫ ===

@visual_builder_bp.route('/api/visual-builder/health')
def health_check():
    """Проверка здоровья API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0'
    })
