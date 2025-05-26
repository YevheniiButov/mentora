# scripts/seed_learning_cards.py
import json
import sys
import logging
from pathlib import Path
import argparse

# --- Настройка для импорта ---
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
# -----------------------------

try:
    from app import app, db
    from models import Module, Lesson # Импортируем только нужные модели
except ImportError as e:
    print(f"Критическая ошибка импорта в seed_learning_cards.py: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def seed_learning_cards_from_json(json_file_path):
    """Загружает учебные карточки из JSON и создает Lesson с типом 'learning_card'."""
    json_path = Path(json_file_path)
    if not json_path.is_file():
        logger.error(f"❌ JSON файл не найден: {json_file_path}")
        return False

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            all_cards_data = json.load(f)
        if not isinstance(all_cards_data, list):
            logger.error(f"❌ Ошибка: JSON должен содержать список (массив) объектов.")
            return False
    except Exception as e:
        logger.error(f"❌ Ошибка чтения или парсинга JSON файла {json_file_path}: {e}")
        return False

    logger.info(f"Начинается загрузка {len(all_cards_data)} учебных карточек из {json_path.name}...")

    lessons_added = 0
    modules_cache = {} # Кэш для ID модулей {title: id}

    with app.app_context():
        # Предзагружаем все модули для быстрого поиска
        try:
            all_modules = Module.query.all()
            modules_cache = {m.title: m.id for m in all_modules}
            logger.info(f"Найдено {len(modules_cache)} модулей в базе данных.")
            if not modules_cache:
                 logger.warning("В базе данных нет модулей! Уроки не будут привязаны. Запустите init_exam_structure.py.")
                 # Можно либо выйти, либо продолжить, но уроки не привяжутся
                 # return False
        except Exception as e:
             logger.error(f"❌ Ошибка при загрузке модулей из БД: {e}")
             return False

        lesson_order_counters = {} # Счетчик порядка уроков для каждого модуля

        for i, card_info in enumerate(all_cards_data):
            # Пропускаем, если это не учебная карточка
            if card_info.get('type') != 'learning':
                # logger.debug(f"Skipping card {i+1}: type is not 'learning'.")
                continue

            module_title = card_info.get('module_title')
            question_text = card_info.get('question')
            answer_text = card_info.get('answer')
            tags = card_info.get('tags') # Получаем теги
            source_references = card_info.get('source_references') # Получаем ссылки

            # --- Валидация базовых полей ---
            if not module_title or not question_text or answer_text is None: # Answer может быть пустой строкой
                logger.warning(f"Пропуск учебной карты #{i+1}: Отсутствуют module_title, question или answer.")
                continue
            # --------------------------------

            # --- Найти ID Модуля ---
            module_id = modules_cache.get(module_title)
            if not module_id:
                logger.warning(f"Модуль '{module_title}' не найден в кэше БД! Пропуск карты #{i+1}. Убедитесь, что модуль создан.")
                continue # Пропускаем эту карточку
            # --------------------

            # --- Формируем контент урока ---
            # Сохраним доп. информацию (answer, tags, refs) в JSON внутри content
            content_data = {
                'answer': answer_text,
                'tags': tags if isinstance(tags, list) else [],
                'source_references': source_references if isinstance(source_references, list) else []
            }
            try:
                lesson_content_json = json.dumps(content_data, ensure_ascii=False)
            except TypeError:
                 logger.error(f"Ошибка при создании JSON для content карты #{i+1}. Пропуск.")
                 continue
            # -----------------------------

            # --- Определяем порядок урока ---
            if module_id not in lesson_order_counters:
                lesson_order_counters[module_id] = 0
            lesson_order_counters[module_id] += 1
            current_order = lesson_order_counters[module_id]
            # ------------------------------

            # --- Создать Урок (Lesson) ---
            try:
                lesson = Lesson(
                    module_id=module_id,
                    title=question_text, # Используем вопрос как заголовок урока
                    content_type='learning_card', # Тип контента
                    content=lesson_content_json, # Сохраняем JSON с ответом и др.
                    order=current_order
                )
                db.session.add(lesson)
                lessons_added += 1
            except Exception as e:
                logger.error(f"Ошибка при создании Lesson для карты #{i+1}: {e}", exc_info=False) # Не показываем полный трейсбек на каждую ошибку
                db.session.rollback() # Откатываем добавление этого урока

            # Периодический коммит для больших файлов
            if lessons_added > 0 and lessons_added % 100 == 0:
                try:
                    db.session.commit()
                    logger.info(f"Сохранено {lessons_added} уроков...")
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Ошибка при промежуточном коммите: {e}", exc_info=True)
                    return False # Прерываем в случае ошибки коммита
        # ----------------------------------

        # Финальный коммит
        try:
            db.session.commit()
            logger.info(f"✅ Загрузка учебных карточек завершена! Добавлено уроков (Lesson): {lessons_added}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Ошибка финального коммита: {e}", exc_info=True)
            return False

# --- Основной блок для запуска из командной строки ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Load learning cards from a JSON file into Lesson objects.')
    parser.add_argument('json_file', type=str, help='Path to the JSON file containing learning card data.')
    args = parser.parse_args()

    success = seed_learning_cards_from_json(args.json_file)

    if success:
        print(f"--- Загрузка учебных карточек из '{args.json_file}' завершена успешно ---")
    else:
        print(f"--- Загрузка учебных карточек из '{args.json_file}' завершена с ошибками ---")
        sys.exit(1)