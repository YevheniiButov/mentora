import functools
import threading
from flask import request, g, current_app, render_template, session, redirect, url_for, Blueprint, after_this_request
from werkzeug.wrappers import Request, Response
from jinja2 import TemplateNotFound
from models import EditablePageTemplate, User
from flask_login import current_user
import hashlib
import time

# --- 1. TemplateOverrideMiddleware ---
class TemplateOverrideMiddleware:
    """
    Перехватывает рендеринг шаблонов и подменяет их на отредактированные версии,
    если таковые есть. Использует кэш для производительности и fallback на оригинал.
    """
    _template_cache = {}
    _cache_lock = threading.Lock()
    _cache_ttl = 60  # секунд

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        # Monkey-patch render_template
        original_render = render_template
        middleware = self

        @functools.wraps(original_render)
        def custom_render_template(template_name, *args, **kwargs):
            lang = getattr(g, 'lang', 'en')
            cache_key = f"{template_name}:{lang}"
            now = time.time()
            # Кэш
            with middleware._cache_lock:
                cached = middleware._template_cache.get(cache_key)
                if cached and now - cached['ts'] < middleware._cache_ttl:
                    if cached['content']:
                        return cached['content']
            # Проверяем наличие отредактированного шаблона
            edited = EditablePageTemplate.get_by_path_and_language(template_name, lang)
            if edited and edited.is_live:
                try:
                    content = original_render_string(edited.get_effective_content(), *args, **kwargs)
                    with middleware._cache_lock:
                        middleware._template_cache[cache_key] = {'content': content, 'ts': now}
                    return content
                except Exception:
                    pass  # fallback
            # Fallback на оригинал
            try:
                content = original_render(template_name, *args, **kwargs)
                with middleware._cache_lock:
                    middleware._template_cache[cache_key] = {'content': content, 'ts': now}
                return content
            except TemplateNotFound:
                return f"<!-- Template not found: {template_name} -->"
        # Monkey-patch
        app.jinja_env.globals['render_template'] = custom_render_template
        app.render_template = custom_render_template

# --- 2. AssetInjectionMiddleware ---
class AssetInjectionMiddleware:
    """
    Инъекция кастомных CSS/JS для отредактированных страниц, поддержка версии и CDN.
    """
    def __init__(self, app=None, cdn_url=None):
        self.cdn_url = cdn_url
        if app:
            self.init_app(app)

    def init_app(self, app):
        @app.after_request
        def inject_assets(response):
            if response.content_type and 'text/html' in response.content_type:
                # Проверяем, есть ли кастомные ассеты для текущей страницы
                template = getattr(g, 'current_template', None)
                if template and isinstance(template, EditablePageTemplate):
                    css_hash = hashlib.md5((template.css_overrides or '').encode()).hexdigest()[:8]
                    js_hash = hashlib.md5((template.js_modifications or '').encode()).hexdigest()[:8]
                    css_url = f"/static/edited/{template.id}.css?v={css_hash}"
                    js_url = f"/static/edited/{template.id}.js?v={js_hash}"
                    if self.cdn_url:
                        css_url = self.cdn_url + css_url
                        js_url = self.cdn_url + js_url
                    # Вставляем ссылки в <head>
                    html = response.get_data(as_text=True)
                    head_idx = html.find('</head>')
                    if head_idx != -1:
                        inject = f'<link rel="stylesheet" href="{css_url}">\n<script src="{js_url}" defer></script>\n'
                        html = html[:head_idx] + inject + html[head_idx:]
                        response.set_data(html)
            return response

# --- 3. EditorAuthMiddleware ---
class EditorAuthMiddleware:
    """
    Контроль доступа к редактору, интеграция с Flask-Login, аудит.
    """
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        @app.before_request
        def check_editor_access():
            # Только для editor/admin страниц
            if request.path.startswith('/admin/content-editor'):
                if not current_user.is_authenticated:
                    return redirect(url_for('auth.login', next=request.url))
                if not getattr(current_user, 'is_admin', False):
                    return "Доступ запрещён", 403
                # Аудит
                g.editor_audit = {
                    'user_id': current_user.id,
                    'username': current_user.username,
                    'ip': request.remote_addr,
                    'ts': time.time(),
                    'action': request.path
                }

# --- 4. CacheInvalidationMiddleware ---
class CacheInvalidationMiddleware:
    """
    Инвалидирует кэш шаблонов/ассетов при изменениях через редактор.
    """
    def __init__(self, app=None, template_mw=None):
        self.template_mw = template_mw
        if app:
            self.init_app(app)

    def init_app(self, app):
        @app.after_request
        def invalidate_cache(response):
            # Если был POST/PUT/DELETE на editor API — сбрасываем кэш шаблонов
            if request.path.startswith('/admin/content-editor/api/') and request.method in ('POST', 'PUT', 'DELETE'):
                if self.template_mw:
                    with self.template_mw._cache_lock:
                        self.template_mw._template_cache.clear()
            return response

# --- Вспомогательная функция для рендера строк ---
def original_render_string(source, *args, **kwargs):
    """Рендерит шаблон из строки с поддержкой Jinja2"""
    from flask import render_template_string
    return render_template_string(source, *args, **kwargs)

# --- Интеграция с Flask app factory ---
def register_editor_middlewares(app, cdn_url=None):
    """Регистрирует все middleware для редактора"""
    template_mw = TemplateOverrideMiddleware()
    template_mw.init_app(app)
    AssetInjectionMiddleware(app, cdn_url=cdn_url)
    EditorAuthMiddleware(app)
    CacheInvalidationMiddleware(app, template_mw=template_mw) 