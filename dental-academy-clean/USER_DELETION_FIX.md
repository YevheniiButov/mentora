# 🔧 Исправление ошибки удаления пользователя

## 🚨 **Проблема:**
```
(psycopg2.errors.ForeignKeyViolation) update or delete on table "user" violates foreign key constraint "registration_visitors_user_id_fkey" on table "registration_visitors"
```

**Причина:** В таблице `registration_visitors` есть записи, которые ссылаются на пользователя с id=70, поэтому его нельзя удалить напрямую.

## ✅ **Решения:**

### **1. Немедленное решение - Безопасное удаление**

Используйте скрипт `delete_user_safely.py` для удаления пользователя с очисткой связанных записей:

```bash
# Показать пользователей с данными регистрации
python3 delete_user_safely.py list

# Удалить конкретного пользователя
python3 delete_user_safely.py 70
```

**Что делает скрипт:**
1. ✅ Находит все записи в `registration_visitors` с `user_id = 70`
2. ✅ Удаляет эти записи
3. ✅ Удаляет самого пользователя
4. ✅ Сохраняет изменения в базе данных

### **2. Долгосрочное решение - Каскадное удаление**

Настройте автоматическое каскадное удаление для предотвращения подобных ошибок в будущем:

```bash
# Настроить каскадное удаление
python3 fix_user_deletion_constraints.py

# Протестировать каскадное удаление
python3 fix_user_deletion_constraints.py test
```

**Что делает скрипт:**
1. ✅ Удаляет старое ограничение внешнего ключа
2. ✅ Создает новое ограничение с `ON DELETE CASCADE`
3. ✅ Применяет ко всем таблицам с внешними ключами на `user.id`
4. ✅ Тестирует работу каскадного удаления

## 📊 **Структура связи:**

```
user (id) 
  ↓
registration_visitors (user_id) ← Ссылается на user.id
```

**До исправления:**
- При удалении пользователя → Ошибка ForeignKeyViolation
- Нужно вручную удалять связанные записи

**После исправления:**
- При удалении пользователя → Автоматически удаляются все связанные записи
- Никаких дополнительных действий не требуется

## 🔍 **Проверка:**

После настройки каскадного удаления можно проверить ограничения:

```sql
-- Проверить ограничения внешних ключей
SELECT 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    tc.constraint_name
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' 
AND ccu.table_name = 'user'
AND ccu.column_name = 'id';
```

## ⚠️ **Важно:**

1. **Резервное копирование:** Всегда делайте бэкап перед массовыми изменениями
2. **Тестирование:** Протестируйте каскадное удаление на тестовых данных
3. **Мониторинг:** Следите за логами после применения изменений

## 🎯 **Результат:**

- ✅ Пользователь ID 70 будет удален безопасно
- ✅ Все связанные записи будут очищены
- ✅ В будущем удаление пользователей будет работать автоматически
- ✅ Никаких ошибок ForeignKeyViolation больше не будет
