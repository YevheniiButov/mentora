"""
File Upload Utilities
Утилиты для загрузки файлов
"""

import os
from werkzeug.utils import secure_filename

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif', 'webp'
}

# Максимальный размер файла (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

def allowed_file(filename):
    """Проверяет, разрешено ли расширение файла"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file):
    """Проверяет размер файла"""
    # Сбрасываем указатель файла в начало
    file.seek(0, 2)  # Переходим в конец файла
    file_size = file.tell()  # Получаем размер
    file.seek(0)  # Возвращаемся в начало
    
    return file_size <= MAX_FILE_SIZE

def get_file_extension(filename):
    """Получает расширение файла"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

def generate_secure_filename(original_filename, prefix=''):
    """Генерирует безопасное имя файла"""
    if prefix:
        return f"{prefix}_{secure_filename(original_filename)}"
    return secure_filename(original_filename)

def ensure_upload_directory(upload_folder):
    """Создает директорию для загрузки, если она не существует"""
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        return True
    return False

def delete_file(filepath):
    """Удаляет файл с диска"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception:
        pass
    return False

def get_file_info(filepath):
    """Получает информацию о файле"""
    if not os.path.exists(filepath):
        return None
    
    stat = os.stat(filepath)
    return {
        'size': stat.st_size,
        'modified': stat.st_mtime,
        'exists': True
    }











