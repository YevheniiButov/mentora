#!/usr/bin/env python3
"""
Скрипт для упрощения регистрации - оставить только быструю регистрацию
"""
import re

def fix_register_route():
    """Исправить роут регистрации"""
    
    # Читаем файл
    with open('routes/auth_routes.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Находим функцию register и заменяем её на простую версию
    pattern = r'@auth_bp\.route\(\'/register\', methods=\[\'GET\', \'POST\'\]\)\s*def register\(\):.*?(?=@auth_bp\.route)'
    
    replacement = '''@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Extended registration form for new users - REDIRECTED TO QUICK REGISTER"""
    from flask import redirect, url_for, g
    lang = g.get('lang', 'nl')
    return redirect(url_for('auth.quick_register', lang=lang))

'''
    
    # Заменяем
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Записываем обратно
    with open('routes/auth_routes.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Роут регистрации упрощен - теперь перенаправляет на быструю регистрацию")

if __name__ == "__main__":
    fix_register_route()
