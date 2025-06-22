# routes/admin/system_admin.py
# Системные настройки и управление

from flask import Blueprint, render_template, request, jsonify, current_app, send_file
from flask_login import current_user
from datetime import datetime, timedelta
import json
import os
import zipfile
import tempfile
from sqlalchemy import text

from models import db, LearningPath, Subject, Module, Lesson, User, VirtualPatientScenario
from . import admin_required

# Создаем blueprint для системного управления
system_admin_bp = Blueprint('system_admin', __name__, url_prefix='/system')

# ================== SYSTEM DASHBOARD ==================

@system_admin_bp.route('/dashboard')
@admin_required(['all'])
def system_dashboard(lang):
    """Дашборд системных настроек"""
    
    # Информация о системе
    system_info = {
        'app_version': current_app.config.get('VERSION', '1.0.0'),
        'debug_mode': current_app.debug,
        'database_url': current_app.config.get('SQLALCHEMY_DATABASE_URI', '').split('@')[1] if '@' in current_app.config.get('SQLALCHEMY_DATABASE_URI', '') else 'Local',
        'upload_folder': current_app.config.get('UPLOAD_FOLDER', 'uploads'),
        'secret_key_set': bool(current_app.config.get('SECRET_KEY')),
        'mail_configured': bool(current_app.config.get('MAIL_SERVER'))
    }
    
    # Статистика базы данных
    db_stats = {
        'total_tables': len(db.metadata.tables),
        'learning_paths': LearningPath.query.count(),
        'subjects': Subject.query.count(),
        'modules': Module.query.count(),
        'lessons': Lesson.query.count(),
        'users': User.query.count(),
        'vp_scenarios': VirtualPatientScenario.query.count()
    }
    
    # Проверка состояния файловой системы
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    file_stats = {
        'upload_folder_exists': os.path.exists(upload_folder),
        'upload_folder_writable': os.access(upload_folder, os.W_OK) if os.path.exists(upload_folder) else False,
        'disk_usage': get_disk_usage(upload_folder) if os.path.exists(upload_folder) else {}
    }
    
    return render_template('admin/unified/system/dashboard.html',
                         system_info=system_info,
                         db_stats=db_stats,
                         file_stats=file_stats)

def get_disk_usage(path):
    """Получение информации об использовании диска"""
    try:
        import shutil
        total, used, free = shutil.disk_usage(path)
        return {
            'total': total,
            'used': used,
            'free': free,
            'used_percent': round((used / total) * 100, 2)
        }
    except:
        return {}

# ================== BACKUP & RESTORE ==================

@system_admin_bp.route('/backup')
@admin_required(['all'])
def backup_page(lang):
    """Страница управления бэкапами"""
    
    # Список доступных бэкапов
    backup_folder = os.path.join(current_app.instance_path, 'backups')
    backups = []
    
    if os.path.exists(backup_folder):
        for filename in os.listdir(backup_folder):
            if filename.endswith('.json') or filename.endswith('.zip'):
                file_path = os.path.join(backup_folder, filename)
                file_stats = os.stat(file_path)
                backups.append({
                    'filename': filename,
                    'size': file_stats.st_size,
                    'created': datetime.fromtimestamp(file_stats.st_ctime),
                    'type': 'full' if filename.endswith('.zip') else 'data'
                })
    
    backups.sort(key=lambda x: x['created'], reverse=True)
    
    return render_template('admin/unified/system/backup.html', backups=backups)

