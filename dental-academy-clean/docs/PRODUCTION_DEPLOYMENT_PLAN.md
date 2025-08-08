# 🚀 ПЛАН ДЕПЛОЯ НА PRODUCTION (Flask + PostgreSQL)

## 📋 **АНАЛИЗ ТЕКУЩЕГО СОСТОЯНИЯ**

### ✅ **Что уже есть:**
- Flask монолитное приложение
- SQLAlchemy ORM
- Alembic миграции
- DigiD интеграция
- IRT система
- BI-toets структура
- Многоязычность (8 языков)
- Виртуальные пациенты
- Система достижений

### ❌ **Что нужно исправить в предложении Claude:**
- **Архитектура:** Node.js → Flask (Python)
- **База данных:** MongoDB → PostgreSQL
- **Зависимости:** Express → Flask ecosystem
- **Структура:** Frontend/Backend → Монолит

## 🎯 **ПРАВИЛЬНЫЙ ПЛАН ДЕПЛОЯ**

### 1. **ОБНОВИТЬ render.yaml**

```yaml
services:
  - type: web
    name: mentora-dental-academy
    env: python
    plan: starter  # или free для тестирования
    buildCommand: |
      pip install -r requirements.txt &&
      python -m flask db upgrade &&
      python scripts/seed_data.py
    startCommand: gunicorn --bind 0.0.0.0:$PORT app:app
    envVars:
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: mentora-db
          property: connectionString
      - key: DIGID_MOCK_MODE
        value: "true"  # для production заменить на false
      - key: DIGID_ENTITY_ID
        value: "your-digid-entity-id"
      - key: DIGID_ACS_URL
        value: "https://your-domain.onrender.com/digid/callback"
      - key: DIGID_SLO_URL
        value: "https://your-domain.onrender.com/digid/logout"
    healthCheckPath: /health
    autoDeploy: true

databases:
  - name: mentora-db
    databaseName: mentora
    user: mentora_user
    plan: starter
```

### 2. **СОЗДАТЬ СКРИПТ ЗАГРУЗКИ ДАННЫХ**

```python
# scripts/seed_data.py
import os
import sys
import json
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent.parent))

from app import app
from extensions import db
from models import (
    BIGDomain, LearningPath, Subject, Module, Lesson,
    Question, IRTParameters, VirtualPatientScenario
)

def load_bi_toets_structure():
    """Загружает структуру BI-toets путей обучения"""
    print("🔄 Загружаем BI-toets структуру...")
    
    # Создаем пути обучения
    learning_paths = [
        {
            'id': 'theoretical',
            'name': 'Theoretische Kennis',
            'name_nl': 'Theoretische Kennis',
            'name_ru': 'Теоретические знания',
            'description': 'Теоретические основы стоматологии',
            'exam_component': 'THEORETICAL',
            'exam_weight': 40.0,
            'exam_type': 'multiple_choice',
            'duration_weeks': 12,
            'total_estimated_hours': 120
        },
        {
            'id': 'methodology',
            'name': 'Methodologie',
            'name_nl': 'Methodologie',
            'name_ru': 'Методология',
            'description': 'Методологические подходы',
            'exam_component': 'METHODOLOGY',
            'exam_weight': 25.0,
            'exam_type': 'open_book',
            'duration_weeks': 8,
            'total_estimated_hours': 80
        },
        {
            'id': 'practical',
            'name': 'Praktische Vaardigheden',
            'name_nl': 'Praktische Vaardigheden',
            'name_ru': 'Практические навыки',
            'description': 'Практические навыки',
            'exam_component': 'PRACTICAL',
            'exam_weight': 20.0,
            'exam_type': 'practical_theory',
            'duration_weeks': 10,
            'total_estimated_hours': 100
        },
        {
            'id': 'clinical',
            'name': 'Klinische Competenties',
            'name_nl': 'Klinische Competenties',
            'name_ru': 'Клинические компетенции',
            'description': 'Клинические компетенции',
            'exam_component': 'CLINICAL',
            'exam_weight': 15.0,
            'exam_type': 'case_study',
            'duration_weeks': 6,
            'total_estimated_hours': 60
        }
    ]
    
    for path_data in learning_paths:
        existing = LearningPath.query.get(path_data['id'])
        if not existing:
            path = LearningPath(**path_data)
            db.session.add(path)
            print(f"✅ Создан путь: {path_data['name']}")
    
    db.session.commit()

def load_domains():
    """Загружает 30 доменов BI-toets"""
    print("🔄 Загружаем домены BI-toets...")
    
    # Инициализируем домены через модель
    BIGDomain.initialize_domains()
    print("✅ Домены загружены")

def load_questions():
    """Загружает вопросы из JSON файлов"""
    print("🔄 Загружаем вопросы...")
    
    # Загружаем основные вопросы
    questions_path = Path(__file__).parent.parent / 'scripts' / '160_2.json'
    if questions_path.exists():
        with open(questions_path, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        
        for q_data in questions_data:
            # Создаем вопрос
            question = Question(
                text=q_data['text'],
                options=q_data['options'],
                correct_answer_index=q_data['correct_answer_index'],
                correct_answer_text=q_data['correct_answer_text'],
                explanation=q_data['explanation'],
                category=q_data.get('category', 'general'),
                domain=q_data.get('domain', 'general'),
                difficulty_level=q_data.get('difficulty_level', 2)
            )
            db.session.add(question)
            db.session.flush()  # Получаем ID
            
            # Создаем IRT параметры
            if 'irt_params' in q_data:
                irt_params = IRTParameters(
                    question_id=question.id,
                    difficulty=q_data['irt_params'].get('difficulty', 0.0),
                    discrimination=q_data['irt_params'].get('discrimination', 1.0),
                    guessing=q_data['irt_params'].get('guessing', 0.25)
                )
                db.session.add(irt_params)
        
        print(f"✅ Загружено {len(questions_data)} вопросов")

def load_virtual_patients():
    """Загружает виртуальных пациентов"""
    print("🔄 Загружаем виртуальных пациентов...")
    
    vp_dir = Path(__file__).parent.parent / 'cards' / 'virtual_patient'
    if vp_dir.exists():
        for vp_file in vp_dir.glob('*.json'):
            with open(vp_file, 'r', encoding='utf-8') as f:
                vp_data = json.load(f)
            
            scenario = VirtualPatientScenario(
                title=vp_data['title'],
                description=vp_data.get('description', ''),
                difficulty=vp_data.get('difficulty', 'medium'),
                category=vp_data.get('category', 'diagnosis'),
                scenario_data=json.dumps(vp_data['scenario_data']),
                is_published=True
            )
            db.session.add(scenario)
        
        print(f"✅ Загружено виртуальных пациентов")

def main():
    """Основная функция загрузки данных"""
    with app.app_context():
        try:
            print("🚀 Начинаем загрузку данных...")
            
            # Создаем таблицы
            db.create_all()
            print("✅ Таблицы созданы")
            
            # Загружаем данные
            load_bi_toets_structure()
            load_domains()
            load_questions()
            load_virtual_patients()
            
            # Коммитим все изменения
            db.session.commit()
            print("🎉 Все данные загружены успешно!")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки данных: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    main()
```

