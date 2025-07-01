# routes/import_export_routes.py
"""
API маршруты для импорта/экспорта проектов в Advanced Dental Editor
Поддерживает ZIP, GitHub, URL импорт и Webpack сборку
"""

import os
import json
import zipfile
import tempfile
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import logging

logger = logging.getLogger(__name__)

# Создаем blueprint
import_export_bp = Blueprint(
    "import_export_bp",
    __name__,
    url_prefix='/<string:lang>/api/import-export',
    template_folder='../templates'
)

# Поддерживаемые форматы
SUPPORTED_FORMATS = {
    'zip': ['.zip'],
    'github': ['github.com'],
    'url': ['.html', '.htm', '.js', '.css'],
    'file': ['.html', '.htm', '.js', '.css', '.jsx', '.tsx', '.vue']
}

# Максимальный размер файла (50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024


@import_export_bp.route('/upload-zip', methods=['POST'])
@login_required
def upload_zip(lang):
    """Загрузка и анализ ZIP архива"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Проверяем расширение
        if not file.filename.lower().endswith('.zip'):
            return jsonify({'error': 'Only ZIP files are supported'}), 400
        
        # Проверяем размер
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'error': f'File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB'
            }), 400
        
        # Сохраняем файл временно
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)
        
        # Анализируем ZIP
        analysis = analyze_zip_file(temp_path)
        
        # Очищаем временные файлы
        os.remove(temp_path)
        os.rmdir(temp_dir)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"Error uploading ZIP: {e}")
        return jsonify({'error': 'Failed to process ZIP file'}), 500


@import_export_bp.route('/import-github', methods=['POST'])
@login_required
def import_github(lang):
    """Импорт проекта с GitHub"""
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        
        if not repo_url:
            return jsonify({'error': 'Repository URL is required'}), 400
        
        # Парсим GitHub URL
        repo_info = parse_github_url(repo_url)
        if not repo_info:
            return jsonify({'error': 'Invalid GitHub URL'}), 400
        
        # Получаем содержимое репозитория
        repo_content = fetch_github_repo(repo_info)
        
        # Анализируем структуру
        analysis = analyze_github_structure(repo_content)
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'repo_info': repo_info
        })
        
    except Exception as e:
        logger.error(f"Error importing from GitHub: {e}")
        return jsonify({'error': 'Failed to import from GitHub'}), 500


@import_export_bp.route('/import-url', methods=['POST'])
@login_required
def import_url(lang):
    """Импорт с URL"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Получаем содержимое
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        content = response.text
        content_type = response.headers.get('content-type', '')
        
        # Определяем тип контента
        if 'html' in content_type or url.endswith(('.html', '.htm')):
            file_type = 'html'
        elif 'javascript' in content_type or url.endswith('.js'):
            file_type = 'javascript'
        elif 'css' in content_type or url.endswith('.css'):
            file_type = 'css'
        else:
            file_type = 'unknown'
        
        # Анализируем контент
        analysis = analyze_content(content, file_type, url)
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'url': url,
            'content_type': file_type
        })
        
    except requests.RequestException as e:
        logger.error(f"Error fetching URL: {e}")
        return jsonify({'error': 'Failed to fetch URL'}), 500
    except Exception as e:
        logger.error(f"Error importing from URL: {e}")
        return jsonify({'error': 'Failed to process URL'}), 500


@import_export_bp.route('/build-project', methods=['POST'])
@login_required
def build_project(lang):
    """Сборка проекта с Webpack"""
    try:
        data = request.get_json()
        framework = data.get('framework', 'vanilla')
        project_data = data.get('project_data', {})
        
        # Создаем временную структуру проекта
        temp_dir = tempfile.mkdtemp()
        project_structure = create_project_structure(temp_dir, framework, project_data)
        
        # Симулируем сборку (в реальном проекте здесь был бы Webpack)
        build_result = simulate_webpack_build(framework, project_structure)
        
        # Создаем ZIP с результатом сборки
        output_zip = create_build_zip(temp_dir, build_result)
        
        # Очищаем временные файлы
        import shutil
        shutil.rmtree(temp_dir)
        
        return send_file(
            output_zip,
            as_attachment=True,
            download_name=f'{framework}-project-{datetime.now().strftime("%Y%m%d-%H%M%S")}.zip',
            mimetype='application/zip'
        )
        
    except Exception as e:
        logger.error(f"Error building project: {e}")
        return jsonify({'error': 'Failed to build project'}), 500


