# Production Deployment Guide - Membership Fields

## 🚨 ВАЖНО: Безопасное развертывание в продакшене

### Проблема с текущей миграцией
Созданная миграция `52664ae226ef_add_membership_fields_to_user_model.py` содержит много изменений, не связанных с полями членства, что может вызвать проблемы в продакшене.

### ✅ Решение: Чистая миграция

Создана чистая миграция `clean_membership_fields_add_membership_fields_to_user_model.py`, которая:
- Добавляет только поля членства
- Безопасна для продакшена
- Не затрагивает существующие данные

## 📋 План развертывания в продакшене

### 1. Подготовка к развертыванию

```bash
# 1. Создать бэкап продакшн БД
pg_dump your_production_db > backup_before_membership.sql

# 2. Проверить текущую версию миграций
flask db current

# 3. Проверить, какие миграции нужно применить
flask db show
```

### 2. Применение миграции

```bash
# Применить только чистую миграцию
flask db upgrade clean_membership_fields
```

### 3. Проверка после развертывания

```sql
-- Проверить, что поля добавлены
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'user' 
AND column_name IN ('membership_type', 'membership_expires', 'member_id', 'qr_code_path');

-- Проверить индекс
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'user' 
AND indexname = 'ix_user_member_id';

-- Проверить данные
SELECT id, email, membership_type, member_id 
FROM "user" 
LIMIT 5;
```

## 🔧 Альтернативный подход: Ручное добавление полей

Если миграции вызывают проблемы, можно добавить поля вручную:

```sql
-- Добавить поля членства
ALTER TABLE "user" ADD COLUMN membership_type VARCHAR(20) DEFAULT 'free';
ALTER TABLE "user" ADD COLUMN membership_expires TIMESTAMP;
ALTER TABLE "user" ADD COLUMN member_id VARCHAR(12);
ALTER TABLE "user" ADD COLUMN qr_code_path VARCHAR(200);

-- Создать индекс
CREATE UNIQUE INDEX ix_user_member_id ON "user" (member_id);

-- Установить значения по умолчанию
UPDATE "user" SET membership_type = 'free' WHERE membership_type IS NULL;

-- Отметить миграцию как выполненную
INSERT INTO alembic_version (version_num) VALUES ('clean_membership_fields');
```

## 🛡️ Безопасность и откат

### План отката
```sql
-- Удалить поля членства (если нужно откатиться)
DROP INDEX IF EXISTS ix_user_member_id;
ALTER TABLE "user" DROP COLUMN IF EXISTS qr_code_path;
ALTER TABLE "user" DROP COLUMN IF EXISTS member_id;
ALTER TABLE "user" DROP COLUMN IF EXISTS membership_expires;
ALTER TABLE "user" DROP COLUMN IF EXISTS membership_type;
```

### Проверка целостности данных
```sql
-- Проверить, что нет пользователей с некорректными данными
SELECT COUNT(*) FROM "user" WHERE membership_type NOT IN ('free', 'premium');
SELECT COUNT(*) FROM "user" WHERE member_id IS NOT NULL AND LENGTH(member_id) != 12;
```

## 📊 Мониторинг после развертывания

### 1. Проверка производительности
```sql
-- Проверить использование индекса
EXPLAIN ANALYZE SELECT * FROM "user" WHERE member_id = 'MNT-12345';
```

### 2. Проверка данных
```sql
-- Статистика по типам членства
SELECT membership_type, COUNT(*) 
FROM "user" 
GROUP BY membership_type;

-- Проверка истечения членства
SELECT COUNT(*) as expired_memberships
FROM "user" 
WHERE membership_type = 'premium' 
AND membership_expires < NOW();
```

## 🚀 Поэтапное развертывание

### Этап 1: Добавление полей
- Добавить поля в БД
- Установить значения по умолчанию
- Создать индексы

### Этап 2: Обновление кода
- Развернуть новую версию приложения
- Проверить работу всех функций

### Этап 3: Активация функций
- Включить платежную систему
- Активировать генерацию QR-кодов
- Убрать ограничения для админов

## ⚠️ Важные замечания

### 1. Совместимость
- Все существующие пользователи получат `membership_type = 'free'`
- Новые поля не влияют на существующую функциональность
- Обратная совместимость сохранена

### 2. Производительность
- Индекс на `member_id` улучшит производительность поиска
- Поля `membership_expires` и `qr_code_path` могут быть NULL

### 3. Безопасность
- `member_id` должен быть уникальным
- Проверка прав доступа остается на уровне приложения

## 📞 Поддержка

При возникновении проблем:
1. Проверить логи приложения
2. Проверить состояние БД
3. При необходимости откатиться к бэкапу
4. Обратиться к команде разработки

## ✅ Чеклист развертывания

- [ ] Создан бэкап БД
- [ ] Проверена текущая версия миграций
- [ ] Применена чистая миграция
- [ ] Проверена целостность данных
- [ ] Протестирована функциональность
- [ ] Настроен мониторинг
- [ ] Документированы изменения

**Дата создания**: 2025-10-02
**Версия**: 1.0
**Статус**: Готово к продакшену



