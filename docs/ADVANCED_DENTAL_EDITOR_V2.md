# Advanced Dental Editor v2.0 - Документация

## 🚀 Обзор

Advanced Dental Editor v2.0 - это продвинутый HTML-редактор на базе GrapesJS с поддержкой современных веб-технологий, 3D моделей, Hot Module Replacement (HMR) и интеграцией с популярными фреймворками.

## ✨ Основные возможности

### 🎨 Визуальный редактор
- **GrapesJS** - мощный drag-and-drop редактор
- **Monaco Editor** - встроенный редактор кода (VS Code движок)
- **3D модели** - поддержка Three.js для стоматологических моделей
- **Режимы устройств** - предварительный просмотр на разных экранах

### 🔥 Hot Module Replacement (HMR)
- **WebSocket соединение** - мгновенное обновление изменений
- **File watching** - автоматическое отслеживание файлов
- **Live reload** - перезагрузка без потери состояния

### 📦 Импорт/Экспорт
- **ZIP архивы** - загрузка и анализ проектов
- **GitHub интеграция** - импорт из репозиториев
- **URL импорт** - загрузка с веб-страниц
- **Множественные форматы** - HTML, CSS, JS, JSX, TSX, Vue

### ⚡ Webpack интеграция
- **React поддержка** - JSX, компоненты, Hooks
- **Vue поддержка** - Single File Components
- **Angular поддержка** - TypeScript, компоненты
- **Vanilla JS** - чистый JavaScript
- **Автоматическая сборка** - оптимизация и минификация

## 🏗️ Архитектура

### Основные компоненты

```
Advanced Dental Editor v2.0
├── 🎨 GrapesJS Editor (Визуальный редактор)
├── 🔥 HotReloadSystem (HMR)
├── 📦 UniversalImporter (Импорт/Экспорт)
├── ⚡ WebpackIntegration (Сборка)
├── 🦷 ThreeDModelSystem (3D модели)
└── 🧠 AdvancedDentalEditorCore (Координация)
```

### Технологический стек

- **Backend**: Flask, Flask-SocketIO, SQLAlchemy
- **Frontend**: GrapesJS, Monaco Editor, Three.js
- **HMR**: WebSocket, Watchdog
- **Build**: Webpack (симуляция), Babel
- **3D**: Three.js, OrbitControls

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Запуск приложения

```bash
python app.py
```

Приложение будет доступно по адресу: `http://localhost:8080`

### 3. Доступ к редактору

Перейдите по адресу: `http://localhost:8080/en/admin/content-editor/grapesjs-builder`

## 📖 Подробное руководство

### 🎨 Использование визуального редактора

#### Основные элементы интерфейса

1. **Верхний тулбар**
   - Кнопки сохранения, предварительного просмотра
   - Селектор фреймворка (React, Vue, Angular, Vanilla)
   - Кнопки импорта/экспорта

2. **Левая панель**
   - Блоки для перетаскивания
   - 3D модели зубов
   - Шаблоны страниц

3. **Центральная область**
   - Канвас для редактирования
   - Режимы устройств (Desktop, Tablet, Mobile)

4. **Правая панель**
   - Стили (CSS)
   - Слои (Layers)
   - Свойства элементов

5. **Нижняя панель**
   - Редакторы кода (HTML, CSS, JavaScript)
   - Консоль вывода

#### Работа с блоками

```javascript
// Добавление кастомного блока
editor.BlockManager.add('dental-card', {
  label: 'Dental Card',
  category: 'Dental',
  content: `
    <div class="dental-card">
      <h3>Tooth Information</h3>
      <p>Description here</p>
    </div>
  `,
  attributes: { class: 'fa fa-tooth' }
});
```

### 🔥 Hot Module Replacement (HMR)

#### Настройка HMR

HMR система автоматически инициализируется при запуске приложения:

```python
# utils/hmr_server.py
from flask_socketio import SocketIO
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class HotReloadSystem:
    def __init__(self):
        self.socketio = None
        self.observer = None
        self.watched_files = set()
```

#### Использование HMR

1. **Автоматическое подключение**
   ```javascript
   // static/js/hot-reload-system.js
   const hmr = new HotReloadSystem();
   await hmr.initialize();
   ```

2. **Отправка обновлений**
   ```javascript
   // Отправка изменений на сервер
   await hmr.sendUpdate({
     html: editor.getComponents(),
     css: editor.getStyle(),
     js: editor.getScript()
   });
   ```

3. **Получение обновлений**
   ```javascript
   // Слушание обновлений от сервера
   hmr.onUpdate((data) => {
     editor.setComponents(data.html);
     editor.setStyle(data.css);
     editor.setScript(data.js);
   });
   ```

### 📦 Импорт/Экспорт проектов

#### Поддерживаемые форматы

- **ZIP архивы**: Полные проекты с зависимостями
- **GitHub**: Прямой импорт из репозиториев
- **URL**: Загрузка с веб-страниц
- **Файлы**: Отдельные HTML, CSS, JS файлы