@import_export_bp.route('/export-project', methods=['POST'])
@login_required
def export_project(lang):
    """Экспорт проекта в различных форматах"""
    try:
        data = request.get_json()
        project_data = data.get('project_data', {})
        export_format = data.get('format', 'zip')
        
        if export_format == 'zip':
            return export_as_zip(project_data)
        elif export_format == 'github':
            return export_to_github(project_data)
        else:
            return jsonify({'error': 'Unsupported export format'}), 400
        
    except Exception as e:
        logger.error(f"Error exporting project: {e}")
        return jsonify({'error': 'Failed to export project'}), 500


def analyze_zip_file(zip_path):
    """Анализирует содержимое ZIP файла"""
    analysis = {
        'files': [],
        'directories': [],
        'package_json': None,
        'readme': None,
        'main_files': [],
        'config_files': [],
        'framework': 'unknown',
        'total_files': 0
    }
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            for file_info in zip_file.filelist:
                file_path = file_info.filename
                
                if file_info.is_dir():
                    analysis['directories'].append(file_path)
                else:
                    analysis['files'].append(file_path)
                    analysis['total_files'] += 1
                    
                    # Определяем важные файлы
                    if file_path == 'package.json':
                        analysis['package_json'] = file_path
                        # Читаем package.json для определения фреймворка
                        try:
                            content = zip_file.read(file_path).decode('utf-8')
                            package_data = json.loads(content)
                            analysis['framework'] = detect_framework_from_package(package_data)
                        except:
                            pass
                    elif 'readme' in file_path.lower():
                        analysis['readme'] = file_path
                    elif is_main_file(file_path):
                        analysis['main_files'].append(file_path)
                    elif is_config_file(file_path):
                        analysis['config_files'].append(file_path)
            
            # Если фреймворк не определен через package.json, определяем по файлам
            if analysis['framework'] == 'unknown':
                analysis['framework'] = detect_framework_from_files(analysis['files'])
    
    except Exception as e:
        logger.error(f"Error analyzing ZIP: {e}")
        analysis['error'] = str(e)
    
    return analysis


def parse_github_url(url):
    """Парсит GitHub URL"""
    import re
    
    # Поддерживаемые форматы:
    # https://github.com/owner/repo
    # https://github.com/owner/repo/tree/branch
    # https://github.com/owner/repo/blob/branch/path
    
    pattern = r'github\.com/([^/]+)/([^/]+)(?:/(?:tree|blob)/([^/]+))?'
    match = re.search(pattern, url)
    
    if match:
        return {
            'owner': match.group(1),
            'repo': match.group(2),
            'branch': match.group(3) or 'main'
        }
    
    return None


def fetch_github_repo(repo_info):
    """Получает содержимое GitHub репозитория"""
    api_url = f"https://api.github.com/repos/{repo_info['owner']}/{repo_info['repo']}/contents"
    params = {'ref': repo_info['branch']}
    
    response = requests.get(api_url, params=params, timeout=30)
    response.raise_for_status()
    
    contents = response.json()
    all_files = {}
    
    # Рекурсивно получаем все файлы
    fetch_github_files_recursive(contents, all_files, repo_info)
    
    return all_files


def fetch_github_files_recursive(contents, all_files, repo_info):
    """Рекурсивно получает файлы из GitHub"""
    for item in contents:
        if item['type'] == 'file':
            try:
                file_response = requests.get(item['download_url'], timeout=30)
                file_response.raise_for_status()
                all_files[item['path']] = file_response.text
            except Exception as e:
                logger.warning(f"Failed to fetch file {item['path']}: {e}")
        elif item['type'] == 'dir':
            try:
                dir_response = requests.get(item['url'], timeout=30)
                dir_response.raise_for_status()
                dir_contents = dir_response.json()
                fetch_github_files_recursive(dir_contents, all_files, repo_info)
            except Exception as e:
                logger.warning(f"Failed to fetch directory {item['path']}: {e}")


