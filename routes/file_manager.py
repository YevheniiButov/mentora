"""
File Manager API для Visual Builder
Управление HTML файлами проекта
"""

from flask import Blueprint, request, jsonify, current_app
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import mimetypes

# Создаем Blueprint
file_manager = Blueprint('file_manager', __name__)

# Настройки
ALLOWED_EXTENSIONS = {'html', 'htm', 'css', 'js', 'json', 'txt', 'md'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    """Проверка разрешенных расширений файлов"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_project_files():
    """Получение списка файлов проекта"""
    project_path = os.path.join(current_app.root_path, 'static', 'js', 'visual-builder')
    files = []
    
    if os.path.exists(project_path):
        for root, dirs, filenames in os.walk(project_path):
            for filename in filenames:
                if allowed_file(filename):
                    filepath = os.path.join(root, filename)
                    rel_path = os.path.relpath(filepath, project_path)
                    
                    try:
                        stat = os.stat(filepath)
                        files.append({
                            'name': filename,
                            'path': rel_path,
                            'full_path': filepath,
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'type': mimetypes.guess_type(filename)[0] or 'text/plain'
                        })
                    except OSError:
                        continue
    
    return files

@file_manager.route('/api/files/list')
def list_project_files():
    """API: Список HTML файлов в проекте"""
    try:
        files = get_project_files()
        
        # Фильтруем по типу запроса
        file_type = request.args.get('type', 'all')
        if file_type != 'all':
            files = [f for f in files if f['type'] == file_type]
        
        # Сортировка
        sort_by = request.args.get('sort', 'name')
        reverse = request.args.get('order', 'asc') == 'desc'
        
        if sort_by == 'name':
            files.sort(key=lambda x: x['name'].lower(), reverse=reverse)
        elif sort_by == 'size':
            files.sort(key=lambda x: x['size'], reverse=reverse)
        elif sort_by == 'modified':
            files.sort(key=lambda x: x['modified'], reverse=reverse)
        
        return jsonify({
            'success': True,
            'files': files,
            'total': len(files),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f'Ошибка получения списка файлов: {e}')
        return jsonify({
            'success': False,
            'error': 'Ошибка получения списка файлов',
            'details': str(e)
        }), 500

@file_manager.route('/api/files/load/<path:filepath>')
def load_file_content(filepath):
    """API: Загрузка содержимого файла"""
    try:
        # Безопасность: проверяем путь
        if '..' in filepath or filepath.startswith('/'):
            return jsonify({
                'success': False,
                'error': 'Недопустимый путь к файлу'
            }), 400
        
        # Получаем полный путь к файлу
        project_path = os.path.join(current_app.root_path, 'static', 'js', 'visual-builder')
        full_path = os.path.join(project_path, filepath)
        
        # Проверяем существование файла
        if not os.path.exists(full_path):
            return jsonify({
                'success': False,
                'error': 'Файл не найден'
            }), 404
        
        # Проверяем размер файла
        file_size = os.path.getsize(full_path)
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'success': False,
                'error': 'Файл слишком большой'
            }), 413
        
        # Читаем содержимое файла
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Получаем информацию о файле
        stat = os.stat(full_path)
        
        return jsonify({
            'success': True,
            'content': content,
            'file_info': {
                'name': os.path.basename(filepath),
                'path': filepath,
                'size': file_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'type': mimetypes.guess_type(filepath)[0] or 'text/plain'
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except UnicodeDecodeError:
        return jsonify({
            'success': False,
            'error': 'Ошибка кодировки файла'
        }), 400
    except Exception as e:
        current_app.logger.error(f'Ошибка загрузки файла {filepath}: {e}')
        return jsonify({
            'success': False,
            'error': 'Ошибка загрузки файла',
            'details': str(e)
        }), 500

@file_manager.route('/api/files/save', methods=['POST'])
def save_file_content():
    """API: Сохранение изменений в файл"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Отсутствуют данные'
            }), 400
        
        filepath = data.get('filepath')
        content = data.get('content')
        backup = data.get('backup', True)
        
        if not filepath or content is None:
            return jsonify({
                'success': False,
                'error': 'Отсутствуют обязательные поля'
            }), 400
        
        # Безопасность: проверяем путь
        if '..' in filepath or filepath.startswith('/'):
            return jsonify({
                'success': False,
                'error': 'Недопустимый путь к файлу'
            }), 400
        
        # Получаем полный путь к файлу
        project_path = os.path.join(current_app.root_path, 'static', 'js', 'visual-builder')
        full_path = os.path.join(project_path, filepath)
        
        # Проверяем директорию
        dir_path = os.path.dirname(full_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        
        # Создаем резервную копию
        if backup and os.path.exists(full_path):
            backup_path = f"{full_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                with open(full_path, 'r', encoding='utf-8') as src:
                    with open(backup_path, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
            except Exception as e:
                current_app.logger.warning(f'Ошибка создания резервной копии: {e}')
        
        # Сохраняем файл
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Получаем информацию о файле
        stat = os.stat(full_path)
        
        return jsonify({
            'success': True,
            'message': 'Файл успешно сохранен',
            'file_info': {
                'name': os.path.basename(filepath),
                'path': filepath,
                'size': len(content),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f'Ошибка сохранения файла: {e}')
        return jsonify({
            'success': False,
            'error': 'Ошибка сохранения файла',
            'details': str(e)
        }), 500

@file_manager.route('/api/files/create', methods=['POST'])
def create_file():
    """API: Создание нового файла"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Отсутствуют данные'
            }), 400
        
        filename = data.get('filename')
        content = data.get('content', '')
        directory = data.get('directory', '')
        
        if not filename:
            return jsonify({
                'success': False,
                'error': 'Отсутствует имя файла'
            }), 400
        
        # Безопасность: проверяем имя файла
        filename = secure_filename(filename)
        if not allowed_file(filename):
            return jsonify({
                'success': False,
                'error': 'Недопустимый тип файла'
            }), 400
        
        # Получаем полный путь к файлу
        project_path = os.path.join(current_app.root_path, 'static', 'js', 'visual-builder')
        if directory:
            full_path = os.path.join(project_path, directory, filename)
        else:
            full_path = os.path.join(project_path, filename)
        
        # Проверяем директорию
        dir_path = os.path.dirname(full_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        
        # Проверяем существование файла
        if os.path.exists(full_path):
            return jsonify({
                'success': False,
                'error': 'Файл уже существует'
            }), 409
        
        # Создаем файл
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Получаем относительный путь
        rel_path = os.path.relpath(full_path, project_path)
        
        # Получаем информацию о файле
        stat = os.stat(full_path)
        
        return jsonify({
            'success': True,
            'message': 'Файл успешно создан',
            'file_info': {
                'name': filename,
                'path': rel_path,
                'size': len(content),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'type': mimetypes.guess_type(filename)[0] or 'text/plain'
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f'Ошибка создания файла: {e}')
        return jsonify({
            'success': False,
            'error': 'Ошибка создания файла',
            'details': str(e)
        }), 500

@file_manager.route('/api/files/delete/<path:filepath>', methods=['DELETE'])
def delete_file(filepath):
    """API: Удаление файла"""
    try:
        # Безопасность: проверяем путь
        if '..' in filepath or filepath.startswith('/'):
            return jsonify({
                'success': False,
                'error': 'Недопустимый путь к файлу'
            }), 400
        
        # Получаем полный путь к файлу
        project_path = os.path.join(current_app.root_path, 'static', 'js', 'visual-builder')
        full_path = os.path.join(project_path, filepath)
        
        # Проверяем существование файла
        if not os.path.exists(full_path):
            return jsonify({
                'success': False,
                'error': 'Файл не найден'
            }), 404
        
        # Создаем резервную копию перед удалением
        backup_path = f"{full_path}.deleted.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            with open(full_path, 'r', encoding='utf-8') as src:
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
        except Exception as e:
            current_app.logger.warning(f'Ошибка создания резервной копии: {e}')
        
        # Удаляем файл
        os.remove(full_path)
        
        return jsonify({
            'success': True,
            'message': 'Файл успешно удален',
            'filepath': filepath,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f'Ошибка удаления файла {filepath}: {e}')
        return jsonify({
            'success': False,
            'error': 'Ошибка удаления файла',
            'details': str(e)
        }), 500

@file_manager.route('/api/files/rename', methods=['POST'])
def rename_file():
    """API: Переименование файла"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Отсутствуют данные'
            }), 400
        
        old_path = data.get('old_path')
        new_name = data.get('new_name')
        
        if not old_path or not new_name:
            return jsonify({
                'success': False,
                'error': 'Отсутствуют обязательные поля'
            }), 400
        
        # Безопасность: проверяем пути
        if '..' in old_path or old_path.startswith('/') or '..' in new_name:
            return jsonify({
                'success': False,
                'error': 'Недопустимый путь к файлу'
            }), 400
        
        # Безопасность: проверяем имя файла
        new_name = secure_filename(new_name)
        if not allowed_file(new_name):
            return jsonify({
                'success': False,
                'error': 'Недопустимый тип файла'
            }), 400
        
        # Получаем полные пути к файлам
        project_path = os.path.join(current_app.root_path, 'static', 'js', 'visual-builder')
        old_full_path = os.path.join(project_path, old_path)
        new_full_path = os.path.join(project_path, os.path.dirname(old_path), new_name)
        
        # Проверяем существование старого файла
        if not os.path.exists(old_full_path):
            return jsonify({
                'success': False,
                'error': 'Файл не найден'
            }), 404
        
        # Проверяем существование нового файла
        if os.path.exists(new_full_path):
            return jsonify({
                'success': False,
                'error': 'Файл с таким именем уже существует'
            }), 409
        
        # Переименовываем файл
        os.rename(old_full_path, new_full_path)
        
        # Получаем новый относительный путь
        new_rel_path = os.path.relpath(new_full_path, project_path)
        
        return jsonify({
            'success': True,
            'message': 'Файл успешно переименован',
            'old_path': old_path,
            'new_path': new_rel_path,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f'Ошибка переименования файла: {e}')
        return jsonify({
            'success': False,
            'error': 'Ошибка переименования файла',
            'details': str(e)
        }), 500

@file_manager.route('/api/files/search')
def search_files():
    """API: Поиск файлов"""
    try:
        query = request.args.get('q', '').lower()
        file_type = request.args.get('type', 'all')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Отсутствует поисковый запрос'
            }), 400
        
        files = get_project_files()
        
        # Фильтруем по типу
        if file_type != 'all':
            files = [f for f in files if f['type'] == file_type]
        
        # Поиск по имени и содержимому
        results = []
        project_path = os.path.join(current_app.root_path, 'static', 'js', 'visual-builder')
        
        for file_info in files:
            # Поиск по имени файла
            if query in file_info['name'].lower():
                results.append({
                    **file_info,
                    'match_type': 'filename',
                    'match_score': 1.0
                })
                continue
            
            # Поиск по содержимому файла
            try:
                with open(file_info['full_path'], 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if query in content:
                        # Вычисляем релевантность
                        occurrences = content.count(query)
                        score = min(occurrences / 10, 0.9)  # Максимум 0.9 для содержимого
                        
                        results.append({
                            **file_info,
                            'match_type': 'content',
                            'match_score': score
                        })
            except Exception:
                continue
        
        # Сортируем по релевантности
        results.sort(key=lambda x: x['match_score'], reverse=True)
        
        return jsonify({
            'success': True,
            'results': results,
            'total': len(results),
            'query': query,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f'Ошибка поиска файлов: {e}')
        return jsonify({
            'success': False,
            'error': 'Ошибка поиска файлов',
            'details': str(e)
        }), 500

@file_manager.route('/api/files/stats')
def get_file_stats():
    """API: Статистика файлов"""
    try:
        files = get_project_files()
        
        # Общая статистика
        total_files = len(files)
        total_size = sum(f['size'] for f in files)
        
        # Статистика по типам
        type_stats = {}
        for file_info in files:
            file_type = file_info['type']
            if file_type not in type_stats:
                type_stats[file_type] = {'count': 0, 'size': 0}
            type_stats[file_type]['count'] += 1
            type_stats[file_type]['size'] += file_info['size']
        
        # Статистика по директориям
        dir_stats = {}
        for file_info in files:
            dir_path = os.path.dirname(file_info['path'])
            if dir_path not in dir_stats:
                dir_stats[dir_path] = {'count': 0, 'size': 0}
            dir_stats[dir_path]['count'] += 1
            dir_stats[dir_path]['size'] += file_info['size']
        
        return jsonify({
            'success': True,
            'stats': {
                'total_files': total_files,
                'total_size': total_size,
                'type_stats': type_stats,
                'dir_stats': dir_stats
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f'Ошибка получения статистики файлов: {e}')
        return jsonify({
            'success': False,
            'error': 'Ошибка получения статистики',
            'details': str(e)
        }), 500

# Регистрация Blueprint
def init_file_manager(app):
    """Инициализация File Manager"""
    app.register_blueprint(file_manager)
    current_app.logger.info('📁 File Manager API зарегистрирован') 