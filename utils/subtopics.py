# utils/subtopics.py
import re

def create_slug(text):
    """Создаёт унифицированный слаг из текста"""
    if not text:
        return ""
    # Заменяем пробелы, дефисы, слеши и другие символы на подчеркивания
    return re.sub(r'[^a-z0-9]+', '_', text.lower()).strip('_')

def update_lesson_subtopics(db, Lesson):
    """Обновляет поля subtopic и subtopic_slug у всех уроков"""
    lessons = Lesson.query.all()
    updated = 0
    
    for lesson in lessons:
        if not lesson.content:
            continue
            
        try:
            content_data = json.loads(lesson.content)
            module_title = None
            
            # Проверяем различные структуры данных
            if 'module_title' in content_data:
                module_title = content_data.get('module_title')
            elif isinstance(content_data, dict):
                # Проверяем карточки
                if 'cards' in content_data and content_data['cards']:
                    for card in content_data['cards']:
                        if 'module_title' in card:
                            module_title = card.get('module_title')
                            break
                # Проверяем вопросы
                elif 'questions' in content_data and content_data['questions']:
                    for question in content_data['questions']:
                        if 'module_title' in question:
                            module_title = question.get('module_title')
                            break
            
            if module_title:
                lesson.subtopic = module_title
                lesson.subtopic_slug = create_slug(module_title)
                updated += 1
        except Exception as e:
            print(f"Error updating lesson {lesson.id}: {e}")
    
    db.session.commit()
    return updated

def reorder_subtopic_lessons(db, Lesson, module_id=None):
    """Переупорядочивает уроки по подтемам, чередуя карточки и тесты"""
    query = Lesson.query
    if module_id:
        query = query.filter_by(module_id=module_id)
        
    # Получаем все уникальные подтемы
    subtopics = db.session.query(Lesson.subtopic_slug).filter(
        Lesson.subtopic_slug.isnot(None)
    ).distinct().all()
    
    total_updated = 0
    
    for subtopic in subtopics:
        subtopic_slug = subtopic[0]
        if not subtopic_slug:
            continue
            
        # Получаем все уроки данной подтемы
        lessons = query.filter_by(subtopic_slug=subtopic_slug).all()
        
        # Разделяем уроки по типу
        learning_cards = [l for l in lessons if l.content_type == 'learning_card']
        tests = [l for l in lessons if l.content_type == 'quiz' or l.content_type == 'test_question']
        
        # Сортируем по имеющемуся порядку
        learning_cards.sort(key=lambda x: x.order or 0)
        tests.sort(key=lambda x: x.order or 0)
        
        # Чередуем карточки и тесты (2 карточки, потом 1 тест)
        new_order = []
        cards_index = 0
        tests_index = 0
        
        while cards_index < len(learning_cards) or tests_index < len(tests):
            # Добавляем до 2 карточек
            for _ in range(2):
                if cards_index < len(learning_cards):
                    new_order.append(learning_cards[cards_index])
                    cards_index += 1
            
            # Добавляем 1 тест
            if tests_index < len(tests):
                new_order.append(tests[tests_index])
                tests_index += 1
        
        # Обновляем порядок
        for i, lesson in enumerate(new_order):
            lesson.subtopic_order = i + 1
            total_updated += 1
    
    db.session.commit()
    return total_updated