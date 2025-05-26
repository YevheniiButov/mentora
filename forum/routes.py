# app/forum/routes.py

from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_required, current_user

# --- Импорты ---
# Адаптируйте пути импорта под вашу структуру!
from extensions import db
from models import User, ForumTopic, Post
from .forms import NewThreadForm, ReplyForm # Импорт форм оставляем относительным '.' или делаем абсолютным 'from forum.forms import ...'
# --- ⬆️ Конец импорта форм ⬆️ ---

forum_bp = Blueprint('forum', __name__) # БЕЗ template_folder, ищем в app/templates/forum/

# --- Роуты Форума ---

@forum_bp.route('/')
def forum_home():
    """Главная страница форума - список тем."""
    try:
        # TODO: Заменить на запрос с пагинацией
        topics = Topic.query.order_by(Topic.timestamp.desc()).limit(20).all()
    except Exception as e:
        flash(f'Произошла ошибка при загрузке тем: {e}', 'danger')
        topics = []
    return render_template('forum/index.html', title="Форум", topics=topics)

@forum_bp.route('/topic/<int:topic_id>', methods=['GET', 'POST'])
def view_topic(topic_id):
    """Просмотр темы и добавление ответа."""
    topic = Topic.query.get_or_404(topic_id)
    # --- ⬇️ Инициализируем форму ответа ⬇️ ---
    form = ReplyForm()
    # --- ⬆️ Конец инициализации формы ⬆️ ---

    # --- ⬇️ Обработка отправки формы ответа (POST-запрос) ⬇️ ---
    if form.validate_on_submit():
        # Проверяем, авторизован ли пользователь
        if not current_user.is_authenticated:
            flash('Vul eerst uw gegevens in om een reactie te plaatsen.', 'warning')
            # Перенаправляем на логин, сохраняя страницу, куда пользователь хотел попасть
            return redirect(url_for('auth.login', next=request.url))

        # Создаем новый пост
        post = Post(content=form.content.data, user_id=current_user.id, topic_id=topic.id)
        try:
            db.session.add(post)
            # TODO: Обновить last_post_timestamp и post_count в Topic
            db.session.commit()
            flash('Uw reactie is geplaatst!', 'success')
            # Перенаправляем на эту же тему, к якорю нового поста
            return redirect(url_for('forum.view_topic', topic_id=topic.id, _anchor=f'post-{post.id}'))
        except Exception as e:
            db.session.rollback() # Откатываем транзакцию в случае ошибки
            flash(f'Произошла ошибка при добавлении ответа: {e}', 'danger')

    # --- ⬆️ Конец обработки POST-запроса ⬆️ ---

    # --- Загрузка постов для GET-запроса или если форма невалидна ---
    try:
        # TODO: Добавить пагинацию постов
        page = request.args.get('page', 1, type=int)
        posts_pagination = topic.posts.order_by(Post.timestamp.asc()).paginate(page=page, per_page=15, error_out=False)
        posts = posts_pagination.items
    except Exception as e:
        flash(f'Произошла ошибка при загрузке сообщений: {e}', 'danger')
        posts = []
        posts_pagination = None # Явно указываем, что пагинации нет

    # Отображаем шаблон, передавая тему, посты, объект пагинации и форму
    return render_template('forum/topic.html',
                           title=topic.title,
                           topic=topic,
                           posts=posts,
                           pagination=posts_pagination, # Передаем для рендера ссылок пагинации
                           form=form) # Передаем форму для отображения

@forum_bp.route('/new_topic', methods=['GET', 'POST'])
@login_required # Доступ только авторизованным
def new_topic():
    """Создание новой темы."""
    # --- ⬇️ Инициализируем форму создания темы ⬇️ ---
    form = NewThreadForm()
    # --- ⬆️ Конец инициализации формы ⬆️ ---

    # --- ⬇️ Обработка отправки формы (POST-запрос) ⬇️ ---
    if form.validate_on_submit():
        try:
            # Создаем тему
            new_topic = Topic(title=form.title.data, user_id=current_user.id)
            # Не добавляем в сессию сразу, сначала создадим первый пост

            # Создаем первый пост, связывая его с темой
            first_post = Post(content=form.body.data, user_id=current_user.id, topic=new_topic)

            # Добавляем оба объекта в сессию
            db.session.add(new_topic)
            db.session.add(first_post)

            # TODO: Установить last_post_timestamp = first_post.timestamp и post_count = 1 для new_topic

            db.session.commit() # Сохраняем изменения в БД
            flash('Nieuw onderwerp succesvol aangemaakt!', 'success')
            # Перенаправляем пользователя на страницу новой темы
            return redirect(url_for('forum.view_topic', topic_id=new_topic.id))
        except Exception as e:
            db.session.rollback() # Откатываем транзакцию
            flash(f'Произошла ошибка при создании темы: {e}', 'danger')
    # --- ⬆️ Конец обработки POST-запроса ⬆️ ---

    # Отображаем шаблон с формой (для GET-запроса или если форма невалидна)
    return render_template('forum/new_topic.html', title="Создать новую тему", form=form)