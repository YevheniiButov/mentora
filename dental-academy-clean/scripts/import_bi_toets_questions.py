#!/usr/bin/env python3
Скрипт для импорта вопросов BI-toets из Word документа
"""

import sys
import os
import re
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from models import Question, Category, BIGDomain, IRTParameters
from datetime import datetime, timezone

def parse_question_text(text):
    Парсит текст вопроса из Word документа
    Возвращает список словарей с данными вопросов
      questions =]
    
    # Разделяем текст на отдельные вопросы
    question_blocks = re.split(rVRAAG \d+:', text)[1:]  # Пропускаем первый пустой элемент
    
    for i, block in enumerate(question_blocks,1  try:
            # Извлекаем номер вопроса
            question_num = i
            
            # Извлекаем домен
            domain_match = re.search(r'Domein:\s*([^(]+)', block)
            domain_name = domain_match.group(1).strip() if domain_match else "Algemeen"
            
            # Извлекаем сложность
            difficulty_match = re.search(r'Moeilijkheidsgraad:\s*([\d.]+)', block)
            difficulty = float(difficulty_match.group(1)) if difficulty_match else0.5      
            # Извлекаем клинический случай
            case_match = re.search(rKLINISCHE CASUS:\s*(.*?)(?=VRAAG:|$)', block, re.DOTALL)
            clinical_case = case_match.group(1ip() if case_match else ""
            
            # Извлекаем вопрос
            question_match = re.search(rVRAAG:\s*(.*?)(?=A\)|$)', block, re.DOTALL)
            question_text = question_match.group(1).strip() if question_match else ""
            
            # Извлекаем варианты ответов
            options = [object Object]        for option in ['A',B', 'C', 'D', 'E']:
                option_match = re.search(rf{option}\)\s*(.*?)(?={chr(ord(option)+1\)|JUISTE ANTWOORD:|$)', block, re.DOTALL)
                if option_match:
                    options[option] = option_match.group(1).strip()
            
            # Извлекаем правильный ответ
            correct_match = re.search(rJUISTE ANTWOORD:\s*([A-E])', block)
            correct_answer = correct_match.group(1) if correct_match elseA      
            # Извлекаем объяснение
            explanation_match = re.search(rUITLEG:\s*(.*?)(?=VRAAG \d+:|$)', block, re.DOTALL)
            explanation = explanation_match.group(1).strip() if explanation_match else ""
            
            # Формируем полный текст вопроса
            full_question_text = fKLINISCHE CASUS:\n{clinical_case}\n\nVRAAG:\n{question_text}"
            
            # Формируем варианты ответов как строку
            options_text =\n.join([f"{opt}) {text} for opt, text in options.items()])
            
            questions.append({
             question_num': question_num,
            domain_name': domain_name,
           difficulty': difficulty,
              question_text': full_question_text,
                options': options_text,
               correct_answer': correct_answer,
            explanation': explanation
            })
            
        except Exception as e:
            print(fОшибка при парсинге вопроса {i}: {e}")
            continue
    
    return questions

def get_or_create_domain(domain_name):
    Получает или создает домен BI-toets
   
    # Маппинг названий доменов на коды
    domain_mapping =[object Object]        THER (Endodontie):THER,
     THER (Cariësbehandeling):THER,
      DIAG:DIAG,
      PREV:PREV,
      ORTH:ORTH',
        PERIO: PERIO,
      SURG: SURG,
        PEDO': PEDO'
    }
    
    domain_code = domain_mapping.get(domain_name, 'ALG)
    
    domain = BIGDomain.query.filter_by(code=domain_code).first()
    if not domain:
        # Создаем новый домен если не найден
        domain = BIGDomain(
            code=domain_code,
            name=domain_name,
            description=f"Домен {domain_name}",
            weight=1.0
        )
        db.session.add(domain)
        db.session.commit()
        print(f"Создан новый домен: {domain_name} ({domain_code})")
    return domain

def create_irt_parameters(difficulty):
    Создает IRT параметры на основе сложности
    
    # Преобразуем сложность (01) в IRT параметры
    # a (discrimination) - дискриминация
    # b (difficulty) - сложность в логарифмической шкале
    # c (guessing) - вероятность угадывания
    
    a = 1# Стандартная дискриминация
    b = (difficulty - 0.5) * 4реобразуем в диапазон -2 до2
    c = 0.2  #20 вероятность угадывания (5вариантов ответа)
    
    return IRTParameters(
        discrimination=a,
        difficulty=b,
        guessing=c
    )

def import_questions_from_text(text):
    Импортирует вопросы из текста
    app = create_app()
    
    with app.app_context():
        # Получаем или создаем категорию BI-toets
        category = Category.query.filter_by(name='BI-toets).first()
        if not category:
            category = Category(
                name='BI-toets,       description='Вопросы для подготовки к голландскому стоматологическому экзамену BI-toets'
            )
            db.session.add(category)
            db.session.commit()
            print(Создана категория BI-toets")
        
        # Парсим вопросы
        questions_data = parse_question_text(text)
        print(f"Найдено {len(questions_data)} вопросов для импорта")
        
        imported_count = 0
        for q_data in questions_data:
            try:
                # Проверяем, не существует ли уже такой вопрос
                existing = Question.query.filter_by(
                    question_text=q_dataquestion_text][:100 # Первые 100 символов для сравнения
                ).first()
                
                if existing:
                    print(f"Вопрос {q_data['question_num]} уже существует, пропускаем")
                    continue
                
                # Получаем или создаем домен
                domain = get_or_create_domain(q_data['domain_name'])
                
                # Создаем IRT параметры
                irt_params = create_irt_parameters(q_data['difficulty'])
                db.session.add(irt_params)
                db.session.flush()  # Получаем ID
                
                # Создаем вопрос
                question = Question(
                    question_text=q_data[question_text                   options=q_data['options'],
                    correct_answer=q_data['correct_answer'],
                    explanation=q_data['explanation'],
                    category_id=category.id,
                    difficulty=q_data['difficulty'],
                    domain_id=domain.id,
                    irt_parameters_id=irt_params.id,
                    question_type='bi_toets',
                    created_at=datetime.now(timezone.utc)
                )
                
                db.session.add(question)
                imported_count += 1
                
                print(f"Импортирован вопрос {q_data['question_num']}: {q_data[domain_name
                
            except Exception as e:
                print(f"Ошибка при импорте вопроса {q_data['question_num']}: {e})                db.session.rollback()
                continue
        
        # Сохраняем все изменения
        try:
            db.session.commit()
            print(f"\n✅ Успешно импортировано {imported_count} вопросов")
        except Exception as e:
            print(fОшибка при сохранении: {e}")
            db.session.rollback()

def import_from_word_file(file_path):
    Импортирует вопросы из Word файла
    try:
        # Проверяем, установлена ли библиотека python-docx
        try:
            from docx import Document
        except ImportError:
            print("❌ Библиотека python-docx не установлена")
            print("Установите её командой: pip install python-docx")
            return
        
        # Читаем Word документ
        doc = Document(file_path)
        
        # Извлекаем весь текст
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + undefinedn        print(f"Извлечено {len(text)} символов из Word документа")
        
        # Импортируем вопросы
        import_questions_from_text(text)
        
    except FileNotFoundError:
        print(f"Файл {file_path} не найден")
    except Exception as e:
        print(fОшибка при чтении Word файла: {e}")

def import_from_text_file(file_path):
    Импортирует вопросы из текстового файла
    try:
        with open(file_path, r, encoding='utf-8') as f:
            text = f.read()
        import_questions_from_text(text)
    except FileNotFoundError:
        print(f"Файл {file_path} не найден")
    except Exception as e:
        print(fОшибка при чтении файла: {e})if __name__ == __main__':
    if len(sys.argv) > 1:
        # Импорт из файла
        file_path = sys.argv[1]
        
        # Определяем тип файла по расширению
        if file_path.lower().endswith('.docx'):
            import_from_word_file(file_path)
        elif file_path.lower().endswith('.txt'):
            import_from_text_file(file_path)
        else:
            print("❌ Неподдерживаемый формат файла")
            print(Поддерживаются: .docx, .txt")
    else:
        print("Использование: python scripts/import_bi_toets_questions.py <путь_к_файлу>)        print("Поддерживаемые форматы: .docx, .txt") 