#### API маршруты

```python
# routes/import_export_routes.py

@import_export_bp.route('/upload-zip', methods=['POST'])
def upload_zip(lang):
    """Загрузка и анализ ZIP архива"""

@import_export_bp.route('/import-github', methods=['POST'])
def import_github(lang):
    """Импорт проекта с GitHub"""

@import_export_bp.route('/import-url', methods=['POST'])
def import_url(lang):
    """Импорт с URL"""

@import_export_bp.route('/build-project', methods=['POST'])
def build_project(lang):
    """Сборка проекта с Webpack"""

@import_export_bp.route('/export-project', methods=['POST'])
def export_project(lang):
    """Экспорт проекта в различных форматах"""
```

#### Примеры использования

**Импорт ZIP архива:**
```javascript
const formData = new FormData();
formData.append('file', zipFile);

const response = await fetch('/api/import-export/upload-zip', {
  method: 'POST',
  body: formData,
  headers: {
    'X-CSRFToken': getCSRFToken()
  }
});

const result = await response.json();
if (result.success) {
  console.log('Analysis:', result.analysis);
}
```

**Импорт с GitHub:**
```javascript
const response = await fetch('/api/import-export/import-github', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCSRFToken()
  },
  body: JSON.stringify({
    repo_url: 'https://github.com/user/repo'
  })
});
```

### ⚡ Webpack интеграция

#### Поддерживаемые фреймворки

1. **React**
   ```javascript
   // Автоматически генерируется:
   // - package.json с React зависимостями
   // - webpack.config.js для JSX
   // - src/index.jsx и App.jsx
   ```

2. **Vue**
   ```javascript
   // Автоматически генерируется:
   // - package.json с Vue зависимостями
   // - webpack.config.js для .vue файлов
   // - src/main.js и App.vue
   ```

3. **Angular**
   ```javascript
   // Автоматически генерируется:
   // - package.json с Angular зависимостями
   // - webpack.config.js для TypeScript
   // - src/main.ts и app.component.ts
   ```

4. **Vanilla JS**
   ```javascript
   // Автоматически генерируется:
   // - package.json с базовыми зависимостями
   // - webpack.config.js для ES6+
   // - src/index.js
   ```

#### Сборка проекта

```javascript
// Сборка React проекта
const response = await fetch('/api/import-export/build-project', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCSRFToken()
  },
  body: JSON.stringify({
    framework: 'react',
    project_data: {
      name: 'my-dental-app',
      components: ['DentalCard', 'ToothViewer'],
      styles: ['main.css', 'components.css']
    }
  })
});

// Скачивание ZIP с собранным проектом
const blob = await response.blob();
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'react-project.zip';
a.click();
```

### 🦷 3D модели

#### Поддерживаемые модели

- **Зубы**: Сферические и цилиндрические модели
- **Челюсти**: Верхняя и нижняя челюсть
- **Кастомные модели**: Загрузка из файлов

#### Использование 3D моделей

```javascript
// Инициализация 3D системы
const modelSystem = new ThreeDModelSystem();
await modelSystem.initialize();

// Добавление модели в сцену
const tooth = modelSystem.addToScene('tooth-1', {
  x: 0, y: 0, z: 0
});

// Управление камерой
modelSystem.resetCamera();
modelSystem.toggleWireframe();
modelSystem.toggleAnimation();
```

#### Интеграция с редактором

```javascript
// Добавление 3D модели на страницу
editor.BlockManager.add('3d-tooth', {
  label: '3D Tooth',
  category: '3D Models',
  content: `
    <div class="3d-model-container" data-model="tooth-1">
      <canvas id="tooth-canvas"></canvas>
    </div>
  `,
  attributes: { class: 'fa fa-cube' }
});
```

## 🔧 Конфигурация

### Настройки приложения

```python
# app.py
app.config.update(
    # Максимальный размер файла для загрузки
    MAX_CONTENT_LENGTH=50 * 1024 * 1024,  # 50MB
    
    # Настройки HMR
    HMR_ENABLED=True,
    HMR_PORT=5001,
    
    # Настройки WebSocket
    SOCKETIO_ASYNC_MODE='eventlet',
    
    # Настройки загрузки файлов
    UPLOAD_FOLDER='static/uploads',
    ALLOWED_EXTENSIONS={'zip', 'html', 'css', 'js', 'jsx', 'tsx', 'vue'}
)
```

### Настройки HMR

```python
# utils/hmr_server.py
HMR_CONFIG = {
    'enabled': True,
    'port': 5001,
    'auto_connect': True,
    'watch_patterns': [
        '*.html', '*.css', '*.js', '*.jsx', '*.tsx', '*.vue'
    ],
    'ignore_patterns': [
        'node_modules/*', '__pycache__/*', '*.pyc'
    ]
}
```

### Настройки импорта/экспорта

