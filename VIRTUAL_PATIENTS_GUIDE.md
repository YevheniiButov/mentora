# 🦷 Система виртуальных пациентов - Краткое руководство

## 🎯 Что добавлено

### ✅ Полная система виртуальных пациентов
- **Интерактивные сценарии** с разветвленными диалогами
- **Система оценки** с баллами и обратной связью
- **Отслеживание прогресса** и детальная аналитика
- **Админ панель** для управления сценариями

### 📁 Новые файлы
- `models.py` - Модели VirtualPatientScenario и VirtualPatientAttempt
- `routes/virtual_patient_routes.py` - Роуты для виртуальных пациентов
- `templates/virtual_patient/` - Шаблоны интерфейса
- `static/js/virtual_patient.js` - Интерактивная логика
- `create_sample_virtual_patients.py` - Образцы сценариев

## 🚀 Быстрый старт

```bash
# 1. Создать образцы
python create_sample_virtual_patients.py

# 2. Запустить приложение
python run.py

# 3. Перейти к виртуальным пациентам
http://localhost:5000/virtual-patients
```

## 📊 Образцы сценариев

### 1. "Боль после пломбирования" (Легкий)
- Пациентка жалуется на боль после установки пломбы
- Обучает базовым навыкам диагностики

### 2. "Острая боль у пациента с диабетом" (Средний)
- Пациент с диабетом и острой зубной болью
- Учит работе с пациентами с сопутствующими заболеваниями

### 3. "Тревожный пациент с стоматофобией" (Сложный)
- Пациентка с выраженной стоматофобией
- Развивает навыки коммуникации и работы с тревожными пациентами

## 🎮 Как использовать

### Для студентов
1. Войдите в систему
2. Выберите "Virtual Patients" в меню
3. Выберите сценарий
4. Читайте информацию о пациенте
5. Принимайте решения в диалоге
6. Получайте обратную связь

### Для администраторов
1. Перейдите в Админ панель
2. Выберите "Управление виртуальными пациентами"
3. Просматривайте статистику
4. Управляйте публикацией сценариев

## 🎨 Особенности

- **Современный интерфейс** с анимациями
- **Мобильная адаптация**
- **Горячие клавиши** (1-9 для быстрого выбора)
- **Автосохранение** прогресса
- **Детальная аналитика** результатов

---

**🎉 Система готова к использованию!** 