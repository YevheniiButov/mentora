from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.menu import MenuLink
from flask_login import current_user
from flask import redirect, url_for, request
from wtforms import TextAreaField
from wtforms.widgets import TextArea
import os.path as op
import os

# Rich text редактор
class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('class_', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)

class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()

# Базовая безопасность
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and (
            hasattr(current_user, 'is_admin') and current_user.is_admin or
            hasattr(current_user, 'role') and current_user.role == 'admin'
        )
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth_bp.login', next=request.url))

# Кастомный дашборд с аналитикой
class DashboardView(AdminIndexView):
    @expose('/')
    def index(self):
        from models import (
            User, Module, Lesson, LearningPath, Subject, 
            VirtualPatientScenario, Test, Question, UserProgress,
            TestAttempt, ForumTopic, Post, Achievement, UserAchievement
        )
        from sqlalchemy import func
        from extensions import db
        
        # Собери статистику для дашборда
        stats = {
            'total_users': User.query.count(),
            'total_learning_paths': LearningPath.query.count(),
            'total_subjects': Subject.query.count(),
            'total_modules': Module.query.count(),
            'total_lessons': Lesson.query.count(),
            'total_tests': Test.query.count(),
            'total_questions': Question.query.count(),
            'virtual_patients': VirtualPatientScenario.query.count(),
            'forum_topics': ForumTopic.query.count(),
            'forum_posts': Post.query.count(),
            'achievements': Achievement.query.count(),
            'user_achievements': UserAchievement.query.count()
        }
        
        # Последние пользователи
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        
        # Популярные модули (если есть прогресс)
        popular_modules = []
        if UserProgress.query.first():
            popular_modules = db.session.query(
                Module.title,
                func.count(UserProgress.id).label('enrollments')
            ).join(UserProgress).group_by(Module.id).order_by(
                func.count(UserProgress.id).desc()
            ).limit(5).all()
        
        # Последние активности
        recent_progress = UserProgress.query.order_by(UserProgress.timestamp.desc()).limit(10).all()
        
        # Статистика по виртуальным пациентам
        vp_stats = {
            'published': VirtualPatientScenario.query.filter_by(is_published=True).count(),
            'draft': VirtualPatientScenario.query.filter_by(is_published=False).count(),
            'premium': VirtualPatientScenario.query.filter_by(is_premium=True).count()
        }
        
        return self.render('admin/dashboard.html',
                         stats=stats,
                         recent_users=recent_users,
                         popular_modules=popular_modules,
                         recent_progress=recent_progress,
                         vp_stats=vp_stats)

# Создай кастомные AdminView для каждой модели:

class UserAdminView(SecureModelView):
    column_list = ['email', 'username', 'name', 'role', 'is_active', 'created_at', 'last_login']
    column_filters = ['role', 'is_active', 'has_subscription', 'language']
    column_searchable_list = ['email', 'username', 'name']
    form_excluded_columns = ['password_hash', 'created_at', 'last_login']
    can_export = True
    export_types = ['csv', 'xlsx']
    column_default_sort = ('created_at', True)

class LearningPathAdminView(SecureModelView):
    column_list = ['name', 'description', 'order', 'exam_phase', 'is_active']
    column_filters = ['exam_phase', 'is_active']
    column_searchable_list = ['name', 'description']
    form_overrides = {
        'description': CKTextAreaField
    }

class SubjectAdminView(SecureModelView):
    column_list = ['name', 'learning_path_id', 'order', 'description']
    column_filters = ['learning_path_id']
    column_searchable_list = ['name', 'description']
    form_overrides = {
        'description': CKTextAreaField
    }

class ModuleAdminView(SecureModelView):
    column_list = ['title', 'subject_id', 'order', 'module_type', 'is_premium', 'is_final_test']
    column_filters = ['subject_id', 'module_type', 'is_premium', 'is_final_test']
    column_searchable_list = ['title', 'description']
    form_overrides = {
        'description': CKTextAreaField
    }

class LessonAdminView(SecureModelView):
    column_list = ['title', 'module_id', 'order', 'content_type', 'subtopic']
    column_filters = ['module_id', 'content_type']
    column_searchable_list = ['title', 'content']
    form_overrides = {
        'content': CKTextAreaField
    }

class TestAdminView(SecureModelView):
    column_list = ['title', 'test_type', 'subject_final_test_owner', 'module_intermediate_test_owner']
    column_filters = ['test_type']
    column_searchable_list = ['title', 'description']

class QuestionAdminView(SecureModelView):
    column_list = ['text', 'category_id', 'correct_answer', 'image_filename']
    column_filters = ['category_id']
    column_searchable_list = ['text', 'explanation']
    form_overrides = {
        'text': CKTextAreaField,
        'explanation': CKTextAreaField
    }

class VirtualPatientScenarioAdminView(SecureModelView):
    column_list = ['title', 'difficulty', 'category', 'is_premium', 'is_published', 'created_at']
    column_filters = ['difficulty', 'category', 'is_premium', 'is_published']
    column_searchable_list = ['title', 'description']
    form_overrides = {
        'description': CKTextAreaField,
        'scenario_data': CKTextAreaField
    }