def analyze_github_structure(contents):
    """Анализирует структуру GitHub репозитория"""
    analysis = {
        'files': list(contents.keys()),
        'total_files': len(contents),
        'package_json': None,
        'readme': None,
        'main_files': [],
        'config_files': [],
        'framework': 'unknown'
    }
    
    for file_path in contents.keys():
        if file_path == 'package.json':
            analysis['package_json'] = file_path
            try:
                package_data = json.loads(contents[file_path])
                analysis['framework'] = detect_framework_from_package(package_data)
            except:
                pass
        elif 'readme' in file_path.lower():
            analysis['readme'] = file_path
        elif is_main_file(file_path):
            analysis['main_files'].append(file_path)
        elif is_config_file(file_path):
            analysis['config_files'].append(file_path)
    
    # Если фреймворк не определен через package.json
    if analysis['framework'] == 'unknown':
        analysis['framework'] = detect_framework_from_files(analysis['files'])
    
    return analysis


def analyze_content(content, file_type, url):
    """Анализирует контент файла"""
    analysis = {
        'file_type': file_type,
        'url': url,
        'size': len(content),
        'lines': content.count('\n') + 1,
        'framework': 'unknown',
        'components': [],
        'styles': [],
        'scripts': []
    }
    
    # Определяем фреймворк по содержимому
    if 'React' in content or 'react' in content or 'jsx' in content:
        analysis['framework'] = 'react'
    elif 'Vue' in content or 'vue' in content:
        analysis['framework'] = 'vue'
    elif 'Angular' in content or 'angular' in content:
        analysis['framework'] = 'angular'
    else:
        analysis['framework'] = 'html'
    
    # Извлекаем компоненты, стили, скрипты
    if file_type == 'html':
        analysis['components'] = extract_html_components(content)
    elif file_type == 'javascript':
        analysis['scripts'] = extract_js_functions(content)
    elif file_type == 'css':
        analysis['styles'] = extract_css_rules(content)
    
    return analysis


def create_project_structure(temp_dir, framework, project_data):
    """Создает структуру проекта"""
    structure = {
        'src': {},
        'public': {},
        'config': {}
    }
    
    # Создаем основные файлы в зависимости от фреймворка
    if framework == 'react':
        structure['src']['index.jsx'] = generate_react_entry(project_data)
        structure['src']['App.jsx'] = generate_react_app(project_data)
        structure['src']['styles.css'] = generate_default_styles()
    elif framework == 'vue':
        structure['src']['main.js'] = generate_vue_entry(project_data)
        structure['src']['App.vue'] = generate_vue_app(project_data)
        structure['src']['styles.css'] = generate_default_styles()
    elif framework == 'angular':
        structure['src']['main.ts'] = generate_angular_entry(project_data)
        structure['src']['app.component.ts'] = generate_angular_app(project_data)
        structure['src']['styles.css'] = generate_default_styles()
    else:
        structure['src']['index.js'] = generate_vanilla_entry(project_data)
        structure['src']['styles.css'] = generate_default_styles()
    
    # Создаем package.json
    structure['package.json'] = generate_package_json(framework, project_data)
    
    # Создаем файлы в временной директории
    create_files_from_structure(temp_dir, structure)
    
    return structure


def simulate_webpack_build(framework, project_structure):
    """Симулирует Webpack сборку"""
    import time
    
    # Симуляция времени сборки
    time.sleep(2)
    
    return {
        'success': True,
        'framework': framework,
        'output': {
            'main': f'dist/main.{framework}.js',
            'styles': 'dist/styles.css',
            'vendor': 'dist/vendor.js'
        },
        'stats': {
            'time': time.time(),
            'errors': [],
            'warnings': []
        }
    }


