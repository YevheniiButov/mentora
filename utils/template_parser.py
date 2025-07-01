#!/usr/bin/env python3
"""
Jinja2 to GrapesJS Template Converter
Конвертер шаблонов Jinja2 в формат GrapesJS

This module provides utilities for converting existing Jinja2 templates
to editable GrapesJS format while preserving template logic and functionality.
"""

import re
import os
import json
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from urllib.parse import urlparse
import logging

# Настройка логирования / Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_sets_to_lists(obj):
    """
    Рекурсивно конвертирует все set в list для JSON сериализации
    Recursively convert all sets to lists for JSON serialization
    
    Args:
        obj: Объект для конвертации / Object to convert
        
    Returns:
        Объект с конвертированными set в list / Object with converted sets to lists
    """
    if isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, dict):
        return {key: convert_sets_to_lists(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_sets_to_lists(item) for item in obj]
    else:
        return obj


class Jinja2ToGrapesJSConverter:
    """
    Конвертер Jinja2 шаблонов в формат GrapesJS
    Jinja2 to GrapesJS template converter
    
    Позволяет конвертировать существующие Jinja2 шаблоны в редактируемый
    формат GrapesJS, сохраняя при этом всю логику шаблонов.
    """
    
    def __init__(self, templates_dir: str = "templates", static_dir: str = "static"):
        """
        Инициализация конвертера / Initialize converter
        
        Args:
            templates_dir (str): Путь к папке шаблонов / Path to templates directory
            static_dir (str): Путь к папке статических файлов / Path to static files directory
        """
        self.templates_dir = Path(templates_dir)
        self.static_dir = Path(static_dir)
        
        # Регулярные выражения для парсинга / Regular expressions for parsing
        self.jinja_patterns = {
            'extends': r'{%\s*extends\s+["\']([^"\']+)["\']\s*%}',
            'include': r'{%\s*include\s+["\']([^"\']+)["\']\s*%}',
            'block': r'{%\s*block\s+(\w+)\s*%}(.*?){%\s*endblock\s*%}',
            'for_loop': r'{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%}(.*?){%\s*endfor\s*%}',
            'if_condition': r'{%\s*if\s+(.*?)\s*%}(.*?){%\s*endif\s*%}',
            'variable': r'{{\s*([^}]+)\s*}}',
            'translation': r'{{\s*t\(["\']([^"\']+)["\'](?:,\s*(\w+))?\)\s*}}',
            'url_for': r'{{\s*url_for\(["\']([^"\']+)["\'](?:,\s*([^)]+))?\)\s*}}',
            'csrf_token': r'{{\s*csrf_token\(\)\s*}}',
        }
        
        # CSS переменные проекта / Project CSS variables
        self.css_variables = {
            '--subject-view-bg': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            '--text-primary': '#333333',
            '--bg-primary': '#ffffff',
            '--subject-view-border': 'rgba(255, 255, 255, 0.2)',
            '--subject-view-text': 'rgba(255, 255, 255, 0.9)',
            '--subject-view-button-bg': 'rgba(255, 255, 255, 0.1)',
            '--subject-view-button-text': 'white',
            '--category-knowledge': 'linear-gradient(135deg, #3498db, #2980b9)',
            '--category-communication': 'linear-gradient(135deg, #9b59b6, #8e44ad)',
            '--category-preclinical': 'linear-gradient(135deg, #1abc9c, #16a085)',
            '--category-workstation': 'linear-gradient(135deg, #e74c3c, #c0392b)',
            '--category-bi-toets': 'linear-gradient(135deg, #f39c12, #e67e22)',
            '--category-virtual-patients': 'linear-gradient(135deg, #667eea, #764ba2)',
        }
        
        # Поддерживаемые языки / Supported languages
        self.supported_languages = ['en', 'ru', 'nl', 'es', 'pt', 'uk', 'fa', 'tr', 'ar']
        
        # Кэш для CSS файлов / Cache for CSS files
        self._css_cache = {}
    
    def parse_template(self, template_path: str) -> Dict[str, Any]:
        """
        Парсинг Jinja2 шаблона и конвертация в GrapesJS формат
        Parse Jinja2 template and convert to GrapesJS format
        
        Args:
            template_path (str): Путь к шаблону / Path to template
            
        Returns:
            Dict[str, Any]: Структура данных для GrapesJS / GrapesJS data structure
        """
        try:
            full_path = self.templates_dir / template_path
            
            if not full_path.exists():
                raise FileNotFoundError(f"Template not found: {template_path}")
            
            # Читаем содержимое шаблона / Read template content
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Определяем язык контента / Detect content language
            language = self.detect_language(content)
            
            # Извлекаем CSS переменные / Extract CSS variables
            css_vars = self.extract_css_variables(content)
            
            # Сохраняем Jinja2 логику / Preserve Jinja2 logic
            preserved_logic = self.preserve_jinja_logic(content)
            
            # Создаем редактируемые компоненты / Create editable components
            components = self.create_editable_components(content)
            
            # Анализируем структуру шаблона / Analyze template structure
            template_structure = self._analyze_template_structure(content)
            
            return {
                'template_path': template_path,
                'language': language,
                'css_variables': css_vars,
                'preserved_logic': preserved_logic,
                'components': components,
                'structure': template_structure,
                'original_content': content,
                'metadata': {
                    'file_size': len(content),
                    'lines_count': content.count('\n') + 1,
                    'has_extends': bool(re.search(self.jinja_patterns['extends'], content)),
                    'has_includes': bool(re.search(self.jinja_patterns['include'], content)),
                    'blocks_count': len(re.findall(self.jinja_patterns['block'], content, re.DOTALL)),
                    'variables_count': len(re.findall(self.jinja_patterns['variable'], content)),
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing template {template_path}: {e}")
            raise
    
    def extract_css_variables(self, css_content: str) -> Dict[str, str]:
        """
        Извлечение CSS переменных из содержимого
        Extract CSS variables from content
        
        Args:
            css_content (str): CSS содержимое / CSS content
            
        Returns:
            Dict[str, str]: Словарь CSS переменных / Dictionary of CSS variables
        """
        variables = {}
        
        # Ищем CSS переменные в содержимом / Find CSS variables in content
        css_var_pattern = r'--([^:]+):\s*([^;]+);'
        matches = re.findall(css_var_pattern, css_content)
        
        for name, value in matches:
            variables[f'--{name.strip()}'] = value.strip()
        
        # Добавляем стандартные переменные проекта / Add standard project variables
        variables.update(self.css_variables)
        
        # Ищем ссылки на CSS файлы и извлекаем переменные / Find CSS file references and extract variables
        css_links = re.findall(r'href=["\']([^"\']*\.css)["\']', css_content)
        
        # Исправление: приводим к списку, если вдруг css_links оказался set
        css_links = list(css_links) if isinstance(css_links, set) else css_links
        
        for css_link in css_links:
            if css_link.startswith('/static/'):
                css_file_path = self.static_dir / css_link.replace('/static/', '')
                if css_file_path.exists():
                    css_vars = self._extract_css_variables_from_file(css_file_path)
                    variables.update(css_vars)
        
        return variables
    
    def _extract_css_variables_from_file(self, css_file_path: Path) -> Dict[str, str]:
        """
        Извлечение CSS переменных из файла
        Extract CSS variables from file
        
        Args:
            css_file_path (Path): Путь к CSS файлу / Path to CSS file
            
        Returns:
            Dict[str, str]: Словарь CSS переменных / Dictionary of CSS variables
        """
        if css_file_path in self._css_cache:
            return self._css_cache[css_file_path]
        
        variables = {}
        
        try:
            with open(css_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ищем CSS переменные / Find CSS variables
            css_var_pattern = r'--([^:]+):\s*([^;]+);'
            matches = re.findall(css_var_pattern, content)
            
            for name, value in matches:
                variables[f'--{name.strip()}'] = value.strip()
            
            # Кэшируем результат / Cache result
            self._css_cache[css_file_path] = variables
            
        except Exception as e:
            logger.warning(f"Error reading CSS file {css_file_path}: {e}")
        
        return variables
    
    def create_editable_components(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Создание редактируемых компонентов из HTML содержимого
        Create editable components from HTML content
        
        Args:
            html_content (str): HTML содержимое / HTML content
            
        Returns:
            List[Dict[str, Any]]: Список компонентов GrapesJS / List of GrapesJS components
        """
        components = []
        
        # Удаляем Jinja2 блоки для анализа HTML / Remove Jinja2 blocks for HTML analysis
        clean_html = re.sub(r'{%[^%]*%}', '', html_content)
        clean_html = re.sub(r'{{[^}]*}}', '', clean_html)
        
        # Разбиваем на секции / Split into sections
        sections = self._split_into_sections(clean_html)
        
        for i, section in enumerate(sections):
            if section.strip():
                component = self._create_component_from_section(section, i)
                if component:
                    components.append(component)
        
        return components
    
    def _split_into_sections(self, html_content: str) -> List[str]:
        """
        Разбиение HTML на секции
        Split HTML into sections
        
        Args:
            html_content (str): HTML содержимое / HTML content
            
        Returns:
            List[str]: Список секций / List of sections
        """
        # Разбиваем по основным блокам / Split by main blocks
        sections = []
        
        # Ищем основные контейнеры / Find main containers
        container_patterns = [
            r'<div[^>]*class="[^"]*container[^"]*"[^>]*>(.*?)</div>',
            r'<section[^>]*>(.*?)</section>',
            r'<main[^>]*>(.*?)</main>',
            r'<header[^>]*>(.*?)</header>',
            r'<footer[^>]*>(.*?)</footer>',
        ]
        
        for pattern in container_patterns:
            matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
            sections.extend(matches)
        
        # Если не найдены контейнеры, разбиваем по div / If no containers found, split by div
        if not sections:
            sections = re.split(r'<div[^>]*>', html_content)
        
        return [s.strip() for s in sections if s.strip()]
    
    def _create_component_from_section(self, section: str, index: int) -> Optional[Dict[str, Any]]:
        """
        Создание компонента из секции
        Create component from section
        
        Args:
            section (str): HTML секция / HTML section
            index (int): Индекс секции / Section index
            
        Returns:
            Optional[Dict[str, Any]]: Компонент GrapesJS или None / GrapesJS component or None
        """
        if not section.strip():
            return None
        
        # Определяем тип компонента / Determine component type
        component_type = self._determine_component_type(section)
        
        # Извлекаем стили / Extract styles
        styles = self._extract_styles_from_section(section)
        
        # Извлекаем атрибуты / Extract attributes
        attributes = self._extract_attributes_from_section(section)
        
        return {
            'id': f'component_{index}',
            'type': component_type,
            'content': section,
            'styles': styles,
            'attributes': attributes,
            'editable': True,
            'draggable': True,
            'droppable': True,
            'category': 'content',
        }
    
    def _determine_component_type(self, section: str) -> str:
        """
        Определение типа компонента
        Determine component type
        
        Args:
            section (str): HTML секция / HTML section
            
        Returns:
            str: Тип компонента / Component type
        """
        section_lower = section.lower()
        
        if '<header' in section_lower:
            return 'header'
        elif '<footer' in section_lower:
            return 'footer'
        elif '<nav' in section_lower:
            return 'navigation'
        elif '<form' in section_lower:
            return 'form'
        elif '<table' in section_lower:
            return 'table'
        elif '<ul' in section_lower or '<ol' in section_lower:
            return 'list'
        elif '<img' in section_lower:
            return 'image'
        elif '<button' in section_lower:
            return 'button'
        elif '<input' in section_lower:
            return 'input'
        else:
            return 'div'
    
    def _extract_styles_from_section(self, section: str) -> Dict[str, str]:
        """
        Извлечение стилей из секции
        Extract styles from section
        
        Args:
            section (str): HTML секция / HTML section
            
        Returns:
            Dict[str, str]: Словарь стилей / Dictionary of styles
        """
        styles = {}
        
        # Ищем inline стили / Find inline styles
        style_pattern = r'style=["\']([^"\']*)["\']'
        matches = re.findall(style_pattern, section)
        
        for style_string in matches:
            style_pairs = style_string.split(';')
            for pair in style_pairs:
                if ':' in pair:
                    key, value = pair.split(':', 1)
                    styles[key.strip()] = value.strip()
        
        return styles
    
    def _extract_attributes_from_section(self, section: str) -> Dict[str, str]:
        """
        Извлечение атрибутов из секции
        Extract attributes from section
        
        Args:
            section (str): HTML секция / HTML section
            
        Returns:
            Dict[str, str]: Словарь атрибутов / Dictionary of attributes
        """
        attributes = {}
        
        # Ищем атрибуты в первом теге / Find attributes in first tag
        tag_pattern = r'<(\w+)([^>]*)>'
        match = re.search(tag_pattern, section)
        
        if match:
            tag_attrs = match.group(2)
            attr_pattern = r'(\w+)=["\']([^"\']*)["\']'
            attr_matches = re.findall(attr_pattern, tag_attrs)
            
            for name, value in attr_matches:
                if name != 'style':  # Исключаем стили / Exclude styles
                    attributes[name] = value
        
        return attributes
    
    def preserve_jinja_logic(self, content: str) -> str:
        """
        Сохранение Jinja2 логики в виде data-атрибутов
        Preserve Jinja2 logic as data attributes
        
        Args:
            content (str): Исходное содержимое / Original content
            
        Returns:
            str: Содержимое с сохраненной логикой / Content with preserved logic
        """
        preserved_content = content
        
        # Сохраняем extends / Preserve extends
        extends_matches = re.findall(self.jinja_patterns['extends'], content)
        for template in extends_matches:
            preserved_content = preserved_content.replace(
                f'{{% extends "{template}" %}}',
                f'<div data-jinja-extends="{template}" style="display: none;"></div>'
            )
        
        # Сохраняем includes / Preserve includes
        include_matches = re.findall(self.jinja_patterns['include'], content)
        for template in include_matches:
            preserved_content = preserved_content.replace(
                f'{{% include "{template}" %}}',
                f'<div data-jinja-include="{template}" style="display: none;"></div>'
            )
        
        # Сохраняем блоки / Preserve blocks
        block_matches = re.findall(self.jinja_patterns['block'], content, re.DOTALL)
        for block_name, block_content in block_matches:
            preserved_content = preserved_content.replace(
                f'{{% block {block_name} %}}{block_content}{{% endblock %}}',
                f'<div data-jinja-block="{block_name}">{block_content}</div>'
            )
        
        # Сохраняем циклы / Preserve loops
        for_matches = re.findall(self.jinja_patterns['for_loop'], content, re.DOTALL)
        for var, collection, loop_content in for_matches:
            preserved_content = preserved_content.replace(
                f'{{% for {var} in {collection} %}}{loop_content}{{% endfor %}}',
                f'<div data-jinja-for="{var} in {collection}">{loop_content}</div>'
            )
        
        # Сохраняем условия / Preserve conditions
        if_matches = re.findall(self.jinja_patterns['if_condition'], content, re.DOTALL)
        for condition, if_content in if_matches:
            preserved_content = preserved_content.replace(
                f'{{% if {condition} %}}{if_content}{{% endif %}}',
                f'<div data-jinja-if="{condition}">{if_content}</div>'
            )
        
        # Сохраняем переменные / Preserve variables
        var_matches = re.findall(self.jinja_patterns['variable'], content)
        for var in var_matches:
            preserved_content = preserved_content.replace(
                f'{{{{ {var} }}}}',
                f'<span data-jinja-var="{var}">{{{{ {var} }}}}</span>'
            )
        
        return preserved_content
    
    def detect_language(self, content: str) -> str:
        """
        Определение языка контента
        Detect content language
        
        Args:
            content (str): Содержимое для анализа / Content to analyze
            
        Returns:
            str: Код языка / Language code
        """
        # Ищем переводы / Find translations
        translation_matches = re.findall(self.jinja_patterns['translation'], content)
        
        if translation_matches:
            # Проверяем второй параметр (язык) / Check second parameter (language)
            for key, lang in translation_matches:
                if lang and lang in self.supported_languages:
                    return lang
        
        # Ищем русский текст / Find Russian text
        russian_pattern = r'[а-яё]'
        if re.search(russian_pattern, content, re.IGNORECASE):
            return 'ru'
        
        # Ищем английский текст / Find English text
        english_pattern = r'\b(the|and|or|but|in|on|at|to|for|of|with|by)\b'
        if re.search(english_pattern, content, re.IGNORECASE):
            return 'en'
        
        # По умолчанию английский / Default to English
        return 'en'
    
    def _analyze_template_structure(self, content: str) -> Dict[str, Any]:
        """
        Анализ структуры шаблона
        Analyze template structure
        
        Args:
            content (str): Содержимое шаблона / Template content
            
        Returns:
            Dict[str, Any]: Структура шаблона / Template structure
        """
        structure = {
            'extends': [],
            'includes': [],
            'blocks': [],
            'variables': [],
            'loops': [],
            'conditions': [],
            'css_files': [],
            'js_files': [],
        }
        
        # Анализируем extends / Analyze extends
        extends_matches = re.findall(self.jinja_patterns['extends'], content)
        structure['extends'] = list(extends_matches)
        
        # Анализируем includes / Analyze includes
        include_matches = re.findall(self.jinja_patterns['include'], content)
        structure['includes'] = list(include_matches)
        
        # Анализируем блоки / Analyze blocks
        block_matches = re.findall(self.jinja_patterns['block'], content, re.DOTALL)
        structure['blocks'] = [name for name, _ in block_matches]
        
        # Анализируем переменные / Analyze variables
        var_matches = re.findall(self.jinja_patterns['variable'], content)
        structure['variables'] = list(var_matches)
        
        # Анализируем циклы / Analyze loops
        for_matches = re.findall(self.jinja_patterns['for_loop'], content, re.DOTALL)
        structure['loops'] = [f"{var} in {collection}" for var, collection, _ in for_matches]
        
        # Анализируем условия / Analyze conditions
        if_matches = re.findall(self.jinja_patterns['if_condition'], content, re.DOTALL)
        structure['conditions'] = [condition for condition, _ in if_matches]
        
        # Анализируем CSS файлы / Analyze CSS files
        css_matches = re.findall(r'href=["\']([^"\']*\.css)["\']', content)
        structure['css_files'] = list(css_matches)
        
        # Анализируем JS файлы / Analyze JS files
        js_matches = re.findall(r'src=["\']([^"\']*\.js)["\']', content)
        structure['js_files'] = list(js_matches)
        
        # Исправление: если вдруг где-то set, приводим к list
        for k, v in structure.items():
            if isinstance(v, set):
                structure[k] = list(v)
        
        return structure
    
    def generate_grapesjs_config(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Генерация конфигурации GrapesJS
        Generate GrapesJS configuration
        
        Args:
            template_data (Dict[str, Any]): Данные шаблона / Template data
            
        Returns:
            Dict[str, Any]: Конфигурация GrapesJS / GrapesJS configuration
        """
        return {
            'components': template_data['components'],
            'style': self._generate_grapesjs_styles(template_data['css_variables']),
            'storage': {
                'type': 'remote',
                'autosave': True,
                'autoload': True,
                'stepsBeforeSave': 1,
            },
            'panels': {
                'defaults': [
                    {
                        'id': 'basic-actions',
                        'el': '.panel__basic-actions',
                        'buttons': [
                            {
                                'id': 'visibility',
                                'active': True,
                                'className': 'btn-toggle-borders',
                                'label': '<u>B</u>',
                                'command': 'sw-visibility',
                            },
                        ],
                    },
                ],
            },
            'deviceManager': {
                'devices': [
                    {
                        'name': 'Desktop',
                        'width': '',
                    },
                    {
                        'name': 'Tablet',
                        'width': '768px',
                        'widthMedia': '992px',
                    },
                    {
                        'name': 'Mobile',
                        'width': '320px',
                        'widthMedia': '480px',
                    },
                ],
            },
            'plugins': [
                'gjs-preset-webpage',
                'gjs-plugin-ckeditor',
            ],
            'pluginsOpts': {
                'gjs-preset-webpage': {},
                'gjs-plugin-ckeditor': {
                    'position: absolute; top: 0; left: 0; z-index: 100;',
                },
            },
        }
    
    def _generate_grapesjs_styles(self, css_variables: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Генерация стилей для GrapesJS
        Generate styles for GrapesJS
        
        Args:
            css_variables (Dict[str, str]): CSS переменные / CSS variables
            
        Returns:
            List[Dict[str, Any]]: Стили GrapesJS / GrapesJS styles
        """
        styles = []
        
        # Добавляем CSS переменные / Add CSS variables
        css_vars_style = {
            'selectors': [{'name': 'body'}],
            'style': css_variables,
        }
        styles.append(css_vars_style)
        
        return styles
    
    def convert_template_to_grapesjs(self, template_path: str) -> Dict[str, Any]:
        """
        Полная конвертация шаблона в GrapesJS формат
        Complete template conversion to GrapesJS format
        
        Args:
            template_path (str): Путь к шаблону / Path to template
            
        Returns:
            Dict[str, Any]: Полная конфигурация GrapesJS / Complete GrapesJS configuration
        """
        # Парсим шаблон / Parse template
        template_data = self.parse_template(template_path)
        
        # Генерируем конфигурацию GrapesJS / Generate GrapesJS configuration
        grapesjs_config = self.generate_grapesjs_config(template_data)
        
        result = {
            'template_data': template_data,
            'grapesjs_config': grapesjs_config,
            'conversion_metadata': {
                'converter_version': '1.0.0',
                'template_path': template_path,
                'conversion_date': str(Path().cwd()),
                'preserved_logic_count': len(template_data['structure']['blocks']) + 
                                       len(template_data['structure']['loops']) + 
                                       len(template_data['structure']['conditions']),
            }
        }
        
        # Конвертируем все set в list для JSON сериализации
        result = convert_sets_to_lists(result)
        
        return result


# Утилитарные функции / Utility functions

def convert_template_file(template_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Конвертация файла шаблона
    Convert template file
    
    Args:
        template_path (str): Путь к шаблону / Path to template
        output_path (Optional[str]): Путь для сохранения результата / Path to save result
        
    Returns:
        Dict[str, Any]: Результат конвертации / Conversion result
    """
    converter = Jinja2ToGrapesJSConverter()
    result = converter.convert_template_to_grapesjs(template_path)
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    
    return result


def batch_convert_templates(templates_dir: str = "templates", output_dir: str = "converted_templates"):
    """
    Пакетная конвертация шаблонов
    Batch convert templates
    
    Args:
        templates_dir (str): Папка с шаблонами / Templates directory
        output_dir (str): Папка для результатов / Output directory
    """
    converter = Jinja2ToGrapesJSConverter(templates_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Находим все HTML шаблоны / Find all HTML templates
    template_files = list(Path(templates_dir).rglob("*.html"))
    
    for template_file in template_files:
        try:
            relative_path = template_file.relative_to(templates_dir)
            result = converter.convert_template_to_grapesjs(str(relative_path))
            
            # Сохраняем результат / Save result
            output_file = output_path / f"{relative_path.stem}_grapesjs.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Converted: {relative_path} -> {output_file}")
            
        except Exception as e:
            logger.error(f"Error converting {template_file}: {e}")


if __name__ == "__main__":
    # Пример использования / Usage example
    converter = Jinja2ToGrapesJSConverter()
    
    # Конвертируем один шаблон / Convert single template
    result = converter.convert_template_to_grapesjs("learning/subject_view.html")
    
    # Сохраняем результат / Save result
    with open("subject_view_grapesjs.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print("Conversion completed successfully!") 