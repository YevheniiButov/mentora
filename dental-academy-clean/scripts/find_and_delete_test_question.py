#!/usr/bin/env python3
"""
Скрипт для поиска и удаления тестового вопроса из базы данных
"""
import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models import Question

def find_test_question():
    """Найти тестовый вопрос"""
    with app.app_context():
        # Ищем вопросы, содержащие "test" в тексте
        questions = Question.query.filter(
            Question.text.ilike('%test%')
        ).all()
        
        print(f"Найдено {len(questions)} вопросов, содержащих 'test':\n")
        
        for q in questions:
            print(f"ID: {q.id}")
            print(f"Текст: {q.text[:200]}...")
            print(f"Категория: {q.category}")
            print(f"Домен: {q.domain}")
            print(f"Варианты ответов: {q.options}")
            print("-" * 80)
        
        # Также ищем вопросы с простыми вариантами ответов (a, b, c, d)
        print("\n\nПоиск вопросов с простыми вариантами ответов (a, b, c, d):\n")
        all_questions = Question.query.all()
        
        test_questions = []
        for q in all_questions:
            if q.options:
                # Проверяем, есть ли простые варианты a, b, c, d
                options_str = str(q.options).lower()
                if ('"a"' in options_str or "'a'" in options_str) and \
                   ('"b"' in options_str or "'b'" in options_str):
                    # Проверяем, содержит ли текст "test"
                    if 'test' in q.text.lower():
                        test_questions.append(q)
        
        if test_questions:
            print(f"Найдено {len(test_questions)} подозрительных тестовых вопросов:\n")
            for q in test_questions:
                print(f"ID: {q.id}")
                print(f"Текст: {q.text}")
                print(f"Варианты: {q.options}")
                print(f"Категория: {q.category}, Домен: {q.domain}")
                print("-" * 80)
        else:
            print("Не найдено вопросов с простыми вариантами a, b, c, d и словом 'test'")
        
        return questions + test_questions

def delete_question(question_id):
    """Удалить вопрос по ID"""
    with app.app_context():
        question = Question.query.get(question_id)
        if question:
            print(f"\nУдаление вопроса ID {question_id}:")
            print(f"Текст: {question.text[:200]}...")
            
            # Показываем связанные данные
            from models import DiagnosticResponse, TestAttempt
            responses = DiagnosticResponse.query.filter_by(question_id=question_id).count()
            attempts = TestAttempt.query.filter_by(question_id=question_id).count()
            
            print(f"Связанных ответов: {responses}")
            print(f"Связанных попыток: {attempts}")
            
            confirm = input(f"\nВы уверены, что хотите удалить вопрос ID {question_id}? (yes/no): ")
            if confirm.lower() == 'yes':
                try:
                    # Удаляем связанные записи
                    DiagnosticResponse.query.filter_by(question_id=question_id).delete()
                    TestAttempt.query.filter_by(question_id=question_id).delete()
                    
                    # Удаляем вопрос
                    db.session.delete(question)
                    db.session.commit()
                    print(f"✅ Вопрос ID {question_id} успешно удален!")
                except Exception as e:
                    db.session.rollback()
                    print(f"❌ Ошибка при удалении: {e}")
            else:
                print("Отменено")
        else:
            print(f"❌ Вопрос с ID {question_id} не найден")

if __name__ == '__main__':
    print("=" * 80)
    print("Поиск тестового вопроса")
    print("=" * 80)
    
    questions = find_test_question()
    
    if questions:
        print("\n" + "=" * 80)
        question_ids = [q.id for q in questions]
        print(f"Найденные ID вопросов: {question_ids}")
        
        if len(sys.argv) > 1:
            # Если передан ID как аргумент, удаляем его
            question_id = int(sys.argv[1])
            delete_question(question_id)
        else:
            print("\nДля удаления вопроса запустите:")
            print(f"python3 scripts/find_and_delete_test_question.py <ID>")
            print("\nИли введите ID вопроса для удаления (или 'exit' для выхода):")
            while True:
                user_input = input("ID: ").strip()
                if user_input.lower() == 'exit':
                    break
                try:
                    question_id = int(user_input)
                    delete_question(question_id)
                    break
                except ValueError:
                    print("Пожалуйста, введите корректный ID (число) или 'exit'")
    else:
        print("\n❌ Тестовые вопросы не найдены")

