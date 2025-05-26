import os
import sys

# --- Настройки ---

# Комментарии для файлов и папок (ключ: относительный путь от корня проекта)
# Например: "app.py", "static/", "static/css/main.css"
# Директории должны заканчиваться на "/"
COMMENTS = {
    # Корневые элементы
    "app.py": "# Основной файл приложения",
    "extensions.py": "# Расширения Flask (SQLAlchemy, Login, и т.д.)",
    "static/": "# Статические файлы",
    "templates/": "# Шаблоны Jinja2",
    "routes/": "# Контроллеры (Blueprint'ы)",
    "models.py": "# Модели данных",
    "requirements.txt": "# Зависимости проекта",

    # Внутри static/
    "static/css/": "# CSS стили",
    "static/css/main.css": "# Основные стили",
    "static/css/pages/": "# Стили для конкретных страниц",
    "static/css/pages/lesson.css": "# Стили для страницы урока",
    "static/css/pages/module.css": "# Стили для страницы модуля",
    # Пример для "..." и "и тд" - если такие файлы/папки существуют:
    # "static/css/pages/...": "# Другие стили страниц",
    # "static/и тд": "# Прочие файлы",
    "static/js/": "# JavaScript файлы",
    "static/images/": "# Изображения",

    # Внутри templates/
    "templates/base.html": "# Базовый шаблон",
    "templates/includes/": "# Включаемые компоненты",
    "templates/includes/_header.html": "# Шапка сайта",
    "templates/includes/_footer.html": "# Подвал",
    "templates/includes/_flash_messages.html": "# Уведомления",

    "templates/learning/": "# Шаблоны для обучения",
    "templates/learning/subject_view.html": "# Карта обучения",
    "templates/learning/dashboard.html": "# Дашборд пользователя",
    "templates/learning/module.html": "# Страница модуля",
    "templates/learning/lesson.html": "# Страница урока",
    "templates/learning/modules_list.html": "# Список модулей",

    "templates/tests/": "# Шаблоны для тестирования",
    "templates/tests/setup.html": "# Настройка теста",
    "templates/tests/question.html": "# Страница вопроса",
    "templates/tests/result.html": "# Результаты теста",

    "templates/profile/": "# Шаблоны для профиля",
    "templates/profile/auth/": "# Шаблоны аутентификации",

    "templates/admin/": "", # Можно оставить пустым, если комментарий не нужен
    "templates/admin/hierarchy_explorer.html": "# Просмотр иерархии", # Изменен для уникальности
    "templates/admin/hierarchy_manager.html": "# Управление иерархией", # Изменен для уникальности
    "templates/admin/base_admin.html": "# Базовый шаблон админки",
    "templates/admin/modals/": "# Модальные окна админки",
    "templates/admin/modals/module_modal.html": "# Модальное окно модуля",
    "templates/admin/modals/subject_modal.html": "# Модальное окно предмета",
    "templates/admin/modals/path_modal.html": "# Модальное окно пути",

    "templates/virtual_patient/": "# Шаблоны виртуального пациента",
    "templates/virtual_patient/interact.html": "# Взаимодействие с пациентом",
    "templates/virtual_patient/scenarios_list.html": "# Список сценариев",
    "templates/virtual_patient/results.html": "# Результаты симуляции", # Для templates/virtual_patient/results.html

    # Внутри routes/
    "routes/main_routes.py": "# Основные маршруты",
    "routes/auth_routes.py": "# Маршруты аутентификации",
    "routes/modules_routes.py": "# Маршруты модулей",
    "routes/lesson_routes.py": "# Маршруты уроков",
    "routes/tests_routes.py": "# Маршруты тестов",
    "routes/Admin_routes.py": "# Маршруты администратора" # Добавлен комментарий
}

# Список игнорируемых файлов и папок (по точному совпадению имени)
DEFAULT_IGNORE_LIST = [
    '.git', '__pycache__', '.vscode', '.idea', '.DS_Store',
    'node_modules', 'venv', '.env', '*.pyc', '*.tmp', 'migrations','.venv','cards','instances','learn',
    'tests', 'test', 'test.py', 'test_*.py', '*.log', '*.sqlite3','structure','summaries','extracted','scripts','data','*.jpeg','*.jpg','*.png','*.gif'
]


# Колонка, с которой начинаются комментарии
COMMENT_ALIGN_COLUMN = 48

# Префиксы для дерева
PREFIX_BRANCH = "├── "
PREFIX_LAST_BRANCH = "└── "
PREFIX_PARENT_OPEN = "│   "
PREFIX_PARENT_CLOSED = "    "

# --- Функции ---

def _get_comment_for_item(item_relative_path, comments_dict):
    """Получает комментарий для элемента по его относительному пути."""
    return comments_dict.get(item_relative_path, "")