class ForumTopicAdminView(SecureModelView):
    column_list = ['title', 'author', 'category', 'is_featured', 'timestamp', 'views']
    column_filters = ['category', 'is_featured']
    column_searchable_list = ['title']
    column_default_sort = ('timestamp', True)

class PostAdminView(SecureModelView):
    column_list = ['content', 'author', 'forum_topic', 'timestamp']
    column_filters = ['forum_topic']
    column_searchable_list = ['content']
    form_overrides = {
        'content': CKTextAreaField
    }

class AchievementAdminView(SecureModelView):
    column_list = ['name', 'type', 'rarity', 'points', 'is_active']
    column_filters = ['type', 'rarity', 'is_active']
    column_searchable_list = ['name', 'description']
    form_overrides = {
        'description': CKTextAreaField,
        'requirement': CKTextAreaField
    }

class UserProgressAdminView(SecureModelView):
    column_list = ['user_id', 'lesson_id', 'completed', 'timestamp', 'time_spent']
    column_filters = ['completed']
    column_default_sort = ('timestamp', True)

class TestAttemptAdminView(SecureModelView):
    column_list = ['user_id', 'test_id', 'question_id', 'is_correct', 'attempt_date']
    column_filters = ['is_correct']
    column_default_sort = ('attempt_date', True)

class ContentCategoryAdminView(SecureModelView):
    column_list = ['name', 'slug', 'icon', 'order']
    column_searchable_list = ['name', 'slug']

class ContentSubcategoryAdminView(SecureModelView):
    column_list = ['name', 'category_id', 'slug', 'icon', 'order']
    column_filters = ['category_id']
    column_searchable_list = ['name', 'slug']

class ContentTopicAdminView(SecureModelView):
    column_list = ['name', 'subcategory_id', 'slug', 'order', 'description']
    column_filters = ['subcategory_id']
    column_searchable_list = ['name', 'slug', 'description']
    form_overrides = {
        'description': CKTextAreaField
    }

class AssessmentCategoryAdminView(SecureModelView):
    column_list = ['name', 'slug', 'weight', 'min_questions', 'max_questions', 'is_dutch_specific']
    column_filters = ['is_dutch_specific']
    column_searchable_list = ['name', 'slug', 'description']
    form_overrides = {
        'description': CKTextAreaField
    }

class AssessmentQuestionAdminView(SecureModelView):
    column_list = ['question_text', 'category_id', 'question_type', 'difficulty_level', 'is_active']
    column_filters = ['category_id', 'question_type', 'difficulty_level', 'is_active']
    column_searchable_list = ['question_text', 'explanation']
    form_overrides = {
        'question_text': CKTextAreaField,
        'explanation': CKTextAreaField
    }

class ContentTemplateAdminView(SecureModelView):
    column_list = ['template_id', 'name', 'category', 'version', 'is_active', 'is_public']
    column_filters = ['category', 'is_active', 'is_public', 'is_system']
    column_searchable_list = ['template_id', 'name']

class ContentPageAdminView(SecureModelView):
    column_list = ['title', 'slug', 'content_type', 'status', 'is_published', 'created_at']
    column_filters = ['content_type', 'status', 'is_published', 'language']
    column_searchable_list = ['title', 'slug', 'description']
    form_overrides = {
        'description': CKTextAreaField,
        'content_data': CKTextAreaField,
        'page_metadata': CKTextAreaField
    }

class GrapesJSPageAdminView(SecureModelView):
    column_list = ['title', 'slug', 'user_id', 'is_published', 'is_template', 'created_at']
    column_filters = ['is_published', 'is_template', 'category']
    column_searchable_list = ['title', 'slug', 'description']
    form_overrides = {
        'description': CKTextAreaField,
        'html': CKTextAreaField,
        'css': CKTextAreaField,
        'components': CKTextAreaField,
        'styles': CKTextAreaField
    }

