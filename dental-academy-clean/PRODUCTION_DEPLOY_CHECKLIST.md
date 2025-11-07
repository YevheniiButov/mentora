# ✅ Чеклист деплоя на продакшен

## После деплоя выполнить:

```bash
# 1. Проверить состояние
flask db current
flask db heads

# 2. Применить миграции
flask db upgrade

# 3. Проверить результат
flask db current
```

## Если ошибка "Can't locate revision":

```bash
# Автоматическое исправление
python3 scripts/fix_migrations.py --force-sync
flask db upgrade
```

## Проверка через SQL:

```sql
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'user' AND column_name = 'other_study_country';
```

Должно вернуть: `other_study_country`

