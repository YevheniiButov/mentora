# 🛡️ ИНСТРУКЦИЯ ДЛЯ LLM АГЕНТОВ - ЗАЩИТА КАЛЕНДАРЯ

## ⚠️ **ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ ДЛЯ LLM АГЕНТОВ**

**НЕ ИЗМЕНЯЙТЕ КРИТИЧЕСКИЕ ФАЙЛЫ БЕЗ СОГЛАСИЯ!**

---

## 🚫 **ФАЙЛЫ ПОД ЗАЩИТОЙ**

### **Критические файлы (НЕ ИЗМЕНЯТЬ!):**
1. `utils/diagnostic_data_manager.py` - логика загрузки данных диагностики
2. `utils/domain_mapping.py` - маппинг доменов и названий
3. `templates/dashboard/learning_planner_translated.html` - календарь
4. `static/css/lib/fullcalendar.min.css` - стили календаря
5. `static/js/lib/fullcalendar.min.js` - скрипты календаря

### **Критические функции (НЕ ИЗМЕНЯТЬ!):**
- `DiagnosticDataManager.get_user_diagnostic_data()`
- `DiagnosticDataManager._process_domain_data()`
- `generateRealLearningEvents()`
- `get_domain_name()`
- `ALL_BIG_DOMAINS` (это список, не словарь!)

---

## ✅ **ПРОЦЕСС ИЗМЕНЕНИЙ**

### **Перед любыми изменениями:**

1. **Проверьте работоспособность:**
   ```bash
   python3 scripts/verify_calendar_health.py
   ```

2. **Создайте backup:**
   ```bash
   BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
   mkdir -p "$BACKUP_DIR"
   cp utils/diagnostic_data_manager.py "$BACKUP_DIR/"
   cp utils/domain_mapping.py "$BACKUP_DIR/"
   cp templates/dashboard/learning_planner_translated.html "$BACKUP_DIR/"
   ```

3. **Спросите разрешения у пользователя:**
   ```
   "Я планирую изменить [файл]. Это может повлиять на работу календаря. 
   Разрешаете ли вы эти изменения?"
   ```

### **После изменений:**

1. **Запустите проверку:**
   ```bash
   python3 scripts/verify_calendar_health.py
   ```

2. **Если что-то сломалось - восстановите:**
   ```bash
   cp backups/YYYYMMDD_HHMMSS/* .
   ```

---

## 🔍 **ПРОВЕРКА РАБОТОСПОСОБНОСТИ**

### **Команды для быстрой проверки:**

```bash
# Проверка данных диагностики
python3 -c "
from app import app
from utils.diagnostic_data_manager import DiagnosticDataManager
app.app_context().push()
data = DiagnosticDataManager.get_user_diagnostic_data(6)
print(f'Has diagnostic: {data.get(\"has_diagnostic\")}')
print(f'Domains count: {len(data.get(\"domains\", []))}')
"

# Проверка названий доменов
python3 -c "
from utils.domain_mapping import get_domain_name
print(get_domain_name('THER'))
print(get_domain_name('SURG'))
"

# Полная проверка
python3 scripts/verify_calendar_health.py
```

### **Ожидаемые результаты:**
- ✅ `Has diagnostic: True`
- ✅ `Domains count: 28`
- ✅ `Therapeutic Dentistry`
- ✅ `Surgical Dentistry`
- ✅ Все 4 проверки пройдены

---

## 🚨 **СИГНАЛЫ ПРОБЛЕМ**

### **Если видите эти ошибки - НЕ ИЗМЕНЯЙТЕ КОД:**
- `'list' object has no attribute 'items'`
- `'NoneType' and 'float'`
- `No diagnostic data available`
- `Domain not found`
- `Calendar not loading`

### **Если календарь не работает:**
1. Проверьте логи браузера
2. Запустите `python3 scripts/verify_calendar_health.py`
3. Восстановите из backup
4. Перезапустите сервер

---

## 📋 **ЧЕКЛИСТ ПЕРЕД ИЗМЕНЕНИЯМИ**

- [ ] Прочитал эту инструкцию
- [ ] Запустил `python3 scripts/verify_calendar_health.py`
- [ ] Создал backup
- [ ] Получил разрешение пользователя
- [ ] Понимаю последствия изменений
- [ ] Готов восстановить из backup при проблемах

---

## 🆘 **ЭКСТРЕННАЯ ВОССТАНОВЛЕНИЕ**

### **Если календарь сломался:**

1. **Остановите изменения**
2. **Восстановите из последнего backup:**
   ```bash
   cp backups/20250806_151527/* .
   ```
3. **Перезапустите сервер:**
   ```bash
   python3 app.py
   ```
4. **Проверьте работоспособность:**
   ```bash
   python3 scripts/verify_calendar_health.py
   ```

---

## 📞 **ПОДДЕРЖКА**

### **Если нужна помощь:**
1. Проверьте `docs/WORKING_CALENDAR_STATE.md`
2. Запустите скрипт проверки
3. Обратитесь к пользователю с описанием проблемы

---

**ПОМНИТЕ: Лучше не изменить ничего, чем сломать работающий календарь!**

**Создано:** 2025-08-06 15:15:27  
**Статус:** ✅ АКТИВНАЯ ЗАЩИТА 