# Главная функция инициализации
def init_admin(app, db):
    admin = Admin(
        app,
        name='🎓 Dental Academy Admin',
        template_mode='bootstrap4',
        index_view=DashboardView(name='📊 Дашборд', url='/admin'),
        base_template='admin/master.html'
    )
    
    # Импорт моделей с проверкой существования
    try:
        from models import User
        admin.add_view(UserAdminView(User, db.session, name='👥 Пользователи', category='👥 Управление'))
    except ImportError:
        print("⚠️ User model not found")
    
    try:
        from models import LearningPath
        admin.add_view(LearningPathAdminView(LearningPath, db.session, name='📚 Пути обучения', category='📖 Образование'))
    except ImportError:
        print("⚠️ LearningPath model not found")
    
    try:
        from models import Subject
        admin.add_view(SubjectAdminView(Subject, db.session, name='📖 Предметы', category='📖 Образование'))
    except ImportError:
        print("⚠️ Subject model not found")
    
    try:
        from models import Module
        admin.add_view(ModuleAdminView(Module, db.session, name='📚 Модули', category='📖 Образование'))
    except ImportError:
        print("⚠️ Module model not found")
    
    try:
        from models import Lesson
        admin.add_view(LessonAdminView(Lesson, db.session, name='📖 Уроки', category='📖 Образование'))
    except ImportError:
        print("⚠️ Lesson model not found")
    
    try:
        from models import Test
        admin.add_view(TestAdminView(Test, db.session, name='✅ Тесты', category='🧪 Тестирование'))
    except ImportError:
        print("⚠️ Test model not found")
    
    try:
        from models import Question
        admin.add_view(QuestionAdminView(Question, db.session, name='❓ Вопросы', category='🧪 Тестирование'))
    except ImportError:
        print("⚠️ Question model not found")
    
    try:
        from models import TestAttempt
        admin.add_view(TestAttemptAdminView(TestAttempt, db.session, name='📋 Попытки тестов', category='🧪 Тестирование'))
    except ImportError:
        print("⚠️ TestAttempt model not found")
    
    try:
        from models import VirtualPatientScenario
        admin.add_view(VirtualPatientScenarioAdminView(VirtualPatientScenario, db.session, name='🏥 Виртуальные пациенты', category='🏥 Симуляция'))
    except ImportError:
        print("⚠️ VirtualPatientScenario model not found")
    
    try:
        from models import ForumTopic
        admin.add_view(ForumTopicAdminView(ForumTopic, db.session, name='💬 Темы форума', category='💬 Социальное'))
    except ImportError:
        print("⚠️ ForumTopic model not found")
    
    try:
        from models import Post
        admin.add_view(PostAdminView(Post, db.session, name='💬 Посты форума', category='💬 Социальное'))
    except ImportError:
        print("⚠️ Post model not found")
    
    try:
        from models import Achievement
        admin.add_view(AchievementAdminView(Achievement, db.session, name='🏆 Достижения', category='🎮 Геймификация'))
    except ImportError:
        print("⚠️ Achievement model not found")
    
    try:
        from models import UserAchievement
        admin.add_view(SecureModelView(UserAchievement, db.session, name='🏆 Достижения пользователей', category='🎮 Геймификация'))
    except ImportError:
        print("⚠️ UserAchievement model not found")
    
    try:
        from models import UserProgress
        admin.add_view(UserProgressAdminView(UserProgress, db.session, name='📊 Прогресс', category='📈 Аналитика'))
    except ImportError:
        print("⚠️ UserProgress model not found")
    
    try:
        from models import ContentCategory
        admin.add_view(ContentCategoryAdminView(ContentCategory, db.session, name='📁 Категории контента', category='📁 Контент'))
    except ImportError:
        print("⚠️ ContentCategory model not found")
    
    try:
        from models import ContentSubcategory
        admin.add_view(ContentSubcategoryAdminView(ContentSubcategory, db.session, name='📁 Подкатегории', category='📁 Контент'))
    except ImportError:
        print("⚠️ ContentSubcategory model not found")
    
    try:
        from models import ContentTopic
        admin.add_view(ContentTopicAdminView(ContentTopic, db.session, name='📁 Темы', category='📁 Контент'))
    except ImportError:
        print("⚠️ ContentTopic model not found")
    
    try:
        from models import AssessmentCategory
        admin.add_view(AssessmentCategoryAdminView(AssessmentCategory, db.session, name='📋 Категории оценки', category='📋 Оценка'))
    except ImportError:
        print("⚠️ AssessmentCategory model not found")
    
    try:
        from models import AssessmentQuestion
        admin.add_view(AssessmentQuestionAdminView(AssessmentQuestion, db.session, name='📋 Вопросы оценки', category='📋 Оценка'))
    except ImportError:
        print("⚠️ AssessmentQuestion model not found")
    
    try:
        from models import ContentTemplate
        admin.add_view(ContentTemplateAdminView(ContentTemplate, db.session, name='📝 Шаблоны контента', category='✏️ Редактор'))
    except ImportError:
        print("⚠️ ContentTemplate model not found")
    
    try:
        from models import ContentPage
        admin.add_view(ContentPageAdminView(ContentPage, db.session, name='📄 Страницы контента', category='✏️ Редактор'))
    except ImportError:
        print("⚠️ ContentPage model not found")
    
    try:
        from models import GrapesJSPage
        admin.add_view(GrapesJSPageAdminView(GrapesJSPage, db.session, name='🎨 GrapesJS страницы', category='✏️ Редактор'))
    except ImportError:
        print("⚠️ GrapesJSPage model not found")
    
    # Файловый менеджер
    uploads_path = op.join(op.dirname(__file__), '../static/uploads')
    if not op.exists(uploads_path):
        os.makedirs(uploads_path)
    admin.add_view(FileAdmin(uploads_path, '/static/uploads/', name='📁 Файлы', category='📁 Медиа'))
    
    # Ссылки
    admin.add_link(MenuLink(name='🏠 На сайт', url='/'))
    admin.add_link(MenuLink(name='📊 Аналитика', url='/analytics'))
    admin.add_link(MenuLink(name='🎨 Веб-редактор', url='/ru/admin/content-editor'))
    
    return admin 