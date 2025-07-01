# routes/content_editor.py - ИСПРАВЛЕННАЯ ВЕРСИЯ

import flask
from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timezone
import json
import logging
import os
import time
import uuid
import shutil
from pathlib import Path
from werkzeug.utils import secure_filename
import mimetypes
from sqlalchemy import or_, desc
from flask_wtf.csrf import generate_csrf

from extensions import db
from models import ContentTemplate, User, ContentPage, GrapesJSPage, GrapesJSAsset, GrapesJSTemplate, Lesson, Module, EditablePageTemplate
from utils.decorators import admin_required, api_login_required, api_admin_required
from utils.template_parser import Jinja2ToGrapesJSConverter

logger = logging.getLogger(__name__)

# Создаем Blueprint для основного интерфейса
content_editor_bp = Blueprint('content_editor', __name__, url_prefix='/<lang>/admin/content-editor')

# Создаем отдельный Blueprint для API редактора
content_editor_api_bp = Blueprint('content_editor_api', __name__, url_prefix='/api/content-editor')

# Функция для получения сообщений об ошибках
def get_error_message(error: str, lang: str = 'en') -> str:
    """Получение сообщения об ошибке на нужном языке"""
    messages = {
        'en': {
            'template_not_found': 'Template not found',
            'invalid_request': 'Invalid request data',
            'permission_denied': 'Permission denied',
            'server_error': 'Internal server error',
            'file_not_found': 'File not found',
            'invalid_template': 'Invalid template format',
            'save_failed': 'Failed to save template',
            'parse_failed': 'Failed to parse template',
            'deploy_failed': 'Failed to deploy template',
            'preview_failed': 'Failed to generate preview'
        },
        'ru': {
            'template_not_found': 'Шаблон не найден',
            'invalid_request': 'Неверные данные запроса',
            'permission_denied': 'Доступ запрещен',
            'server_error': 'Внутренняя ошибка сервера',
            'file_not_found': 'Файл не найден',
            'invalid_template': 'Неверный формат шаблона',
            'save_failed': 'Не удалось сохранить шаблон',
            'parse_failed': 'Не удалось разобрать шаблон',
            'deploy_failed': 'Не удалось опубликовать шаблон',
            'preview_failed': 'Не удалось создать предпросмотр'
        }
    }
    return messages.get(lang, messages['en']).get(error, error)

# Функция для получения сообщений об успехе
def get_success_message(message: str, lang: str = 'en') -> str:
    """Получение сообщения об успехе на нужном языке"""
    messages = {
        'en': {
            'template_saved': 'Template saved successfully',
            'template_loaded': 'Template loaded successfully',
            'template_parsed': 'Template parsed successfully',
            'template_deployed': 'Template deployed successfully',
            'preview_generated': 'Preview generated successfully',
            'css_updated': 'CSS variables updated successfully'
        },
        'ru': {
            'template_saved': 'Шаблон успешно сохранен',
            'template_loaded': 'Шаблон успешно загружен',
            'template_parsed': 'Шаблон успешно разобран',
            'template_deployed': 'Шаблон успешно опубликован',
            'preview_generated': 'Предпросмотр успешно создан',
            'css_updated': 'CSS переменные успешно обновлены'
        }
    }
    return messages.get(lang, messages['en']).get(message, message)

# API роуты для редактора (без языкового префикса)
@content_editor_api_bp.route('/templates', methods=['GET'])
@api_login_required
@api_admin_required
def api_get_templates():
    """API для получения списка шаблонов"""
    try:
        logger.info(f"API: Getting templates for user {current_user.id}")
        
        # Определяем язык из заголовка или параметра
        lang = request.args.get('lang', 'en')
        category = request.args.get('category')
        
        query = ContentTemplate.query.filter_by(language=lang)
        if category:
            query = query.filter_by(category=category)
        
        templates = query.all()
        
        result = []
        for template in templates:
            result.append({
                'id': template.id,
                'template_id': template.template_id,
                'name': template.name,
                'description': template.description,
                'category': template.category,
                'content': template.content,
                'type': template.type or 'html',
                'structure': json.loads(template.structure) if template.structure else [],
                'template_metadata': json.loads(template.template_metadata) if template.template_metadata else {},
                'tags': json.loads(template.tags) if template.tags else [],
                'is_system': template.is_system,
                'created_at': template.created_at.isoformat() if template.created_at else None
            })
        
        logger.info(f"API: Found {len(result)} templates")
        
        return jsonify({
            'success': True,
            'templates': result,
            'message': get_success_message('templates_loaded', lang)
        })
    except Exception as e:
        logger.error(f"API Error getting templates: {e}")
        return jsonify({
            'success': False,
            'error': get_error_message('server_error', 'en'),
            'details': str(e)
        }), 500

@content_editor_api_bp.route('/template/<template_id>', methods=['GET'])
@api_login_required
@api_admin_required
def api_get_template(template_id):
    """API для получения конкретного шаблона"""
    try:
        logger.info(f"API: Getting template {template_id} for user {current_user.id}")
        
        # Определяем язык из заголовка или параметра
        lang = request.args.get('lang', 'en')
        
        template = ContentTemplate.query.get_or_404(template_id)
        
        return jsonify({
            'success': True,
            'template': {
                'id': template.id,
                'template_id': template.template_id,
                'name': template.name,
                'description': template.description,
                'category': template.category,
                'content': template.content,
                'type': template.type or 'html',
                'structure': json.loads(template.structure) if template.structure else [],
                'template_metadata': json.loads(template.template_metadata) if template.template_metadata else {},
                'tags': json.loads(template.tags) if template.tags else [],
                'is_system': template.is_system,
                'language': template.language,
                'created_at': template.created_at.isoformat() if template.created_at else None
            },
            'message': get_success_message('template_loaded', lang)
        })
    except Exception as e:
        logger.error(f"API Error getting template {template_id}: {e}")
        return jsonify({
            'success': False,
            'error': get_error_message('template_not_found', 'en'),
            'details': str(e)
        }), 404

@content_editor_api_bp.route('/parse', methods=['POST'])
@api_login_required
@api_admin_required
def api_parse_template():
    """API для парсинга шаблона"""
    try:
        logger.info(f"API: Parsing template for user {current_user.id}")
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': get_error_message('invalid_request', 'en')
            }), 400
        
        template_content = data.get('template_content')
        template_type = data.get('template_type', 'html')
        
        if not template_content:
            return jsonify({
                'success': False,
                'error': get_error_message('invalid_request', 'en')
            }), 400
        
        # Используем парсер шаблонов
        converter = Jinja2ToGrapesJSConverter()
        
        if template_type == 'jinja2':
            # Парсим Jinja2 шаблон
            parsed = converter.parse_template(template_content)
            css_variables = converter.extract_css_variables(template_content)
        else:
            # Обычный HTML
            parsed = {
                'html': template_content,
                'css': '',
                'components': []
            }
            css_variables = {}
        
        logger.info(f"API: Template parsed successfully")
        
        return jsonify({
            'success': True,
            'html': parsed.get('html', template_content),
            'css': parsed.get('css', ''),
            'components': parsed.get('components', []),
            'css_variables': css_variables,
            'message': get_success_message('template_parsed', 'en')
        })
    except Exception as e:
        logger.error(f"API Error parsing template: {e}")
        return jsonify({
            'success': False,
            'error': get_error_message('parse_failed', 'en'),
            'details': str(e)
        }), 500

