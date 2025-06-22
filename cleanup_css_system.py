#!/usr/bin/env python3
"""
CSS Architecture Cleanup Script
Автоматически очищает дублирование CSS переменных и оптимизирует архитектуру стилей
"""

import re
import os
import shutil
from pathlib import Path

def create_backup():
    """Создает бекап CSS файлов"""
    print("🔄 Создание бекапа...")
    backup_dir = Path("css_backup")
    
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    
    shutil.copytree("static/css", backup_dir / "static_css")
    shutil.copytree("templates", backup_dir / "templates")
    print(f"✅ Бекап создан: {backup_dir}")

def remove_css_variables_from_html():
    """Удаляет CSS переменные из HTML"""
    print("\n🧹 Очистка переменных из HTML...")
    count = 0
    
    for html_file in Path("templates").rglob("*.html"):
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        # Удаляем :root блоки
        content = re.sub(r':root\s*{[^}]*--[^}]*}', '', content, flags=re.DOTALL)
        # Удаляем пустые <style> блоки  
        content = re.sub(r'<style>\s*</style>', '', content)
        
        if content != original:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ {html_file}")
            count += 1
    
    print(f"📊 Очищено {count} файлов")

def main():
    print("🚀 CSS CLEANUP TOOL")
    response = input("⚠️  Изменить файлы? (y/N): ")
    if response.lower() in ['y', 'yes']:
        create_backup()
        remove_css_variables_from_html()
        print("✅ Готово!")
    else:
        print("❌ Отменено")

if __name__ == "__main__":
    main()
