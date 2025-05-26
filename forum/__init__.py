from flask import Blueprint

# Создаем экземпляр Blueprint
# 'forum' - имя блюпринта (используется во flask.url_for)
# __name__ - стандартная практика
# template_folder='templates' - указываем, где искать шаблоны для этого блюпринта
forum_bp = Blueprint('forum', __name__, template_folder='templates')

# Импортируем роуты в конце, чтобы избежать циклических импортов
# Это важно, если ваши роуты будут импортировать forum_bp
from.import routes