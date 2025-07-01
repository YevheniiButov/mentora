# Content Editor Testing Guide

Руководство по тестированию системы Content Editor для Dental Academy.

## 🚀 Быстрое тестирование

### Простая команда
```bash
./test.sh
```

Эта команда запускает быстрый тест основных компонентов Content Editor.

### Полное тестирование
```bash
./test_content_editor.sh
```

Эта команда запускает полное тестирование всех компонентов системы.

## 📋 Пошаговое тестирование

### Шаг 1: Проверка окружения
```bash
# Проверяем Python
python3 --version

# Проверяем что мы в правильной директории
ls app.py
```

### Шаг 2: Создание таблиц БД
```bash
python3 -c "
import sys
sys.path.insert(0, '.')
from app import app, db
with app.app_context():
    db.create_all()
    print('✅ Database tables created')
"
```

### Шаг 3: Тестирование модели
```bash
python3 -c "
import sys
sys.path.insert(0, '.')
from app import app, db
from models import ContentTemplate
import json

with app.app_context():
    # Создаем тестовый шаблон
    template = ContentTemplate(
        template_id='test_001',
        name='Test Template',
        description='Test',
        category='test',
        structure=json.dumps([]),
        template_metadata=json.dumps({}),
        tags=json.dumps([]),
        language='en'
    )
    db.session.add(template)
    db.session.commit()
    print('✅ Test template created')
    
    # Удаляем тестовый шаблон
    db.session.delete(template)
    db.session.commit()
    print('✅ Test template cleaned up')
"
```

### Шаг 4: Тестирование template_manager
```bash
python3 -c "
import sys
sys.path.insert(0, '.')
from app import app
from utils.template_manager import template_manager

with app.app_context():
    templates = template_manager.get_all_templates()
    print(f'✅ Template manager works, found {len(templates)} templates')
"
```

### Шаг 5: Тестирование routes
```bash
python3 -c "
import sys
sys.path.insert(0, '.')
from routes.content_editor import content_editor_bp
print('✅ Content editor routes imported successfully')
"
```

### Шаг 6: Инициализация шаблонов
```bash
python3 init_content_editor.py
```

### Шаг 7: Проверка результатов
```bash
python3 -c "
import sys
sys.path.insert(0, '.')
from app import app, db
from models import ContentTemplate

with app.app_context():
    templates = ContentTemplate.query.all()
    print(f'📊 Found {len(templates)} templates:')
    for template in templates:
        print(f'   • {template.name} ({template.category})')
"
```

## 🔧 Тестирование API

### Запуск приложения
```bash
python3 app.py
```

### Тестирование endpoints
```bash
# Главная страница
curl http://localhost:5000/content-editor/

# API шаблонов
curl http://localhost:5000/content-editor/api/templates

# Список шаблонов
curl http://localhost:5000/content-editor/templates
```

## 📊 Проверка компонентов

### 1. Модель ContentTemplate
- ✅ Создание шаблона
- ✅ Сохранение в БД
- ✅ Извлечение из БД
- ✅ Обновление шаблона
- ✅ Удаление шаблона

### 2. Template Manager
- ✅ Получение всех шаблонов
- ✅ Создание нового шаблона
- ✅ Обновление шаблона
- ✅ Удаление шаблона
- ✅ Поиск по категории
- ✅ Поиск по тегам

### 3. Content Editor Routes
- ✅ Импорт blueprint
- ✅ Регистрация маршрутов
- ✅ Доступность страниц
- ✅ Работа API endpoints

### 4. База данных
- ✅ Создание таблиц
- ✅ Связи между таблицами
- ✅ Индексы
- ✅ Ограничения

## 🐛 Устранение неполадок

### Ошибка импорта
```
ImportError: No module named 'routes.content_editor'
```
**Решение:** Проверьте что файл `routes/content_editor.py` существует.

### Ошибка базы данных
```
sqlalchemy.exc.OperationalError: no such table
```
**Решение:** Запустите `db.create_all()` в контексте приложения.

### Ошибка template_manager
```
AttributeError: 'NoneType' object has no attribute
```
**Решение:** Проверьте что модель ContentTemplate правильно определена.

### Ошибка маршрутов
```
404 Not Found
```
**Решение:** Убедитесь что blueprint зарегистрирован в `app.py`.

## 📁 Структура тестовых файлов

```
├── test.sh                    # Простая команда тестирования
├── quick_test.py             # Быстрое тестирование
├── test_content_editor.py    # Полное тестирование
├── test_content_editor.sh    # Bash скрипт полного тестирования
└── TESTING_README.md         # Это руководство
```

## 🎯 Результаты тестирования

### Успешное тестирование
```
🎉 All tests passed!
📋 Content Editor is ready to use:
• Access at: /content-editor/
• Templates at: /content-editor/templates
• API at: /content-editor/api/templates
```

### Неудачное тестирование
```
❌ Some tests failed. Check the errors above.
🔧 Troubleshooting:
1. Check that all required files exist
2. Verify database connection
3. Ensure all dependencies are installed
4. Check file permissions
```

## 📞 Поддержка

Если у вас возникли проблемы с тестированием:

1. Проверьте логи ошибок
2. Убедитесь что все зависимости установлены
3. Проверьте права доступа к файлам
4. Убедитесь что база данных доступна

Для получения дополнительной информации см. `CONTENT_EDITOR_README.md`. 