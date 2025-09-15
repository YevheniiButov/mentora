#!/usr/bin/env python3
"""
Скрипт для заполнения данных административных инструментов
Создает тестовые данные для демонстрации функциональности
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, AdminAuditLog, SystemHealthLog, DatabaseBackup, EmailTemplate, EmailCampaign, SystemNotification, User
from datetime import datetime, timedelta
import json
import random

def create_admin_tools_data():
    """Создает тестовые данные для административных инструментов"""
    
    with app.app_context():
        print("🚀 Создание данных административных инструментов...")
        
        # Получаем админа
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print("❌ Админ не найден. Создайте админа сначала.")
            return
        
        # 1. Создаем логи аудита
        print("📝 Создание логов аудита...")
        audit_actions = [
            ('user_created', 'user', 'Создание нового пользователя'),
            ('user_updated', 'user', 'Обновление данных пользователя'),
            ('user_deleted', 'user', 'Удаление пользователя'),
            ('database_backup_created', 'system', 'Создание резервной копии БД'),
            ('notification_created', 'system', 'Создание системного уведомления'),
            ('bulk_delete', 'contact', 'Массовое удаление контактов'),
            ('data_export', 'system', 'Экспорт данных системы'),
            ('profession_created', 'profession', 'Создание новой профессии'),
            ('contact_updated', 'contact', 'Обновление контакта'),
            ('analytics_export', 'system', 'Экспорт аналитических данных')
        ]
        
        for i in range(50):
            action, target_type, description = random.choice(audit_actions)
            
            audit_log = AdminAuditLog(
                admin_user_id=admin.id,
                action=action,
                target_type=target_type,
                target_id=random.randint(1, 100) if random.choice([True, False]) else None,
                details=json.dumps({
                    'description': description,
                    'timestamp': datetime.utcnow().isoformat(),
                    'additional_info': f'Test data {i+1}'
                }),
                old_values=json.dumps({'old_value': f'old_{i}'}) if random.choice([True, False]) else None,
                new_values=json.dumps({'new_value': f'new_{i}'}) if random.choice([True, False]) else None,
                ip_address=f'192.168.1.{random.randint(1, 254)}',
                user_agent='Mozilla/5.0 (Test Browser)',
                request_url=f'/admin/{target_type}/action',
                request_method=random.choice(['GET', 'POST', 'PUT', 'DELETE']),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            
            db.session.add(audit_log)
        
        # 2. Создаем логи состояния системы
        print("💓 Создание логов состояния системы...")
        
        for i in range(30):
            # Генерируем реалистичные метрики
            cpu_usage = random.uniform(10, 90)
            memory_usage = random.uniform(20, 85)
            disk_usage = random.uniform(30, 80)
            
            # Определяем статус на основе метрик
            if cpu_usage > 80 or memory_usage > 80 or disk_usage > 85:
                status = 'critical'
            elif cpu_usage > 60 or memory_usage > 70 or disk_usage > 70:
                status = 'warning'
            else:
                status = 'healthy'
            
            # Генерируем предупреждения для критических состояний
            alerts = None
            if status == 'critical':
                alert_list = []
                if cpu_usage > 80:
                    alert_list.append('High CPU usage detected')
                if memory_usage > 80:
                    alert_list.append('High memory usage detected')
                if disk_usage > 85:
                    alert_list.append('Disk space running low')
                alerts = json.dumps(alert_list)
            
            health_log = SystemHealthLog(
                cpu_usage=round(cpu_usage, 1),
                memory_usage=round(memory_usage, 1),
                disk_usage=round(disk_usage, 1),
                database_connections=random.randint(5, 25),
                response_time=random.uniform(50, 500),
                active_users=random.randint(10, 100),
                total_requests=random.randint(1000, 10000),
                error_count=random.randint(0, 50),
                cache_hit_rate=random.uniform(0.7, 0.95),
                status=status,
                alerts=alerts,
                created_at=datetime.utcnow() - timedelta(hours=random.randint(0, 72))
            )
            
            db.session.add(health_log)
        
        # 3. Создаем записи резервных копий
        print("💾 Создание записей резервных копий...")
        
        backup_types = ['manual', 'scheduled', 'before_deploy']
        backup_statuses = ['completed', 'failed', 'pending']
        
        for i in range(15):
            backup_type = random.choice(backup_types)
            status = random.choice(backup_statuses)
            
            started_at = datetime.utcnow() - timedelta(days=random.randint(0, 30))
            completed_at = started_at + timedelta(minutes=random.randint(5, 60)) if status == 'completed' else None
            
            backup = DatabaseBackup(
                admin_user_id=admin.id if random.choice([True, False]) else None,
                backup_name=f"{backup_type}_backup_{started_at.strftime('%Y%m%d_%H%M%S')}",
                backup_type=backup_type,
                file_path=f"/backups/{backup_type}_backup_{started_at.strftime('%Y%m%d_%H%M%S')}.sql",
                file_size=random.randint(1024*1024, 100*1024*1024) if status == 'completed' else None,
                status=status,
                error_message=f"Backup failed: {random.choice(['Disk full', 'Permission denied', 'Database locked'])}" if status == 'failed' else None,
                tables_count=random.randint(20, 50),
                records_count=random.randint(10000, 100000),
                backup_duration=random.uniform(30, 300),
                started_at=started_at,
                completed_at=completed_at,
                expires_at=started_at + timedelta(days=30)
            )
            
            db.session.add(backup)
        
        # 4. Создаем email шаблоны
        print("📧 Создание email шаблонов...")
        
        templates_data = [
            {
                'name': 'Добро пожаловать',
                'subject': 'Добро пожаловать в Mentora!',
                'template_type': 'welcome',
                'html_content': '<h1>Добро пожаловать!</h1><p>Спасибо за регистрацию в Mentora.</p>',
                'text_content': 'Добро пожаловать! Спасибо за регистрацию в Mentora.',
                'is_system': True,
                'sent_count': random.randint(50, 200)
            },
            {
                'name': 'Напоминание о курсе',
                'subject': 'Не забудьте продолжить обучение',
                'template_type': 'reminder',
                'html_content': '<h2>Продолжите обучение</h2><p>У вас есть незавершенные курсы.</p>',
                'text_content': 'Продолжите обучение. У вас есть незавершенные курсы.',
                'is_system': False,
                'sent_count': random.randint(20, 100)
            },
            {
                'name': 'Уведомление о новом курсе',
                'subject': 'Новый курс доступен!',
                'template_type': 'notification',
                'html_content': '<h2>Новый курс</h2><p>Доступен новый курс для изучения.</p>',
                'text_content': 'Новый курс доступен для изучения.',
                'is_system': False,
                'sent_count': random.randint(30, 150)
            },
            {
                'name': 'Маркетинговая рассылка',
                'subject': 'Специальное предложение',
                'template_type': 'marketing',
                'html_content': '<h2>Специальное предложение</h2><p>Скидка 20% на все курсы!</p>',
                'text_content': 'Специальное предложение: скидка 20% на все курсы!',
                'is_system': False,
                'sent_count': random.randint(100, 500)
            }
        ]
        
        for template_data in templates_data:
            template = EmailTemplate(
                name=template_data['name'],
                subject=template_data['subject'],
                template_type=template_data['template_type'],
                html_content=template_data['html_content'],
                text_content=template_data['text_content'],
                variables=json.dumps(['user_name', 'course_name', 'expiry_date']),
                is_active=True,
                is_system=template_data['is_system'],
                sent_count=template_data['sent_count'],
                last_sent_at=datetime.utcnow() - timedelta(days=random.randint(0, 7)),
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            
            db.session.add(template)
        
        # 5. Создаем email кампании
        print("📢 Создание email кампаний...")
        
        templates = EmailTemplate.query.all()
        campaign_statuses = ['draft', 'scheduled', 'sending', 'sent', 'failed']
        
        for i in range(10):
            template = random.choice(templates)
            status = random.choice(campaign_statuses)
            
            campaign = EmailCampaign(
                admin_user_id=admin.id,
                name=f"Кампания {i+1}: {template.name}",
                description=f"Описание кампании {i+1}",
                template_id=template.id,
                target_criteria=json.dumps({
                    'profession': random.choice(['dentist', 'doctor', 'nurse']),
                    'country': random.choice(['NL', 'DE', 'BE']),
                    'registration_date': 'last_30_days'
                }),
                target_count=random.randint(100, 1000),
                status=status,
                scheduled_at=datetime.utcnow() + timedelta(days=random.randint(1, 7)) if status == 'scheduled' else None,
                started_at=datetime.utcnow() - timedelta(days=random.randint(0, 5)) if status in ['sending', 'sent'] else None,
                completed_at=datetime.utcnow() - timedelta(days=random.randint(0, 3)) if status == 'sent' else None,
                sent_count=random.randint(50, 500) if status in ['sending', 'sent'] else 0,
                delivered_count=random.randint(45, 480) if status in ['sending', 'sent'] else 0,
                opened_count=random.randint(20, 200) if status in ['sending', 'sent'] else 0,
                clicked_count=random.randint(5, 50) if status in ['sending', 'sent'] else 0,
                bounced_count=random.randint(0, 20) if status in ['sending', 'sent'] else 0,
                unsubscribed_count=random.randint(0, 10) if status in ['sending', 'sent'] else 0,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 15))
            )
            
            db.session.add(campaign)
        
        # 6. Создаем системные уведомления
        print("🔔 Создание системных уведомлений...")
        
        notifications_data = [
            {
                'title': 'Система обновлена',
                'message': 'Система была успешно обновлена до версии 2.1.0',
                'notification_type': 'success',
                'priority': 'normal'
            },
            {
                'title': 'Высокая нагрузка на сервер',
                'message': 'Обнаружена высокая нагрузка на сервер. Рекомендуется проверить производительность.',
                'notification_type': 'warning',
                'priority': 'high'
            },
            {
                'title': 'Ошибка базы данных',
                'message': 'Обнаружена ошибка подключения к базе данных. Требуется немедленное вмешательство.',
                'notification_type': 'error',
                'priority': 'critical'
            },
            {
                'title': 'Новая функция доступна',
                'message': 'Доступна новая функция аналитики. Проверьте раздел "Аналитика" в админ панели.',
                'notification_type': 'info',
                'priority': 'normal'
            },
            {
                'title': 'Плановое обслуживание',
                'message': 'Запланировано техническое обслуживание на завтра с 02:00 до 04:00',
                'notification_type': 'info',
                'priority': 'high'
            }
        ]
        
        for i, notif_data in enumerate(notifications_data):
            notification = SystemNotification(
                title=notif_data['title'],
                message=notif_data['message'],
                notification_type=notif_data['notification_type'],
                priority=notif_data['priority'],
                target_users=json.dumps('all'),
                target_roles=json.dumps(['admin']),
                is_read=random.choice([True, False]),
                is_active=True,
                action_url='/admin/system' if random.choice([True, False]) else None,
                action_text='Перейти к настройкам' if random.choice([True, False]) else None,
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 7))
            )
            
            db.session.add(notification)
        
        # Сохраняем все изменения
        try:
            db.session.commit()
            print("✅ Данные административных инструментов созданы успешно!")
            print(f"📊 Создано:")
            print(f"   - {AdminAuditLog.query.count()} логов аудита")
            print(f"   - {SystemHealthLog.query.count()} логов состояния системы")
            print(f"   - {DatabaseBackup.query.count()} записей резервных копий")
            print(f"   - {EmailTemplate.query.count()} email шаблонов")
            print(f"   - {EmailCampaign.query.count()} email кампаний")
            print(f"   - {SystemNotification.query.count()} системных уведомлений")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Ошибка при создании данных: {str(e)}")
            raise

if __name__ == '__main__':
    create_admin_tools_data()
