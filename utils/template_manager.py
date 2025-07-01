# utils/template_manager.py - ИСПРАВЛЕННАЯ ВЕРСИЯ

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import current_app

logger = logging.getLogger(__name__)

class TemplateManager:
    """Менеджер для работы с шаблонами контента"""
    
    def __init__(self):
        # НЕ инициализируем пути здесь - только при первом использовании
        self._templates_file = None
        self._templates_cache = {}
        
    @property
    def templates_file(self):
        """Ленивая инициализация пути к файлу шаблонов"""
        if self._templates_file is None:
            self._templates_file = os.path.join(current_app.root_path, 'data', 'content_templates.json')
        return self._templates_file
    
    def load_templates_from_file(self) -> Dict[str, Any]:
        """Загружает шаблоны из JSON файла"""
        try:
            if os.path.exists(self.templates_file):
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Templates file not found: {self.templates_file}")
                return {}
        except Exception as e:
            logger.error(f"Error loading templates from file: {e}")
            return {}
    
    def save_templates_to_file(self, templates: Dict[str, Any]) -> bool:
        """Сохраняет шаблоны в JSON файл"""
        try:
            # Создаем директорию если не существует
            os.makedirs(os.path.dirname(self.templates_file), exist_ok=True)
            
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(templates, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Templates saved to {self.templates_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving templates to file: {e}")
            return False
    
    def get_template_by_id(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Получает шаблон по ID из базы данных"""
        try:
            from models import ContentTemplate
            template = ContentTemplate.query.filter_by(template_id=template_id).first()
            if template:
                return {
                    'id': template.id,
                    'template_id': template.template_id,
                    'name': template.name,
                    'description': template.description,
                    'category': template.category,
                    'structure': template.structure,
                    'template_metadata': template.template_metadata,
                    'tags': template.tags,
                    'is_system': template.is_system,
                    'language': template.language,
                    'created_at': template.created_at.isoformat() if template.created_at else None
                }
            return None
        except Exception as e:
            logger.error(f"Error getting template {template_id}: {e}")
            return None
    
    def get_all_templates(self, category: Optional[str] = None, language: str = 'en') -> List[Dict[str, Any]]:
        """Получает все шаблоны из базы данных"""
        try:
            from models import ContentTemplate
            query = ContentTemplate.query.filter_by(language=language)
            
            if category:
                query = query.filter_by(category=category)
            
            templates = query.all()
            result = []
            
            for template in templates:
                result.append({
                    'id': template.id,
                    'template_id': template.template_id,
                    'name': template.name,
                    'description': template.description,
                    'category': template.category,
                    'structure': template.structure,
                    'template_metadata': template.template_metadata,
                    'tags': template.tags,
                    'is_system': template.is_system,
                    'language': template.language,
                    'created_at': template.created_at.isoformat() if template.created_at else None
                })
            
            return result
        except Exception as e:
            logger.error(f"Error getting templates: {e}")
            return []
    
    def create_template(self, template_data: Dict[str, Any]) -> Optional[int]:
        """Создает новый шаблон в базе данных"""
        try:
            from models import ContentTemplate
            from extensions import db
            
            template = ContentTemplate(
                template_id=template_data.get('template_id'),
                name=template_data.get('name'),
                description=template_data.get('description', {}),
                category=template_data.get('category', 'general'),
                structure=template_data.get('structure', []),
                template_metadata=template_data.get('template_metadata', {}),
                tags=template_data.get('tags', []),
                is_system=template_data.get('is_system', False),
                language=template_data.get('language', 'en'),
                created_by=template_data.get('created_by')
            )
            
            db.session.add(template)
            db.session.commit()
            
            logger.info(f"Template created: {template.name} (ID: {template.id})")
            return template.id
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            return None
    
    def update_template(self, template_id: int, template_data: Dict[str, Any]) -> bool:
        """Обновляет существующий шаблон"""
        try:
            from models import ContentTemplate
            from extensions import db
            
            template = ContentTemplate.query.get(template_id)
            if not template:
                logger.warning(f"Template {template_id} not found")
                return False
            
            # Обновляем поля
            for field in ['name', 'description', 'category', 'language']:
                if field in template_data:
                    setattr(template, field, template_data[field])
            
            if 'structure' in template_data:
                template.structure = template_data['structure']  # Уже JSON
            
            if 'template_metadata' in template_data:
                template.template_metadata = template_data['template_metadata']  # Уже JSON
            
            if 'tags' in template_data:
                template.tags = template_data['tags']  # Уже JSON
            
            template.updated_at = datetime.utcnow()
            
            db.session.commit()
            logger.info(f"Template updated: {template.name} (ID: {template.id})")
            return True
        except Exception as e:
            logger.error(f"Error updating template {template_id}: {e}")
            return False
    
    def delete_template(self, template_id: int) -> bool:
        """Удаляет шаблон"""
        try:
            from models import ContentTemplate
            from extensions import db
            
            template = ContentTemplate.query.get(template_id)
            if not template:
                logger.warning(f"Template {template_id} not found")
                return False
            
            # Системные шаблоны нельзя удалять
            if template.is_system:
                logger.warning(f"Cannot delete system template: {template.name}")
                return False
            
            db.session.delete(template)
            db.session.commit()
            
            logger.info(f"Template deleted: {template.name} (ID: {template.id})")
            return True
        except Exception as e:
            logger.error(f"Error deleting template {template_id}: {e}")
            return False
    
    def import_templates_from_file(self) -> int:
        """Импортирует шаблоны из JSON файла в базу данных"""
        templates_data = self.load_templates_from_file()
        if not templates_data:
            return 0
        
        imported_count = 0
        
        for template_id, template_info in templates_data.items():
            try:
                # Проверяем, существует ли уже такой шаблон
                existing = self.get_template_by_id(template_id)
                if existing:
                    logger.info(f"Template {template_id} already exists, skipping")
                    continue
                
                # Создаем новый шаблон
                template_data = {
                    'template_id': template_id,
                    'name': template_info.get('name', template_id),
                    'description': template_info.get('description', ''),
                    'category': template_info.get('category', 'general'),
                    'structure': template_info.get('structure', []),
                    'template_metadata': template_info.get('template_metadata', {}),
                    'tags': template_info.get('tags', []),
                    'is_system': template_info.get('is_system', True),
                    'language': template_info.get('language', 'en')
                }
                
                if self.create_template(template_data):
                    imported_count += 1
                    
            except Exception as e:
                logger.error(f"Error importing template {template_id}: {e}")
        
        logger.info(f"Imported {imported_count} templates from file")
        return imported_count
    
    def export_templates_to_file(self, language: str = 'en') -> bool:
        """Экспортирует шаблоны из базы данных в JSON файл"""
        templates = self.get_all_templates(language=language)
        
        # Конвертируем в формат для JSON файла
        export_data = {}
        for template in templates:
            export_data[template['template_id']] = {
                'name': template['name'],
                'description': template['description'],
                'category': template['category'],
                'structure': template['structure'],
                'template_metadata': template['template_metadata'],
                'tags': template['tags'],
                'is_system': template['is_system'],
                'language': template['language']
            }
        
        return self.save_templates_to_file(export_data)


# Создаем глобальный экземпляр БЕЗ инициализации путей
template_manager = TemplateManager()