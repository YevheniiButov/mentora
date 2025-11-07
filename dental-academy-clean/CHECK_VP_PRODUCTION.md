# Проверка виртуальных пациентов на продакшене

## Способ 1: Через Flask Shell (рекомендуется)

На продакшене (Render/Heroku) подключитесь к shell и выполните:

```bash
# Если на Render
render run:shell python

# Или если есть доступ к Flask CLI
flask shell
```

Затем в Python shell:

```python
from models import VirtualPatientScenario, db

# Подсчет всех
total = VirtualPatientScenario.query.count()
print(f"Всего сценариев: {total}")

# Опубликованных
published = VirtualPatientScenario.query.filter_by(is_published=True).count()
print(f"Опубликованных: {published}")

# Список всех
scenarios = VirtualPatientScenario.query.all()
for s in scenarios:
    print(f"ID: {s.id} | {s.title} | specialty: {s.specialty} | published: {s.is_published}")
```

---

## Способ 2: Через SQL запрос (PostgreSQL)

Если у вас есть прямой доступ к базе данных PostgreSQL:

```sql
-- Общее количество
SELECT COUNT(*) FROM virtual_patient_scenario;

-- Опубликованные
SELECT COUNT(*) FROM virtual_patient_scenario WHERE is_published = true;

-- Список всех
SELECT id, title, specialty, difficulty, is_published 
FROM virtual_patient_scenario 
ORDER BY id;

-- По специальностям
SELECT specialty, COUNT(*) as count 
FROM virtual_patient_scenario 
GROUP BY specialty;

-- По сложности
SELECT difficulty, COUNT(*) as count 
FROM virtual_patient_scenario 
GROUP BY difficulty;
```

---

## Способ 3: Через скрипт

Загрузите скрипт `scripts/check_vp_scenarios.py` на сервер и выполните:

```bash
python scripts/check_vp_scenarios.py
```

Скрипт покажет:
- Общее количество
- Опубликованные/неопубликованные
- Группировку по специальностям
- Группировку по сложности
- Список всех сценариев

---

## Способ 4: Через админ панель

Если у вас есть доступ к админ панели:

1. Зайдите на `/admin/virtual-patients`
2. Там будет список всех виртуальных пациентов со статистикой

---

## Способ 5: Через API (если доступен)

```bash
curl https://bigmentor.nl/api/virtual-patients/scenarios
```

Или через браузер:
```
https://bigmentor.nl/api/virtual-patients/scenarios
```

---

## Быстрая проверка через браузер

1. Зайдите на `/admin/virtual-patients` (требуется админ доступ)
2. Или на `/virtual-patients` (если есть публичный список)

