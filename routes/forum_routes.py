# /routes/forum_routes.py
# Полный обновленный код с исправлением NameError для current_app

# --- ИСПРАВЛЕНИЕ: Добавляем 'g' и 'current_app' в импорт из Flask ---
from flask import render_template, redirect, url_for, flash, request, Blueprint, g, current_app # <--- ДОБАВЛЕНО 'current_app'
# -----------------------------------------------------------------
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

# --- Абсолютные импорты от корня проекта ---
try:
    from extensions import db
    from models import User, ForumTopic, Post
    from forum.forms import NewThreadForm, ReplyForm
except ImportError as e:
    print(f"КРИТИЧЕСКАЯ ОШИБКА ИМПОРТА в forum_routes.py: {e}")
    print("Не удалось импортировать db, модели или формы.")
    print("Убедитесь, что структура вашего проекта соответствует путям в импортах.")
    raise

# --- Создание Blueprint ---
forum_bp = Blueprint('forum_bp', __name__)

@forum_bp.context_processor
def inject_lang_forum():
    # Теперь 'current_app' импортирован и доступен
    lang = getattr(g, 'lang', current_app.config['DEFAULT_LANGUAGE'])
    return dict(lang=lang)

# --- Роуты Форума ---

@forum_bp.route('/<string:lang>/forum/')
def forum_home(lang):
    """Главная страница форума - список тем."""
    g.lang = lang # Устанавливаем g.lang
    page = request.args.get('page', 1, type=int)
    try:
        pagination = ForumTopic.query.order_by(ForumTopic.timestamp.desc()).paginate(
            page=page, per_page=15, error_out=False
        )
        topics = pagination.items
    except Exception as e:
        flash('Произошла ошибка при загрузке тем.', 'danger')
        print(f"Error in forum_home: {e}")
        topics = []
        pagination = None

    return render_template('forum/index.html',
                           title="Форум",
                           topics=topics,
                           pagination=pagination)

@forum_bp.route('/<string:lang>/forum/topic/<int:topic_id>', methods=['GET', 'POST'])
def view_topic(lang, topic_id):
    """Просмотр конкретной темы и добавление ответа."""
    g.lang = lang # Устанавливаем g.lang
    topic = ForumTopic.query.get_or_404(topic_id)
    form = ReplyForm()
    page = request.args.get('page', 1, type=int)

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('Vul eerst uw gegevens in om een reactie te plaatsen.', 'warning')
            return redirect(url_for('auth_bp.login', lang=lang, next=request.url))

        post = Post(content=form.content.data, user_id=current_user.id, topic_id=topic.id)
        try:
            db.session.add(post)
            db.session.commit()
            flash('Uw reactie is geplaatst!', 'success')
            total_posts = topic.posts.count()
            posts_per_page = 15
            last_page = (total_posts + posts_per_page - 1) // posts_per_page
            return redirect(url_for('.view_topic', lang=lang, topic_id=topic.id, page=last_page, _anchor=f'post-{post.id}'))
        except Exception as e:
            db.session.rollback()
            flash('Произошла ошибка при добавлении ответа.', 'danger')
            print(f"Error adding post: {e}")

    try:
        posts_pagination = topic.posts.order_by(Post.timestamp.asc()).paginate(
            page=page, per_page=15, error_out=False
        )
        posts = posts_pagination.items
    except Exception as e:
        flash('Произошла ошибка при загрузке сообщений.', 'danger')
        print(f"Error loading posts: {e}")
        posts = []
        posts_pagination = None

    # Передаем page в шаблон, т.к. он используется в action формы
    return render_template('forum/topic.html',
                           title=topic.title,
                           topic=topic,
                           posts=posts,
                           pagination=posts_pagination,
                           form=form,
                           page=page)

@forum_bp.route('/<string:lang>/forum/new_topic', methods=['GET', 'POST'])
@login_required
def new_topic(lang):
    """Создание новой темы."""
    g.lang = lang # Устанавливаем g.lang
    form = NewThreadForm()

    if form.validate_on_submit():
        try:
            new_topic = ForumTopic(title=form.title.data, user_id=current_user.id)
            first_post = Post(content=form.body.data, user_id=current_user.id, topic=new_topic)
            db.session.add(new_topic)
            db.session.add(first_post)
            db.session.commit()
            flash('Nieuw onderwerp succesvol aangemaakt!', 'success')
            return redirect(url_for('.view_topic', lang=lang, topic_id=new_topic.id))
        except Exception as e:
            db.session.rollback()
            flash('Произошла ошибка при создании темы.', 'danger')
            print(f"Error creating topic: {e}")

    # Передаем form в шаблон
    return render_template('forum/new_topic.html', title="Создать новую тему", form=form)