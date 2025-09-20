#!/usr/bin/env python3
"""
Скрипт для тестирования рендеринга комьюнити
"""

import os
import sys

def test_community_render():
    """Тестирует рендеринг комьюнити"""
    
    try:
        # Добавляем путь к проекту
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        # Импортируем Flask приложение
        from app import app
        from extensions import db
        from models import ForumCategory, ForumTopic, User
        from flask import render_template_string
        
        print("🔍 Testing community render...")
        
        with app.app_context():
            # Проверяем подключение к БД
            try:
                db.session.execute(db.text("SELECT 1"))
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {str(e)}")
                return False
            
            # Тестируем запросы как в роуте
            print("\n📁 Getting categories...")
            categories = ForumCategory.query.filter_by(is_active=True).order_by(ForumCategory.order).all()
            print(f"✅ Found {len(categories)} active categories")
            
            print("\n📝 Getting recent topics...")
            recent_topics = ForumTopic.query.order_by(ForumTopic.created_at.desc()).limit(10).all()
            print(f"✅ Found {len(recent_topics)} recent topics")
            
            print("\n🔥 Getting popular topics...")
            popular_topics = ForumTopic.query.order_by(ForumTopic.views_count.desc()).limit(5).all()
            print(f"✅ Found {len(popular_topics)} popular topics")
            
            # Тестируем простой рендеринг
            print("\n🎨 Testing template render...")
            try:
                # Простой тест рендеринга
                test_template = """
                <div class="test-topics">
                    {% for topic in recent_topics %}
                    <div class="topic-item">
                        <h3>{{ topic.title }}</h3>
                        <p>{{ topic.content[:100] }}...</p>
                        <small>Created: {{ topic.created_at }}</small>
                    </div>
                    {% endfor %}
                </div>
                """
                
                rendered = render_template_string(test_template, recent_topics=recent_topics)
                print(f"✅ Template rendered successfully")
                print(f"📄 Rendered content length: {len(rendered)} characters")
                
                # Показываем первые несколько тем
                if recent_topics:
                    print(f"\n📋 First few topics:")
                    for i, topic in enumerate(recent_topics[:3]):
                        print(f"  {i+1}. '{topic.title}' - {topic.created_at}")
                else:
                    print("❌ No topics found!")
                
            except Exception as e:
                print(f"❌ Template render error: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("🚀 Community Render Tester")
    print("=" * 50)
    
    success = test_community_render()
    
    if success:
        print("✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("❌ Script failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
