# utils/ai_notifications.py

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import current_app, url_for
from sqlalchemy import and_, or_, func
from models import db, User, AIConversation, UserStats
from utils.ai_analytics import AIAnalyticsDashboard
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AINotificationManager:
    """
    Менеджер уведомлений для системы ИИ аналитики.
    Отслеживает критические метрики и отправляет алерты админам.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.analytics = AIAnalyticsDashboard()
        
        # Пороговые значения по умолчанию
        self.default_thresholds = {
            'error_rate_critical': 0.15,      # 15% ошибок - критично
            'error_rate_warning': 0.10,       # 10% ошибок - предупреждение
            'satisfaction_critical': 0.60,    # Удовлетворенность ниже 60% - критично
            'satisfaction_warning': 0.70,     # Удовлетворенность ниже 70% - предупреждение
            'response_time_critical': 5.0,    # Время ответа больше 5 сек - критично
            'response_time_warning': 3.0,     # Время ответа больше 3 сек - предупреждение
            'active_users_drop': 0.30,        # Падение активных пользователей на 30%
            'system_health_critical': 0.80,   # Здоровье системы ниже 80%
            'daily_interactions_drop': 0.40   # Падение взаимодействий на 40%
        }
        
        # Типы уведомлений
        self.notification_types = {
            'error_rate': 'Высокий процент ошибок ИИ',
            'satisfaction': 'Низкая удовлетворенность пользователей',
            'response_time': 'Медленное время ответа ИИ',
            'user_activity': 'Падение активности пользователей',
            'system_health': 'Проблемы со здоровьем системы',
            'interactions_drop': 'Резкое снижение взаимодействий'
        }
        
    def get_thresholds(self) -> Dict[str, float]:
        """Получает пороговые значения из настроек или возвращает дефолтные."""
        try:
            # Здесь можно добавить загрузку из базы данных или конфига
            # Пока используем дефолтные значения
            return self.default_thresholds.copy()
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке пороговых значений: {e}")
            return self.default_thresholds.copy()
    
    def check_critical_metrics(self) -> List[Dict[str, Any]]:
        """
        Проверяет критические метрики и возвращает список алертов.
        """
        alerts = []
        thresholds = self.get_thresholds()
        
        try:
            # Получаем текущие метрики
            current_metrics = self.analytics.get_realtime_metrics()
            historical_data = self.analytics.get_historical_analytics(days=7)
            
            # Проверка процента ошибок
            error_rate = current_metrics.get('error_rate', 0)
            if error_rate >= thresholds['error_rate_critical']:
                alerts.append({
                    'type': 'error_rate',
                    'severity': 'critical',
                    'title': 'КРИТИЧНО: Высокий процент ошибок ИИ',
                    'message': f'Процент ошибок составляет {error_rate:.1%}, что превышает критический порог {thresholds["error_rate_critical"]:.1%}',
                    'value': error_rate,
                    'threshold': thresholds['error_rate_critical'],
                    'timestamp': datetime.now(),
                    'actions': ['Проверить логи ошибок', 'Перезапустить ИИ сервисы', 'Связаться с поддержкой']
                })
            elif error_rate >= thresholds['error_rate_warning']:
                alerts.append({
                    'type': 'error_rate',
                    'severity': 'warning',
                    'title': 'ВНИМАНИЕ: Повышенный процент ошибок ИИ',
                    'message': f'Процент ошибок составляет {error_rate:.1%}, что превышает предупредительный порог {thresholds["error_rate_warning"]:.1%}',
                    'value': error_rate,
                    'threshold': thresholds['error_rate_warning'],
                    'timestamp': datetime.now(),
                    'actions': ['Мониторить ситуацию', 'Проверить логи']
                })
            
            # Проверка удовлетворенности пользователей
            satisfaction = current_metrics.get('user_satisfaction', 1.0)
            if satisfaction <= thresholds['satisfaction_critical']:
                alerts.append({
                    'type': 'satisfaction',
                    'severity': 'critical',
                    'title': 'КРИТИЧНО: Низкая удовлетворенность пользователей',
                    'message': f'Удовлетворенность пользователей составляет {satisfaction:.1%}, что ниже критического порога {thresholds["satisfaction_critical"]:.1%}',
                    'value': satisfaction,
                    'threshold': thresholds['satisfaction_critical'],
                    'timestamp': datetime.now(),
                    'actions': ['Проанализировать отзывы', 'Улучшить промпты ИИ', 'Обучить модель']
                })
            elif satisfaction <= thresholds['satisfaction_warning']:
                alerts.append({
                    'type': 'satisfaction',
                    'severity': 'warning',
                    'title': 'ВНИМАНИЕ: Снижение удовлетворенности пользователей',
                    'message': f'Удовлетворенность пользователей составляет {satisfaction:.1%}, что ниже предупредительного порога {thresholds["satisfaction_warning"]:.1%}',
                    'value': satisfaction,
                    'threshold': thresholds['satisfaction_warning'],
                    'timestamp': datetime.now(),
                    'actions': ['Проанализировать тренды', 'Собрать больше обратной связи']
                })
            
            # Проверка времени ответа (если есть данные о производительности)
            performance_metrics = current_metrics.get('performance_metrics', {})
            response_time = performance_metrics.get('response_time', 0)
            if response_time >= thresholds['response_time_critical']:
                alerts.append({
                    'type': 'response_time',
                    'severity': 'critical',
                    'title': 'КРИТИЧНО: Медленное время ответа ИИ',
                    'message': f'Время ответа ИИ составляет {response_time:.2f} сек, что превышает критический порог {thresholds["response_time_critical"]:.1f} сек',
                    'value': response_time,
                    'threshold': thresholds['response_time_critical'],
                    'timestamp': datetime.now(),
                    'actions': ['Проверить нагрузку на сервер', 'Оптимизировать запросы', 'Масштабировать ресурсы']
                })
            elif response_time >= thresholds['response_time_warning']:
                alerts.append({
                    'type': 'response_time',
                    'severity': 'warning',
                    'title': 'ВНИМАНИЕ: Увеличенное время ответа ИИ',
                    'message': f'Время ответа ИИ составляет {response_time:.2f} сек, что превышает предупредительный порог {thresholds["response_time_warning"]:.1f} сек',
                    'value': response_time,
                    'threshold': thresholds['response_time_warning'],
                    'timestamp': datetime.now(),
                    'actions': ['Мониторить производительность', 'Проверить использование ресурсов']
                })
            
            # Проверка здоровья системы
            system_health = current_metrics.get('system_health', 1.0)
            if system_health <= thresholds['system_health_critical']:
                alerts.append({
                    'type': 'system_health',
                    'severity': 'critical',
                    'title': 'КРИТИЧНО: Проблемы со здоровьем системы',
                    'message': f'Здоровье системы составляет {system_health:.1%}, что ниже критического порога {thresholds["system_health_critical"]:.1%}',
                    'value': system_health,
                    'threshold': thresholds['system_health_critical'],
                    'timestamp': datetime.now(),
                    'actions': ['Проверить все сервисы', 'Перезапустить проблемные компоненты', 'Связаться с DevOps']
                })
            
            # Проверка изменений в активности пользователей
            if historical_data and len(historical_data.get('daily_metrics', [])) >= 2:
                daily_metrics = historical_data['daily_metrics']
                
                # Сравниваем последние два дня
                yesterday_users = daily_metrics[-2].get('active_users', 0)
                today_users = daily_metrics[-1].get('active_users', 0)
                
                if yesterday_users > 0:
                    user_change = (today_users - yesterday_users) / yesterday_users
                    if user_change <= -thresholds['active_users_drop']:
                        alerts.append({
                            'type': 'user_activity',
                            'severity': 'warning',
                            'title': 'ВНИМАНИЕ: Резкое падение активности пользователей',
                            'message': f'Количество активных пользователей упало на {abs(user_change):.1%} за последний день (с {yesterday_users} до {today_users})',
                            'value': user_change,
                            'threshold': -thresholds['active_users_drop'],
                            'timestamp': datetime.now(),
                            'actions': ['Проанализировать причины', 'Проверить доступность системы', 'Провести пользовательские интервью']
                        })
                
                # Проверка изменений в количестве взаимодействий
                yesterday_interactions = daily_metrics[-2].get('ai_interactions', 0)
                today_interactions = daily_metrics[-1].get('ai_interactions', 0)
                
                if yesterday_interactions > 0:
                    interaction_change = (today_interactions - yesterday_interactions) / yesterday_interactions
                    if interaction_change <= -thresholds['daily_interactions_drop']:
                        alerts.append({
                            'type': 'interactions_drop',
                            'severity': 'warning',
                            'title': 'ВНИМАНИЕ: Резкое снижение ИИ взаимодействий',
                            'message': f'Количество ИИ взаимодействий упало на {abs(interaction_change):.1%} за последний день (с {yesterday_interactions} до {today_interactions})',
                            'value': interaction_change,
                            'threshold': -thresholds['daily_interactions_drop'],
                            'timestamp': datetime.now(),
                            'actions': ['Проверить работу ИИ системы', 'Анализировать пользовательское поведение', 'Проверить интерфейс']
                        })
            
        except Exception as e:
            self.logger.error(f"Ошибка при проверке критических метрик: {e}")
            alerts.append({
                'type': 'system_error',
                'severity': 'critical',
                'title': 'ОШИБКА: Проблема с системой мониторинга',
                'message': f'Произошла ошибка при проверке метрик: {str(e)}',
                'timestamp': datetime.now(),
                'actions': ['Проверить логи системы', 'Перезапустить мониторинг']
            })
        
        return alerts
    
    def send_email_notification(self, alert: Dict[str, Any], recipients: List[str]) -> bool:
        """
        Отправляет email уведомление администраторам.
        """
        try:
            # Настройки SMTP (должны быть в конфигурации приложения)
            smtp_config = {
                'host': current_app.config.get('SMTP_HOST', 'localhost'),
                'port': current_app.config.get('SMTP_PORT', 587),
                'username': current_app.config.get('SMTP_USERNAME'),
                'password': current_app.config.get('SMTP_PASSWORD'),
                'use_tls': current_app.config.get('SMTP_USE_TLS', True)
            }
            
            if not smtp_config['username']:
                self.logger.warning("SMTP настройки не найдены, пропускаем отправку email")
                return False
            
            # Создаем сообщение
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[ИИ Алерт] {alert['title']}"
            msg['From'] = smtp_config['username']
            msg['To'] = ', '.join(recipients)
            
            # HTML версия письма
            html_content = self._generate_email_html(alert)
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            # Текстовая версия письма
            text_content = self._generate_email_text(alert)
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Отправляем email
            with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
                if smtp_config['use_tls']:
                    server.starttls()
                server.login(smtp_config['username'], smtp_config['password'])
                server.send_message(msg)
            
            self.logger.info(f"Email уведомление отправлено: {alert['type']} -> {recipients}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при отправке email уведомления: {e}")
            return False
    
    def _generate_email_html(self, alert: Dict[str, Any]) -> str:
        """Генерирует HTML содержимое для email уведомления."""
        severity_colors = {
            'critical': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8'
        }
        
        color = severity_colors.get(alert.get('severity', 'info'), '#6c757d')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>ИИ Алерт</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: {color}; color: white; padding: 15px; border-radius: 5px 5px 0 0;">
                    <h2 style="margin: 0;">{alert['title']}</h2>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border: 1px solid #dee2e6; border-top: none;">
                    <p><strong>Сообщение:</strong> {alert['message']}</p>
                    <p><strong>Время:</strong> {alert['timestamp'].strftime('%d.%m.%Y %H:%M:%S')}</p>
                    
                    {f'<p><strong>Текущее значение:</strong> {alert["value"]}</p>' if 'value' in alert else ''}
                    {f'<p><strong>Пороговое значение:</strong> {alert["threshold"]}</p>' if 'threshold' in alert else ''}
                </div>
                
                {self._generate_actions_html(alert.get('actions', []))}
                
                <div style="margin-top: 20px; padding: 15px; background: #e9ecef; border-radius: 5px; font-size: 12px; color: #6c757d;">
                    <p>Это автоматическое уведомление от системы мониторинга ИИ аналитики Стоматологической Академии.</p>
                    <p>Для получения дополнительной информации войдите в административную панель.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_actions_html(self, actions: List[str]) -> str:
        """Генерирует HTML для рекомендуемых действий."""
        if not actions:
            return ""
        
        actions_html = "<div style='margin-top: 15px;'><strong>Рекомендуемые действия:</strong><ul>"
        for action in actions:
            actions_html += f"<li>{action}</li>"
        actions_html += "</ul></div>"
        
        return actions_html
    
    def _generate_email_text(self, alert: Dict[str, Any]) -> str:
        """Генерирует текстовое содержимое для email уведомления."""
        text = f"""
{alert['title']}

