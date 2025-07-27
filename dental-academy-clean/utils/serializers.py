# utils/serializers.py - Универсальная система сериализации
from datetime import datetime, date
from decimal import Decimal
import json
from flask import jsonify as flask_jsonify
from sqlalchemy.ext.declarative import DeclarativeMeta

class UniversalJSONEncoder(json.JSONEncoder):
    """Универсальный JSON encoder для всех типов данных"""
    
    def default(self, obj):
        # Datetime и date объекты
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        
        # Decimal числа
        elif isinstance(obj, Decimal):
            return float(obj)
        
        # SQLAlchemy модели
        elif isinstance(obj.__class__, DeclarativeMeta):
            return obj.to_dict() if hasattr(obj, 'to_dict') else self._model_to_dict(obj)
        
        # Обычные объекты с __dict__
        elif hasattr(obj, '__dict__'):
            return {key: value for key, value in obj.__dict__.items() 
                   if not key.startswith('_')}
        
        return super().default(obj)
    
    def _model_to_dict(self, model):
        """Конвертация SQLAlchemy модели в словарь"""
        result = {}
        for column in model.__table__.columns:
            value = getattr(model, column.name)
            if isinstance(value, (datetime, date)):
                result[column.name] = value.isoformat() if value else None
            elif isinstance(value, Decimal):
                result[column.name] = float(value)
            else:
                result[column.name] = value
        return result

# Глобальные функции для использования везде
def safe_jsonify(data, **kwargs):
    """Безопасная замена Flask jsonify"""
    return flask_jsonify(json.loads(json.dumps(data, cls=UniversalJSONEncoder)), **kwargs)

def to_json_safe(obj):
    """Конвертация любого объекта в JSON-safe формат"""
    return json.loads(json.dumps(obj, cls=UniversalJSONEncoder))

def clean_for_template(data):
    """Очистка данных для передачи в Jinja2 шаблоны"""
    return to_json_safe(data)

# Базовый mixin для моделей
class JSONSerializableMixin:
    """Mixin для добавления JSON сериализации к любой модели"""
    
    def to_dict(self, include_relationships=False):
        """Конвертация модели в словарь с безопасной сериализацией datetime"""
        result = {}
        
        # Обычные колонки
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat() if value else None
            elif isinstance(value, date):
                result[column.name] = value.isoformat() if value else None
            elif isinstance(value, Decimal):
                result[column.name] = float(value)
            else:
                result[column.name] = value
        
        # Relationships (опционально)
        if include_relationships:
            for relationship in self.__mapper__.relationships:
                value = getattr(self, relationship.key)
                if value is None:
                    result[relationship.key] = None
                elif hasattr(value, '__iter__') and not isinstance(value, str):
                    # One-to-many или many-to-many
                    result[relationship.key] = [
                        item.to_dict() if hasattr(item, 'to_dict') else str(item)
                        for item in value
                    ]
                else:
                    # One-to-one или many-to-one
                    result[relationship.key] = (
                        value.to_dict() if hasattr(value, 'to_dict') else str(value)
                    )
        
        return result
    
    def to_json(self, include_relationships=False):
        """Прямая сериализация в JSON строку"""
        return json.dumps(self.to_dict(include_relationships), cls=UniversalJSONEncoder)

# Flask app configuration
def setup_json_serialization(app):
    """Настройка JSON сериализации для Flask приложения"""
    # Устанавливаем кастомный JSON encoder
    app.json_encoder = UniversalJSONEncoder
    
    # Добавляем Jinja2 фильтры
    @app.template_filter('safe_json')
    def safe_json_filter(data):
        """Jinja2 фильтр для безопасной JSON сериализации"""
        return json.dumps(data, cls=UniversalJSONEncoder)
    
    @app.template_filter('clean_datetime')
    def clean_datetime_filter(data):
        """Jinja2 фильтр для очистки datetime объектов"""
        return to_json_safe(data)

# Декоратор для API endpoints
from functools import wraps

def json_response(f):
    """Декоратор для автоматической JSON сериализации в API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        result = f(*args, **kwargs)
        if isinstance(result, tuple):
            # Если возвращается (data, status_code)
            data, status_code = result
            return safe_jsonify(data), status_code
        else:
            return safe_jsonify(result)
    return decorated_function

# Примеры использования:

"""
# 1. В app.py
from utils.serializers import setup_json_serialization
setup_json_serialization(app)

# 2. В models.py - добавить mixin к моделям
class PersonalLearningPlan(db.Model, JSONSerializableMixin):
    # ... поля модели ...
    pass

class DiagnosticResponse(db.Model, JSONSerializableMixin):
    # ... поля модели ...
    pass

# 3. В routes - использовать декоратор для API
@dashboard_bp.route('/api/learning-plan', methods=['POST'])
@json_response
def create_learning_plan_api():
    plan = PersonalLearningPlan(...)
    db.session.add(plan)
    db.session.commit()
    
    # Автоматически сериализуется в JSON
    return {
        'success': True,
        'plan': plan,  # Автоматически вызовется plan.to_dict()
        'message': 'План создан'
    }

# 4. В шаблонах
<!-- Вместо {{ data | tojson }} используй: -->
{{ data | safe_json }}

# 5. Для передачи в шаблоны
return render_template('template.html', 
                     data=clean_for_template(complex_data))

# 6. Прямое использование в любом месте
any_object_with_datetime = get_complex_data()
json_safe_data = to_json_safe(any_object_with_datetime)
""" 