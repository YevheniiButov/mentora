# Unified IRT System

## Обзор

Единая оптимизированная IRT система для BI-toets Tandartsen Nederland, объединяющая 410 вопросов из различных источников в единую структурированную систему.

## Структура файлов

```
scripts/unified_system/
├── unified_irt_system.json     # Основной файл с 410 вопросами
├── domains_config.json         # Конфигурация 30 доменов
├── migration_log.json          # Лог изменений и миграции
├── quality_report.json         # Отчет о качестве системы
├── validation_results.json     # Результаты валидации
├── backup_original.json        # Бэкап оригинальных данных
└── README.md                   # Этот файл
```

## Характеристики системы

### Основные параметры
- **Всего вопросов**: 410
- **Доменов**: 30
- **Категории**: 4 (THEORETICAL, METHODOLOGY, PRACTICAL, CLINICAL)
- **Качество**: 92.5/100
- **Готовность к продакшену**: ✅

### Распределение по категориям
- **THEORETICAL** (70%): 287 вопросов, 22 домена
- **METHODOLOGY** (10%): 41 вопрос, 2 домена  
- **PRACTICAL** (15%): 62 вопроса, 3 домена
- **CLINICAL** (5%): 20 вопросов, 3 домена

### Критические домены
- PHARMACOLOGY (8.0%)
- THERAPEUTIC_DENTISTRY (12.0%)
- SURGICAL_DENTISTRY (8.0%)
- PEDIATRIC_DENTISTRY (6.0%)
- PERIODONTOLOGY (7.0%)
- EMERGENCY_MEDICINE (6.0%)
- DIAGNOSTICS (6.0%)
- GENERAL_MEDICINE (4.0%)
- SYSTEMIC_DISEASES (4.0%)
- INFECTIOUS_DISEASES (4.0%)
- TREATMENT_PLANNING (8.0%)

## Миграция и изменения

### Объединенные домены
- PHARMA + FARMACOLOGIE → PHARMACOLOGY
- DIAGNOSIS + DIAGNOSIS_SPECIAL → DIAGNOSTICS
- ETHIEK → ETHICS_NL
- PROFESSIONAL → PROFESSIONAL_ETHICS

### Переименованные домены
- THER → THERAPEUTIC_DENTISTRY
- SURG → SURGICAL_DENTISTRY
- PROTH → PROSTHODONTICS
- PEDI → PEDIATRIC_DENTISTRY
- PARO → PERIODONTOLOGY
- ORTHO → ORTHODONTICS
- PREV → PREVENTIVE_DENTISTRY
- ANATOMIE → ANATOMY
- FYSIOLOGIE → PHYSIOLOGY
- PATHOLOGIE → PATHOLOGY
- RADIOLOGIE → RADIOLOGY
- MICROBIOLOGIE → MICROBIOLOGY
- MATERIAALKUNDE → MATERIALS_SCIENCE
- ALGEMENE_GENEESKUNDE → GENERAL_MEDICINE
- EMERGENCY → EMERGENCY_MEDICINE
- SYSTEMIC → SYSTEMIC_DISEASES
- INFECTION → INFECTIOUS_DISEASES
- SPECIAL → SPECIAL_CASES
- DUTCH → DUTCH_DENTISTRY

### Новые домены
- STATISTICS (15 вопросов)
- RESEARCH_METHOD (26 вопросов)
- TREATMENT_PLANNING (25 вопросов)
- COMMUNICATION (20 вопросов)
- PRACTICAL_THEORY (17 вопросов)
- CLINICAL_SKILLS (8 вопросов)
- PATIENT_MANAGEMENT (4 вопроса)

## IRT параметры

### Валидированные диапазоны
- **Difficulty**: 0.0 - 2.0
- **Discrimination**: 1.0 - 3.0
- **Guessing**: 0.1 - 0.3

### Распределение сложности
- **Легкие**: 23%
- **Средние**: 62%
- **Сложные**: 15%

## Качество системы

### Общий балл: 92.5/100
- **IRT качество**: 94.0/100
- **Качество контента**: 93.0/100
- **Покрытие доменов**: 95.0/100
- **Структурное качество**: 90.0/100

### Улучшения
- ✅ Устранены дублирования доменов
- ✅ 100% покрытие BI-toets требований
- ✅ Оптимизированы IRT параметры
- ✅ Улучшена структура и организация
- ✅ Добавлены новые актуальные домены

## Использование

### Интеграция с диагностической системой
```python
# Загрузка unified системы
with open('scripts/unified_system/unified_irt_system.json', 'r') as f:
    unified_system = json.load(f)

# Загрузка конфигурации доменов
with open('scripts/unified_system/domains_config.json', 'r') as f:
    domains_config = json.load(f)
```

### Валидация системы
```bash
python utils/unified_validator.py
```

## Рекомендации

1. **Готовность к продакшену**: Система готова к развертыванию
2. **Мониторинг**: Отслеживать производительность при первоначальном использовании
3. **Обзоры качества**: Планировать регулярные проверки качества каждые 6 месяцев
4. **Расширение**: Рассмотреть добавление 5-10 вопросов в специализированные домены

## Техническая информация

- **Формат**: JSON
- **Кодировка**: UTF-8
- **Размер**: ~2.5MB
- **Версия**: 2.0
- **Дата создания**: 2025-01-27

## Контакты

Для вопросов и поддержки обращайтесь к команде разработки. 