Сообщение: {alert['message']}
Время: {alert['timestamp'].strftime('%d.%m.%Y %H:%M:%S')}
"""
        
        if 'value' in alert:
            text += f"Текущее значение: {alert['value']}\n"
        
        if 'threshold' in alert:
            text += f"Пороговое значение: {alert['threshold']}\n"
        
        actions = alert.get('actions', [])
        if actions:
            text += "\nРекомендуемые действия:\n"
            for action in actions:
                text += f"- {action}\n"
        
        text += "\n---\nЭто автоматическое уведомление от системы мониторинга ИИ аналитики Стоматологической Академии."
        
        return text
    
    def log_alert(self, alert: Dict[str, Any]) -> None:
        """Логирует алерт в систему."""
        try:
            log_level = logging.CRITICAL if alert.get('severity') == 'critical' else logging.WARNING
            self.logger.log(log_level, f"ИИ Алерт [{alert['type']}]: {alert['message']}")
            
            # Здесь можно добавить сохранение в базу данных
            # Создание записи в таблице notifications или alerts
            
        except Exception as e:
            self.logger.error(f"Ошибка при логировании алерта: {e}")
    
    def get_admin_emails(self) -> List[str]:
        """Получает список email адресов администраторов."""
        try:
            admin_users = User.query.filter_by(role='admin').all()
            emails = [user.email for user in admin_users if user.email]
            return emails
        except Exception as e:
            self.logger.error(f"Ошибка при получении email админов: {e}")
            return []
    
    def process_alerts(self, send_notifications: bool = True) -> List[Dict[str, Any]]:
        """
        Основная функция обработки алертов.
        Проверяет метрики, генерирует алерты и отправляет уведомления.
        """
        alerts = self.check_critical_metrics()
        
        if not alerts:
            self.logger.info("Критических алертов не обнаружено")
            return []
        
        # Логируем все алерты
        for alert in alerts:
            self.log_alert(alert)
        
        # Отправляем уведомления если включено
        if send_notifications:
            admin_emails = self.get_admin_emails()
            
            if admin_emails:
                critical_alerts = [a for a in alerts if a.get('severity') == 'critical']
                warning_alerts = [a for a in alerts if a.get('severity') == 'warning']
                
                # Отправляем критические алерты немедленно
                for alert in critical_alerts:
                    self.send_email_notification(alert, admin_emails)
                
                # Группируем предупреждения в один email, если их несколько
                if warning_alerts:
                    if len(warning_alerts) == 1:
                        self.send_email_notification(warning_alerts[0], admin_emails)
                    else:
                        grouped_alert = self._create_grouped_warning_alert(warning_alerts)
                        self.send_email_notification(grouped_alert, admin_emails)
            else:
                self.logger.warning("Не найдены email адреса администраторов для отправки уведомлений")
        
        return alerts
    
    def _create_grouped_warning_alert(self, warnings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Создает групповой алерт для нескольких предупреждений."""
        return {
            'type': 'grouped_warnings',
            'severity': 'warning',
            'title': f'ВНИМАНИЕ: Обнаружено {len(warnings)} предупреждений в системе ИИ',
            'message': f'Система обнаружила {len(warnings)} предупреждений, требующих внимания: ' + 
                      ', '.join([w['type'] for w in warnings]),
            'timestamp': datetime.now(),
            'warnings': warnings,
            'actions': ['Проверить дашборд аналитики', 'Проанализировать каждое предупреждение отдельно']
        }
    
    def get_notification_settings(self) -> Dict[str, Any]:
        """Получает текущие настройки уведомлений."""
        try:
            smtp_configured = bool(current_app.config.get('SMTP_USERNAME')) if current_app else False
        except RuntimeError:
            # Работаем вне контекста приложения
            smtp_configured = False
            
        return {
            'thresholds': self.get_thresholds(),
            'notification_types': self.notification_types,
            'admin_emails': self.get_admin_emails(),
            'smtp_configured': smtp_configured
        }
    
    def update_thresholds(self, new_thresholds: Dict[str, float]) -> bool:
        """Обновляет пороговые значения для алертов."""
        try:
            # Валидация новых значений
            for key, value in new_thresholds.items():
                if key not in self.default_thresholds:
                    raise ValueError(f"Неизвестный параметр порога: {key}")
                
                if not isinstance(value, (int, float)) or value < 0:
                    raise ValueError(f"Некорректное значение для {key}: {value}")
            
            # Здесь можно добавить сохранение в базу данных или конфиг файл
            # Пока просто обновляем в памяти
            self.default_thresholds.update(new_thresholds)
            
            self.logger.info(f"Пороговые значения обновлены: {new_thresholds}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении пороговых значений: {e}")
            return False


# Функция для периодической проверки (можно использовать с планировщиком задач)
def run_periodic_check():
    """Функция для периодической проверки алертов (для cron или планировщика)."""
    try:
        notification_manager = AINotificationManager()
        alerts = notification_manager.process_alerts(send_notifications=True)
        
        if alerts:
            print(f"Обработано {len(alerts)} алертов:")
            for alert in alerts:
                print(f"- {alert['type']}: {alert['title']}")
        else:
            print("Алерты не обнаружены")
            
    except Exception as e:
        print(f"Ошибка при периодической проверке: {e}")
        logging.error(f"Ошибка при периодической проверке алертов: {e}")


# Настройка логгера
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    run_periodic_check() 