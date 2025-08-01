# 🦷 Mentora - Clean Version

## 📋 Описание
Это **чистая версия** проекта Mentora, содержащая только критически важные файлы для работы основного функционала.

## 🎯 Что включено
- ✅ **Основные шаблоны**: base.html, index.html, learning/*, auth/*, tests/*, virtual_patient/*
- ✅ **Критические роуты**: main, auth, dashboard, learning, tests, admin, virtual_patient
- ✅ **Основные модели БД**: User, LearningPath, Subject, Module, Lesson, UserProgress, VirtualPatientScenario
- ✅ **Виртуальные пациенты**: интерактивные клинические сценарии
- ✅ **Необходимые статические файлы**: только используемые CSS/JS
- ✅ **Система тем**: работающая смена темы light/dark
- ✅ **Мобильная поддержка**: адаптивные шаблоны
- ✅ **Минимальные зависимости**: только нужные Python пакеты

## 🚫 Что убрано
- ❌ **Редактор контента**: content_editor, visual_builder, grapesjs
- ❌ **Форум**: forum routes и модели
- ❌ **AI функции**: ai_routes, embedding, rag система
- ❌ **Геймификация**: achievements, stats, leaderboards  
- ❌ **Аналитика**: детальная analytics система
- ❌ **Дублирующие файлы**: backup/, css_backup/, устаревшие стили
- ❌ **Сложные утилиты**: template_parser, deployer, advanced редакторы

## 📊 Результат оптимизации
| Метрика | Оригинал | Чистая версия | Экономия |
|---------|----------|---------------|----------|
| Файлы проекта | ~2000+ | ~150 | **92%** |
| CSS файлы | ~80 | ~10 | **88%** |
| JS файлы | ~120 | ~8 | **93%** |
| Модели БД | 40+ | 8 | **80%** |
| Routes файлы | 25+ | 6 | **76%** |
| Python зависимости | 71 | ~25 | **65%** |

## 🏗️ Структура проекта

```
dental-academy-clean/
├── app.py                      # Основное приложение
├── models.py                   # Критические модели БД
├── requirements.txt            # Минимальные зависимости
├── extensions.py               # Flask расширения
├── 
├── routes/                     # Основные роуты
│   ├── main_routes.py          # Главная страница
│   ├── auth_routes.py          # Аутентификация  
│   ├── dashboard_routes.py     # Дашборд обучения
│   ├── learning_map_routes.py  # Карта обучения
│   ├── tests_routes.py         # Тестирование
│   └── admin_routes.py         # Административная панель
│
├── templates/                  # Основные шаблоны
│   ├── base.html              # Базовый шаблон
│   ├── index.html             # Главная страница
│   ├── auth/
│   │   ├── login.html         # Страница входа
│   │   └── register.html      # Регистрация
│   ├── learning/
│   │   ├── dashboard.html     # Дашборд обучения
│   │   └── lesson.html        # Страница урока
│   ├── tests/
│   │   └── setup.html         # Настройка тестов
│   └── includes/
│       ├── _header.html       # Шапка сайта
│       └── _footer.html       # Подвал
│
├── static/
│   ├── css/                   # Критические стили
│   │   ├── themes/themes.css  # Система тем
│   │   ├── main.css          # Основные стили
│   │   ├── universal-styles.css # Универсальные стили
│   │   └── pages/            # Стили страниц
│   │       ├── learning_map.css
│   │       └── learning_dashboard.css
│   │
│   ├── js/                   # Критические скрипты
│   │   ├── theme-controller.js # Контроллер тем
│   │   ├── universal-scripts.js # Универсальные скрипты
│   │   ├── modern_flash_messages.js # Flash сообщения
│   │   └── mobile/
│   │       └── mobile-app.js  # Мобильная версия
│   │
│   └── images/               # Основные изображения
│       ├── logo.png          # Логотип
│       └── icons/            # Иконки интерфейса
│
├── utils/                    # Вспомогательные утилиты
│   ├── mobile_detection.py   # Определение мобильных устройств
│   └── unified_stats.py      # Базовая статистика
│
└── translations_modules/     # Система переводов
    ├── app.py               # Основные переводы
    ├── auth.py             # Переводы аутентификации
    └── learning.py         # Переводы обучения
```

## 🚀 Быстрый запуск

```bash
# 1. Перейти в папку проекта
cd dental-academy-clean/

# 2. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Настроить базу данных
flask db upgrade

# 5. Создать администратора
flask create-admin

# 6. Создать образцы виртуальных пациентов (опционально)
python create_sample_virtual_patients.py

# 7. Запустить проект
python app.py
```

## ✨ Основной функционал
- 🏠 **Главная страница** с информацией о платформе
- 🔐 **Аутентификация** (вход/регистрация/выход)
- 📊 **Дашборд обучения** с прогрессом пользователя
- 🗺️ **Карта обучения** с модулями и уроками
- 📝 **Система тестов** с вопросами и результатами
- 🦷 **Виртуальные пациенты** для отработки клинических навыков
- ⚙️ **Админ панель** для управления контентом
- 🎨 **Переключение тем** (светлая/темная)
- 📱 **Мобильная адаптация** для всех экранов
- 🌍 **Мультиязычность** (9 языков)

## 🎯 Идеально подходит для:
- 🚀 **MVP версии** проекта
- 🧪 **Тестирования** основного функционала  
- 📚 **Изучения** архитектуры Flask приложений
- 🔧 **Разработки** новых функций на чистой базе
- 📦 **Деплоймента** с минимальными ресурсами

## 💡 Следующие шаги
После развертывания чистой версии можно постепенно добавлять:
1. **Расширенные тесты** и аналитику
2. **AI ассистента** для помощи в обучении
3. **Виртуальных пациентов** для практики
4. **Форум** для общения студентов
5. **Редактор контента** для создания уроков
6. **Геймификацию** с достижениями и рейтингами

## 🦷 Виртуальные пациенты

Система виртуальных пациентов позволяет студентам отрабатывать клинические навыки на интерактивных сценариях:

### 📋 Возможности
- **Интерактивные диалоги** с виртуальными пациентами
- **Сценарии разной сложности**: от простых до сложных случаев
- **Система оценки**: баллы за правильные решения
- **Отслеживание прогресса**: статистика попыток и результатов
- **Категории сценариев**: реставрация, эндодонтия, коммуникация и др.

### 🎮 Процесс прохождения
1. Выбор сценария из каталога
2. Знакомство с информацией о пациенте
3. Пошаговое принятие клинических решений
4. Получение обратной связи за каждое действие
5. Просмотр результатов с рекомендациями

### 📊 Образцы сценариев
После запуска скрипта `create_sample_virtual_patients.py` будут созданы:
- **"Боль после пломбирования"** (легкий уровень)
- **"Острая боль у пациента с диабетом"** (средний уровень)  
- **"Тревожный пациент с стоматофобией"** (сложный уровень)

---

**🎉 Mentora Clean - максимальный функционал с минимальной сложностью!** # Force deploy Thu Jul 31 04:47:23 CEST 2025
