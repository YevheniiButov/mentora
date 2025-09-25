# 🚀 STAGING ENVIRONMENT SETUP GUIDE

## **Полная настройка staging environment для безопасного развертывания IRT системы**

---

## **📋 ЧТО СОЗДАНО:**

### **1. Основные скрипты:**
- ✅ `setup_staging.py` - настройка staging environment
- ✅ `backup_production.py` - создание бэкапа продакшн БД
- ✅ `safe_migration.py` - безопасная миграция с rollback
- ✅ `monitoring_system.py` - система мониторинга
- ✅ `feature_flags.py` - управление feature flags

### **2. Автоматически создаваемые файлы:**
- ✅ `.env.staging` - конфигурация staging
- ✅ `run_staging.sh` - запуск staging сервера
- ✅ `test_irt_staging.py` - тестирование IRT системы
- ✅ `health_check.py` - проверка здоровья системы
- ✅ `migration_plan.json` - план миграции

---

## **🚀 БЫСТРЫЙ СТАРТ:**

### **Шаг 1: Настройка staging environment**
```bash
python3 setup_staging.py
```

### **Шаг 2: Создание бэкапа продакшн БД**
```bash
python3 backup_production.py
```

### **Шаг 3: Запуск staging сервера**
```bash
./run_staging.sh
```

### **Шаг 4: Тестирование IRT системы**
```bash
./test_irt_staging.py
```

### **Шаг 5: Проверка здоровья системы**
```bash
./health_check.py
```

---

## **🔧 ДЕТАЛЬНАЯ ИНСТРУКЦИЯ:**

### **1. ПОДГОТОВКА STAGING ENVIRONMENT**

#### **A. Запуск настройки:**
```bash
python3 setup_staging.py
```

**Что происходит:**
- Создается `.env.staging` с конфигурацией
- Создается директория `staging/`
- Копируется продакшн БД в staging
- Создаются скрипты для работы

#### **B. Проверка настройки:**
```bash
ls -la staging/
ls -la .env.staging
ls -la run_staging.sh
```

### **2. СОЗДАНИЕ БЭКАПА ПРОДАКШН БД**

#### **A. Автоматический бэкап:**
```bash
python3 backup_production.py
```

**Что происходит:**
- Создается полный бэкап продакшн БД
- Создается копия для staging
- Сохраняются метаданные бэкапа
- Проверяется целостность

#### **B. Ручной бэкап (если нужно):**
```bash
# Для SQLite
cp instance/app.db backups/production_backup_$(date +%Y%m%d_%H%M%S).db

# Для PostgreSQL
pg_dump $DATABASE_URL > backups/production_backup_$(date +%Y%m%d_%H%M%S).sql
```

### **3. ЗАПУСК STAGING СЕРВЕРА**

#### **A. Запуск staging:**
```bash
./run_staging.sh
```

**Что происходит:**
- Загружается staging конфигурация
- Запускается сервер в staging режиме
- Включается debug режим
- Активируются feature flags

#### **B. Проверка работы:**
```bash
curl http://localhost:5000/health
```

### **4. ТЕСТИРОВАНИЕ IRT СИСТЕМЫ**

#### **A. Запуск тестов:**
```bash
./test_irt_staging.py
```

**Что проверяется:**
- Доступность IRT моделей
- Подключение к базе данных
- Работа scipy и numpy
- Целостность данных

#### **B. Ручное тестирование:**
```bash
python3 -c "
from app import app
from models import IRTParameters, DiagnosticSession
print('✅ IRT models imported successfully')
"
```

### **5. МОНИТОРИНГ СИСТЕМЫ**

#### **A. Однократная проверка:**
```bash
./health_check.py
```

#### **B. Непрерывный мониторинг:**
```bash
python3 monitoring_system.py --continuous --interval 60
```

**Что мониторится:**
- Здоровье базы данных
- Доступность IRT моделей
- Производительность системы
- Использование памяти
- API endpoints

---

## **🔄 БЕЗОПАСНАЯ МИГРАЦИЯ:**

### **1. АВТОМАТИЧЕСКАЯ МИГРАЦИЯ:**
```bash
python3 safe_migration.py
```

**Что происходит:**
1. Создается бэкап БД
2. Добавляются IRT модели
3. Запускается миграция специальностей
4. Включаются IRT функции
5. Тестируется система
6. При ошибке - автоматический rollback

### **2. РУЧНАЯ МИГРАЦИЯ (пошагово):**

#### **Шаг 1: Бэкап**
```bash
python3 backup_production.py
```