@content_editor_api_bp.route('/save', methods=['POST'])
@api_login_required
@api_admin_required
def api_save_template():
    """API для сохранения шаблона"""
    try:
        logger.info(f"API: Saving template for user {current_user.id}")
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': get_error_message('invalid_request', 'en')
            }), 400
        
        html = data.get('html')
        css = data.get('css', '')
        components = data.get('components', [])
        page_id = data.get('page_id')
        
        if not html:
            return jsonify({
                'success': False,
                'error': get_error_message('invalid_request', 'en')
            }), 400
        
        # Создаем резервную копию
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Сохраняем в базу данных или файл
        if page_id:
            # Сохраняем как страницу
            page = ContentPage.query.get(page_id)
            if not page:
                page = ContentPage(
                    id=page_id,
                    title=f"Page {page_id}",
                    content=html,
                    css=css,
                    created_by=current_user.id
                )
                db.session.add(page)
            else:
                page.content = html
                page.css = css
                page.updated_at = datetime.now()
            
            db.session.commit()
            logger.info(f"API: Page {page_id} saved successfully")
        else:
            # Сохраняем как шаблон
            template = ContentTemplate(
                name=f"Template {timestamp}",
                content=html,
                css=css,
                type='html',
                language='en',
                created_by=current_user.id
            )
            db.session.add(template)
            db.session.commit()
            logger.info(f"API: Template saved with ID {template.id}")
        
        return jsonify({
            'success': True,
            'message': get_success_message('template_saved', 'en'),
            'timestamp': timestamp
        })
    except Exception as e:
        logger.error(f"API Error saving template: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': get_error_message('save_failed', 'en'),
            'details': str(e)
        }), 500

@content_editor_api_bp.route('/preview', methods=['POST'])
@api_login_required
@api_admin_required
def api_preview_template():
    """API для создания предпросмотра"""
    try:
        logger.info(f"API: Generating preview for user {current_user.id}")
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': get_error_message('invalid_request', 'en')
            }), 400
        
        html = data.get('html')
        css = data.get('css', '')
        
        if not html:
            return jsonify({
                'success': False,
                'error': get_error_message('invalid_request', 'en')
            }), 400
        
        # Создаем полную HTML страницу для предпросмотра
        full_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Template Preview</title>
    <style>
        {css}
    </style>
</head>
<body>
    {html}
