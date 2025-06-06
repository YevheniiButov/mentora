# 🧠 RAG System для Dental Academy

Полноценная RAG (Retrieval-Augmented Generation) система с поддержкой пользовательских API ключей, семантическим поиском и мультиязычностью.

## 🎯 Возможности

### ✅ Что реализовано:

1. **🔒 Система шифрования API ключей**
   - Безопасное хранение пользовательских API ключей
   - Поддержка 3 провайдеров: Groq, DeepSeek, OpenAI
   - Автоматическое отслеживание лимитов токенов

2. **🧠 RAG система**
   - Семантический поиск по образовательному контенту
   - Vectorization с `sentence-transformers/all-MiniLM-L6-v2`
   - Умное разбиение текста на чанки с перекрытием
   - Кэширование результатов поиска

3. **💬 AI чат с контекстом**
   - Интеграция RAG контекста в AI ответы
   - Поддержка 8 языков
   - История разговоров с оценками
   - Отображение источников информации

4. **📊 Админ панель**
   - CLI инструменты для управления системой
   - Статистика обработанного контента
   - Управление кэшем и эмбеддингами

5. **🌍 Мультиязычность**
   - Системные промпты на 8 языках
   - Фильтрация контента по языкам
   - Локализация интерфейса

## 🏗️ Архитектура

```
📁 Dental Academy RAG System
├── 🗄️ Модели данных
│   ├── UserAPIKey - зашифрованные API ключи
│   ├── AIConversation - история чатов
│   ├── ContentEmbedding - векторные представления
│   └── RAGCache - кэш поисковых результатов
│
├── 🧠 Основные компоненты  
│   ├── RAGSystem - семантический поиск
│   ├── AIManager - управление AI провайдерами
│   └── EncryptionManager - шифрование ключей
│
├── 🛤️ API маршруты
│   ├── /ai-assistant/ - главная страница чата
│   ├── /ai-assistant/chat - обработка сообщений
│   ├── /ai-assistant/settings - управление ключами
│   ├── /ai-assistant/search - семантический поиск
│   └── /ai-assistant/statistics - статистика
│
└── 🖥️ CLI инструменты
    └── manage_rag.py - админ команды
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Применение миграций

```bash
flask db upgrade
```

### 3. Инициализация RAG системы

```bash
python manage_rag.py init-db
```

### 4. Обработка контента

```bash
# Обработать весь контент
python manage_rag.py process-content --language en

# Обработать только уроки
python manage_rag.py process-content --content-type lessons

# Посмотреть статистику
python manage_rag.py stats
```

### 5. Настройка AI провайдера

1. Перейдите в `/en/ai-assistant/settings`
2. Добавьте API ключ для одного из провайдеров:
   - **Groq**: Бесплатно 10k токенов/день
   - **DeepSeek**: Бесплатно 10k токенов/день  
   - **OpenAI**: Платный сервис

## 📚 Поддерживаемые провайдеры

| Провайдер | Модели | Лимиты | Статус |
|-----------|--------|--------|--------|
| **Groq** | llama-3.1-8b-instant, llama-3.1-70b-versatile | 10k токенов/день | ✅ Бесплатно |
| **DeepSeek** | deepseek-chat, deepseek-coder | 10k токенов/день | ✅ Бесплатно |
| **OpenAI** | gpt-4o-mini, gpt-4o, gpt-3.5-turbo | По тарифу | 💰 Платно |

## 🔧 CLI команды

### Управление контентом

```bash
# Обработать весь контент для создания эмбеддингов
python manage_rag.py process-content --language ru --batch-size 5

# Обработать только определенный тип
python manage_rag.py process-content --content-type lessons

# Показать статистику
python manage_rag.py stats --language en
```

### Семантический поиск

```bash
# Поиск по контенту
python manage_rag.py search "dental anatomy" --language en --limit 3

# Генерация RAG контекста
python manage_rag.py generate-context --query "What is periodontal disease?"
```

### Управление кэшем

```bash
# Очистить просроченный кэш
python manage_rag.py clear-cache --expired-only

# Полная очистка кэша
python manage_rag.py clear-cache

# Удалить эмбеддинги
python manage_rag.py clear-embeddings --language en
```

### Тестирование провайдеров

```bash
# Список доступных провайдеров
python manage_rag.py list-providers

# Тест API ключа
python manage_rag.py test-provider groq "gsk_..."
```

## 📊 Мониторинг и статистика

### Веб-интерфейс

- **AI настройки**: `/en/ai-assistant/settings`
- **Статистика**: `/en/ai-assistant/statistics`
- **История чатов**: Автоматически в интерфейсе

### CLI мониторинг

```bash
# Общая статистика
python manage_rag.py stats

