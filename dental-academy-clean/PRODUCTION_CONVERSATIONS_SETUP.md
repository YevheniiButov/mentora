# Инструкция по настройке переписок на продакшене

## 🎯 Цель
Очистить все существующие переписки и создать новые в стиле WhatsApp на основе скриншотов.

## 📋 Шаги выполнения

### 1. Подготовка окружения
```bash
# Установить переменные окружения для продакшн базы
export DATABASE_PASSWORD='ваш_пароль_от_продакшн_базы'

# Проверить подключение
echo $DATABASE_PASSWORD
```

### 2. Полная очистка переписок
```bash
# Запустить скрипт очистки
python3 clear_all_production_conversations.py
```

**Что будет удалено:**
- ✅ Все сообщения
- ✅ Все темы
- ✅ Все категории форума
- ✅ Счетчики сообщений пользователей

### 3. Создание новых переписок
```bash
# Запустить скрипт создания
python3 create_whatsapp_style_conversations.py
```

**Что будет создано:**
- ✅ 11 пользователей из скриншотов
- ✅ 3 темы с голландскими сообщениями
- ✅ Реалистичные временные метки
- ✅ Переписки в стиле WhatsApp

## 📱 Создаваемые переписки

### 1. "Collega Chat - Taal certificaten"
**Участники:** Liliam, Ümit Isiklar, Bahar Yıldız, Drs. B. De lange
**Тема:** Обсуждение языковых сертификатов и признания дипломов

**Ключевые сообщения:**
- "Goedemiddag collega's heeft iemand material voor lezen exam van BGB academy?"
- "Welke niveau taal certificaat moet ik hebben? Engels en Nederlands."
- "B2 lezen voor Engels ook heb jij nodig"
- "C1 Nederlands"

### 2. "AKV Tandartsen - BIG Registratie"
**Участники:** Karlien Bruwer, Pelin Babayigit, Rinsy, Yuliya Termonia, Rami
**Тема:** Информация о BIG регистрации и рабочих процессах

**Ключевые сообщения:**
- "heeft iemand informatie over het proces van een tijdelijk 'onofficiële' BIG registratie?"
- "Kan ik hier meer over leren, alstublieft?"
- "Zeer geinteresseerd"
- "Hallo allemaal is er iemand die het spreken-examen op de Babel School wil doen?"

### 3. "BGB Examen Materialen"
**Участники:** Shiva, Ümit Isiklar
**Тема:** Обмен материалами и опытом для BGB экзаменов

**Ключевые сообщения:**
- "Heeft iemand van mijn vrienden onlangs het BGB-examen gedaan?"
- "Betekent het 4.1 mondeling?"

## 👥 Создаваемые пользователи

| Имя | Email | Телефон | Аватар |
|-----|-------|---------|--------|
| Liliam | liliam@example.com | +31 6 21657736 | L (синий) |
| Ümit Isiklar | umit@example.com | +32 485 82 22 30 | Ü (зеленый) |
| Bahar Yıldız | bahar@example.com | +31 6 85293141 | B (фиолетовый) |
| Drs. B. De lange | dr.bdelange@example.com | +31 6 38699969 | D (синий) |
| Viktoriia | viktoriia@example.com | +31 6 15403678 | V (розовый) |
| Shiva | shiva@example.com | +31 6 28130004 | S (оранжевый) |
| Karlien Bruwer | karlien@example.com | +27 60 996 6634 | K (розовый) |
| Pelin Babayigit | pelin@example.com | +90 536 202 01 | P (синий) |
| Rinsy | rinsy@example.com | +91 85900 24133 | R (фиолетовый) |
| Yuliya Termonia | yuliya@example.com | +32 456 18 65 74 | Y (зеленый) |
| Rami | rami@example.com | +31 6 87917954 | R (красный) |

## ⚠️ Важные замечания

1. **Бэкап:** Скрипт очистки удаляет ВСЕ переписки безвозвратно
2. **Пароли:** Все созданные пользователи имеют временный пароль `hashed_password_123`
3. **Время:** Временные метки генерируются случайно в пределах последних 30 дней
4. **Язык:** Все сообщения на голландском языке, как в оригинальных скриншотах

## 🔧 Устранение проблем

### Ошибка подключения к базе
```bash
# Проверить переменные окружения
echo $DATABASE_HOST
echo $DATABASE_NAME
echo $DATABASE_USER
echo $DATABASE_PASSWORD

# Установить недостающие
export DATABASE_HOST='dpg-d0t3qvh2g6b8s7i1q1kg-a.oregon-postgres.render.com'
export DATABASE_NAME='mentora_production'
export DATABASE_USER='mentora_user'
```

### Ошибка прав доступа
- Убедитесь, что пользователь базы данных имеет права на удаление и создание записей
- Проверьте SSL соединение (sslmode='require')

### Скрипт не работает
- Проверьте версию Python (требуется 3.6+)
- Установите зависимости: `pip install psycopg2-binary`

## ✅ Проверка результата

После выполнения скриптов проверьте:

1. **Количество сообщений:** Должно быть около 20-30 новых сообщений
2. **Количество тем:** Должно быть 3 новые темы
3. **Количество пользователей:** Должно быть 11 новых пользователей
4. **Язык сообщений:** Все сообщения на голландском
5. **Временные метки:** Разбросаны по последним 30 дням

## 🎉 Результат

После выполнения всех шагов у вас будет:
- ✅ Чистая база данных без старых переписок
- ✅ Новые переписки в стиле WhatsApp
- ✅ Голландские сообщения как в скриншотах
- ✅ Реалистичные временные метки
- ✅ Разнообразные участники с аватарами
