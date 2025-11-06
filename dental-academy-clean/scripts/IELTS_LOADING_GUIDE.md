# IELTS Passage Loading Guide

## Шаги для создания и загрузки IELTS Reading Passage

### Шаг 1: Генерация текста

Используйте промпт для генерации текста:

```python
from utils.ielts_generator import generate_ielts_prompt

prompt = generate_ielts_prompt(
    topic="Ancient Architecture",
    word_count=450,
    band_level=7.0,
    num_paragraphs=3
)

print(prompt)
```

Или используйте шаблон:

```python
from utils.ielts_prompt_template import format_ielts_prompt

prompt = format_ielts_prompt(
    topic="Climate Change",
    word_count=500,
    band_level=7.5,
    num_paragraphs=4
)
```

**Скопируйте промпт в ChatGPT/Claude и получите сгенерированный текст.**

### Шаг 2: Генерация вопросов

После получения текста, используйте промпт для генерации вопросов:

```python
from utils.ielts_generator import generate_questions_prompt

# Вставьте сгенерированный текст
passage_text = """
Paragraph A
Your generated text here...
"""

prompt = generate_questions_prompt(
    passage_text=passage_text,
    num_multiple_choice=5,
    num_true_false_ng=3,
    num_fill_blank=4
)

print(prompt)
```

Или используйте шаблон:

```python
from utils.ielts_prompt_template import format_questions_prompt

prompt = format_questions_prompt(
    passage_text=passage_text,
    num_multiple_choice=5,
    num_true_false_ng=3,
    num_fill_blank=4
)
```

**Скопируйте промпт в ChatGPT/Claude и получите JSON с вопросами.**

### Шаг 3: Загрузка в базу данных

#### Вариант 1: Использование скрипта напрямую

```python
from scripts.load_ielts_passage import load_passage_with_questions

# Вставьте сгенерированные данные
passage_text = """
Paragraph A
Your generated text here...

Paragraph B
More text...

Paragraph C
Final text...
"""

questions_data = [
    {
        "type": "multiple_choice",
        "number": 1,
        "text": "According to the passage, when did modern urban planning emerge?",
        "options": {"A": "18th century", "B": "19th century", "C": "20th century", "D": "21st century"},
        "correct_answer": "B",
        "explanation": "Paragraph B explicitly states that modern urban planning emerged in the 19th century."
    },
    {
        "type": "true_false_ng",
        "number": 2,
        "text": "Urban planning has been a continuous process throughout human history.",
        "correct_answer": "TRUE",
        "explanation": "Paragraph A states that 'The evolution of urban planning has been a continuous process throughout human history'."
    },
    {
        "type": "fill_blank",
        "number": 3,
        "text": "Today, urban planning is guided by _______ development principles.",
        "correct_answer": "sustainable",
        "explanation": "Paragraph C states that 'sustainable development principles guide urban planning'."
    }
    # ... добавьте остальные вопросы
]

load_passage_with_questions(
    title="The Evolution of Urban Planning",
    text=passage_text.strip(),
    category="architecture",
    difficulty=7,
    word_count=450,
    questions_data=questions_data
)
```

#### Вариант 2: Загрузка из JSON файла

Создайте файл `ielts_passage.json`:

```json
{
    "title": "The Evolution of Urban Planning",
    "text": "Paragraph A\nYour generated text here...\n\nParagraph B\nMore text...",
    "category": "architecture",
    "difficulty": 7,
    "word_count": 450,
    "questions": [
        {
            "type": "multiple_choice",
            "number": 1,
            "text": "According to the passage, when did modern urban planning emerge?",
            "options": {"A": "18th century", "B": "19th century", "C": "20th century", "D": "21st century"},
            "correct_answer": "B",
            "explanation": "Paragraph B explicitly states that modern urban planning emerged in the 19th century."
        }
    ]
}
```

Затем загрузите:

```python
from scripts.load_ielts_passage import load_from_json

load_from_json('ielts_passage.json')
```

#### Вариант 3: Использование Python скрипта

Создайте файл `load_custom_passage.py`:

```python
from app import app, db
from models import EnglishPassage, EnglishQuestion
import json

with app.app_context():
    # Create passage
    passage = EnglishPassage(
        title="The Evolution of Urban Planning",
        text="""[paste generated text]""",
        category="architecture",
        difficulty=7,
        word_count=450
    )
    
    db.session.add(passage)
    db.session.flush()
    
    # Add questions
    questions_data = [
        {
            "type": "multiple_choice",
            "number": 1,
            "text": "...",
            "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
            "correct_answer": "B",
            "explanation": "..."
        },
        # ... добавьте остальные вопросы
    ]
    
    for q_data in questions_data:
        question = EnglishQuestion(
            passage_id=passage.id,
            question_number=q_data['number'],
            question_type=q_data['type'],
            question_text=q_data['text'],
            correct_answer=q_data['correct_answer'],
            options=json.dumps(q_data.get('options', {})) if q_data.get('options') else None,
            explanation=q_data.get('explanation')
        )
        
        db.session.add(question)
    
    db.session.commit()
    print(f"Added passage '{passage.title}' with {len(questions_data)} questions")
```

Запустите:

```bash
python load_custom_passage.py
```

## Проверка загруженных данных

```python
from app import app
from models import EnglishPassage, EnglishQuestion

with app.app_context():
    # Список всех passages
    passages = EnglishPassage.query.all()
    for p in passages:
        print(f"{p.id}: {p.title} ({p.questions.count()} questions)")
    
    # Получить конкретный passage с вопросами
    passage = EnglishPassage.query.first()
    if passage:
        print(f"\nPassage: {passage.title}")
        print(f"Text: {passage.text[:100]}...")
        print(f"\nQuestions:")
        for q in passage.questions.order_by(EnglishQuestion.question_number):
            print(f"  Q{q.question_number} ({q.question_type}): {q.question_text[:50]}...")
```

## Полезные функции

### Парсинг сгенерированного текста

```python
from utils.ielts_generator import parse_generated_passage

generated_text = """
Paragraph A
Text here...

Paragraph B
More text...
"""

parsed = parse_generated_passage(generated_text)
print(f"Title: {parsed['title']}")
print(f"Word count: {parsed['word_count']}")
print(f"Paragraphs: {len(parsed['paragraphs'])}")
```

## Примеры категорий

- `architecture` - Архитектура
- `science` - Наука
- `history` - История
- `technology` - Технологии
- `environment` - Окружающая среда
- `medicine` - Медицина
- `education` - Образование
- `general` - Общая тематика