def _generate_tree_recursive(
    root_path_for_rel,
    current_dir_path,
    prefix,
    ignore_list,
    comments_dict,
    current_rel_dir_path=""
):
    """
    Рекурсивная функция для генерации и вывода структуры дерева.
    """
    try:
        # Игнорируем директорию, если она в списке (кроме корневой)
        if os.path.basename(current_dir_path) in ignore_list and current_dir_path != root_path_for_rel:
            return

        entries = os.listdir(current_dir_path)
        # Сортировка: сначала папки, потом файлы, все по алфавиту
        entries.sort(key=lambda x: (not os.path.isdir(os.path.join(current_dir_path, x)), x.lower()))

    except OSError as e:
        # Ошибка доступа к директории
        print(f"{prefix}{PREFIX_LAST_BRANCH}[Ошибка чтения: {os.path.basename(current_dir_path)} ({e.strerror})]")
        return

    # Фильтрация игнорируемых элементов
    filtered_entries = [entry for entry in entries if entry not in ignore_list]

    for i, name in enumerate(filtered_entries):
        is_last_entry = (i == len(filtered_entries) - 1)
        item_full_path = os.path.join(current_dir_path, name)

        try:
            is_dir = os.path.isdir(item_full_path)
        except OSError: # Например, "битая" символическая ссылка
            is_dir = False

        # Формируем имя для отображения и относительный путь для комментария
        display_name = name + ("/" if is_dir else "")
        
        # Нормализуем разделители для ключей комментариев
        item_relative_path = os.path.join(current_rel_dir_path, display_name).replace("\\", "/")


        comment_str = _get_comment_for_item(item_relative_path, comments_dict)
        if not comment_str and not is_dir : # Если для файла нет комментария по полному пути, пробуем по имени файла
             comment_str = _get_comment_for_item(name, comments_dict)


        if comment_str:
            comment_str = f" {comment_str}" # Добавляем пробел перед комментарием

        # Формируем строку вывода
        connector = PREFIX_LAST_BRANCH if is_last_entry else PREFIX_BRANCH
        line_str = f"{prefix}{connector}{display_name}"

        padding_str = ""
        if comment_str:
            # Используем длину в символах для выравнивания
            current_len_chars = len(line_str)
            if current_len_chars < COMMENT_ALIGN_COLUMN:
                padding_str = " " * (COMMENT_ALIGN_COLUMN - current_len_chars)
            else:
                padding_str = "  " # Минимальный отступ, если строка уже длинная

        print(f"{line_str}{padding_str}{comment_str}")

        if is_dir:
            # Рекурсивный вызов для поддиректории
            new_prefix = prefix + (PREFIX_PARENT_CLOSED if is_last_entry else PREFIX_PARENT_OPEN)
            new_rel_dir_path = os.path.join(current_rel_dir_path, name + "/").replace("\\", "/")
            _generate_tree_recursive(
                root_path_for_rel,
                item_full_path,
                new_prefix,
                ignore_list,
                comments_dict,
                new_rel_dir_path
            )

def generate_directory_tree(
    root_dir_path,
    user_comments=None,
    user_ignore_list=None,
    sort_order=None # 'alpha', 'dirsfirst', None (OS default)
):
    """
    Основная функция для генерации и вывода дерева директории.

    Args:
        root_dir_path (str): Путь к корневой директории проекта.
        user_comments (dict, optional): Пользовательский словарь комментариев.
                                        Переопределяет и дополняет COMMENTS.
        user_ignore_list (list, optional): Пользовательский список игнорируемых элементов.
                                           Дополняет DEFAULT_IGNORE_LIST.
    """
    if not os.path.isdir(root_dir_path):
        print(f"Ошибка: Директория не найдена - {root_dir_path}")
        return

    abs_root_path = os.path.abspath(root_dir_path)
    root_name = os.path.basename(abs_root_path)

    # Объединение комментариев и списков игнорирования
    comments_to_use = COMMENTS.copy()
    if user_comments:
        comments_to_use.update(user_comments)

    ignore_list_to_use = DEFAULT_IGNORE_LIST[:]
    if user_ignore_list:
        ignore_list_to_use.extend(user_ignore_list)
    ignore_list_to_use = list(set(ignore_list_to_use)) # Удаление дубликатов

    # Вывод корневой директории
    root_comment = _get_comment_for_item(root_name + "/", comments_to_use) or \
                   _get_comment_for_item(root_name, comments_to_use) # Для случая, если корень тоже комментируется
    if root_comment:
         root_comment = f" {root_comment}"
    
    line_str = f"{root_name}/"
    padding_str = ""
    if root_comment:
        current_len_chars = len(line_str)
        if current_len_chars < COMMENT_ALIGN_COLUMN:
            padding_str = " " * (COMMENT_ALIGN_COLUMN - current_len_chars)
        else:
            padding_str = "  "
            
    print(f"{line_str}{padding_str}{root_comment}")
    
    # Запуск рекурсивной генерации
    _generate_tree_recursive(
        abs_root_path,    # Абсолютный путь к корню для сравнений
        abs_root_path,    # Текущая обрабатываемая директория
        "",               # Начальный префикс
        ignore_list_to_use,
        comments_to_use,
        ""                # Начальный относительный путь
    )

# --- Пример использования ---
if __name__ == "__main__":
    # Получаем путь к директории для отображения из аргументов командной строки
    # или используем текущую директорию по умолчанию
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        # Если вы хотите отобразить структуру директории, в которой находится скрипт:
        # project_path = os.path.dirname(os.path.abspath(__file__))
        # Или для тестирования можно указать конкретный путь:
        project_path = "." # Отобразить текущую директорию
        print(f"Путь не указан. Используется текущая директория: {os.path.abspath(project_path)}")
        print("Для указания пути: python ваш_скрипт.py /путь/к/вашей/flask-app")
        print("-" * 30)


    # Предполагается, что ваша структура "flask-app/" находится по этому пути.
    # Если скрипт лежит, например, рядом с папкой "flask-app", то вызовите:
    # generate_directory_tree("flask-app")
    # Если скрипт внутри "flask-app", то:
    # generate_directory_tree(".")

    # Вы можете передать свои комментарии и список игнорирования:
    # my_custom_comments = {"my_file.txt": "# Это мой особый файл"}
    # my_custom_ignores = ["temp_folder", "*.log"]
    # generate_directory_tree(project_path, user_comments=my_custom_comments, user_ignore_list=my_custom_ignores)

    generate_directory_tree(project_path)