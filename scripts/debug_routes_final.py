#!/usr/bin/env python3
"""
Финальная диагностика маршрутов редактора контента
Проверяет исправления конфликтов маршрутов
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from routes import register_content_editor_blueprints
from routes.admin_routes import admin_bp
from routes.content_editor import content_editor_bp, content_editor_api_bp

def create_test_app():
    """Создает тестовое Flask приложение"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-key'
    app.config['TESTING'] = True
    
    # Регистрируем blueprints в правильном порядке
    app.register_blueprint(admin_bp, url_prefix='/<lang>/admin')
    register_content_editor_blueprints(app)
    
    return app

def analyze_routes(app):
    """Анализирует все маршруты приложения"""
    print("🔍 АНАЛИЗ МАРШРУТОВ РЕДАКТОРА КОНТЕНТА")
    print("=" * 60)
    
    # Собираем все маршруты
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': str(rule),
            'blueprint': rule.endpoint.split('.')[0] if '.' in rule.endpoint else 'main'
        })
    
    # Группируем по blueprint
    blueprints = {}
    for route in routes:
        bp = route['blueprint']
        if bp not in blueprints:
            blueprints[bp] = []
        blueprints[bp].append(route)
    
    # Анализируем content_editor маршруты
    print("\n📋 МАРШРУТЫ CONTENT EDITOR:")
    print("-" * 40)
    
    content_editor_routes = []
    for route in routes:
        if 'content_editor' in route['endpoint']:
            content_editor_routes.append(route)
    
    if not content_editor_routes:
        print("❌ Нет маршрутов content_editor!")
        return
    
    # Сортируем по URL
    content_editor_routes.sort(key=lambda x: x['rule'])
    
    for route in content_editor_routes:
        methods = ', '.join([m for m in route['methods'] if m not in ['HEAD', 'OPTIONS']])
        print(f"✅ {route['rule']:<50} [{methods}]")
        print(f"   Endpoint: {route['endpoint']}")
    
    # Проверяем конфликты
    print("\n🔍 ПРОВЕРКА КОНФЛИКТОВ:")
    print("-" * 40)
    
    conflicts = []
    seen_rules = {}
    
    for route in routes:
        rule = route['rule']
        if rule in seen_rules:
            conflicts.append({
                'rule': rule,
                'endpoint1': seen_rules[rule]['endpoint'],
                'endpoint2': route['endpoint']
            })
        else:
            seen_rules[rule] = route
    
    if conflicts:
        print(f"❌ Найдено {len(conflicts)} конфликтов:")
        for conflict in conflicts:
            print(f"   🔴 {conflict['rule']}")
            print(f"      - {conflict['endpoint1']}")
            print(f"      - {conflict['endpoint2']}")
    else:
        print("✅ Конфликтов не найдено!")
    
    # Проверяем специфические маршруты
    print("\n🎯 ПРОВЕРКА КЛЮЧЕВЫХ МАРШРУТОВ:")
    print("-" * 40)
    
    key_routes = [
        '/<lang>/admin/content-editor/',
        '/<lang>/admin/content-editor/grapejs',
        '/<lang>/admin/content-editor/visual-builder-grapejs',
        '/<lang>/admin/content-editor/templates',
        '/<lang>/admin/content-editor/pages',
        '/api/content-editor/templates'
    ]
    
    for key_route in key_routes:
        found = False
        for route in routes:
            if route['rule'] == key_route:
                methods = ', '.join([m for m in route['methods'] if m not in ['HEAD', 'OPTIONS']])
                print(f"✅ {key_route:<50} [{methods}] -> {route['endpoint']}")
                found = True
                break
        
        if not found:
            print(f"❌ {key_route:<50} НЕ НАЙДЕН")
    
    # Проверяем перенаправления
    print("\n🔄 ПРОВЕРКА ПЕРЕНАПРАВЛЕНИЙ:")
    print("-" * 40)
    
    redirect_routes = []
    for route in routes:
        if 'grapejs' in route['rule'] and 'visual-builder' not in route['rule']:
            redirect_routes.append(route)
    
    for route in redirect_routes:
        print(f"🔄 {route['rule']} -> должен перенаправлять на visual-builder-grapejs")
    
    # Статистика
    print("\n📊 СТАТИСТИКА:")
    print("-" * 40)
    print(f"Всего маршрутов: {len(routes)}")
    print(f"Content Editor маршрутов: {len(content_editor_routes)}")
    print(f"Blueprints: {len(blueprints)}")
    
    for bp, bp_routes in blueprints.items():
        if 'content_editor' in bp:
            print(f"  {bp}: {len(bp_routes)} маршрутов")

def test_route_resolution(app):
    """Тестирует разрешение маршрутов"""
    print("\n🧪 ТЕСТИРОВАНИЕ РАЗРЕШЕНИЯ МАРШРУТОВ:")
    print("-" * 40)
    
    with app.test_request_context():
        try:
            # Тест перенаправления
            from routes.content_editor import grapejs_builder
            print("✅ Функция grapejs_builder доступна")
            
            # Тест нового маршрута
            from routes.content_editor import grapesjs_builder_new
            print("✅ Функция grapesjs_builder_new доступна")
            
        except ImportError as e:
            print(f"❌ Ошибка импорта: {e}")

def main():
    """Основная функция"""
    print("🚀 ЗАПУСК ФИНАЛЬНОЙ ДИАГНОСТИКИ МАРШРУТОВ")
    print("=" * 60)
    
    try:
        app = create_test_app()
        analyze_routes(app)
        test_route_resolution(app)
        
        print("\n✅ ДИАГНОСТИКА ЗАВЕРШЕНА")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Ошибка диагностики: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main() 