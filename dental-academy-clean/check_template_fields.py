#!/usr/bin/env python3
"""
Скрипт для проверки полей в шаблонах аналитики
"""

import re
from pathlib import Path

def extract_template_fields(template_path):
    """Извлекает все поля из шаблона"""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем все поля вида {{ field.subfield }}
        field_pattern = r'\{\{\s*([^}]+)\s*\}\}'
        fields = re.findall(field_pattern, content)
        
        # Ищем поля в условиях {% if field.subfield %}
        if_pattern = r'\{%\s*if\s+([^%]+)\s*%\}'
        if_fields = re.findall(if_pattern, content)
        
        # Ищем поля в циклах {% for item in collection %}
        for_pattern = r'\{%\s*for\s+\w+\s+in\s+([^%]+)\s*%\}'
        for_fields = re.findall(for_pattern, content)
        
        all_fields = set()
        
        # Обрабатываем обычные поля
        for field in fields:
            # Убираем фильтры и функции
            clean_field = re.sub(r'\s*\|\s*\w+.*', '', field)
            clean_field = re.sub(r'\s*\([^)]*\)', '', clean_field)
            all_fields.add(clean_field.strip())
        
        # Обрабатываем поля в условиях
        for field in if_fields:
            clean_field = re.sub(r'\s*\|\s*\w+.*', '', field)
            clean_field = re.sub(r'\s*\([^)]*\)', '', clean_field)
            all_fields.add(clean_field.strip())
        
        # Обрабатываем поля в циклах
        for field in for_fields:
            clean_field = re.sub(r'\s*\|\s*\w+.*', '', field)
            clean_field = re.sub(r'\s*\([^)]*\)', '', clean_field)
            all_fields.add(clean_field.strip())
        
        return sorted(all_fields)
        
    except Exception as e:
        print(f"❌ Ошибка чтения {template_path}: {e}")
        return []

def check_registration_visitor_fields():
    """Проверяет поля модели RegistrationVisitor"""
    from models import RegistrationVisitor
    
    # Получаем все колонки модели
    columns = RegistrationVisitor.__table__.columns.keys()
    return sorted(columns)

def main():
    """Основная функция"""
    print("🔍 ПРОВЕРКА ПОЛЕЙ В ШАБЛОНАХ АНАЛИТИКИ")
    print("=" * 50)
    
    # Проверяем поля модели RegistrationVisitor
    print("📊 ПОЛЯ МОДЕЛИ RegistrationVisitor:")
    print("-" * 30)
    model_fields = check_registration_visitor_fields()
    for field in model_fields:
        print(f"   ✅ {field}")
    print()
    
    # Проверяем шаблон registration_analytics.html
    print("📄 ПОЛЯ В registration_analytics.html:")
    print("-" * 35)
    template_fields = extract_template_fields("templates/admin/registration_analytics.html")
    for field in template_fields:
        print(f"   📝 {field}")
    print()
    
    # Проверяем шаблон monitoring_dashboard.html
    print("📄 ПОЛЯ В monitoring_dashboard.html:")
    print("-" * 35)
    dashboard_fields = extract_template_fields("templates/admin/monitoring_dashboard.html")
    for field in dashboard_fields:
        print(f"   📝 {field}")
    print()
    
    # Проверяем, какие поля из шаблонов отсутствуют в модели
    print("⚠️ ПОТЕНЦИАЛЬНЫЕ ПРОБЛЕМЫ:")
    print("-" * 25)
    
    # Поля, которые могут отсутствовать
    potential_issues = []
    
    for field in template_fields:
        if '.' in field:
            # Поле вида visitor.field
            if field.startswith('visitor.'):
                model_field = field.split('.')[1]
                if model_field not in model_fields:
                    potential_issues.append(f"❌ {field} - поле {model_field} отсутствует в модели")
            # Поле вида stats.field
            elif field.startswith('stats.'):
                stats_field = field.split('.')[1]
                if stats_field not in ['total_users', 'active_users', 'total_topics', 'total_messages']:
                    potential_issues.append(f"❌ {field} - поле {stats_field} может отсутствовать")
            # Поле вида registration_stats.field
            elif field.startswith('registration_stats.'):
                reg_field = field.split('.')[1]
                if reg_field not in ['total_visitors', 'completed_registrations', 'email_entries', 'name_entries']:
                    potential_issues.append(f"❌ {field} - поле {reg_field} может отсутствовать")
            # Поле вида latest_health.field
            elif field.startswith('latest_health.'):
                health_field = field.split('.')[1]
                if health_field not in ['status', 'created_at', 'details']:
                    potential_issues.append(f"❌ {field} - поле {health_field} может отсутствовать")
    
    if potential_issues:
        for issue in potential_issues:
            print(f"   {issue}")
    else:
        print("   ✅ Потенциальных проблем не найдено")
    
    print()
    print("🎯 РЕЗУЛЬТАТ:")
    print(f"   📊 Поля модели: {len(model_fields)}")
    print(f"   📄 Поля в registration_analytics: {len(template_fields)}")
    print(f"   📄 Поля в monitoring_dashboard: {len(dashboard_fields)}")
    print(f"   ⚠️ Потенциальных проблем: {len(potential_issues)}")

if __name__ == "__main__":
    main()