# Проверка конкретного языка
python manage_rag.py stats --language ru
```

## 🛡️ Безопасность

### Шифрование API ключей

1. **Автоматическое шифрование**: Все API ключи шифруются перед сохранением
2. **Ключ шифрования**: Генерируется автоматически и сохраняется в `ENCRYPTION_KEY`
3. **Дневные лимиты**: Автоматическое отслеживание использования токенов

### Рекомендации

```bash
# Установить ключ шифрования в production
export ENCRYPTION_KEY="your-encryption-key-here"

# Регулярная очистка кэша
python manage_rag.py clear-cache --expired-only
```

## 🌍 Поддерживаемые языки

| Код | Язык | Системный промпт | RAG поиск |
|-----|------|------------------|-----------|
| `en` | English | ✅ | ✅ |
| `ru` | Русский | ✅ | ✅ |
| `nl` | Nederlands | ✅ | ✅ |
| `es` | Español | ✅ | ✅ |
| `pt` | Português | ✅ | ✅ |
| `tr` | Türkçe | ✅ | ✅ |
| `uk` | Українська | ✅ | ✅ |
| `fa` | فارسی | ✅ | ✅ |

## 🔍 Как работает RAG

### 1. Обработка контента

```python
# Текст разбивается на чанки
chunks = rag_system.chunk_text(lesson.content, lesson.title)

# Создаются векторные представления
embedding = model.encode(chunk_text)

# Сохраняются в базе данных
ContentEmbedding(content_type='lesson', embedding_vector=embedding.tolist())
```

### 2. Семантический поиск

```python
# Векторизация запроса
query_embedding = model.encode(user_query)

# Поиск похожих векторов
similarity = cosine_similarity([query_embedding], stored_embeddings)

# Фильтрация и ранжирование
results = filter_and_rank(similarity, threshold=0.3)
```

### 3. Генерация контекста

```python
# Сборка релевантного контекста
context = "\n\n---\n\n".join([result['text'] for result in results])

# Отправка в AI с системным промптом
system_prompt += f"\n\nКонтекст:\n{context}"
ai_response = ai_client.chat.completions.create(...)
```

## 📈 Производительность

### Рекомендации по оптимизации

1. **Размер батча**: 10-20 для обработки контента
2. **Кэширование**: TTL 24 часа для RAG запросов  
3. **Лимиты поиска**: Максимум 20 результатов
4. **Чанки**: 512 символов с перекрытием 50

### Мониторинг производительности

```bash
# Проверить покрытие контента
python manage_rag.py stats

# Очистить неэффективный кэш
python manage_rag.py clear-cache --expired-only
```

## ⚠️ Устранение неполадок

### Частые проблемы

1. **Модель не загружается**
   ```bash
   # Убедитесь что установлены зависимости
   pip install sentence-transformers torch
   ```

2. **API ключ не работает**
   ```bash
   # Протестируйте ключ
   python manage_rag.py test-provider groq "your-key"
   ```

3. **Нет результатов поиска**
   ```bash
   # Обработайте контент заново  
   python manage_rag.py process-content --language en
   ```

4. **Ошибки шифрования**
   ```bash
   # Установите переменную среды
   export ENCRYPTION_KEY="your-key"
   ```

### Логи и отладка

```python
# Включить детальное логирование
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Следующие шаги

### Планируемые улучшения

1. **🎯 Персонализация**
   - Адаптивный поиск на основе прогресса пользователя
   - Рекомендации по темам для изучения

2. **⚡ Производительность**
   - Асинхронная обработка контента
   - Векторная база данных (ChromaDB/Pinecone)

3. **🤖 Расширенный AI**
   - Поддержка новых провайдеров
   - Fine-tuning под стоматологический контент

4. **📊 Аналитика**
   - Метрики эффективности RAG
   - A/B тестирование ответов

### Интеграция с экосистемой

- **LangChain**: Для продвинутых RAG пайплайнов
- **Llamaindex**: Для индексации больших объемов данных
- **Streamlit**: Для админ панели с визуализацией

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи приложения
2. Запустите диагностику: `python manage_rag.py stats`
3. Проверьте CLI команды: `python manage_rag.py --help`

---

**🎉 RAG система успешно интегрирована в Dental Academy!**

Система готова к использованию и предоставляет студентам умного AI помощника с доступом к образовательному контенту. 