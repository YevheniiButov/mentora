# 💊 Интерактивные Фармацевтические Инструменты

## 📋 Обзор

В разделе "Interacties & Contraindicaties" добавлены интерактивные инструменты для проверки лекарственных взаимодействий, которые помогают студентам-фармацевтам практиковать навыки оценки совместимости препаратов.

## 🔧 Реализованные Инструменты

### 1. Quick Drug Interaction Checker

**Расположение**: Встроен в шаблон `interactive_subtopic.html` для разделов с "interacties" или "contraindicaties" в названии.

**Функциональность**:
- Быстрая проверка взаимодействий между двумя препаратами
- База данных из 8 основных лекарственных взаимодействий
- Цветовая индикация серьезности (MAJOR, MODERATE, MINOR)
- Мгновенный результат без перезагрузки страницы

**Поддерживаемые взаимодействия**:
```javascript
const knownInteractions = {
    'warfarine+ibuprofen': {
        severity: 'MAJOR',
        warning: '⚠️ MAJOR: Verhoogd bloedingsrisico'
    },
    'digoxine+furosemide': {
        severity: 'MAJOR', 
        warning: '⚠️ MAJOR: Digitalis toxiciteit risico'
    },
    'amiodarone+digoxine': {
        severity: 'MAJOR',
        warning: '⚠️ MAJOR: Verhoogde digoxine concentratie'
    },
    'simvastatine+amiodarone': {
        severity: 'MAJOR',
        warning: '⚠️ MAJOR: Verhoogd risico op rhabdomyolyse'
    },
    'metoprolol+verapamil': {
        severity: 'MODERATE',
        warning: '⚠️ MODERATE: Verhoogd risico op bradycardie'
    },
    'aspirine+clopidogrel': {
        severity: 'MAJOR',
        warning: '⚠️ MAJOR: Verhoogd bloedingsrisico'
    },
    'paracetamol+ibuprofen': {
        severity: 'MINOR',
        warning: 'ℹ️ MINOR: Geen klinisch relevante interactie'
    },
    'omeprazol+clopidogrel': {
        severity: 'MODERATE',
        warning: '⚠️ MODERATE: Verminderde effectiviteit clopidogrel'
    }
};
```

### 2. Advanced Drug Interaction Checker

**URL**: `/farmacie/advanced-drug-checker`

**Функциональность**:
- Расширенная база данных лекарственных взаимодействий
- Поиск лекарств с автодополнением
- Детальная информация о механизмах взаимодействий
- Рекомендации по мониторингу и дозировке
- Фильтрация по категориям лекарств

**API Endpoints**:
- `GET /api/search-drugs?q=<query>` - поиск лекарств
- `POST /api/check-interaction` - проверка взаимодействий

## 🎨 Дизайн и UX

### Цветовая схема
- **MAJOR** (Красный): `linear-gradient(135deg, #ff6b6b, #ee5a52)`
- **MODERATE** (Желтый): `linear-gradient(135deg, #ffd43b, #fcc419)`
- **MINOR** (Зеленый): `linear-gradient(135deg, #51cf66, #40c057)`

### Адаптивность
- Responsive дизайн для мобильных устройств
- Оптимизированная сетка для планшетов и десктопов
- Touch-friendly интерфейс

## 🔧 Техническая Реализация

### Файлы
- `templates/learning/interactive_subtopic.html` - основной шаблон с быстрым чекером
- `templates/learning/advanced_drug_checker.html` - расширенный чекер
- `routes/learning_routes.py` - API endpoints
- `routes/__init__.py` - регистрация Blueprint

### JavaScript Функции
```javascript
// Быстрая проверка
function quickInteractionCheck() {
    const drug1 = document.getElementById('drug1').value;
    const drug2 = document.getElementById('drug2').value;
    
    if (!drug1 || !drug2) {
        alert('Vul beide medicijnen in');
        return;
    }
    
    // Логика проверки...
}

// API поиск
async function searchDrugs(query, resultsContainer) {
    const response = await fetch(`/api/search-drugs?q=${encodeURIComponent(query)}`);
    const data = await response.json();
    // Обработка результатов...
}
```

## 📊 База Данных Взаимодействий

### Категории лекарств
1. **Anticoagulantia**: warfarine, acenocoumarol, fenprocoumon
2. **Cardiaca**: digoxine, amiodarone, verapamil, diltiazem
3. **Lipidenverlagers**: simvastatine, atorvastatine, pravastatine
4. **Beta-blokkers**: metoprolol, atenolol, bisoprolol
5. **Antiplaatjesmiddelen**: clopidogrel, aspirine, ticagrelor
6. **NSAIDs**: ibuprofen, diclofenac, naproxen
7. **Protonpompremmers**: omeprazol, pantoprazol, esomeprazol

### Структура данных
```python
drug_interactions = {
    'warfarine': {
        'name': 'Warfarine',
        'category': 'Anticoagulantia',
        'interactions': {
            'ibuprofen': {
                'severity': 'MAJOR',
                'description': 'Verhoogd bloedingsrisico door remming van bloedplaatjesaggregatie',
                'recommendation': 'Vermijd combinatie. Gebruik paracetamol als alternatief.',
                'mechanism': 'Synergistische remming van bloedstolling'
            }
        }
    }
}
```

## 🧪 Тестирование

### Быстрый чекер
- ✅ Все 6 тестовых комбинаций работают корректно
- ✅ Правильная классификация серьезности
- ✅ Корректные предупреждения

### API (требует авторизации)
- ⚠️ CSRF защита активна
- ✅ Структура ответов корректна
- ✅ Обработка ошибок реализована

## 🚀 Использование

### Для студентов
1. Перейдите в раздел "Interacties & Contraindicaties"
2. Найдите интерактивный виджет справа
3. Введите названия двух препаратов
4. Нажмите "Check Interactie"
5. Изучите результат и рекомендации

### Для разработчиков
1. Добавьте новые взаимодействия в `knownInteractions`
2. Расширьте базу данных в `drug_interactions`
3. Обновите категории в `drug_categories`

## 🔮 Планы развития

### Краткосрочные
- [ ] Добавить больше лекарственных взаимодействий
- [ ] Реализовать сохранение истории проверок
- [ ] Добавить экспорт результатов

### Долгосрочные
- [ ] Интеграция с внешними API лекарственных баз
- [ ] Машинное обучение для предсказания взаимодействий
- [ ] Мобильное приложение

## 📝 Примечания

- Все инструменты работают в рамках существующей системы авторизации
- CSRF защита активна для всех POST запросов
- Многоязычная поддержка через систему переводов
- Совместимость с темной/светлой темами

---

**Автор**: AI Assistant  
**Дата**: 2024  
**Версия**: 1.0 