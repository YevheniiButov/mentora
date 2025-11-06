# BIG Domains Setup

## Проблема
Вопросы в базе данных не были привязаны к доменам BIG, из-за чего IRT тестирование завершалось после 1 вопроса.

## Решение
Созданы скрипты для инициализации доменов BIG и привязки существующих вопросов к этим доменам.

## Установка на продакшене

### Шаг 1: Создать домены BIG
```bash
flask create-domains
```

Это создаст **30 доменов BIG** на основе файла `scripts/unified_system/domains_config.json`:

**Теоретические домены (22):**
- PHARMACOLOGY - Farmacologie
- THERAPEUTIC_DENTISTRY - Therapeutische Tandheelkunde
- SURGICAL_DENTISTRY - Chirurgische Tandheelkunde
- PROSTHODONTICS - Prothetische Tandheelkunde
- PEDIATRIC_DENTISTRY - Kindertandheelkunde
- PERIODONTOLOGY - Parodontologie
- ORTHODONTICS - Orthodontie
- PREVENTIVE_DENTISTRY - Preventieve Tandheelkunde
- ANATOMY - Anatomie
- PHYSIOLOGY - Fysiologie
- PATHOLOGY - Pathologie
- RADIOLOGY - Radiologie
- MICROBIOLOGY - Microbiologie
- MATERIALS_SCIENCE - Materiaalkunde
- GENERAL_MEDICINE - Algemene Geneeskunde
- EMERGENCY_MEDICINE - Spoedeisende Geneeskunde
- SYSTEMIC_DISEASES - Systemische Ziekten
- INFECTIOUS_DISEASES - Infectieziekten
- SPECIAL_CASES - Bijzondere Gevallen
- DUTCH_DENTISTRY - Nederlandse Tandheelkunde
- DIAGNOSTICS - Diagnostiek
- ETHICS_NL - Ethiek

**Методологические домены (2):**
- PROFESSIONAL_ETHICS - Professionele Ethiek
- STATISTICS - Statistiek
- RESEARCH_METHOD - Onderzoeksmethoden

**Практические домены (3):**
- TREATMENT_PLANNING - Behandelplanning
- COMMUNICATION - Communicatie
- PRACTICAL_THEORY - Praktische Theorie

**Клинические домены (3):**
- SPECIAL_DIAGNOSTICS - Bijzondere Diagnostiek
- CLINICAL_SKILLS - Klinische Vaardigheden
- PATIENT_MANAGEMENT - Patiëntmanagement

### Шаг 2: Привязать существующие вопросы к доменам
```bash
flask update-domains
```

Это обновит все существующие вопросы, добавив им `big_domain_id` на основе их текстового поля `domain`.

## Проверка

После выполнения обеих команд:

1. **Все домены созданы:**
   ```python
   from models import BIGDomain
   BIGDomain.query.count()  # Должно быть 30
   ```

2. **Вопросы привязаны к доменам:**
   ```python
   from models import Question
   Question.query.filter(Question.big_domain_id != None).count()  # Должно быть ~320
   Question.query.filter_by(big_domain_id=None).count()  # Должно быть 0
   ```

3. **IRT тестирование работает корректно:**
   - Express test: 20-25 вопросов
   - Preliminary test: 50-75 вопросов
   - Readiness test: 100-130 вопросов

## Для будущего

При импорте новых вопросов через `flask import-questions`, они автоматически привяжутся к доменам, если:
1. Домены BIG уже созданы в БД
2. В JSON файле у вопросов есть поле `domain` с правильным кодом (THER, SURG, и т.д.)

## Техническая информация

### Файлы:
- `scripts/create_big_domains.py` - Создание доменов BIG
- `scripts/update_questions_domains.py` - Обновление привязки вопросов
- `commands/import_questions.py` - Импорт вопросов (автоматически привязывает к доменам)

### База данных:
- Таблица: `big_domain`
- Поля: `id`, `code`, `name`, `description`, `weight_percentage`, `is_core`
- Связь: `Question.big_domain_id -> BIGDomain.id`