```python
# routes/import_export_routes.py
SUPPORTED_FORMATS = {
    'zip': ['.zip'],
    'github': ['github.com'],
    'url': ['.html', '.htm', '.js', '.css'],
    'file': ['.html', '.htm', '.js', '.css', '.jsx', '.tsx', '.vue']
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
```

## 🧪 Тестирование

### Запуск тестов

```bash
# Тестирование API маршрутов
python -m pytest tests/test_import_export.py

# Тестирование HMR системы
python -m pytest tests/test_hmr.py

# Тестирование Webpack интеграции
python -m pytest tests/test_webpack.py
```

### Тестирование в браузере

1. Откройте `http://localhost:8080/en/admin/content-editor/grapesjs-builder`
2. Протестируйте импорт ZIP файла
3. Проверьте HMR функциональность
4. Протестируйте сборку проекта

## 🐛 Отладка

### Логирование

```python
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Логирование HMR
logger = logging.getLogger('hmr')
logger.info('HMR system initialized')

# Логирование импорта/экспорта
logger = logging.getLogger('import_export')
logger.info('ZIP file processed successfully')
```

### Отладка WebSocket

```javascript
// Включение отладки WebSocket
localStorage.setItem('debug', 'socket.io-client:socket');

// Отладка HMR
const hmr = new HotReloadSystem();
hmr.on('debug', (message) => {
  console.log('HMR Debug:', message);
});
```

### Отладка Monaco Editor

```javascript
// Включение отладки Monaco
window.monaco.editor.setModelMarkers(model, 'debug', [
  {
    startLineNumber: 1,
    startColumn: 1,
    endLineNumber: 1,
    endColumn: 10,
    message: 'Debug marker',
    severity: monaco.MarkerSeverity.Info
  }
]);
```

## 📚 API Reference

### HotReloadSystem

```javascript
class HotReloadSystem {
  constructor()
  async initialize()
  async connect()
  async disconnect()
  async sendUpdate(data)
  onUpdate(callback)
  onConnect(callback)
  onDisconnect(callback)
}
```

### UniversalImporter

```javascript
class UniversalImporter {
  constructor()
  async handleZipImport(event)
  async handleGitHubImport(event)
  async handleUrlImport(event)
  displayAnalysis(analysis, source)
  async importToEditor(source, data)
  downloadAnalysis(analysis)
}
```

### WebpackIntegration

```javascript
class WebpackIntegration {
  constructor()
  async buildProject()
  async exportProject()
  onFrameworkChange(framework)
  updateFrameworkConfig(framework)
  getBuildOptions(framework)
  getDependencies(framework)
}
```

### AdvancedDentalEditorCore

```javascript
class AdvancedDentalEditorCore {
  constructor()
  async initialize()
  async createProject(framework, options)
  async exportProject(format)
  async importProject(source, data)
  generateProjectTemplate(framework, options)
  getStatus()
}
```

## 🔮 Планы развития

### v2.1 (Планируется)
- [ ] Поддержка TypeScript
- [ ] Интеграция с Vite
- [ ] Поддержка Svelte
- [ ] Улучшенные 3D модели
- [ ] Коллаборативная работа

### v2.2 (Планируется)
- [ ] AI-ассистент для кода
- [ ] Автоматическая оптимизация
- [ ] Поддержка PWA
- [ ] Интеграция с Git
- [ ] Расширенная аналитика

## 🤝 Вклад в проект

### Установка для разработки

```bash
# Клонирование репозитория
git clone https://github.com/your-repo/advanced-dental-editor.git
cd advanced-dental-editor

# Установка зависимостей
pip install -r requirements-dev.txt

# Запуск в режиме разработки
python app.py --dev
```

### Структура проекта

```
advanced-dental-editor/
├── app.py                          # Основное приложение
├── routes/
│   ├── import_export_routes.py     # API импорта/экспорта
│   └── ...
├── static/
│   └── js/
│       ├── hot-reload-system.js    # HMR система
│       ├── universal-importer.js   # Импорт/экспорт
│       ├── webpack-integration.js  # Webpack интеграция
│       └── advanced-dental-editor-core.js # Основной модуль
├── utils/
│   └── hmr_server.py               # Серверная часть HMR
├── templates/
│   └── admin/
│       └── content_editor/
│           └── grapesjs_builder.html # Шаблон редактора
└── docs/
    └── ADVANCED_DENTAL_EDITOR_V2.md # Эта документация
```

### Стиль кода

- **Python**: PEP 8, type hints
- **JavaScript**: ES6+, JSDoc комментарии
- **HTML/CSS**: BEM методология
- **Коммиты**: Conventional Commits

## 📄 Лицензия

MIT License - см. файл LICENSE для подробностей.

## 👥 Авторы

- **Основной разработчик**: [Ваше имя]
- **Дизайн**: [Дизайнер]
- **Тестирование**: [Тестировщик]

## 📞 Поддержка

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@dental-editor.com

---

**Advanced Dental Editor v2.0** - Продвинутый HTML-редактор для стоматологического образования 🦷 