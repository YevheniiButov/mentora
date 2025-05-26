# scripts/init_exam_structure.py
import sys
from pathlib import Path

# --- Настройка для импорта ---
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
# -----------------------------

from app import app, db
from models import LearningPath, Module # Импортируем нужные модели

def init_structure():
    with app.app_context():
        # Проверка, существуют ли уже пути
        if LearningPath.query.count() > 0:
            print("Structure (Learning Paths) already exists. Skipping initialization.")
            return

        print("Creating Learning Paths (Exam Categories)...")
        # 1. Создаем LearningPath (Категории)
        path1 = LearningPath(name="Теоретическая часть (MCQ)", order=1, icon="list-check")
        path2 = LearningPath(name="Короткие ответы (Short Answer)", order=2, icon="pencil-square")
        path3 = LearningPath(name="Клинические кейсы (Casus)", order=3, icon="briefcase-fill")
        path4 = LearningPath(name="Практическая часть (Simodont, Gebitsreiniging)", order=4, icon="tools") # Иконку можно подобрать лучше
        path5 = LearningPath(name="Интервью Intake gesprek", order=5, icon="person-video3") # Иконку можно подобрать лучше

        db.session.add_all([path1, path2, path3, path4, path5])
        db.session.flush() # Получаем ID для путей

        print("Creating Modules (Exam Sub-topics)...")
        # 2. Создаем Module (Подпункты) и привязываем к LearningPath
        modules_to_add = []

        # --- Категория 1: Теоретическая часть (MCQ) ---
        modules_to_add.extend([
            Module(title="Basic Medical Sciences", learning_path_id=path1.id, order=1, icon="heart-pulse"),
            Module(title="THK I: Cariology, Endodontics, Periodontology, Pedodontics", learning_path_id=path1.id, order=2, icon="journal-medical"),
            Module(title="THK II: Prosthodontics, Oral Surgery, Orthodontics", learning_path_id=path1.id, order=3, icon="journal-richtext"),
            Module(title="Radiology", learning_path_id=path1.id, order=4, icon="radioactive"), # Иконку можно подобрать лучше
            Module(title="Statistics", learning_path_id=path1.id, order=5, icon="graph-up"),
            Module(title="Methodology", learning_path_id=path1.id, order=6, icon="sliders") # Методология также есть в Short Answer
        ])

        # --- Категория 2: Короткие ответы (Short Answer) ---
        modules_to_add.extend([
            Module(title="Methodology", learning_path_id=path2.id, order=1, icon="sliders"), # Дублируем название, но привязка к другому пути
            Module(title="Intake/Ethics (эссе)", learning_path_id=path2.id, order=2, icon="file-earmark-richtext")
        ])

        # --- Категория 3: Клинические кейсы (Casus) ---
        modules_to_add.extend([
            Module(title="Casus 1 (Комплексное лечение)", learning_path_id=path3.id, order=1, icon="person-workspace"),
            Module(title="Casus 2 (Педиатрия / Кариес по ICDAS)", learning_path_id=path3.id, order=2, icon="person-hearts"), # Иконку можно подобрать лучше
            Module(title="Casus 3 (Травма / Резорбция)", learning_path_id=path3.id, order=3, icon="bandaid") # Иконку можно подобрать лучше
        ])

        # --- Категория 4: Практическая часть ---
        modules_to_add.extend([
            Module(title="Видео + чеклист оценивания", learning_path_id=path4.id, order=1, icon="play-btn-fill"),
            Module(title="Тренировочные задания / рефлексия пользователя", learning_path_id=path4.id, order=2, icon="clipboard-data")
        ])

        # --- Категория 5: Интервью Intake gesprek ---
        modules_to_add.extend([
             Module(title="Сценарии + самопроверка по чеклисту (10 пунктов)", learning_path_id=path5.id, order=1, icon="person-check-fill")
        ])

        db.session.add_all(modules_to_add)
        db.session.commit()
        print(f"Successfully added {len(modules_to_add)} modules.")
        print("Exam structure initialization complete.")

# Блок для запуска функции
if __name__ == "__main__":
    init_structure()