# 🇳🇱 Голландская система оценки знаний

## Обзор

Голландская система оценки знаний расширяет стандартную систему оценки, добавляя специфичные для Нидерландов категории, уровни компетенции и результаты оценки.

## 🏗️ Архитектура

### Новые поля в AssessmentCategory

```python
# Голландские специфичные поля
is_dutch_specific = db.Column(db.Boolean, default=False)  # Специфично для Нидерландов
dutch_weight = db.Column(db.Float, default=1.0)  # Вес для голландской оценки
critical_for_netherlands = db.Column(db.Boolean, default=False)  # Критично для работы в Нидерландах
name_en = db.Column(db.String(100))  # Английский перевод названия
name_ru = db.Column(db.String(100))  # Русский перевод названия
```

### Новые модели

#### DutchCompetencyLevel
Уровни компетенции для голландской системы оценки:

```python
class DutchCompetencyLevel(db.Model):
    level_name = db.Column(db.String(20), nullable=False)  # insufficient, basic, competent, proficient
    threshold = db.Column(db.Float, nullable=False)  # Пороговое значение для уровня
    description = db.Column(db.Text)  # Описание уровня
    recommendation = db.Column(db.Text)  # Рекомендации для достижения уровня
```

#### DutchAssessmentResult
Результаты голландской оценки знаний:

```python
class DutchAssessmentResult(db.Model):
    # Результаты оценки
    competency_level = db.Column(db.String(20), nullable=False)  # insufficient, basic, competent, proficient
    overall_score = db.Column(db.Float, nullable=False)  # Общий балл
    critical_areas_score = db.Column(db.Float, nullable=False)  # Балл по критическим областям
    
    # Возможности работы
    can_work_supervised = db.Column(db.Boolean, default=False)  # Может работать под надзором
    can_work_independently = db.Column(db.Boolean, default=False)  # Может работать самостоятельно
    
    # Региональная специфика
    regional_focus = db.Column(db.String(20))  # urban, rural
    
    # Сертификация и следующие шаги
    certification_pathway = db.Column(db.Text)  # JSON с путем сертификации
    next_steps = db.Column(db.Text)  # JSON с следующими шагами
    
    # Детальные результаты по категориям
    category_scores = db.Column(db.Text)  # JSON с результатами по категориям
```

## 🎯 Уровни компетенции

### 1. Insufficient (≥0%)
- **Описание**: Недостаточный уровень знаний. Требуется дополнительное обучение.
- **Рекомендация**: Пройти базовый курс и повторить оценку.

### 2. Basic (≥50%)
- **Описание**: Базовый уровень знаний. Может работать под постоянным надзором.
- **Рекомендация**: Продолжить обучение для достижения компетентного уровня.

### 3. Competent (≥70%)
- **Описание**: Компетентный уровень. Может работать под минимальным надзором.
- **Рекомендация**: Фокус на практических навыках и специализации.

### 4. Proficient (≥85%)
- **Описание**: Высокий уровень компетенции. Может работать самостоятельно.
- **Рекомендация**: Поддержание высокого уровня через непрерывное обучение.

## 📚 Голландские категории

### 1. Nederlandse Tandheelkunde (Голландская стоматология)
- **Вес**: 1.5
- **Критично**: Да
- **Описание**: Основы стоматологической практики в Нидерландах

### 2. Wetgeving en Regulering (Законодательство и регулирование)
- **Вес**: 1.3
- **Критично**: Да
- **Описание**: Голландские законы и правила стоматологической практики

### 3. Patiëntenzorg (Уход за пациентами)
- **Вес**: 1.2
- **Критично**: Да
- **Описание**: Стандарты ухода за пациентами в голландской практике

### 4. Communicatie (Коммуникация)
- **Вес**: 1.1
- **Критично**: Да
- **Описание**: Коммуникация с пациентами и коллегами на голландском языке

### 5. Klinische Procedures (Клинические процедуры)
- **Вес**: 1.0
- **Критично**: Нет
- **Описание**: Стандартные клинические процедуры в Нидерландах

## 💻 Использование

### Создание голландской оценки