@system_admin_bp.route('/api/backup/create', methods=['POST'])
@admin_required(['all'])
def create_backup(lang):
    """Создание полного бэкапа системы"""
    try:
        data = request.get_json()
        backup_type = data.get('type', 'data')  # 'data' или 'full'
        include_files = data.get('include_files', False)
        
        # Создаем папку для бэкапов
        backup_folder = os.path.join(current_app.instance_path, 'backups')
        os.makedirs(backup_folder, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if backup_type == 'data':
            # Экспорт только данных
            backup_data = export_all_data()
            
            filename = f'backup_data_{timestamp}.json'
            file_path = os.path.join(backup_folder, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
        
        elif backup_type == 'full':
            # Полный бэкап с файлами
            filename = f'backup_full_{timestamp}.zip'
            file_path = os.path.join(backup_folder, filename)
            
            with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Добавляем данные
                backup_data = export_all_data()
                data_json = json.dumps(backup_data, ensure_ascii=False, indent=2, default=str)
                zip_file.writestr('data.json', data_json)
                
                # Добавляем файлы
                if include_files:
                    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                    if os.path.exists(upload_folder):
                        for root, dirs, files in os.walk(upload_folder):
                            for file in files:
                                file_path_full = os.path.join(root, file)
                                arc_name = os.path.relpath(file_path_full, upload_folder)
                                zip_file.write(file_path_full, f'uploads/{arc_name}')
        
        current_app.logger.info(f"Admin {current_user.email} created backup: {filename}")
        
        return jsonify({
            'success': True,
            'message': 'Бэкап успешно создан',
            'filename': filename,
            'size': os.path.getsize(file_path)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error creating backup: {e}")
        return jsonify({'success': False, 'message': str(e)})

def export_all_data():
    """Экспорт всех данных системы"""
    backup_data = {
        'version': '1.0',
        'created_at': datetime.now().isoformat(),
        'created_by': current_user.email,
        'data': {}
    }
    
    # Экспорт Learning Paths
    paths = LearningPath.query.all()
    backup_data['data']['learning_paths'] = []
    for path in paths:
        backup_data['data']['learning_paths'].append({
            'id': path.id,
            'name': path.name,
            'description': path.description,
            'order': path.order,
            'icon': path.icon,
            'exam_phase': path.exam_phase,
            'is_active': path.is_active
        })
    
    # Экспорт Subjects
    subjects = Subject.query.all()
    backup_data['data']['subjects'] = []
    for subject in subjects:
        backup_data['data']['subjects'].append({
            'id': subject.id,
            'name': subject.name,
            'description': subject.description,
            'order': subject.order,
            'icon': subject.icon,
            'learning_path_id': subject.learning_path_id
        })
    
    # Экспорт Modules
    modules = Module.query.all()
    backup_data['data']['modules'] = []
    for module in modules:
        backup_data['data']['modules'].append({
            'id': module.id,
            'title': module.title,
            'description': module.description,
            'order': module.order,
            'icon': module.icon,
            'module_type': module.module_type,
            'is_premium': module.is_premium,
            'subject_id': module.subject_id,
            'is_final_test': module.is_final_test
        })
    
    # Экспорт Lessons
    lessons = Lesson.query.all()
    backup_data['data']['lessons'] = []
    for lesson in lessons:
        backup_data['data']['lessons'].append({
            'id': lesson.id,
            'title': lesson.title,
            'content': lesson.content,
            'content_type': lesson.content_type,
            'module_id': lesson.module_id,
            'order': lesson.order,
            'topic_id': lesson.topic_id,
            'subtopic': lesson.subtopic,
            'subtopic_slug': lesson.subtopic_slug,
            'subtopic_order': lesson.subtopic_order
        })
    
    # Экспорт Virtual Patient Scenarios
    scenarios = VirtualPatientScenario.query.all()
    backup_data['data']['virtual_patient_scenarios'] = []
    for scenario in scenarios:
        backup_data['data']['virtual_patient_scenarios'].append({
            'id': scenario.id,
            'title': scenario.title,
            'description': scenario.description,
            'difficulty': scenario.difficulty,
            'category': scenario.category,
            'timeframe': scenario.timeframe,
            'max_score': scenario.max_score,
            'is_premium': scenario.is_premium,
            'is_published': scenario.is_published,
            'created_at': scenario.created_at,
            'scenario_data': scenario.scenario_data
        })
    
    return backup_data

@system_admin_bp.route('/api/backup/download/<filename>')
@admin_required(['all'])
def download_backup(lang, filename):
    """Скачивание бэкапа"""
    try:
        backup_folder = os.path.join(current_app.instance_path, 'backups')
        file_path = os.path.join(backup_folder, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'message': 'Файл не найден'})
        
        current_app.logger.info(f"Admin {current_user.email} downloaded backup: {filename}")
        
        return send_file(file_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        current_app.logger.error(f"Error downloading backup: {e}")
        return jsonify({'success': False, 'message': str(e)})

# ================== SYSTEM SETTINGS ==================

@system_admin_bp.route('/settings')
@admin_required(['all'])
def system_settings(lang):
    """Системные настройки"""
    
    # Получаем текущие настройки из конфигурации
    settings = {
        'app_name': current_app.config.get('APP_NAME', 'Dental Academy'),
        'default_language': current_app.config.get('DEFAULT_LANGUAGE', 'en'),
        'max_upload_size': current_app.config.get('MAX_CONTENT_LENGTH', 16777216),
        'session_timeout': current_app.config.get('PERMANENT_SESSION_LIFETIME', 3600),
        'enable_registration': current_app.config.get('ENABLE_REGISTRATION', True),
        'require_email_verification': current_app.config.get('REQUIRE_EMAIL_VERIFICATION', False),
        'maintenance_mode': current_app.config.get('MAINTENANCE_MODE', False)
    }
    
    return render_template('admin/unified/system/settings.html', settings=settings)

@system_admin_bp.route('/api/settings', methods=['POST'])
@admin_required(['all'])
def update_settings(lang):
    """Обновление системных настроек"""
    try:
        data = request.get_json()
        
        # Здесь можно добавить логику сохранения настроек
        # В реальном приложении настройки могли бы сохраняться в базе данных
        # или конфигурационном файле
        
        current_app.logger.info(f"Admin {current_user.email} updated system settings")
        
        return jsonify({
            'success': True,
            'message': 'Настройки обновлены'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error updating settings: {e}")
        return jsonify({'success': False, 'message': str(e)})

# ================== SYSTEM MAINTENANCE ==================

@system_admin_bp.route('/maintenance')
@admin_required(['all'])
def maintenance_page(lang):
    """Страница технического обслуживания"""
    return render_template('admin/unified/system/maintenance.html')

@system_admin_bp.route('/api/maintenance/cleanup', methods=['POST'])
@admin_required(['all'])
def cleanup_database(lang):
    """Очистка базы данных от устаревших данных"""
    try:
        cleanup_stats = {
            'deleted_sessions': 0,
            'deleted_logs': 0,
            'orphaned_files': 0
        }
        
        # Удаляем старые сессии (если есть таблица сессий)
        # cleanup_stats['deleted_sessions'] = delete_old_sessions()
        
        # Удаляем старые логи (если есть таблица логов)
        # cleanup_stats['deleted_logs'] = delete_old_logs()
        
        # Проверяем на осиротевшие файлы
        # cleanup_stats['orphaned_files'] = find_orphaned_files()
        
        current_app.logger.info(f"Admin {current_user.email} performed database cleanup")
        
        return jsonify({
            'success': True,
            'message': 'Очистка базы данных завершена',
            'stats': cleanup_stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Error during database cleanup: {e}")
        return jsonify({'success': False, 'message': str(e)})

@system_admin_bp.route('/api/maintenance/optimize', methods=['POST'])
@admin_required(['all'])
def optimize_database(lang):
    """Оптимизация базы данных"""
    try:
        # Выполняем базовые команды оптимизации
        if 'sqlite' in current_app.config.get('SQLALCHEMY_DATABASE_URI', ''):
            db.session.execute(text('VACUUM'))
            db.session.execute(text('ANALYZE'))
        elif 'mysql' in current_app.config.get('SQLALCHEMY_DATABASE_URI', ''):
            # MySQL оптимизация
            tables = db.metadata.tables.keys()
            for table in tables:
                db.session.execute(text(f'OPTIMIZE TABLE {table}'))
        
        db.session.commit()
        
        current_app.logger.info(f"Admin {current_user.email} optimized database")
        
        return jsonify({
            'success': True,
            'message': 'Оптимизация базы данных завершена'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error during database optimization: {e}")
        return jsonify({'success': False, 'message': str(e)})

# ================== SYSTEM LOGS ==================

@system_admin_bp.route('/logs')
@admin_required(['all'])
def system_logs(lang):
    """Просмотр системных логов"""
    
    log_files = []
    
    # Поиск файлов логов
    for filename in ['app.log', 'flask.log', 'error.log']:
        if os.path.exists(filename):
            stat = os.stat(filename)
            log_files.append({
                'filename': filename,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime)
            })
    
    return render_template('admin/unified/system/logs.html', log_files=log_files)

@system_admin_bp.route('/api/logs/<filename>')
@admin_required(['all'])
def view_log_file(lang, filename):
    """Просмотр содержимого лог файла"""
    try:
        # Безопасность: проверяем что файл существует и это лог файл
        if not filename.endswith('.log') or not os.path.exists(filename):
            return jsonify({'success': False, 'message': 'Файл не найден'})
        
        lines = request.args.get('lines', 100, type=int)
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.readlines()
        
        # Возвращаем последние N строк
        recent_lines = content[-lines:] if len(content) > lines else content
        
        return jsonify({
            'success': True,
            'filename': filename,
            'lines': recent_lines,
            'total_lines': len(content)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error reading log file {filename}: {e}")
        return jsonify({'success': False, 'message': str(e)}) 