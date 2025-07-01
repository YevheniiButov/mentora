"""
Visual Builder Manager
Основная бизнес-логика для Visual Page Builder
"""

import json
import logging
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path
import os

from extensions import db
from models import VisualBuilderPage, VisualBuilderTemplate, VisualBuilderMedia, VisualBuilderVersion, User

logger = logging.getLogger(__name__)

class VisualBuilderManager:
    """Менеджер для работы с Visual Builder"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_page(self, user_id: int, title: str, content_data: Dict, 
                   language: str = 'en', template_id: Optional[int] = None) -> VisualBuilderPage:
        """Создать новую страницу"""
        try:
            # Генерируем slug из заголовка
            slug = self._generate_slug(title)
            
            # Создаем страницу
            page = VisualBuilderPage(
                title=title,
                slug=slug,
                content_data=json.dumps(content_data, ensure_ascii=False),
                language=language,
                template_id=template_id,
                created_by=user_id
            )
            
            db.session.add(page)
            db.session.commit()
            
            self.logger.info(f"Created Visual Builder page: {page.id} by user {user_id}")
            return page
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creating Visual Builder page: {e}")
            raise
    
    def update_page(self, page_id: int, user_id: int, **kwargs) -> VisualBuilderPage:
        """Обновить страницу"""
        try:
            page = VisualBuilderPage.query.get_or_404(page_id)
            
            # Обновляем поля
            for key, value in kwargs.items():
                if hasattr(page, key):
                    if key in ['content_data', 'page_settings'] and isinstance(value, dict):
                        setattr(page, key, json.dumps(value, ensure_ascii=False))
                    else:
                        setattr(page, key, value)
            
            page.updated_at = datetime.now(timezone.utc)
            page.updated_by = user_id
            
            db.session.commit()
            
            self.logger.info(f"Updated Visual Builder page: {page_id} by user {user_id}")
            return page
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error updating Visual Builder page {page_id}: {e}")
            raise
    
    def get_page(self, page_id: int) -> Optional[VisualBuilderPage]:
        """Получить страницу по ID"""
        try:
            return VisualBuilderPage.query.get(page_id)
        except Exception as e:
            self.logger.error(f"Error getting Visual Builder page {page_id}: {e}")
            return None
    
    def get_page_by_slug(self, slug: str, language: str = 'en') -> Optional[VisualBuilderPage]:
        """Получить страницу по slug и языку"""
        try:
            return VisualBuilderPage.query.filter_by(slug=slug, language=language).first()
        except Exception as e:
            self.logger.error(f"Error getting Visual Builder page by slug {slug}: {e}")
            return None
    
    def list_pages(self, user_id: Optional[int] = None, language: str = 'en', 
                  status: Optional[str] = None, limit: Optional[int] = None) -> List[VisualBuilderPage]:
        """Получить список страниц"""
        try:
            query = VisualBuilderPage.query.filter_by(language=language)
            
            if user_id:
                query = query.filter_by(created_by=user_id)
            
            if status:
                query = query.filter_by(status=status)
            
            query = query.order_by(VisualBuilderPage.updated_at.desc())
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
            
        except Exception as e:
            self.logger.error(f"Error listing Visual Builder pages: {e}")
            return []
    
    def delete_page(self, page_id: int, user_id: int) -> bool:
        """Удалить страницу"""
        try:
            page = VisualBuilderPage.query.get_or_404(page_id)
            
            # Проверяем права доступа
            if page.created_by != user_id:
                raise PermissionError("User can only delete their own pages")
            
            db.session.delete(page)
            db.session.commit()
            
            self.logger.info(f"Deleted Visual Builder page: {page_id} by user {user_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error deleting Visual Builder page {page_id}: {e}")
            return False
    
    def publish_page(self, page_id: int, user_id: int) -> bool:
        """Опубликовать страницу"""
        try:
            page = VisualBuilderPage.query.get_or_404(page_id)
            page.publish()
            page.updated_by = user_id
            page.updated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            self.logger.info(f"Published Visual Builder page: {page_id} by user {user_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error publishing Visual Builder page {page_id}: {e}")
            return False
    
    def create_version(self, page_id: int, user_id: int, version_notes: Optional[str] = None) -> Optional[VisualBuilderVersion]:
        """Создать новую версию страницы"""
        try:
            page = VisualBuilderPage.query.get_or_404(page_id)
            version = page.create_version(user_id, version_notes)
            
            db.session.add(version)
            db.session.commit()
            
            self.logger.info(f"Created version for Visual Builder page: {page_id} by user {user_id}")
            return version
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creating version for Visual Builder page {page_id}: {e}")
            return None
    
    def restore_version(self, version_id: int, user_id: int) -> bool:
        """Восстановить версию страницы"""
        try:
            version = VisualBuilderVersion.query.get_or_404(version_id)
            page = version.vb_page
            
            # Восстанавливаем данные версии
            version.restore_to_page(page)
            page.updated_by = user_id
            page.updated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            self.logger.info(f"Restored version {version_id} for Visual Builder page: {page.id} by user {user_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error restoring version {version_id}: {e}")
            return False
    
    def validate_content_data(self, content_data: Dict) -> Dict[str, Any]:
        """Валидация данных контента"""
        errors = []
        warnings = []
        
        try:
            # Проверяем структуру
            if not isinstance(content_data, dict):
                errors.append("Content data must be a dictionary")
                return {'valid': False, 'errors': errors, 'warnings': warnings}
            
            # Проверяем наличие элементов
            if 'elements' not in content_data:
                errors.append("Content data must contain 'elements' array")
            else:
                elements = content_data['elements']
                if not isinstance(elements, list):
                    errors.append("Elements must be an array")
                else:
                    # Проверяем каждый элемент
                    for i, element in enumerate(elements):
                        element_errors = self._validate_element(element, i)
                        errors.extend(element_errors)
            
            # Проверяем настройки
            if 'settings' in content_data:
                settings = content_data['settings']
                if not isinstance(settings, dict):
                    errors.append("Settings must be a dictionary")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings
            }
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
    
    def _validate_element(self, element: Dict, index: int) -> List[str]:
        """Валидация отдельного элемента"""
        errors = []
        
        # Проверяем обязательные поля
        if 'id' not in element:
            errors.append(f"Element {index}: missing 'id' field")
        
        if 'type' not in element:
            errors.append(f"Element {index}: missing 'type' field")
        
        if 'content' not in element:
            errors.append(f"Element {index}: missing 'content' field")
        
        # Проверяем тип элемента
        if 'type' in element:
            valid_types = ['text', 'heading', 'image', 'video', 'button', 'form', 'quiz', 'hero', 'feature']
            if element['type'] not in valid_types:
                errors.append(f"Element {index}: invalid type '{element['type']}'")
        
        return errors
    
    def sanitize_content_data(self, content_data: Dict) -> Dict:
        """Санитизация данных контента"""
        try:
            # Создаем копию для безопасного изменения
            sanitized = json.loads(json.dumps(content_data))
            
            # Очищаем HTML в текстовых полях
            if 'elements' in sanitized:
                for element in sanitized['elements']:
                    if 'content' in element:
                        element['content'] = self._sanitize_element_content(element['content'])
            
            return sanitized
            
        except Exception as e:
            self.logger.error(f"Error sanitizing content data: {e}")
            return content_data
    
    def _sanitize_element_content(self, content: Any) -> Any:
        """Санитизация контента элемента"""
        if isinstance(content, dict):
            sanitized = {}
            for key, value in content.items():
                if isinstance(value, str):
                    # Очищаем HTML теги, оставляя только безопасные
                    sanitized[key] = self._clean_html(value)
                else:
                    sanitized[key] = self._sanitize_element_content(value)
            return sanitized
        elif isinstance(content, list):
            return [self._sanitize_element_content(item) for item in content]
        elif isinstance(content, str):
            return self._clean_html(content)
        else:
            return content
    
    def _clean_html(self, html: str) -> str:
        """Очистка HTML от потенциально опасных тегов"""
        # Разрешенные теги
        allowed_tags = {
            'p', 'br', 'strong', 'b', 'em', 'i', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'span', 'div'
        }
        
        # Разрешенные атрибуты
        allowed_attrs = {
            'class', 'id', 'style', 'title', 'alt', 'src', 'href', 'target'
        }
        
        # Простая очистка (в продакшене лучше использовать библиотеку типа bleach)
        import re
        
        # Удаляем скрипты
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)
        
        # Удаляем опасные атрибуты
        html = re.sub(r'on\w+\s*=', '', html, flags=re.IGNORECASE)
        html = re.sub(r'javascript:', '', html, flags=re.IGNORECASE)
        
        return html
    
    def _generate_slug(self, title: str) -> str:
        """Генерация slug из заголовка"""
        # Транслитерация кириллицы
        translit_map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
        }
        
        # Приводим к нижнему регистру и транслитерируем
        slug = title.lower()
        for cyr, lat in translit_map.items():
            slug = slug.replace(cyr, lat)
        
        # Заменяем все кроме букв и цифр на дефисы
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        
        # Убираем дефисы в начале и конце
        slug = slug.strip('-')
        
        # Ограничиваем длину
        if len(slug) > 100:
            slug = slug[:100].rstrip('-')
        
        # Добавляем timestamp если slug пустой
        if not slug:
            slug = f"page-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        return slug
    
    def get_page_statistics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Получить статистику страниц"""
        try:
            query = VisualBuilderPage.query
            
            if user_id:
                query = query.filter_by(created_by=user_id)
            
            total_pages = query.count()
            published_pages = query.filter_by(is_published=True).count()
            draft_pages = query.filter_by(status='draft').count()
            
            # Статистика по языкам
            language_stats = db.session.query(
                VisualBuilderPage.language,
                db.func.count(VisualBuilderPage.id)
            ).group_by(VisualBuilderPage.language).all()
            
            # Статистика по шаблонам
            template_stats = db.session.query(
                VisualBuilderTemplate.name,
                db.func.count(VisualBuilderPage.id)
            ).join(VisualBuilderPage).group_by(VisualBuilderTemplate.name).all()
            
            return {
                'total_pages': total_pages,
                'published_pages': published_pages,
                'draft_pages': draft_pages,
                'language_stats': dict(language_stats),
                'template_stats': dict(template_stats)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting page statistics: {e}")
            return {}
    
    def generate_html_export(self, content_data: Dict, page_title: str) -> str:
        """Генерировать HTML для экспорта страницы"""
        try:
            html_parts = []
            
            # Начало HTML документа
            html_parts.append(f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
            line-height: 1.6; 
            color: #333; 
            background: #fff;
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px; 
        }}
        .element {{ 
            margin: 1rem 0; 
            padding: 1rem; 
        }}
        .element-content {{ 
            padding: 1rem; 
        }}
        .hero-section {{
            text-align: center;
            padding: 4rem 2rem;
            background: linear-gradient(135deg, #3ECDC1 0%, #2ba89e 100%);
            color: white;
            border-radius: 12px;
            margin: 2rem 0;
        }}
        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin: 2rem 0;
        }}
        .feature-item {{
            text-align: center;
            padding: 2rem;
            background: #f8f9fa;
            border-radius: 12px;
        }}
        .feature-icon {{
            font-size: 3rem;
            margin-bottom: 1rem;
        }}
        .quiz-container {{
            background: #f8f9fa;
            padding: 2rem;
            border-radius: 12px;
            margin: 2rem 0;
        }}
        .quiz-option {{
            display: block;
            margin: 0.5rem 0;
            padding: 0.75rem;
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .quiz-option:hover {{
            border-color: #3ECDC1;
            background: #f0f9ff;
        }}
        .form-container {{
            max-width: 500px;
            margin: 2rem auto;
            padding: 2rem;
            background: #f8f9fa;
            border-radius: 12px;
        }}
        .form-group {{
            margin-bottom: 1rem;
        }}
        .form-label {{
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }}
        .form-input {{
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 1rem;
        }}
        .btn {{
            padding: 0.75rem 1.5rem;
            background: #3ECDC1;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn:hover {{
            background: #2ba89e;
            transform: translateY(-1px);
        }}
        .image-container {{
            text-align: center;
            margin: 2rem 0;
        }}
        .image-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .video-container {{
            position: relative;
            width: 100%;
            max-width: 800px;
            margin: 2rem auto;
        }}
        .video-container iframe {{
            width: 100%;
            height: 400px;
            border-radius: 8px;
        }}
        @media (max-width: 768px) {{
            .container {{ padding: 10px; }}
            .hero-section {{ padding: 2rem 1rem; }}
            .feature-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">""")
            
            # Обрабатываем элементы контента
            if 'elements' in content_data:
                for element in content_data['elements']:
                    element_type = element.get('type', 'text')
                    element_content = element.get('content', {})
                    
                    if element_type == 'hero':
                        html_parts.append(f"""
        <div class="hero-section">
            <h1>{element_content.get('title', 'Заголовок')}</h1>
            <p>{element_content.get('subtitle', 'Подзаголовок')}</p>
            <div style="margin-top: 2rem;">
                <button class="btn">{element_content.get('button_text', 'Начать')}</button>
            </div>
        </div>""")
                    
                    elif element_type == 'feature':
                        html_parts.append(f"""
        <div class="feature-grid">
            <div class="feature-item">
                <div class="feature-icon">⚡</div>
                <h3>{element_content.get('title1', 'Преимущество 1')}</h3>
                <p>{element_content.get('description1', 'Описание преимущества')}</p>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🛡️</div>
                <h3>{element_content.get('title2', 'Преимущество 2')}</h3>
                <p>{element_content.get('description2', 'Описание преимущества')}</p>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🎨</div>
                <h3>{element_content.get('title3', 'Преимущество 3')}</h3>
                <p>{element_content.get('description3', 'Описание преимущества')}</p>
            </div>
        </div>""")
                    
                    elif element_type == 'quiz':
                        html_parts.append(f"""
        <div class="quiz-container">
            <h3>{element_content.get('question', 'Вопрос теста')}</h3>
            <div class="quiz-options">
                <label class="quiz-option">
                    <input type="radio" name="quiz" value="1">
                    {element_content.get('option1', 'Вариант 1')}
                </label>
                <label class="quiz-option">
                    <input type="radio" name="quiz" value="2">
                    {element_content.get('option2', 'Вариант 2')}
                </label>
                <label class="quiz-option">
                    <input type="radio" name="quiz" value="3">
                    {element_content.get('option3', 'Вариант 3')}
                </label>
            </div>
        </div>""")
                    
                    elif element_type == 'form':
                        html_parts.append(f"""
        <div class="form-container">
            <h3>{element_content.get('title', 'Форма обратной связи')}</h3>
            <form>
                <div class="form-group">
                    <label class="form-label">Имя:</label>
                    <input type="text" class="form-input" placeholder="Введите ваше имя">
                </div>
                <div class="form-group">
                    <label class="form-label">Email:</label>
                    <input type="email" class="form-input" placeholder="your@email.com">
                </div>
                <div class="form-group">
                    <label class="form-label">Сообщение:</label>
                    <textarea class="form-input" rows="4" placeholder="Введите ваше сообщение"></textarea>
                </div>
                <button type="submit" class="btn">Отправить</button>
            </form>
        </div>""")
                    
                    elif element_type == 'image':
                        if 'src' in element_content:
                            html_parts.append(f"""
        <div class="image-container">
            <img src="{element_content['src']}" alt="{element_content.get('alt', 'Изображение')}">
        </div>""")
                    
                    elif element_type == 'video':
                        if 'src' in element_content:
                            html_parts.append(f"""
        <div class="video-container">
            <iframe src="{element_content['src']}" frameborder="0" allowfullscreen></iframe>
        </div>""")
                    
                    else:
                        # Обычный текстовый элемент
                        text_content = element_content.get('text', 'Текст элемента')
                        html_parts.append(f"""
        <div class="element">
            <div class="element-content">
                {text_content}
            </div>
        </div>""")
            
            # Закрытие HTML документа
            html_parts.append("""
    </div>
</body>
</html>""")
            
            return '\n'.join(html_parts)
            
        except Exception as e:
            self.logger.error(f"Error generating HTML export: {e}")
            return f"""<!DOCTYPE html>
<html>
<head>
    <title>{page_title}</title>
</head>
<body>
    <h1>{page_title}</h1>
    <p>Ошибка генерации контента</p>
</body>
</html>"""

# Создаем глобальный экземпляр менеджера
visual_builder_manager = VisualBuilderManager() 