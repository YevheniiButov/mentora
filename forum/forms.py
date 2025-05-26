# app/forum/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class NewThreadForm(FlaskForm):
    """Форма для создания новой темы."""
    title = StringField(
        'Заголовок темы',
        validators=[
            DataRequired(message='Заголовок не может быть пустым.'),
            Length(min=5, max=255, message='Заголовок должен быть от 5 до 255 символов.')
        ],
        render_kw={"placeholder": "Введите понятный заголовок для вашей темы"}
    )
    body = TextAreaField(
        'Первое сообщение',
        validators=[
            DataRequired(message='Сообщение не может быть пустым.'),
            Length(min=10, message='Сообщение должно содержать минимум 10 символов.')
        ],
        render_kw={"rows": 10, "placeholder": "Напишите ваше сообщение или вопрос здесь..."}
    )
    submit = SubmitField('Создать тему')

class ReplyForm(FlaskForm):
    """Форма для ответа в теме."""
    content = TextAreaField(
        'Ваш ответ',
        validators=[
            DataRequired(message='Ответ не может быть пустым.'),
            Length(min=3, message='Ответ должен содержать минимум 3 символа.')
        ],
        render_kw={"rows": 5, "placeholder": "Напишите ваш ответ..."}
    )
    submit = SubmitField('Отправить ответ')