### 3. **ОБНОВИТЬ requirements.txt**

```txt
# Добавить для production
gunicorn==23.0.0
psycopg2-binary==2.9.9
python-dotenv==1.1.0
```

### 4. **СОЗДАТЬ .env.example**

```bash
# .env.example
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://user:password@host:port/database

# DigiD Configuration
DIGID_MOCK_MODE=true
DIGID_ENTITY_ID=your-entity-id
DIGID_ACS_URL=https://your-domain.com/digid/callback
DIGID_SLO_URL=https://your-domain.com/digid/logout

# Security
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
```

### 5. **ДОБАВИТЬ HEALTH CHECK**

```python
# В app.py добавить
@app.route('/health')
def health_check():
    """Health check для Render"""
    try:
        # Проверяем подключение к БД
        db.session.execute('SELECT 1')
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'environment': app.config.get('FLASK_ENV', 'unknown')
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, 500
```

## 🎯 **ПОШАГОВЫЙ ПЛАН ДЕПЛОЯ**

### 1. **Подготовка репозитория**
```bash
# Создать скрипт загрузки данных
mkdir -p scripts
# Создать seed_data.py (см. выше)

# Обновить render.yaml
# Обновить requirements.txt
# Создать .env.example
```

### 2. **Настройка Render**
1. Создать аккаунт на Render.com
2. Подключить GitHub репозиторий
3. Создать PostgreSQL базу данных
4. Настроить переменные окружения
5. Запустить деплой

### 3. **Проверка после деплоя**
- ✅ Health check: `https://your-app.onrender.com/health`
- ✅ Главная страница: `https://your-app.onrender.com/`
- ✅ Регистрация/вход
- ✅ BI-toets пути обучения
- ✅ Вопросы загружены
- ✅ Виртуальные пациенты

## 🚨 **ВАЖНЫЕ ЗАМЕЧАНИЯ**

### ✅ **Преимущества этого подхода:**
- Сохраняет всю существующую функциональность
- Не требует переписывания кода
- Использует правильную архитектуру
- Поддерживает все компоненты (DigiD, IRT, BI-toets)

### ⚠️ **Что нужно учесть:**
- DigiD в production требует реальных сертификатов
- PostgreSQL вместо SQLite для production
- Настройка SSL сертификатов
- Мониторинг и логирование

## 🎉 **РЕЗУЛЬТАТ**

Полностью рабочая платформа на Render с:
- ✅ Flask приложением
- ✅ PostgreSQL базой данных
- ✅ Автоматической загрузкой данных
- ✅ DigiD интеграцией
- ✅ IRT системой
- ✅ BI-toets структурой
- ✅ Виртуальными пациентами
- ✅ Многоязычностью 