</body>
</html>
        """
        
        logger.info(f"API: Preview generated successfully")
        
        return jsonify({
            'success': True,
            'html': full_html,
            'message': get_success_message('preview_generated', 'en')
        })
    except Exception as e:
        logger.error(f"API Error generating preview: {e}")
        return jsonify({
            'success': False,
            'error': get_error_message('preview_failed', 'en'),
            'details': str(e)
        }), 500

@content_editor_api_bp.route('/deploy', methods=['POST'])
@api_login_required
@api_admin_required
def api_deploy_template():
    """API для публикации шаблона"""
    try:
        logger.info(f"API: Deploying template for user {current_user.id}")
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': get_error_message('invalid_request', 'en')
            }), 400
        
        html = data.get('html')
        css = data.get('css', '')
        page_id = data.get('page_id')
        
        if not html:
            return jsonify({
                'success': False,
                'error': get_error_message('invalid_request', 'en')
            }), 400
        
        # Здесь должна быть логика публикации в продакшн
        # Пока что просто сохраняем как опубликованную версию
        
        if page_id:
            page = ContentPage.query.get(page_id)
            if page:
                page.content = html
                page.css = css
                page.is_published = True
                page.published_at = datetime.now()
                page.updated_at = datetime.now()
                db.session.commit()
        
        logger.info(f"API: Template deployed successfully")
        
        return jsonify({
            'success': True,
            'message': get_success_message('template_deployed', 'en'),
            'deployed_at': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"API Error deploying template: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': get_error_message('deploy_failed', 'en'),
            'details': str(e)
        }), 500

@content_editor_api_bp.route('/css-variables', methods=['GET'])
@api_login_required
@api_admin_required
def api_get_css_variables():
    """API для получения CSS переменных"""
    try:
        logger.info(f"API: Getting CSS variables for user {current_user.id}")
        
        # Загружаем CSS переменные из файла или базы данных
        css_vars_file = Path('static/css/themes/core-variables.css')
        
        if css_vars_file.exists():
            content = css_vars_file.read_text(encoding='utf-8')
            # Простой парсинг CSS переменных
            variables = {}
            for line in content.split('\n'):
                if line.strip().startswith('--'):
                    parts = line.strip().split(':')
                    if len(parts) == 2:
                        var_name = parts[0].strip()
                        var_value = parts[1].strip().rstrip(';')
                        variables[var_name] = var_value
        else:
            # Дефолтные переменные
            variables = {
                '--primary-color': '#667eea',
                '--secondary-color': '#764ba2',
                '--accent-color': '#f093fb',
                '--text-color': '#333333',
                '--background-color': '#ffffff',
                '--border-radius': '5px'
            }
        
        logger.info(f"API: Found {len(variables)} CSS variables")
        
        return jsonify({
            'success': True,
            'variables': variables,
            'message': 'CSS variables loaded successfully'
        })
    except Exception as e:
        logger.error(f"API Error getting CSS variables: {e}")
        return jsonify({
            'success': False,
            'error': get_error_message('server_error', 'en'),
            'details': str(e)
        }), 500

@content_editor_api_bp.route('/css-variables', methods=['PUT', 'POST'])
@api_login_required
@api_admin_required
def api_update_css_variables():
    """API для обновления CSS переменных"""
    try:
        logger.info(f"API: Updating CSS variables for user {current_user.id}")
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': get_error_message('invalid_request', 'en')
            }), 400
        
        variables = data.get('variables', {})
        
        if not variables:
            return jsonify({
                'success': False,
                'error': get_error_message('invalid_request', 'en')
            }), 400
        
        # Обновляем CSS переменные в файле
        css_vars_file = Path('static/css/themes/core-variables.css')
        
        # Создаем директорию если не существует
        css_vars_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Формируем CSS контент
        css_content = ":root {\n"
        for var_name, var_value in variables.items():
            css_content += f"    {var_name}: {var_value};\n"
        css_content += "}\n"
        
        # Создаем резервную копию
        if css_vars_file.exists():
            backup_file = css_vars_file.with_suffix('.css.backup')
            shutil.copy2(css_vars_file, backup_file)
        
        # Сохраняем новые переменные
        css_vars_file.write_text(css_content, encoding='utf-8')
        
        logger.info(f"API: CSS variables updated successfully")
        
        return jsonify({
            'success': True,
            'message': get_success_message('css_updated', 'en'),
            'variables': variables
        })
    except Exception as e:
        logger.error(f"API Error updating CSS variables: {e}")
        return jsonify({
            'success': False,
            'error': get_error_message('server_error', 'en'),
            'details': str(e)
        }), 500

# Обработчик ошибок для API
@content_editor_api_bp.errorhandler(403)
def forbidden_error(error):
    logger.warning(f"API: 403 Forbidden error - User: {current_user.id if current_user.is_authenticated else 'Anonymous'}")
    return jsonify({
        'success': False,
        'error': get_error_message('permission_denied', 'en'),
        'details': 'Access denied. Please check your permissions.'
    }), 403

@content_editor_api_bp.errorhandler(404)
def not_found_error(error):
    logger.warning(f"API: 404 Not Found error - User: {current_user.id if current_user.is_authenticated else 'Anonymous'}")
    return jsonify({
        'success': False,
        'error': get_error_message('file_not_found', 'en'),
        'details': 'Resource not found.'
    }), 404

@content_editor_api_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"API: 500 Internal Server Error - User: {current_user.id if current_user.is_authenticated else 'Anonymous'}")
    return jsonify({
        'success': False,
        'error': get_error_message('server_error', 'en'),
        'details': 'Internal server error occurred.'
    }), 500

@content_editor_bp.route('/')
@login_required
@admin_required
def dashboard(lang):
    """Главная страница Content Editor"""
    try:
        # Получаем статистику
        total_templates = ContentTemplate.query.filter_by(language=lang).count()
        system_templates = ContentTemplate.query.filter_by(language=lang, is_system=True).count()
        user_templates = ContentTemplate.query.filter_by(language=lang, is_system=False).count()
        
        # Получаем последние шаблоны
        recent_templates = ContentTemplate.query.filter_by(language=lang).order_by(ContentTemplate.created_at.desc()).limit(5).all()
        
        return render_template('admin/content_editor/dashboard.html', 
                             lang=lang,
                             total_templates=total_templates,
                             system_templates=system_templates,
                             user_templates=user_templates,
                             recent_templates=recent_templates)
    except Exception as e:
        logger.error(f"Error loading content editor dashboard: {e}")
        return render_template('admin/content_editor/dashboard.html', 
                             lang=lang,
                             total_templates=0,
                             system_templates=0,
                             user_templates=0,
                             recent_templates=[])

@content_editor_bp.route('/templates')
@login_required
@admin_required
def templates_page(lang):
    """Страница управления шаблонами"""
    try:
        # Получаем все шаблоны
        templates = ContentTemplate.query.filter_by(language=lang).all()
        
        # Группируем по категориям
        categories = {}
        for template in templates:
            category = template.category or 'general'
            if category not in categories:
                categories[category] = []
            categories[category].append({
                'id': template.id,
                'template_id': template.template_id,
                'name': template.name,
                'description': template.description,
                'is_system': template.is_system,
                'created_at': template.created_at,
                'tags': template.tags if template.tags else []
            })
        
        return render_template('admin/content_editor/templates.html', 
                             categories=categories, 
                             lang=lang)
    except Exception as e:
        logger.error(f"Error loading templates page: {e}")
        return render_template('admin/content_editor/templates.html', 
                             categories={}, 
                             lang=lang)

@content_editor_bp.route('/templates-list')
@login_required
@admin_required
def templates_list(lang):
    """Список шаблонов (альтернативное представление)"""
    return templates_page(lang)

@content_editor_bp.route('/pages')
@login_required
@admin_required
def pages_list(lang):
    """Страница управления страницами контента"""
    try:
        # Пока что возвращаем заглушку
        return render_template('admin/content_editor/pages.html', 
                             lang=lang,
                             pages=[])
    except Exception as e:
        logger.error(f"Error loading pages list: {e}")
        return render_template('admin/content_editor/pages.html', 
                             lang=lang,
                             pages=[])

@content_editor_bp.route('/api/templates')
@login_required
@admin_required
def api_get_templates(lang):
    """API для получения списка шаблонов"""
    try:
        category = request.args.get('category')
        
        query = ContentTemplate.query.filter_by(language=lang)
        if category:
            query = query.filter_by(category=category)
        
        templates = query.all()
        
        result = []
        for template in templates:
            result.append({
                'id': template.id,
                'template_id': template.template_id,
                'name': template.name,
                'description': template.description,
                'category': template.category,
                'structure': json.loads(template.structure) if template.structure else [],
                'template_metadata': json.loads(template.template_metadata) if template.template_metadata else {},
                'tags': json.loads(template.tags) if template.tags else [],
                'is_system': template.is_system,
                'created_at': template.created_at.isoformat() if template.created_at else None
            })
        
        return jsonify({
            'success': True,
            'templates': result
        })
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_editor_bp.route('/api/templates/<int:template_id>')
@login_required
@admin_required
def api_get_template(lang, template_id):
    """API для получения конкретного шаблона"""
    try:
        template = ContentTemplate.query.get_or_404(template_id)
        
        return jsonify({
            'success': True,
            'template': {
                'id': template.id,
                'template_id': template.template_id,
                'name': template.name,
                'description': template.description,
                'category': template.category,
                'structure': json.loads(template.structure) if template.structure else [],
                'template_metadata': json.loads(template.template_metadata) if template.template_metadata else {},
                'tags': json.loads(template.tags) if template.tags else [],
                'is_system': template.is_system,
                'language': template.language,
                'created_at': template.created_at.isoformat() if template.created_at else None
            }
        })
    except Exception as e:
        logger.error(f"Error getting template {template_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_editor_bp.route('/api/templates', methods=['POST'])
@login_required
@admin_required
def api_create_template(lang):
    """API для создания нового шаблона"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Template name is required'
            }), 400
        
        template = ContentTemplate(
            template_id=data.get('template_id', f"custom_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"),
            name=data['name'],
            description=data.get('description', ''),
            category=data.get('category', 'general'),
            structure=json.dumps(data.get('structure', [])),
            template_metadata=json.dumps(data.get('template_metadata', {})),
            tags=json.dumps(data.get('tags', [])),
            is_system=False,  # Пользовательские шаблоны не системные
            language=lang,
            created_by=current_user.id
        )
        
        db.session.add(template)
        db.session.commit()
        
        logger.info(f"Template created: {template.id} by user {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': 'Template created successfully',
            'template_id': template.id
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating template: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_editor_bp.route('/api/templates/<int:template_id>', methods=['PUT'])
@login_required
@admin_required
def api_update_template(lang, template_id):
    """API для обновления шаблона"""
    try:
        template = ContentTemplate.query.get_or_404(template_id)
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Обновляем поля
        if 'name' in data:
            template.name = data['name']
        if 'description' in data:
            template.description = data['description']
        if 'category' in data:
            template.category = data['category']
        if 'structure' in data:
            template.structure = json.dumps(data['structure'])
        if 'template_metadata' in data:
            template.template_metadata = json.dumps(data['template_metadata'])
        if 'tags' in data:
            template.tags = json.dumps(data['tags'])
        
        template.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Template updated: {template.id} by user {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': 'Template updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating template {template_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_editor_bp.route('/api/templates/<int:template_id>', methods=['DELETE'])
@login_required
@admin_required
def api_delete_template(lang, template_id):
    """API для удаления шаблона"""
    try:
        template = ContentTemplate.query.get_or_404(template_id)
        
        # Проверяем права доступа
        if template.is_system and current_user.role != 'admin':
            return jsonify({
                'success': False,
                'error': 'Cannot delete system templates'
            }), 403
        
        if template.created_by != current_user.id and current_user.role != 'admin':
            return jsonify({
                'success': False,
                'error': 'Cannot delete template created by another user'
            }), 403
        
        db.session.delete(template)
        db.session.commit()
        
        logger.info(f"Template deleted: {template_id} by user {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': 'Template deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting template {template_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_editor_bp.route('/api/templates/import', methods=['POST'])
@login_required
@admin_required
def api_import_templates(lang):
    """API для импорта шаблонов"""
    try:
        # Здесь будет логика импорта шаблонов
        return jsonify({
            'success': True,
            'message': 'Templates imported successfully'
        })
    except Exception as e:
        logger.error(f"Error importing templates: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_editor_bp.route('/api/templates/export')
@login_required
@admin_required
def api_export_templates(lang):
    """API для экспорта шаблонов"""
    try:
        # Здесь будет логика экспорта шаблонов
        return jsonify({
            'success': True,
            'message': 'Templates exported successfully'
        })
    except Exception as e:
        logger.error(f"Error exporting templates: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_editor_bp.route('/api/templates/<int:template_id>/clone', methods=['POST'])
@login_required
@admin_required
def api_clone_template(lang, template_id):
    """API для клонирования шаблона"""
    try:
        original_template = ContentTemplate.query.get_or_404(template_id)
        
        # Создаем копию шаблона
        cloned_template = ContentTemplate(
            template_id=f"clone_{original_template.template_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            name=f"Copy of {original_template.name}",
            description=original_template.description,
            category=original_template.category,
            structure=original_template.structure,
            template_metadata=original_template.template_metadata,
            tags=original_template.tags,
            is_system=False,  # Клонированные шаблоны не системные
            language=lang,
            created_by=current_user.id
        )
        
        db.session.add(cloned_template)
        db.session.commit()
        
        logger.info(f"Template cloned: {original_template.id} -> {cloned_template.id} by user {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': 'Template cloned successfully',
            'template_id': cloned_template.id
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error cloning template {template_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_editor_bp.route('/api/media/upload', methods=['POST'])
@login_required
@admin_required
def api_media_upload(lang):
    """API для загрузки медиа файлов"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Здесь будет логика загрузки файла
        # Пока что возвращаем заглушку
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'file_url': f'/static/uploads/{file.filename}'
        })
    except Exception as e:
        logger.error(f"Error uploading media: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_editor_bp.route('/api/media/library', methods=['GET'])
@login_required
@admin_required
def api_media_library(lang):
    """API для получения медиа библиотеки"""
    try:
        # Здесь будет логика получения медиа файлов
        # Пока что возвращаем пустой список
        return jsonify({
            'success': True,
            'media': []
        })
    except Exception as e:
        logger.error(f"Error getting media library: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_editor_bp.route('/api/media/<file_id>', methods=['DELETE'])
@login_required
@admin_required
def api_delete_media(lang, file_id):
    """API для удаления медиа файла"""
    try:
        # Здесь будет логика удаления файла
        return jsonify({
            'success': True,
            'message': 'File deleted successfully'
        })
    except Exception as e:
        logger.error(f"Error deleting media {file_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_editor_bp.route('/api/export/<format>', methods=['POST'])
@login_required
@admin_required
def api_export_page(lang, format):
    """API для экспорта страницы"""
    try:
        data = request.get_json()
        
        if not data or not data.get('content'):
            return jsonify({
                'success': False,
                'error': 'Content is required'
            }), 400
        
        # Здесь будет логика экспорта в разных форматах
        return jsonify({
            'success': True,
            'message': f'Page exported to {format} successfully',
            'download_url': f'/api/download/export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.{format}'
        })
    except Exception as e:
        logger.error(f"Error exporting page to {format}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===== GRAPESJS API ENDPOINTS =====

@content_editor_bp.route('/grapejs')
# @login_required
# @admin_required
def grapejs_builder(lang):
    """GrapesJS Visual Builder"""
    try:
        page_id = request.args.get('page_id')
        page = None
        if page_id:
            page = ContentPage.query.get(page_id)
        csrf_token = generate_csrf()
        return flask.render_template(
            'admin/content_editor/grapesjs_builder.html',
            lang=lang,
            page=page,
            csrf_token=csrf_token
        )
    except Exception as e:
        logger.error(f"Error loading GrapesJS builder: {e}")
        flash(f"Ошибка загрузки редактора: {e}", 'danger')
        csrf_token = generate_csrf()
        return flask.render_template(
            'admin/content_editor/grapesjs_builder.html',
            lang=lang,
            page=None,
            csrf_token=csrf_token
        )

@content_editor_bp.route('/api/grapejs/save', methods=['POST'])
@login_required
@admin_required
def api_grapejs_save(lang):
    """API для сохранения страницы GrapesJS"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Валидация обязательных полей
        required_fields = ['html', 'css']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Определяем, создаем новую страницу или обновляем существующую
        page_id = data.get('page_id')
        title = data.get('title', 'Новая страница')
        
        if page_id:
            # Обновляем существующую страницу
            page = ContentPage.query.get(page_id)
            if not page:
                return jsonify({
                    'success': False,
                    'error': 'Page not found'
                }), 404
            
            # Проверяем права доступа
            if page.created_by != current_user.id and current_user.role != 'admin':
                return jsonify({
                    'success': False,
                    'error': 'Access denied'
                }), 403
            
            # Обновляем данные
            page.title = title
            page.content_data = json.dumps({
                'html': data['html'],
                'css': data['css'],
                'components': data.get('components'),
                'styles': data.get('styles')
            })
            page.updated_at = datetime.now(timezone.utc)
            page.updated_by = current_user.id
            
        else:
            # Создаем новую страницу
            page = ContentPage(
                title=title,
                slug=f"page-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                content_type='custom',
                content_data=json.dumps({
                    'html': data['html'],
                    'css': data['css'],
                    'components': data.get('components'),
                    'styles': data.get('styles')
                }),
                language=lang,
                created_by=current_user.id
            )
            db.session.add(page)
        
        db.session.commit()
        
        logger.info(f"GrapesJS page saved: {page.id} by user {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': 'Page saved successfully',
            'page_id': page.id,
            'page_slug': page.slug,
            'saved_at': page.updated_at.isoformat() if page.updated_at else page.created_at.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving GrapesJS page: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_editor_bp.route('/api/grapejs/load')
@login_required
@admin_required
def api_grapejs_load(lang):
    """API для загрузки страницы GrapesJS"""
    try:
        page_id = request.args.get('page_id')
        
        if not page_id:
            return jsonify({
                'success': False,
                'error': 'Page ID required'
            }), 400
        
        page = ContentPage.query.get(page_id)
        if not page:
            return jsonify({
                'success': False,
                'error': 'Page not found'
            }), 404
        
        # Проверяем права доступа
        if page.created_by != current_user.id and current_user.role != 'admin':
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        # Парсим данные контента
        content_data = page.get_content_data()
        
        return jsonify({
            'success': True,
            'html': content_data.get('html', ''),
            'css': content_data.get('css', ''),
            'components': content_data.get('components'),
            'styles': content_data.get('styles'),
            'page_info': {
                'id': page.id,
                'title': page.title,
                'slug': page.slug,
                'created_at': page.created_at.isoformat(),
                'updated_at': page.updated_at.isoformat() if page.updated_at else None
            }
        })
        
    except Exception as e:
        logger.error(f"Error loading GrapesJS page: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_editor_bp.route('/api/grapejs/upload-asset', methods=['POST'])
@login_required
@admin_required
def api_grapejs_upload_asset(lang):
    """API для загрузки медиа файлов в GrapesJS"""
    try:
        if 'files' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No files provided'
            }), 400
        
        files = request.files.getlist('files')
        uploaded_files = []
        
        for file in files:
            if file.filename == '':
                continue
            
            # Проверяем тип файла
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'mp4', 'webm', 'ogg', 'mp3', 'wav', 'pdf'}
            if not ('.' in file.filename and 
                    file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
                continue
            
            # Проверяем размер файла (10MB максимум)
            if len(file.read()) > 10 * 1024 * 1024:
                file.seek(0)  # Сбрасываем позицию чтения
                continue
            
            file.seek(0)  # Сбрасываем позицию чтения
            
            # Сохраняем файл
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            
            # Создаем директорию если не существует
            upload_dir = os.path.join('static', 'uploads', 'grapejs')
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            # Определяем тип файла
            file_extension = filename.rsplit('.', 1)[1].lower()
            if file_extension in {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}:
                file_type = 'image'
            elif file_extension in {'mp4', 'webm', 'ogg'}:
                file_type = 'video'
            elif file_extension in {'mp3', 'wav'}:
                file_type = 'audio'
            else:
                file_type = 'document'
            
            uploaded_files.append({
                'src': f'/static/uploads/grapejs/{filename}',
                'type': file_type,
                'name': filename,
                'size': os.path.getsize(file_path)
            })
        
        return jsonify({
            'success': True,
            'files': uploaded_files
        })
        
    except Exception as e:
        logger.error(f"Error uploading GrapesJS assets: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_editor_bp.route('/api/grapejs/templates')
@login_required
@admin_required
def api_grapejs_templates(lang):
    """API для получения шаблонов GrapesJS"""
    try:
        # Здесь можно загружать шаблоны из базы данных или файлов
        templates = [
            {
                'id': 'dental-chart',
                'name': 'Зубная формула',
                'description': 'Интерактивная зубная формула для записи состояния зубов',
                'category': 'Стоматология',
                'thumbnail': '/static/images/templates/dental-chart.png'
            },
            {
                'id': 'case-study',
                'name': 'Клинический случай',
                'description': 'Шаблон для описания клинических случаев',
                'category': 'Стоматология',
                'thumbnail': '/static/images/templates/case-study.png'
            },
            {
                'id': 'treatment-plan',
                'name': 'План лечения',
                'description': 'Структурированный план лечения пациента',
                'category': 'Стоматология',
                'thumbnail': '/static/images/templates/treatment-plan.png'
            },
            {
                'id': 'quiz-template',
                'name': 'Образовательный тест',
                'description': 'Интерактивный тест для проверки знаний',
                'category': 'Образование',
                'thumbnail': '/static/images/templates/quiz.png'
            }
        ]
        
        return jsonify({
            'success': True,
            'templates': templates
        })
        
    except Exception as e:
        logger.error(f"Error getting GrapesJS templates: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_editor_bp.route('/api/grapejs/templates/<template_id>')
@login_required
@admin_required
def api_grapejs_template(lang, template_id):
    """API для получения конкретного шаблона GrapesJS"""
    try:
        # Здесь можно загружать шаблоны из базы данных или файлов
        templates = {
            'dental-chart': {
                'id': 'dental-chart',
                'name': 'Зубная формула',
                'description': 'Интерактивная зубная формула',
                'html': '''
                    <div class="dental-chart-block">
                        <h3>Зубная формула пациента</h3>
                        <div class="teeth-container">
                            <div class="teeth-row">
                                <div class="jaw-label">Верхняя челюсть</div>
                                <div class="teeth-grid">
                                    <!-- Зубы будут добавлены динамически -->
                                </div>
                            </div>
                        </div>
                    </div>
                ''',
                'css': '''
                    .dental-chart-block {
                        background: linear-gradient(135deg, #3ECDC1 0%, #2ba89e 100%);
                        color: white;
                        padding: 2rem;
                        border-radius: 12px;
                        margin: 1rem 0;
                    }
                '''
            },
            'case-study': {
                'id': 'case-study',
                'name': 'Клинический случай',
                'description': 'Шаблон для описания клинических случаев',
                'html': '''
                    <div class="case-study-block">
                        <h3>Клинический случай</h3>
                        <div class="row">
                            <div class="col-md-6">
                                <h4>Информация о пациенте</h4>
                                <p><strong>Возраст:</strong> <span contenteditable="true">35 лет</span></p>
                                <p><strong>Жалобы:</strong> <span contenteditable="true">Боль в области верхних моляров</span></p>
                            </div>
                            <div class="col-md-6">
                                <h4>Диагноз и лечение</h4>
                                <p><strong>Диагноз:</strong> <span contenteditable="true">Острый пульпит</span></p>
                                <p><strong>Лечение:</strong> <span contenteditable="true">Эндодонтическое лечение</span></p>
                            </div>
                        </div>
                    </div>
                ''',
                'css': '''
                    .case-study-block {
                        background: linear-gradient(135deg, #6C5CE7 0%, #5a4fcf 100%);
                        color: white;
                        padding: 2rem;
                        border-radius: 12px;
                        margin: 1rem 0;
                    }
                '''
            }
        }
        
        template = templates.get(template_id)
        if not template:
            return jsonify({
                'success': False,
                'error': 'Template not found'
            }), 404
        
        return jsonify({
            'success': True,
            'template': template
        })
        
    except Exception as e:
        logger.error(f"Error getting GrapesJS template {template_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============= GRAPESJS API =============

@content_editor_bp.route('/visual-builder-grapejs')
@login_required
@admin_required
def grapesjs_builder_new(lang):
    """Главная страница GrapesJS редактора"""
    page_id = request.args.get('page_id', type=int)
    lesson_id = request.args.get('lesson_id', type=int)
    module_id = request.args.get('module_id', type=int)
    
    page = None
    if page_id:
        page = GrapesJSPage.query.filter_by(id=page_id, user_id=current_user.id).first()
        if not page:
            flash('Страница не найдена или у вас нет прав доступа', 'error')
            return redirect(url_for('content_editor.dashboard', lang=lang))
    
    lesson = None
    module = None
    if lesson_id:
        lesson = Lesson.query.get_or_404(lesson_id)
    if module_id:
        module = Module.query.get_or_404(module_id)
    
    return flask.render_template('admin/content_editor/grapesjs_builder.html',
                         page=page, lesson=lesson, module=module, lang=lang)


@content_editor_bp.route('/api/grapejs/save', methods=['POST'])
@login_required
@admin_required
def save_grapesjs_page(lang):
    """Сохранение страницы GrapesJS"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Нет данных для сохранения'}), 400
        
        page_id = data.get('page_id')
        
        # Валидация данных
        title = data.get('title', '').strip()
        if not title:
            title = f'Страница {datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M")}'
        
        page_data = {
            'title': title[:255],  # Ограничиваем длину
            'html': data.get('html', ''),
            'css': data.get('css', ''),
            'components': data.get('components', ''),
            'styles': data.get('styles', ''),
            'description': data.get('description', ''),
            'category': data.get('category', 'general'),
            'lesson_id': data.get('lesson_id'),
            'module_id': data.get('module_id'),
        }
        
        if page_id:
            # Обновление существующей страницы
            page = GrapesJSPage.query.filter_by(id=page_id, user_id=current_user.id).first()
            if not page:
                return jsonify({'success': False, 'error': 'Страница не найдена или нет прав доступа'}), 404
            
            # Обновляем поля
            for key, value in page_data.items():
                if hasattr(page, key):
                    setattr(page, key, value)
            
            page.updated_at = datetime.now(timezone.utc)
            
        else:
            # Создание новой страницы
            page_data['user_id'] = current_user.id
            page_data['slug'] = GrapesJSPage.generate_slug(title)
            
            # Проверяем уникальность slug
            existing_slug = GrapesJSPage.query.filter_by(slug=page_data['slug']).first()
            if existing_slug:
                page_data['slug'] = f"{page_data['slug']}-{uuid.uuid4().hex[:8]}"
            
            page = GrapesJSPage(**page_data)
            db.session.add(page)
        
        db.session.commit()
        
        logger.info(f'GrapesJS page saved: {page.id} by user {current_user.id}')
        
        return jsonify({
            'success': True,
            'page_id': page.id,
            'slug': page.slug,
            'message': 'Страница сохранена успешно'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error saving GrapesJS page: {str(e)}')
        return jsonify({'success': False, 'error': 'Ошибка сохранения страницы'}), 500


@content_editor_bp.route('/api/grapejs/load')
@login_required
@admin_required
def load_grapesjs_page(lang):
    """Загрузка страницы GrapesJS"""
    try:
        page_id = request.args.get('page_id', type=int)
        
        if not page_id:
            return jsonify({
                'html': '',
                'css': '',
                'components': '',
                'styles': '',
                'title': ''
            })
        
        page = GrapesJSPage.query.filter_by(id=page_id, user_id=current_user.id).first()
        
        if not page:
            return jsonify({'error': 'Страница не найдена или нет прав доступа'}), 404
        
        return jsonify({
            'html': page.html or '',
            'css': page.css or '',
            'components': page.components or '',
            'styles': page.styles or '',
            'title': page.title,
            'description': page.description,
            'category': page.category,
            'lesson_id': page.lesson_id,
            'module_id': page.module_id,
            'is_published': page.is_published
        })
        
    except Exception as e:
        logger.error(f'Error loading GrapesJS page: {str(e)}')
        return jsonify({'error': 'Ошибка загрузки страницы'}), 500


@content_editor_bp.route('/api/grapejs/upload-asset', methods=['POST'])
@login_required
@admin_required
def upload_grapesjs_asset(lang):
    """Загрузка медиа ресурсов для GrapesJS"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'Файлы не выбраны'}), 400
        
        files = request.files.getlist('files')
        uploaded_files = []
        
        # Создаем папку если не существует
        upload_folder = os.path.join('static', 'uploads', 'grapejs')
        os.makedirs(upload_folder, exist_ok=True)
        
        for file in files:
            if file and file.filename:
                if not allowed_file(file.filename):
                    continue
                
                # Генерируем уникальное имя файла
                original_filename = secure_filename(file.filename)
                file_extension = os.path.splitext(original_filename)[1]
                unique_filename = f"{uuid.uuid4().hex}{file_extension}"
                file_path = os.path.join(upload_folder, unique_filename)
                
                # Сохраняем файл
                file.save(file_path)
                
                # Получаем размеры изображения
                width, height = None, None
                mime_type = mimetypes.guess_type(file_path)[0]
                
                if mime_type and mime_type.startswith('image/'):
                    try:
                        from PIL import Image
                        with Image.open(file_path) as img:
                            width, height = img.size
                            
                            # Оптимизация изображения
                            if width > 1920 or height > 1080:
                                img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
                                img.save(file_path, optimize=True, quality=85)
                                width, height = img.size
                    except Exception as e:
                        logger.warning(f'Error processing image {file_path}: {str(e)}')
                
                # Сохраняем информацию о файле в БД
                asset = GrapesJSAsset(
                    filename=unique_filename,
                    original_name=original_filename,
                    file_path=file_path,
                    file_size=os.path.getsize(file_path),
                    mime_type=mime_type,
                    width=width,
                    height=height,
                    user_id=current_user.id,
                    page_id=request.form.get('page_id', type=int)
                )
                
                db.session.add(asset)
                
                uploaded_files.append({
                    'src': url_for('static', filename=f'uploads/grapejs/{unique_filename}'),
                    'name': original_filename,
                    'size': asset.file_size,
                    'width': width,
                    'height': height
                })
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': uploaded_files
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error uploading GrapesJS assets: {str(e)}')
        return jsonify({'error': 'Ошибка загрузки файлов'}), 500


@content_editor_bp.route('/api/grapejs/templates')
@login_required
@admin_required
def get_grapesjs_templates(lang):
    """Получение списка шаблонов"""
    try:
        # Получаем публичные шаблоны и пользовательские
        templates = GrapesJSTemplate.query.filter(
            or_(
                GrapesJSTemplate.is_public == True,
                GrapesJSTemplate.user_id == current_user.id
            )
        ).order_by(desc(GrapesJSTemplate.is_official), desc(GrapesJSTemplate.created_at)).all()
        
        return jsonify([template.to_dict() for template in templates])
        
    except Exception as e:
        logger.error(f'Error getting GrapesJS templates: {str(e)}')
        return jsonify({'error': 'Ошибка получения шаблонов'}), 500


@content_editor_bp.route('/api/grapejs/templates/<int:template_id>')
@login_required
@admin_required
def get_grapesjs_template(lang, template_id):
    """Получение конкретного шаблона"""
    try:
        template = GrapesJSTemplate.query.filter(
            GrapesJSTemplate.id == template_id,
            or_(
                GrapesJSTemplate.is_public == True,
                GrapesJSTemplate.user_id == current_user.id
            )
        ).first()
        
        if not template:
            return jsonify({'error': 'Шаблон не найден'}), 404
        
        # Увеличиваем счетчик использования
        template.usage_count += 1
        db.session.commit()
        
        return jsonify(template.to_dict())
        
    except Exception as e:
        logger.error(f'Error getting GrapesJS template {template_id}: {str(e)}')
        return jsonify({'error': 'Ошибка получения шаблона'}), 500


@content_editor_bp.route('/api/grapejs/templates', methods=['POST'])
@login_required
@admin_required
def create_grapesjs_template(lang):
    """Создание нового шаблона"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'error': 'Название шаблона обязательно'}), 400
        
        template = GrapesJSTemplate(
            name=data['name'][:255],
            description=data.get('description', ''),
            html=data.get('html', ''),
            css=data.get('css', ''),
            components=data.get('components', ''),
            styles=data.get('styles', ''),
            category=data.get('category', 'general'),
            is_public=data.get('is_public', False),
            user_id=current_user.id
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'template_id': template.id,
            'message': 'Шаблон создан успешно'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error creating GrapesJS template: {str(e)}')
        return jsonify({'error': 'Ошибка создания шаблона'}), 500


@content_editor_bp.route('/api/grapejs/pages')
@login_required
@admin_required
def get_grapesjs_pages(lang):
    """Получение списка страниц пользователя"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        
        query = GrapesJSPage.query.filter_by(user_id=current_user.id)
        
        if search:
            query = query.filter(
                or_(
                    GrapesJSPage.title.ilike(f'%{search}%'),
                    GrapesJSPage.description.ilike(f'%{search}%')
                )
            )
        
        pagination = query.order_by(desc(GrapesJSPage.updated_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'pages': [page.to_dict() for page in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        })
        
    except Exception as e:
        logger.error(f'Error getting GrapesJS pages: {str(e)}')
        return jsonify({'error': 'Ошибка получения страниц'}), 500


@content_editor_bp.route('/api/grapejs/pages/<int:page_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_grapesjs_page(lang, page_id):
    """Удаление страницы"""
    try:
        page = GrapesJSPage.query.filter_by(id=page_id, user_id=current_user.id).first()
        
        if not page:
            return jsonify({'error': 'Страница не найдена'}), 404
        
        # Удаляем связанные ресурсы
        for asset in page.assets:
            try:
                if os.path.exists(asset.file_path):
                    os.remove(asset.file_path)
            except:
                pass
        
        db.session.delete(page)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Страница удалена'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting GrapesJS page {page_id}: {str(e)}')
        return jsonify({'error': 'Ошибка удаления страницы'}), 500


# Утилиты
def allowed_file(filename):
    """Проверка разрешенных расширений файлов"""
    ALLOWED_EXTENSIONS = {
        'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg',
        'mp4', 'webm', 'ogg',
        'mp3', 'wav', 'ogg',
        'pdf', 'doc', 'docx'
    }
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@content_editor_bp.route('/visual-builder')
@login_required
@admin_required
def visual_builder(lang):
    """Перенаправление на GrapesJS редактор"""
    return redirect(url_for('content_editor.grapesjs_builder_new', lang=lang))

@content_editor_bp.route('/api/grapejs/create-default-templates')
@login_required
def create_default_templates():
    """Создание стандартных шаблонов (только для админов)"""
    if not getattr(current_user, 'is_admin', False):  # Измени на свою логику проверки админа
        return jsonify({'error': 'Нет прав доступа'}), 403
    
    templates_data = [
        {
            'name': 'Стоматологический курс',
            'description': 'Шаблон для образовательного курса по стоматологии',
            'category': 'education',
            'html': '''
                <div class="container my-5">
                    <div class="dental-chart-block">
                        <h3>Анатомия зубов</h3>
                        <div class="teeth-container">
                            <div class="teeth-row">
                                <div class="jaw-label">Верхняя челюсть</div>
                                <div class="teeth-grid">
                                    <!-- Автоматически сгенерированные зубы -->
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="quiz-container mt-4">
                        <h3>Проверьте свои знания</h3>
                        <p>Какой зуб отвечает за жевание?</p>
                        <!-- Quiz options here -->
                    </div>
                </div>
            ''',
            'is_public': True,
            'is_official': True
        },
        {
            'name': 'Клинический случай',
            'description': 'Шаблон для разбора клинических случаев',
            'category': 'medical',
            'html': '''
                <div class="container my-5">
                    <div class="case-study-block">
                        <h3>Клинический случай #001</h3>
                        <div class="row">
                            <div class="col-md-6">
                                <h4>Пациент</h4>
                                <p><strong>Возраст:</strong> 35 лет</p>
                                <p><strong>Жалобы:</strong> Боль при жевании</p>
                            </div>
                            <div class="col-md-6">
                                <h4>Диагноз</h4>
                                <p><strong>Предварительный:</strong> Пульпит</p>
                            </div>
                        </div>
                    </div>
                </div>
            ''',
            'is_public': True,
            'is_official': True
        },
        {
            'name': 'Лендинг стоматологии',
            'description': 'Современный лендинг для стоматологической клиники',
            'category': 'landing',
            'html': '''
                <div class="hero-section text-center py-5" style="background: linear-gradient(135deg, #3ECDC1 0%, #2ba89e 100%); color: white;">
                    <div class="container">
                        <h1 class="display-4 fw-bold">Здоровая улыбка</h1>
                        <p class="lead">Современная стоматология для всей семьи</p>
                        <button class="btn btn-light btn-lg">Записаться на прием</button>
                    </div>
                </div>
                <div class="container py-5">
                    <div class="row">
                        <div class="col-md-4 text-center">
                            <i class="bi bi-shield-check" style="font-size: 3rem; color: #3ECDC1;"></i>
                            <h4>Безопасность</h4>
                            <p>Соблюдаем все стандарты стерилизации</p>
                        </div>
                        <div class="col-md-4 text-center">
                            <i class="bi bi-people" style="font-size: 3rem; color: #3ECDC1;"></i>
                            <h4>Опыт</h4>
                            <p>Более 15 лет в стоматологии</p>
                        </div>
                        <div class="col-md-4 text-center">
                            <i class="bi bi-heart" style="font-size: 3rem; color: #3ECDC1;"></i>
                            <h4>Забота</h4>
                            <p>Индивидуальный подход к каждому</p>
                        </div>
                    </div>
                </div>
            ''',
            'is_public': True,
            'is_official': True
        }
    ]
    
    created_count = 0
    for template_data in templates_data:
        existing = GrapesJSTemplate.query.filter_by(name=template_data['name']).first()
        if not existing:
            template = GrapesJSTemplate(**template_data, user_id=current_user.id)
            db.session.add(template)
            created_count += 1
    
    db.session.commit()
    return jsonify({'success': True, 'created': created_count})

@content_editor_bp.route('/grapejs-test')
def grapejs_test(lang):
    """Простая тестовая страница GrapesJS"""
    try:
        return flask.render_template('admin/content_editor/grapesjs_builder.html', 
                                   lang=lang, 
                                   page=None, 
                                   csrf_token='test')
    except Exception as e:
        return f"Error: {str(e)}", 500


# ===== НОВЫЕ API РОУТЫ ДЛЯ РЕДАКТОРА СТРАНИЦ =====
# ===== NEW API ROUTES FOR PAGE EDITOR =====

def create_backup(file_path: str) -> str:
    """
    Создание резервной копии файла
    Create backup of file
    
    Args:
        file_path (str): Путь к файлу / Path to file
        
    Returns:
        str: Путь к резервной копии / Path to backup
    """
    try:
        backup_dir = Path("backup/templates")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = Path(file_path).name
        backup_path = backup_dir / f"{filename}.backup_{timestamp}"
        
        shutil.copy2(file_path, backup_path)
        logger.info(f"Backup created: {backup_path}")
        return str(backup_path)
    except Exception as e:
        logger.error(f"Error creating backup for {file_path}: {e}")
        return None


@content_editor_bp.route('/api/editor/templates')
@login_required
@admin_required
def api_editor_templates(lang):
    """
    GET /api/editor/templates - список всех редактируемых шаблонов
    GET /api/editor/templates - list all editable templates
    """
    try:
        # Получаем все шаблоны из базы данных
        templates = EditablePageTemplate.query.filter_by(language=lang).all()
        
        # Получаем список файлов шаблонов из папки templates
        templates_dir = Path("templates")
        template_files = []
        
        if templates_dir.exists():
            for template_file in templates_dir.rglob("*.html"):
                relative_path = str(template_file.relative_to(templates_dir))
                
                # Проверяем, есть ли уже запись в базе
                db_template = EditablePageTemplate.query.filter_by(
                    template_path=relative_path,
                    language=lang
                ).first()
                
                template_files.append({
                    'path': relative_path,
                    'name': template_file.stem,
                    'size': template_file.stat().st_size,
                    'modified': datetime.fromtimestamp(template_file.stat().st_mtime).isoformat(),
                    'is_live': db_template.is_live if db_template else False,
                    'has_backup': db_template is not None,
                    'template_id': db_template.id if db_template else None
                })
        
        return jsonify({
            'success': True,
            'message': f'Found {len(template_files)} templates',
            'data': {
                'templates': template_files,
                'total': len(template_files)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting editor templates: {e}")
        return jsonify({
            'success': False,
            'message': get_error_message('template_not_found', lang),
            'error': str(e)
        }), 500


@content_editor_bp.route('/api/editor/template/<path:template_path>')
@login_required
@admin_required
def api_editor_template(lang, template_path):
    """
    GET /api/editor/template/<path> - получить конкретный шаблон для редактирования
    GET /api/editor/template/<path> - get specific template for editing
    """
    try:
        # Проверяем безопасность пути
        if '..' in template_path or template_path.startswith('/'):
            return jsonify({
                'success': False,
                'message': get_error_message('invalid_template_path', lang)
            }), 400
        
        full_path = Path("templates") / template_path
        
        if not full_path.exists():
            return jsonify({
                'success': False,
                'message': get_error_message('template_not_found', lang)
            }), 404
        
        # Читаем содержимое файла
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Получаем или создаем запись в базе данных
        db_template = EditablePageTemplate.query.filter_by(
            template_path=template_path,
            language=lang
        ).first()
        
        if not db_template:
            db_template = EditablePageTemplate(
                template_path=template_path,
                original_content=content,
                grapesjs_content='',
                css_overrides='',
                js_modifications='',
                is_live=False,
                language=lang,
                created_by=current_user.id
            )
            db.session.add(db_template)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Template loaded successfully',
            'data': {
                'template': db_template.to_dict(),
                'file_content': content,
                'file_size': len(content),
                'last_modified': datetime.fromtimestamp(full_path.stat().st_mtime).isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting editor template {template_path}: {e}")
        return jsonify({
            'success': False,
            'message': get_error_message('template_not_found', lang),
            'error': str(e)
        }), 500


@content_editor_bp.route('/api/editor/template/parse', methods=['POST'])
@login_required
@admin_required
def api_editor_template_parse(lang):
    """
    POST /api/editor/template/parse - парсинг Jinja2 шаблона в GrapesJS
    POST /api/editor/template/parse - parse Jinja2 template to GrapesJS
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('template_path'):
            return jsonify({
                'success': False,
                'message': get_error_message('invalid_data', lang)
            }), 400
        
        template_path = data['template_path']
        
        # Создаем конвертер
        converter = Jinja2ToGrapesJSConverter()
        
        # Парсим шаблон
        result = converter.parse_template(template_path)
        
        # Сохраняем результат в базу данных
        db_template = EditablePageTemplate.query.filter_by(
            template_path=template_path,
            language=lang
        ).first()
        
        if db_template:
            db_template.grapesjs_content = json.dumps(result['components'])
            db_template.css_overrides = json.dumps(result['css_variables'])
            db_template.updated_at = datetime.now(timezone.utc)
        else:
            db_template = EditablePageTemplate(
                template_path=template_path,
                original_content=result['original_content'],
                grapesjs_content=json.dumps(result['components']),
                css_overrides=json.dumps(result['css_variables']),
                js_modifications='',
                is_live=False,
                language=lang,
                created_by=current_user.id
            )
            db.session.add(db_template)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': get_success_message('template_parsed', lang),
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error parsing template: {e}")
        return jsonify({
            'success': False,
            'message': get_error_message('parse_error', lang),
            'error': str(e)
        }), 500


@content_editor_bp.route('/api/editor/template/save', methods=['POST'])
@login_required
@admin_required
def api_editor_template_save(lang):
    """
    POST /api/editor/template/save - сохранить отредактированный шаблон
    POST /api/editor/template/save - save edited template
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('template_path'):
            return jsonify({
                'success': False,
                'message': get_error_message('invalid_data', lang)
            }), 400
        
        template_path = data['template_path']
        grapesjs_content = data.get('grapesjs_content', '')
        css_overrides = data.get('css_overrides', '')
        js_modifications = data.get('js_modifications', '')
        
        # Создаем резервную копию
        full_path = Path("templates") / template_path
        backup_path = None
        
        if full_path.exists():
            backup_path = create_backup(str(full_path))
        
        # Обновляем запись в базе данных
        db_template = EditablePageTemplate.query.filter_by(
            template_path=template_path,
            language=lang
        ).first()
        
        if db_template:
            db_template.grapesjs_content = grapesjs_content
            db_template.css_overrides = css_overrides
            db_template.js_modifications = js_modifications
            db_template.updated_at = datetime.now(timezone.utc)
        else:
            db_template = EditablePageTemplate(
                template_path=template_path,
                original_content='',
                grapesjs_content=grapesjs_content,
                css_overrides=css_overrides,
                js_modifications=js_modifications,
                is_live=False,
                language=lang,
                created_by=current_user.id
            )
            db.session.add(db_template)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': get_success_message('template_saved', lang),
            'data': {
                'template_id': db_template.id,
                'backup_path': backup_path,
                'updated_at': db_template.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error saving template: {e}")
        return jsonify({
            'success': False,
            'message': get_error_message('save_error', lang),
            'error': str(e)
        }), 500


@content_editor_bp.route('/api/editor/template/preview', methods=['POST'])
@login_required
@admin_required
def api_editor_template_preview(lang):
    """
    POST /api/editor/template/preview - создать превью-версию шаблона
    POST /api/editor/template/preview - create preview version
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('template_path'):
            return jsonify({
                'success': False,
                'message': get_error_message('invalid_data', lang)
            }), 400
        
        template_path = data['template_path']
        preview_content = data.get('preview_content', '')
        
        # Создаем временный файл для превью
        preview_dir = Path("static/preview")
        preview_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        preview_filename = f"preview_{Path(template_path).stem}_{timestamp}.html"
        preview_path = preview_dir / preview_filename
        
        # Создаем HTML с базовой структурой
        preview_html = f"""
<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preview - {Path(template_path).stem}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <style>
        {preview_content}
    </style>
</head>
<body>
    <div class="container-fluid">
        {preview_content}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        """
        
        with open(preview_path, 'w', encoding='utf-8') as f:
            f.write(preview_html)
        
        return jsonify({
            'success': True,
            'message': get_success_message('template_preview_created', lang),
            'data': {
                'preview_url': f'/static/preview/{preview_filename}',
                'preview_path': str(preview_path)
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating preview: {e}")
        return jsonify({
            'success': False,
            'message': get_error_message('save_error', lang),
            'error': str(e)
        }), 500


@content_editor_bp.route('/api/editor/template/deploy', methods=['POST'])
@login_required
@admin_required
def api_editor_template_deploy(lang):
    """
    POST /api/editor/template/deploy - опубликовать шаблон в продакшн
    POST /api/editor/template/deploy - deploy template to production
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('template_path'):
            return jsonify({
                'success': False,
                'message': get_error_message('invalid_data', lang)
            }), 400
        
        template_path = data['template_path']
        deploy_content = data.get('deploy_content', '')
        
        # Создаем резервную копию
        full_path = Path("templates") / template_path
        backup_path = None
        
        if full_path.exists():
            backup_path = create_backup(str(full_path))
        
        # Записываем новый контент в файл
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(deploy_content)
        
        # Обновляем статус в базе данных
        db_template = EditablePageTemplate.query.filter_by(
            template_path=template_path,
            language=lang
        ).first()
        
        if db_template:
            db_template.is_live = True
            db_template.updated_at = datetime.now(timezone.utc)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': get_success_message('template_deployed', lang),
            'data': {
                'template_path': template_path,
                'backup_path': backup_path,
                'deployed_at': datetime.now(timezone.utc).isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error deploying template: {e}")
        return jsonify({
            'success': False,
            'message': get_error_message('deploy_error', lang),
            'error': str(e)
        }), 500


@content_editor_bp.route('/api/editor/css-variables')
@login_required
@admin_required
def api_editor_css_variables(lang):
    """
    GET /api/editor/css-variables - получить CSS переменные проекта
    GET /api/editor/css-variables - get project CSS variables
    """
    try:
        # Создаем конвертер для получения CSS переменных
        converter = Jinja2ToGrapesJSConverter()
        
        # Получаем все CSS файлы проекта
        css_files = []
        static_css_dir = Path("static/css")
        
        if static_css_dir.exists():
            for css_file in static_css_dir.rglob("*.css"):
                relative_path = str(css_file.relative_to(Path("static")))
                
                try:
                    with open(css_file, 'r', encoding='utf-8') as f:
                        css_content = f.read()
                    
                    # Извлекаем CSS переменные
                    css_vars = converter.extract_css_variables(css_content)
                    
                    css_files.append({
                        'path': relative_path,
                        'name': css_file.stem,
                        'variables': css_vars,
                        'variables_count': len(css_vars)
                    })
                except Exception as e:
                    logger.warning(f"Error reading CSS file {css_file}: {e}")
        
        return jsonify({
            'success': True,
            'message': f'Found {len(css_files)} CSS files',
            'data': {
                'css_files': css_files,
                'total_files': len(css_files),
                'total_variables': sum(len(f['variables']) for f in css_files)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting CSS variables: {e}")
        return jsonify({
            'success': False,
            'message': get_error_message('css_variables_error', lang),
            'error': str(e)
        }), 500


@content_editor_bp.route('/api/editor/css-variables', methods=['POST'])
@login_required
@admin_required
def api_editor_update_css_variables(lang):
    """
    POST /api/editor/css-variables - обновить CSS переменные
    POST /api/editor/css-variables - update CSS variables
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('css_file') or not data.get('variables'):
            return jsonify({
                'success': False,
                'message': get_error_message('invalid_data', lang)
            }), 400
        
        css_file_path = data['css_file']
        variables = data['variables']
        
        # Проверяем безопасность пути
        if '..' in css_file_path or css_file_path.startswith('/'):
            return jsonify({
                'success': False,
                'message': get_error_message('invalid_template_path', lang)
            }), 400
        
        full_path = Path("static") / css_file_path
        
        if not full_path.exists():
            return jsonify({
                'success': False,
                'message': 'CSS file not found'
            }), 404
        
        # Создаем резервную копию
        backup_path = create_backup(str(full_path))
        
        # Читаем текущий CSS файл
        with open(full_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Обновляем переменные
        for var_name, var_value in variables.items():
            # Ищем существующую переменную
            pattern = rf'({re.escape(var_name)}:\s*)([^;]+);'
            replacement = rf'\1{var_value};'
            
            if re.search(pattern, css_content):
                css_content = re.sub(pattern, replacement, css_content)
            else:
                # Добавляем новую переменную в :root
                root_pattern = r'(:root\s*\{)'
                if re.search(root_pattern, css_content):
                    css_content = re.sub(root_pattern, rf'\1\n  {var_name}: {var_value};', css_content)
                else:
                    # Добавляем :root блок в начало файла
                    css_content = f':root {{\n  {var_name}: {var_value};\n}}\n\n{css_content}'
        
        # Записываем обновленный CSS файл
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        return jsonify({
            'success': True,
            'message': get_success_message('css_variables_updated', lang),
            'data': {
                'css_file': css_file_path,
                'backup_path': backup_path,
                'updated_variables': len(variables),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error updating CSS variables: {e}")
        return jsonify({
            'success': False,
            'message': get_error_message('css_variables_error', lang),
            'error': str(e)
        }), 500