def create_build_zip(temp_dir, build_result):
    """Создает ZIP с результатом сборки"""
    import zipfile
    import tempfile
    
    # Создаем временный ZIP файл
    zip_path = tempfile.mktemp(suffix='.zip')
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Добавляем файлы из временной директории
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, temp_dir)
                zip_file.write(file_path, arc_name)
        
        # Добавляем файлы сборки
        zip_file.writestr('dist/main.js', '// Compiled main file\n')
        zip_file.writestr('dist/styles.css', '/* Compiled styles */\n')
        zip_file.writestr('dist/vendor.js', '// Vendor libraries\n')
        
        # Добавляем README
        readme_content = f"""# {build_result['framework'].title()} Project

Generated by Advanced Dental Editor

## Build Info
- Framework: {build_result['framework']}
- Build Time: {datetime.now().isoformat()}
- Status: {'Success' if build_result['success'] else 'Failed'}

## Usage
1. Extract this ZIP file
2. Run `npm install` to install dependencies
3. Run `npm start` to start development server
4. Run `npm run build` to build for production

## Files
- `dist/main.js` - Main application bundle
- `dist/styles.css` - Compiled styles
- `dist/vendor.js` - Vendor libraries
"""
        zip_file.writestr('README.md', readme_content)
    
    return zip_path


def export_as_zip(project_data):
    """Экспортирует проект как ZIP"""
    try:
        # Создаем временную структуру
        temp_dir = tempfile.mkdtemp()
        framework = project_data.get('framework', 'vanilla')
        
        structure = create_project_structure(temp_dir, framework, project_data)
        output_zip = create_build_zip(temp_dir, {'success': True, 'framework': framework})
        
        # Очищаем временные файлы
        import shutil
        shutil.rmtree(temp_dir)
        
        return send_file(
            output_zip,
            as_attachment=True,
            download_name=f'{framework}-project-{datetime.now().strftime("%Y%m%d-%H%M%S")}.zip',
            mimetype='application/zip'
        )
        
    except Exception as e:
        logger.error(f"Error exporting as ZIP: {e}")
        return jsonify({'error': 'Failed to export as ZIP'}), 500


def export_to_github(project_data):
    """Экспортирует проект на GitHub (заглушка)"""
    return jsonify({
        'success': True,
        'message': 'GitHub export is not implemented yet',
        'project_data': project_data
    })


# Вспомогательные функции

def detect_framework_from_package(package_data):
    """Определяет фреймворк из package.json"""
    dependencies = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}
    
    if 'react' in dependencies or 'react-dom' in dependencies:
        return 'react'
    elif 'vue' in dependencies:
        return 'vue'
    elif '@angular/core' in dependencies:
        return 'angular'
    
    return 'unknown'


def detect_framework_from_files(files):
    """Определяет фреймворк по файлам"""
    file_extensions = [os.path.splitext(f)[1].lower() for f in files]
    
    if any(ext in ['.jsx', '.tsx'] for ext in file_extensions):
        return 'react'
    elif any(ext == '.vue' for ext in file_extensions):
        return 'vue'
    elif any(ext == '.ts' for ext in file_extensions) and any('angular' in f for f in files):
        return 'angular'
    
    return 'html'


def is_main_file(file_path):
    """Проверяет, является ли файл основным"""
    main_patterns = [
        'index.html', 'main.html', 'app.html',
        'index.js', 'main.js', 'app.js',
        'index.jsx', 'main.jsx', 'app.jsx',
        'index.tsx', 'main.tsx', 'app.tsx',
        'index.vue', 'main.vue', 'app.vue'
    ]
    
    file_name = os.path.basename(file_path).lower()
    return any(pattern in file_name for pattern in main_patterns)


def is_config_file(file_path):
    """Проверяет, является ли файл конфигурационным"""
    config_patterns = [
        'webpack.config', 'vite.config', 'rollup.config',
        'babel.config', 'tsconfig', 'eslint',
        '.env', 'tailwind.config', 'postcss.config'
    ]
    
    file_name = os.path.basename(file_path).lower()
    return any(pattern in file_name for pattern in config_patterns)


