# scripts/populate_questions.py

import json
import os
import sys
from pathlib import Path # <-- Импортируем pathlib

# Добавляем корневую папку проекта в sys.path
project_root_path = Path(__file__).parent.parent.resolve() # Получаем Path объект для корня проекта
if str(project_root_path) not in sys.path:
    sys.path.insert(0, str(project_root_path))

try:
    from app import app # Импортируем app из вашего app.py
    from models import db, Question, Category # Импортируем модели
except ImportError as e:
    print(f"Error importing Flask app or models: {e}")
    print("Make sure this script is in a 'scripts' folder sibling to your 'app.py' or main package.")
    sys.exit(1)

def load_questions(json_rel_path, default_category_name="General"):
    """Загружает вопросы из JSON файла в базу данных."""
    questions_added = 0
    categories_created = 0
    # Строим полный путь к JSON файлу
    full_json_path = project_root_path / json_rel_path # Используем Path объекты

    print(f"\nProcessing file: {full_json_path}")

    try:
        with open(full_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"  ERROR: File not found at {full_json_path}")
        return 0, 0
    except json.JSONDecodeError:
        print(f"  ERROR: Could not decode JSON from {full_json_path}")
        return 0, 0

    # Обрабатываем возможные структуры JSON
    questions_list = data if isinstance(data, list) else data.get("questions", [])

    if not isinstance(questions_list, list):
        print(f"  ERROR: Expected a list of questions in {full_json_path}")
        return 0, 0

    print(f"  Found {len(questions_list)} questions in file.")

    created_category_names = set()

    for q_data in questions_list:
        if not isinstance(q_data, dict):
            print(f"  Skipping invalid question data item: {q_data}")
            continue

        text = q_data.get("question") or q_data.get("text")
        options_list = q_data.get("options", [])
        correct_answer = q_data.get("answer") or q_data.get("correct_answer")
        category_name = q_data.get("category", default_category_name).strip() # Берем из JSON или default
        explanation = q_data.get("explanation", None)
        image_filename = q_data.get("image_filename", None)

        if not text or not options_list or correct_answer is None:
            print(f"  Skipping question due to missing data (text, options, or answer): {str(q_data)[:100]}...")
            continue
        if not isinstance(options_list, list):
             print(f"  Skipping question due to invalid options format (must be a list): {str(q_data)[:100]}...")
             continue

        # --- Работа с категорией ---
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            category = Category(name=category_name)
            db.session.add(category)
            try:
                db.session.flush()
                if category_name not in created_category_names:
                     print(f"  Creating new category: '{category_name}'")
                     created_category_names.add(category_name)
                categories_created += 1
            except Exception as e:
                print(f"  ERROR creating category '{category_name}': {e}. Skipping question.")
                db.session.rollback()
                continue

        # --- Создание вопроса ---
        existing_question = Question.query.filter_by(text=text, category_id=category.id).first()
        if existing_question:
           continue

        new_question = Question(
            text=text,
            options=options_list,
            correct_answer=str(correct_answer),
            category_id=category.id,
            explanation=explanation,
            image_filename=image_filename
        )
        db.session.add(new_question)
        questions_added += 1

    try:
        db.session.commit()
        print(f"  Successfully added {questions_added} new questions from {json_rel_path}.")
    except Exception as e:
        db.session.rollback()
        print(f"  ERROR committing questions from {json_rel_path}: {e}")
        questions_added = 0
        categories_created = 0

    return questions_added, categories_created

# --- Основной блок выполнения скрипта ---
if __name__ == "__main__":
    # !!! УКАЗЫВАЕМ ПАПКУ С ДАННЫМИ ОТНОСИТЕЛЬНО КОРНЯ ПРОЕКТА !!!
    DATA_FOLDER_PATH = "cards/test_data"
    # Устанавливаем имя категории по умолчанию для всех файлов, найденных автоматически
    DEFAULT_CATEGORY = "Imported Questions"

    data_dir = project_root_path / DATA_FOLDER_PATH

    if not data_dir.is_dir():
        print(f"ERROR: Data directory not found at '{data_dir}'")
        print(f"Please create the directory '{DATA_FOLDER_PATH}' in your project root ('{project_root_path}') and place JSON files there.")
        sys.exit(1)

    # Запускаем скрипт в контексте приложения Flask
    with app.app_context():
        print(f"Starting question population from folder: {DATA_FOLDER_PATH}")
        total_added = 0
        total_cats = 0

        # !!! НАХОДИМ ВСЕ .json ФАЙЛЫ АВТОМАТИЧЕСКИ !!!
        json_files = list(data_dir.glob('*.json'))

        if not json_files:
             print(f"No .json files found in '{data_dir}'. Nothing to import.")
        else:
            print(f"Found {len(json_files)} JSON files to process:")
            for json_file_path in json_files:
                # Получаем путь к файлу относительно корня проекта для передачи в функцию
                relative_path = str(json_file_path.relative_to(project_root_path))
                # Вызываем функцию загрузки для каждого найденного файла
                added, cats = load_questions(relative_path, DEFAULT_CATEGORY)
                total_added += added
                total_cats += cats

        print(f"\n-----------------------------------------")
        print(f"Finished population.")
        print(f"Total NEW categories created: {total_cats}")
        print(f"Total NEW questions added: {total_added}")
        print(f"-----------------------------------------")