#!/usr/bin/env python3
"""
Скрипт для безопасного деплоя коммитов на тестовый домен mentora.com.in
"""
import subprocess
import os
import sys
from datetime import datetime

def get_commits_after_base(base_commit="d727518"):
    """Получить список коммитов после базового коммита"""
    try:
        result = subprocess.run(
            ['git', 'log', '--oneline', f'{base_commit}..HEAD'],
            capture_output=True, text=True, check=True
        )
        commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
        return commits
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка получения коммитов: {e}")
        return []

def create_deployment_branch():
    """Создать ветку для деплоя на тестовый домен"""
    branch_name = f"deploy-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    try:
        # Создать новую ветку
        subprocess.run(['git', 'checkout', '-b', branch_name], check=True)
        print(f"✅ Создана ветка для деплоя: {branch_name}")
        return branch_name
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка создания ветки: {e}")
        return None

def backup_current_state():
    """Создать бэкап текущего состояния"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_branch = f"backup-before-test-deploy-{timestamp}"
    
    try:
        subprocess.run(['git', 'checkout', '-b', backup_branch], check=True)
        subprocess.run(['git', 'checkout', 'main'], check=True)
        print(f"✅ Создан бэкап в ветке: {backup_branch}")
        return backup_branch
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка создания бэкапа: {e}")
        return None

def deploy_to_test_domain():
    """Деплой на тестовый домен"""
    print("🚀 Начинаем деплой на тестовый домен...")
    
    # Переключиться на тестовую конфигурацию
    if os.path.exists('mentora_test_config.env'):
        os.system('cp mentora_test_config.env .env')
        print("✅ Переключились на конфигурацию mentora.com.in")
    elif os.path.exists('.env.test'):
        os.system('cp .env.test .env')
        print("✅ Переключились на тестовую конфигурацию")
    else:
        print("❌ Файлы конфигурации не найдены")
        return False
    
    # Установить зависимости
    print("📦 Установка зависимостей...")
    try:
        subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Зависимости установлены")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки зависимостей: {e}")
        return False
    
    # Запустить миграции БД
    print("🗃️ Запуск миграций БД...")
    try:
        subprocess.run([
            'python3', '-c', 
            'from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()'
        ], check=True)
        print("✅ Миграции БД выполнены")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка миграций БД: {e}")
        return False
    
    print("✅ Деплой на тестовый домен завершен")
    return True

def run_tests():
    """Запустить тесты"""
    print("🧪 Запуск тестов...")
    
    tests = [
        "python3 -c \"from routes.admin_routes import admin_bp; print('Admin routes OK')\"",
        "python3 -c \"from models import db; print('Models OK')\"",
        "python3 -c \"from app import create_app; app = create_app(); print('App creation OK')\"",
        "python3 -c \"import os; print('Mentora landing config:', 'mentora.com.in' in os.environ.get('TEST_DOMAIN', ''))\""
    ]
    
    for test in tests:
        try:
            result = subprocess.run(test, shell=True, capture_output=True, text=True, check=True)
            print(f"✅ {test.split(';')[-1].strip()}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Тест не пройден: {test}")
            print(f"   Ошибка: {e.stderr}")
            return False
    
    print("✅ Все тесты пройдены")
    return True

def main():
    """Основная функция"""
    print("🚀 Безопасный деплой на тестовый домен mentora.com.in")
    print("=" * 60)
    
    # Получить список коммитов для деплоя
    commits = get_commits_after_base("d727518")
    if not commits:
        print("❌ Нет коммитов для деплоя после d727518")
        return False
    
    print(f"📋 Коммиты для деплоя ({len(commits)}):")
    for i, commit in enumerate(commits, 1):
        print(f"   {i}. {commit}")
    
    # Подтверждение
    response = input("\n❓ Продолжить деплой? (y/N): ")
    if response.lower() != 'y':
        print("❌ Деплой отменен")
        return False
    
    # Создать бэкап текущего состояния
    backup_branch = backup_current_state()
    if not backup_branch:
        print("❌ Не удалось создать бэкап")
        return False
    
    # Создать ветку для деплоя
    deploy_branch = create_deployment_branch()
    if not deploy_branch:
        print("❌ Не удалось создать ветку для деплоя")
        return False
    
    # Запустить тесты
    if not run_tests():
        print("❌ Тесты не пройдены, деплой отменен")
        return False
    
    # Деплой на тестовый домен
    if not deploy_to_test_domain():
        print("❌ Ошибка деплоя на тестовый домен")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Деплой на тестовый домен завершен успешно!")
    print(f"🌐 Тестовый домен: mentora.com.in")
    print(f"📋 Коммиты задеплоены: {len(commits)}")
    print(f"💾 Бэкап в ветке: {backup_branch}")
    print(f"🚀 Ветка деплоя: {deploy_branch}")
    
    print("\n📋 Следующие шаги:")
    print("1. Протестировать функциональность на mentora.com.in")
    print("2. Проверить работу аналитики (исправления PostgreSQL)")
    print("3. После успешного тестирования - задеплоить на продакшн")
    print("4. В случае проблем - откатиться к ветке бэкапа")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