def extract_html_components(content):
    """Извлекает HTML компоненты"""
    import re
    
    components = []
    # Простой парсер для поиска тегов
    tag_pattern = r'<(\w+)[^>]*>'
    matches = re.findall(tag_pattern, content)
    
    for tag in set(matches):
        if tag not in ['html', 'head', 'body', 'div', 'span', 'p']:
            components.append(tag)
    
    return components[:10]  # Ограничиваем количество


def extract_js_functions(content):
    """Извлекает JavaScript функции"""
    import re
    
    functions = []
    # Простой парсер для поиска функций
    func_pattern = r'function\s+(\w+)\s*\('
    matches = re.findall(func_pattern, content)
    
    return matches[:10]  # Ограничиваем количество


def extract_css_rules(content):
    """Извлекает CSS правила"""
    import re
    
    rules = []
    # Простой парсер для поиска CSS селекторов
    selector_pattern = r'([.#]?\w+[^}]*)\s*{'
    matches = re.findall(selector_pattern, content)
    
    return rules[:10]  # Ограничиваем количество


# Генераторы файлов (упрощенные версии)

def generate_react_entry(project_data):
    return """import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import './styles.css';

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);"""


def generate_react_app(project_data):
    return """import React from 'react';

function App() {
  return (
    <div className="app">
      <h1>React App</h1>
      <p>Generated by Advanced Dental Editor</p>
    </div>
  );
}

export default App;"""


def generate_vue_entry(project_data):
    return """import { createApp } from 'vue';
import App from './App.vue';
import './styles.css';

createApp(App).mount('#app');"""


def generate_vue_app(project_data):
    return """<template>
  <div class="app">
    <h1>Vue App</h1>
    <p>Generated by Advanced Dental Editor</p>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>"""


def generate_angular_entry(project_data):
    return """import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app.module';

platformBrowserDynamic().bootstrapModule(AppModule)
  .catch(err => console.error(err));"""


def generate_angular_app(project_data):
    return """import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: \`
    <div class="app">
      <h1>Angular App</h1>
      <p>Generated by Advanced Dental Editor</p>
    </div>
  \`
})
export class AppComponent {
  title = 'angular-app';
}"""


def generate_vanilla_entry(project_data):
    return """import './styles.css';

document.addEventListener('DOMContentLoaded', () => {
  const app = document.getElementById('app');
  if (app) {
    app.innerHTML = \`
      <div class="app">
        <h1>Vanilla JS App</h1>
        <p>Generated by Advanced Dental Editor</p>
      </div>
    \`;
  }
});"""


def generate_default_styles():
    return """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.6;
  color: #333;
}

.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
}

h1 {
  color: #2c3e50;
  margin-bottom: 20px;
}

p {
  color: #7f8c8d;
}"""


def generate_package_json(framework, project_data):
    """Генерирует package.json"""
    base_package = {
        "name": project_data.get('name', f'{framework}-app'),
        "version": "1.0.0",
        "description": "Generated by Advanced Dental Editor",
        "main": "dist/main.js",
        "scripts": {
            "start": "webpack serve --mode development",
            "build": "webpack --mode production",
            "dev": "webpack serve --mode development"
        },
        "dependencies": {},
        "devDependencies": {
            "webpack": "^5.88.0",
            "webpack-cli": "^5.1.0",
            "webpack-dev-server": "^4.15.1"
        }
    }
    
    # Добавляем зависимости в зависимости от фреймворка
    if framework == 'react':
        base_package['dependencies'] = {
            "react": "^18.2.0",
            "react-dom": "^18.2.0"
        }
    elif framework == 'vue':
        base_package['dependencies'] = {
            "vue": "^3.3.0"
        }
    elif framework == 'angular':
        base_package['dependencies'] = {
            "@angular/core": "^16.0.0",
            "@angular/platform-browser": "^16.0.0"
        }
    
    return json.dumps(base_package, indent=2)


def create_files_from_structure(base_dir, structure):
    """Создает файлы из структуры"""
    for path, content in structure.items():
        if isinstance(content, dict):
            # Это директория
            dir_path = os.path.join(base_dir, path)
            os.makedirs(dir_path, exist_ok=True)
            create_files_from_structure(dir_path, content)
        else:
            # Это файл
            file_path = os.path.join(base_dir, path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content) 