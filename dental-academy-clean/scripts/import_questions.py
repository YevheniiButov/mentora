#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Question, QuestionCategory, BIGDomain, IRTParameters
from datetime import datetime
from docx import Document
import re

def import_questions():
    with app.app_context():
        # Читаем Word документ
        doc = Document('./IRT vragen.docx')
        text = ''
        for paragraph in doc.paragraphs:
            text += paragraph.text + '\n'    
        print(f'Извлечено {len(text)} символов из Word документа')
        
        # Получаем или создаем категорию BI-toets
        category = QuestionCategory.query.filter_by(name='BI-toets').first()
        if not category:
            category = QuestionCategory(name='BI-toets', description='Вопросы для подготовки к голландскому стоматологическому экзамену BI-toets')
            db.session.add(category)
            db.session.commit()
            print('Создана категория BI-toets')
        
        # Разделяем на вопросы
        questions = re.split(r'VRAAG \d+:', text)[1:]
        print(f'Найдено {len(questions)} вопросов')
        
        imported = 0
        for i, block in enumerate(questions, 1):
            try:
                # Извлекаем домен
                domain_match = re.search(r'Domein:\s*([^(]+)', block)
                domain_name = domain_match.group(1).strip() if domain_match else 'Algemeen'
                
                # Извлекаем сложность
                difficulty_match = re.search(r'Moeilijkheidsgraad:\s*([\d.]+)', block)
                difficulty = float(difficulty_match.group(1)) if difficulty_match else 0.5
                
                # Извлекаем клинический случай
                case_match = re.search(r'KLINISCHE CASUS:\s*(.*?)(?=VRAAG:|$)', block, re.DOTALL)
                clinical_case = case_match.group(1).strip() if case_match else ''
                
                # Извлекаем вопрос
                question_match = re.search(r'VRAAG:\s*(.*?)(?=A\)|$)', block, re.DOTALL)
                question_text = question_match.group(1).strip() if question_match else ''
                
                # Извлекаем варианты ответов
                options = {}
                for option in ['A', 'B', 'C', 'D', 'E']:
                    option_match = re.search(rf'{option}\)\s*(.*?)(?={chr(ord(option)+1)}|JUISTE ANTWOORD:|$)', block, re.DOTALL)
                    if option_match:
                        options[option] = option_match.group(1).strip()
                
                # Извлекаем правильный ответ
                correct_match = re.search(r'JUISTE ANTWOORD:\s*([A-E])', block)
                correct_answer = correct_match.group(1) if correct_match else 'A'
                
                # Извлекаем объяснение
                explanation_match = re.search(r'UITLEG:\s*(.*?)(?=VRAAG \d+:|$)', block, re.DOTALL)
                explanation = explanation_match.group(1).strip() if explanation_match else ''
                
                # Формируем полный текст вопроса
                full_question_text = f'KLINISCHE CASUS:\n{clinical_case}\n\nVRAAG:\n{question_text}'
                
                # Формируем варианты ответов как строку
                options_text = '\n'.join([f'{opt}) {text}' for opt, text in options.items()])
                
                # Получаем или создаем домен
                domain = BIGDomain.query.filter_by(code='THER').first()
                if not domain:
                    domain = BIGDomain(code='THER', name=domain_name, description=f'Домен {domain_name}', weight=1.0)
                    db.session.add(domain)
                    db.session.commit()
                
                # Создаем вопрос
                question = Question(
                    text=full_question_text,
                    options=options_text,
                    correct_answer=correct_answer,
                    explanation=explanation,
                    category_id=category.id
                )
                db.session.add(question)
                db.session.flush()  # Получаем ID вопроса
                
                # Создаем IRT параметры
                irt_params = IRTParameters(
                    question_id=question.id,
                    discrimination=1.0,
                    difficulty=(difficulty - 0.5) * 4,
                    guessing=0.2
                )
                db.session.add(irt_params)
                imported += 1
                print(f'Импортирован вопрос {i}: {domain_name}')
                
            except Exception as e:
                print(f'Ошибка при импорте вопроса {i}: {e}')
                db.session.rollback()
                continue
        
        try:
            db.session.commit()
            print(f'\n✅ Успешно импортировано {imported} вопросов')
        except Exception as e:
            print(f'Ошибка при сохранении: {e}')
            db.session.rollback()

if __name__ == '__main__':
    import_questions() 