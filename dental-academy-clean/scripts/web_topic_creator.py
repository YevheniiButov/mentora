#!/usr/bin/env python3
"""
Веб-скрипт для создания тем через HTTP запрос
Можно запустить на продакшене через curl или браузер
"""

import os
import sys
import json
import requests
from datetime import datetime

def create_topics_via_web(base_url, admin_token=None):
    """Создает темы через веб-интерфейс"""
    
    print("🌐 Creating topics via web interface...")
    
    # Данные для создания тем
    topics_data = [
        {
            'title': 'AKV tandartsen - BIG Registration Discussion 🦷',
            'content': 'Discussion about AKV tests and BIG registration process for dentists. Share your experiences and get help from the community!',
            'category': 'general'
        },
        {
            'title': 'General Chat - Let\'s talk about everything! 💬',
            'content': 'This is a general discussion thread where you can talk about anything - from your day to your experiences in the Netherlands, or just have a casual conversation with fellow healthcare professionals!',
            'category': 'general'
        },
        {
            'title': 'Welcome to Mentora Community! 👋',
            'content': 'Welcome to our community! This is a place where international healthcare professionals can share experiences, ask questions, and support each other on their journey to BIG registration in the Netherlands.\n\nFeel free to introduce yourself and share your background!',
            'category': 'general'
        }
    ]
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'TopicCreator/1.0'
    }
    
    if admin_token:
        headers['Authorization'] = f'Bearer {admin_token}'
    
    created_count = 0
    
    for topic_data in topics_data:
        try:
            # Отправляем POST запрос для создания темы
            response = requests.post(
                f"{base_url}/api/community/create-topic",
                json=topic_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    created_count += 1
                    print(f"✅ Created topic: {topic_data['title']}")
                else:
                    print(f"❌ Failed to create topic: {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {str(e)}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print(f"\n🎉 Successfully created {created_count} topics via web!")
    return created_count

def create_topics_via_curl(base_url):
    """Создает темы через curl команды"""
    
    print("📝 Generating curl commands for topic creation...")
    
    topics_data = [
        {
            'title': 'AKV tandartsen - BIG Registration Discussion 🦷',
            'content': 'Discussion about AKV tests and BIG registration process for dentists. Share your experiences and get help from the community!',
            'category': 'general'
        },
        {
            'title': 'General Chat - Let\'s talk about everything! 💬',
            'content': 'This is a general discussion thread where you can talk about anything - from your day to your experiences in the Netherlands, or just have a casual conversation with fellow healthcare professionals!',
            'category': 'general'
        },
        {
            'title': 'Welcome to Mentora Community! 👋',
            'content': 'Welcome to our community! This is a place where international healthcare professionals can share experiences, ask questions, and support each other on their journey to BIG registration in the Netherlands.\n\nFeel free to introduce yourself and share your background!',
            'category': 'general'
        }
    ]
    
    curl_commands = []
    
    for i, topic_data in enumerate(topics_data):
        # Экранируем JSON для curl
        json_data = json.dumps(topic_data).replace('"', '\\"')
        
        curl_cmd = f'''curl -X POST "{base_url}/api/community/create-topic" \\
  -H "Content-Type: application/json" \\
  -H "User-Agent: TopicCreator/1.0" \\
  -d "{json_data}"'''
        
        curl_commands.append(curl_cmd)
    
    # Сохраняем команды в файл
    with open('create_topics_curl.sh', 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# Commands to create topics via curl\n")
        f.write(f"# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for i, cmd in enumerate(curl_commands, 1):
            f.write(f"# Topic {i}\n")
            f.write(cmd + "\n\n")
    
    print("✅ Curl commands saved to create_topics_curl.sh")
    print("📋 To run on production:")
    print("   1. Upload create_topics_curl.sh to your server")
    print("   2. Make it executable: chmod +x create_topics_curl.sh")
    print("   3. Run: ./create_topics_curl.sh")
    
    return curl_commands

def main():
    """Основная функция"""
    
    print("🚀 Web Topic Creator")
    print("=" * 50)
    
    # Получаем URL из аргументов или переменной окружения
    base_url = sys.argv[1] if len(sys.argv) > 1 else os.getenv('BASE_URL', 'https://bigmentor.nl')
    
    print(f"🌐 Base URL: {base_url}")
    
    # Проверяем доступность сервера
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ Server is accessible")
        else:
            print(f"⚠️ Server returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot reach server: {str(e)}")
        print("📝 Generating curl commands instead...")
        create_topics_via_curl(base_url)
        return
    
    # Пытаемся создать темы через веб-интерфейс
    print("\n🌐 Attempting to create topics via web interface...")
    created_count = create_topics_via_web(base_url)
    
    if created_count == 0:
        print("\n📝 Web interface failed, generating curl commands...")
        create_topics_via_curl(base_url)

if __name__ == '__main__':
    main()