```python
from models import DutchAssessmentResult, DutchCompetencyLevel

def create_dutch_assessment(user_id, attempt_id, scores):
    # Определяем уровень компетенции
    overall_score = calculate_overall_score(scores)
    competency_level = determine_competency_level(overall_score)
    
    # Создаем результат
    result = DutchAssessmentResult(
        user_id=user_id,
        attempt_id=attempt_id,
        competency_level=competency_level,
        overall_score=overall_score,
        critical_areas_score=calculate_critical_score(scores),
        can_work_supervised=competency_level in ['basic', 'competent', 'proficient'],
        can_work_independently=competency_level == 'proficient',
        regional_focus='urban',  # или 'rural'
        category_scores=json.dumps(scores)
    )
    
    db.session.add(result)
    db.session.commit()
    return result
```

### Определение уровня компетенции

```python
def determine_competency_level(score):
    levels = DutchCompetencyLevel.query.order_by(DutchCompetencyLevel.threshold.desc()).all()
    
    for level in levels:
        if score >= level.threshold:
            return level.level_name
    
    return 'insufficient'
```

### Получение рекомендаций

```python
def get_dutch_recommendations(result):
    level = DutchCompetencyLevel.query.filter_by(level_name=result.competency_level).first()
    
    recommendations = {
        'level_description': level.description,
        'recommendation': level.recommendation,
        'can_work_supervised': result.can_work_supervised,
        'can_work_independently': result.can_work_independently,
        'next_steps': result.get_next_steps(),
        'certification_pathway': result.get_certification_pathway()
    }
    
    return recommendations
```

## 🔧 Инициализация

Для инициализации голландской системы выполните:

```bash
python scripts/init_dutch_assessment.py
```

Этот скрипт создаст:
- 4 уровня компетенции
- 5 голландских категорий оценки
- Настроит веса и критические области

## 📊 API Endpoints

### Получение голландских результатов

```python
@app.route('/api/dutch-assessment/<int:user_id>')
def get_dutch_assessment(user_id):
    results = DutchAssessmentResult.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': r.id,
        'competency_level': r.competency_level,
        'overall_score': r.overall_score,
        'critical_areas_score': r.critical_areas_score,
        'can_work_supervised': r.can_work_supervised,
        'can_work_independently': r.can_work_independently,
        'created_at': r.created_at.isoformat()
    } for r in results])
```

### Создание голландской оценки

```python
@app.route('/api/dutch-assessment', methods=['POST'])
def create_dutch_assessment_api():
    data = request.get_json()
    
    result = create_dutch_assessment(
        user_id=data['user_id'],
        attempt_id=data['attempt_id'],
        scores=data['scores']
    )
    
    return jsonify({
        'id': result.id,
        'competency_level': result.competency_level,
        'overall_score': result.overall_score
    })
```

## 🎨 Frontend интеграция

### Отображение результатов

```javascript
function displayDutchResults(result) {
    const levelColors = {
        'insufficient': '#ef4444',
        'basic': '#f59e0b',
        'competent': '#3b82f6',
        'proficient': '#22c55e'
    };
    
    return `
        <div class="dutch-result" style="border-left: 4px solid ${levelColors[result.competency_level]}">
            <h3>Уровень компетенции: ${result.competency_level}</h3>
            <p>Общий балл: ${result.overall_score}%</p>
            <p>Критические области: ${result.critical_areas_score}%</p>
            <p>Может работать под надзором: ${result.can_work_supervised ? 'Да' : 'Нет'}</p>
            <p>Может работать самостоятельно: ${result.can_work_independently ? 'Да' : 'Нет'}</p>
        </div>
    `;
}
```

## 🔍 Мониторинг и аналитика

### Статистика по уровням

```python
def get_dutch_statistics():
    stats = db.session.query(
        DutchAssessmentResult.competency_level,
        db.func.count(DutchAssessmentResult.id).label('count')
    ).group_by(DutchAssessmentResult.competency_level).all()
    
    return {level: count for level, count in stats}
```

### Тренды по времени

```python
def get_dutch_trends():
    results = db.session.query(
        db.func.date(DutchAssessmentResult.created_at).label('date'),
        db.func.avg(DutchAssessmentResult.overall_score).label('avg_score')
    ).group_by(db.func.date(DutchAssessmentResult.created_at)).all()
    
    return [{'date': date, 'avg_score': avg_score} for date, avg_score in results]
```

## 🚀 Будущие улучшения

1. **Интеграция с голландскими регуляторными органами**
2. **Автоматическая генерация сертификатов**
3. **Интеграция с системами трудоустройства**
4. **Многоязычная поддержка для всех голландских регионов**
5. **AI-ассистент для персонализации обучения**

## 📞 Поддержка

Для вопросов по голландской системе оценки обращайтесь к команде разработки или создайте issue в репозитории проекта. 