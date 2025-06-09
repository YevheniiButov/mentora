# extensions.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_babel import Babel
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect

# --- Naming convention for SQLAlchemy/Alembic ---
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
# --- Create MetaData with this convention ---
metadata = MetaData(naming_convention=convention)
# --- Initialize SQLAlchemy with metadata ---
db = SQLAlchemy(metadata=metadata)

# --- Initialize other extensions as usual ---
bcrypt = Bcrypt()
login_manager = LoginManager()
babel = Babel()
cache = Cache()
csrf = CSRFProtect()
import json

def register_template_filters(app):
    """Регистрирует пользовательские фильтры для Jinja2."""
    
    @app.template_filter('fromjson')
    def fromjson_filter(value):
        """Jinja2 фильтр для преобразования JSON-строки в объект Python."""
        if value is None or value == '':
            return {}
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return {}

