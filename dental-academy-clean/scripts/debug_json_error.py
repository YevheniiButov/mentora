#!/usr/bin/env python3
"""
Скрипт для диагностики ошибки JSON сериализации
"""
import os
import sys
import json
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app
from models import db, User, WebsiteVisit, UserSession, PageView

def debug_json_error():
    """Диагностирует ошибку JSON сериализации"""
    
    with app.app_context():
        try:
            print("🔍 ДИАГНОСТИКА ОШИБКИ JSON СЕРИАЛИЗАЦИИ")
            print("=" * 60)
            
            # Тест 1: Популярные страницы (может быть проблемным)
            print("\n1. Тестируем популярные страницы...")
            try:
                # Имитируем запрос, который может возвращать Row объекты
                popular_pages = db.session.query(
                    PageView.page_url,
                    db.func.count(PageView.id).label('visits'),
                    db.func.count(db.func.distinct(PageView.user_id)).label('unique_visitors')
                ).group_by(PageView.page_url).order_by(
                    db.func.count(PageView.id).desc()
                ).limit(10).all()
                
                print(f"   Найдено страниц: {len(popular_pages)}")
                
                # Пробуем сериализовать Row объекты
                pages_data = []
                for page in popular_pages:
                    pages_data.append({
                        'page_url': page.page_url,
                        'visits': page.visits,
                        'unique_visitors': page.unique_visitors
                    })
                
                json.dumps(pages_data)
                print("   ✅ Популярные страницы - OK")
                
            except Exception as e:
                print(f"   ❌ Популярные страницы - ОШИБКА: {e}")
                print(f"   Тип ошибки: {type(e).__name__}")
                
                # Пробуем сериализовать Row объекты напрямую
                try:
                    json.dumps(popular_pages)
                    print("   ❌ Row объекты напрямую - ОШИБКА")
                except Exception as e2:
                    print(f"   ❌ Row объекты напрямую - ОШИБКА: {e2}")
            
            # Тест 2: Статистика по странам
            print("\n2. Тестируем статистику по странам...")
            try:
                country_stats = db.session.query(
                    WebsiteVisit.country,
                    db.func.count(WebsiteVisit.id).label('visits'),
                    db.func.count(db.func.distinct(WebsiteVisit.user_id)).label('unique_visitors')
                ).group_by(WebsiteVisit.country).order_by(
                    db.func.count(WebsiteVisit.id).desc()
                ).limit(10).all()
                
                print(f"   Найдено стран: {len(country_stats)}")
                
                # Пробуем сериализовать Row объекты
                countries_data = []
                for country in country_stats:
                    countries_data.append({
                        'country': country.country,
                        'visits': country.visits,
                        'unique_visitors': country.unique_visitors
                    })
                
                json.dumps(countries_data)
                print("   ✅ Статистика по странам - OK")
                
            except Exception as e:
                print(f"   ❌ Статистика по странам - ОШИБКА: {e}")
                print(f"   Тип ошибки: {type(e).__name__}")
            
            # Тест 3: Статистика по браузерам
            print("\n3. Тестируем статистику по браузерам...")
            try:
                browser_stats = db.session.query(
                    WebsiteVisit.browser,
                    db.func.count(WebsiteVisit.id).label('visits')
                ).group_by(WebsiteVisit.browser).order_by(
                    db.func.count(WebsiteVisit.id).desc()
                ).limit(10).all()
                
                print(f"   Найдено браузеров: {len(browser_stats)}")
                
                # Пробуем сериализовать Row объекты
                browsers_data = []
                for browser in browser_stats:
                    browsers_data.append({
                        'browser': browser.browser,
                        'visits': browser.visits
                    })
                
                json.dumps(browsers_data)
                print("   ✅ Статистика по браузерам - OK")
                
            except Exception as e:
                print(f"   ❌ Статистика по браузерам - ОШИБКА: {e}")
                print(f"   Тип ошибки: {type(e).__name__}")
            
            # Тест 4: Почасовая статистика
            print("\n4. Тестируем почасовую статистику...")
            try:
                hourly_stats = db.session.query(
                    db.func.extract('hour', WebsiteVisit.created_at).label('hour'),
                    db.func.count(WebsiteVisit.id).label('visits')
                ).group_by(
                    db.func.extract('hour', WebsiteVisit.created_at)
                ).order_by('hour').all()
                
                print(f"   Найдено часов: {len(hourly_stats)}")
                
                # Пробуем сериализовать Row объекты
                hours_data = []
                for hour in hourly_stats:
                    hours_data.append({
                        'hour': int(hour.hour) if hour.hour else 0,
                        'visits': hour.visits
                    })
                
                json.dumps(hours_data)
                print("   ✅ Почасовая статистика - OK")
                
            except Exception as e:
                print(f"   ❌ Почасовая статистика - ОШИБКА: {e}")
                print(f"   Тип ошибки: {type(e).__name__}")
            
            print("\n✅ ДИАГНОСТИКА ЗАВЕРШЕНА")
            
        except Exception as e:
            print(f"❌ Ошибка диагностики: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    debug_json_error()