#### **Шаг 2: Добавление моделей**
```bash
# Проверяем, что модели есть в models.py
grep -n "class IRTParameters" models.py
```

#### **Шаг 3: Миграция специальностей**
```bash
python3 specialty_migration.py
```

#### **Шаг 4: Включение feature flags**
```bash
python3 feature_flags.py --enable-irt
```

#### **Шаг 5: Тестирование**
```bash
./test_irt_staging.py
```

---

## **🎛️ УПРАВЛЕНИЕ FEATURE FLAGS:**

### **1. Просмотр статуса:**
```bash
python3 feature_flags.py --status
```

### **2. Включение IRT системы:**
```bash
python3 feature_flags.py --enable-irt
```

### **3. Включение пилотного режима:**
```bash
python3 feature_flags.py --pilot-mode
```

### **4. Отключение IRT системы:**
```bash
python3 feature_flags.py --disable-irt
```

### **5. Управление отдельными флагами:**
```bash
python3 feature_flags.py --enable irt_dentists
python3 feature_flags.py --disable irt_general_practitioners
```

---

## **📊 МОНИТОРИНГ И ОТЧЕТЫ:**

### **1. Health Reports:**
```bash
# Автоматически создаются в:
ls -la health_report_*.json
```

### **2. Migration Logs:**
```bash
# Автоматически создаются в:
ls -la migration_log_*.json
```

### **3. Backup Metadata:**
```bash
# Автоматически создаются в:
ls -la backups/backup_metadata_*.json
```

---

## **⚠️ БЕЗОПАСНОСТЬ И ОТКАТ:**

### **1. АВТОМАТИЧЕСКИЙ ОТКАТ:**
- При любой ошибке миграции автоматически запускается rollback
- Все изменения откатываются к предыдущему состоянию
- Восстанавливается бэкап БД

### **2. РУЧНОЙ ОТКАТ:**
```bash
# Восстановление из бэкапа
python3 restore_from_backup.py backups/production_backup_YYYYMMDD_HHMMSS.db

# Отключение IRT системы
python3 feature_flags.py --disable-irt
```

### **3. ПРОВЕРКА ЦЕЛОСТНОСТИ:**
```bash
# После каждого шага
./health_check.py
```

---

## **🎯 ПЛАН РАЗВЕРТЫВАНИЯ НА ПРОДАКШЕНЕ:**

### **Этап 1: Подготовка (1 день)**
1. ✅ Настроить staging environment
2. ✅ Создать бэкап продакшн БД
3. ✅ Протестировать все на staging

### **Этап 2: Миграция (1 день)**
1. ✅ Запустить безопасную миграцию
2. ✅ Включить feature flags
3. ✅ Протестировать систему

### **Этап 3: Активация (1 день)**
1. ✅ Включить IRT для стоматологов
2. ✅ Мониторить производительность
3. ✅ Собрать первые метрики

### **Этап 4: Расширение (по мере готовности)**
1. ✅ Включить IRT для врачей общей практики
2. ✅ Активировать калибровку
3. ✅ Включить аналитику

---

## **🚨 ЭКСТРЕННЫЕ СИТУАЦИИ:**

### **1. ПРОБЛЕМЫ С БАЗОЙ ДАННЫХ:**
```bash
# Немедленный откат
python3 restore_from_backup.py [backup_file]
```

### **2. ПРОБЛЕМЫ С ПРОИЗВОДИТЕЛЬНОСТЬЮ:**
```bash
# Отключение IRT системы
python3 feature_flags.py --disable-irt
```

### **3. ОШИБКИ В СИСТЕМЕ:**
```bash
# Проверка здоровья
./health_check.py

# Непрерывный мониторинг
python3 monitoring_system.py --continuous
```

---

## **📞 ПОДДЕРЖКА:**

### **Логи и отчеты:**
- `health_report_*.json` - отчеты о здоровье системы
- `migration_log_*.json` - логи миграции
- `backup_metadata_*.json` - метаданные бэкапов

### **Полезные команды:**
```bash
# Статус системы
python3 feature_flags.py --status

# Проверка здоровья
./health_check.py

# Мониторинг
python3 monitoring_system.py --continuous

# Тестирование
./test_irt_staging.py
```

---

## **🎉 ГОТОВО К РАЗВЕРТЫВАНИЮ!**

**Staging environment настроен и готов к безопасному развертыванию IRT системы на продакшене!**

**Следующий шаг:** Запустить `python3 setup_staging.py` и следовать инструкциям! 🚀
