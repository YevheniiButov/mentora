#!/usr/bin/env python3
"""
Система уведомлений для планировщика обучения
"""

import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, timezone
from flask import current_app, render_template_string
from models import User, PersonalLearningPlan, StudySession
from extensions import db

class LearningNotificationSystem:
    """Система уведомлений для планировщика обучения"""
    
    def __init__(self):
        self.email_templates = {
            'session_reminder': {
                'subject': 'Напоминание о занятии - {{session_title}}',
                'template': '''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #3ECDC1, #6C5CE7); color: white; padding: 20px; text-align: center;">
                        <h1>🦷 Mentora Academy</h1>
                        <h2>Напоминание о занятии</h2>
                    </div>
                    
                    <div style="padding: 20px; background: #f8f9fa;">
                        <h3>Привет, {{user_name}}!</h3>
                        
                        <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #3ECDC1;">
                            <h4>📚 Сегодня у вас запланировано занятие:</h4>
                            <p><strong>{{session_title}}</strong></p>
                            <p><strong>Время:</strong> {{session_time}}</p>
                            <p><strong>Длительность:</strong> {{session_duration}} часов</p>
                            <p><strong>Домен:</strong> {{domain_name}}</p>
                        </div>
                        
                        <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <h4>🎯 Ваш прогресс:</h4>
                            <p>Общий прогресс: <strong>{{overall_progress}}%</strong></p>
                            <p>Дней до экзамена: <strong>{{days_to_exam}}</strong></p>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{{login_url}}" style="background: #3ECDC1; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block;">
                                Начать занятие
                            </a>
                        </div>
                        
                        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <h4>💡 Совет дня:</h4>
                            <p>{{daily_tip}}</p>
                        </div>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 20px; text-align: center; color: #6c757d;">
                        <p>Это автоматическое уведомление от Mentora Academy</p>
                        <p>Если вы не хотите получать уведомления, <a href="{{unsubscribe_url}}">отпишитесь здесь</a></p>
                    </div>
                </div>
                '''
            },
            'weekly_progress': {
                'subject': 'Еженедельный отчет прогресса - {{week_number}} неделя',
                'template': '''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #22c55e, #3ECDC1); color: white; padding: 20px; text-align: center;">
                        <h1>📊 Еженедельный отчет</h1>
                        <h2>Неделя {{week_number}} обучения</h2>
                    </div>
                    
                    <div style="padding: 20px; background: #f8f9fa;">
                        <h3>Привет, {{user_name}}!</h3>
                        
                        <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h4>📈 Ваши достижения на этой неделе:</h4>
                            <ul>
                                <li>Занятий завершено: <strong>{{completed_sessions}}</strong></li>
                                <li>Часов изучено: <strong>{{hours_studied}}</strong></li>
                                <li>Вопросов отвечено: <strong>{{questions_answered}}</strong></li>
                                <li>Правильных ответов: <strong>{{correct_answers}}</strong></li>
                            </ul>
                        </div>
                        
                        <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <h4>🎯 Прогресс по доменам:</h4>
                            {% for domain in domain_progress %}
                            <div style="margin: 10px 0;">
                                <p><strong>{{domain.name}}:</strong> {{domain.progress}}% → {{domain.target}}%</p>
                                <div style="background: #ddd; height: 8px; border-radius: 4px;">
                                    <div style="background: #22c55e; height: 8px; border-radius: 4px; width: {{domain.progress}}%"></div>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                        
                        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <h4>📅 План на следующую неделю:</h4>
                            <ul>
                                {% for session in next_week_sessions %}
                                <li>{{session.day}}: {{session.title}} ({{session.duration}}ч)</li>
                                {% endfor %}
                            </ul>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{{dashboard_url}}" style="background: #22c55e; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block;">
                                Посмотреть детали
                            </a>
                        </div>
                    </div>
                </div>
                '''
            },
            'exam_reminder': {
                'subject': '⚠️ Напоминание о экзамене BIG - осталось {{days_left}} дней',
                'template': '''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #ef4444, #f59e0b); color: white; padding: 20px; text-align: center;">
                        <h1>⚠️ Напоминание о экзамене</h1>
                        <h2>Осталось {{days_left}} дней до BIG экзамена</h2>
                    </div>
                    
                    <div style="padding: 20px; background: #f8f9fa;">
                        <h3>Привет, {{user_name}}!</h3>
                        
                        <div style="background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f59e0b;">
                            <h4>📅 Ваш экзамен состоится:</h4>
                            <p><strong>{{exam_date}}</strong></p>
                            <p><strong>Время:</strong> {{exam_time}}</p>
                            <p><strong>Место:</strong> {{exam_location}}</p>
                        </div>
                        
                        <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h4>📊 Ваша готовность:</h4>
                            <p>Общий прогресс: <strong>{{readiness_percentage}}%</strong></p>
                            <p>Оценка готовности: <strong>{{readiness_level}}</strong></p>
                            
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;">
                                <h5>Рекомендации на оставшееся время:</h5>
                                <ul>
                                    {% for recommendation in recommendations %}
                                    <li>{{recommendation}}</li>
                                    {% endfor %}
                                </ul>
                            </div>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{{study_url}}" style="background: #ef4444; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block;">
                                Продолжить подготовку
                            </a>
                        </div>
                    </div>
                </div>
                '''
            }
        }
    
    def send_email_notification(self, user_id, notification_type, context_data):
        """Отправка email уведомления"""
        try:
            user = User.query.get(user_id)
            if not user or not user.email:
                return False
            
            template = self.email_templates.get(notification_type)
            if not template:
                return False
            
            # Подготавливаем контекст
            context = {
                'user_name': user.first_name or user.username,
                'user_email': user.email,
                'login_url': f"{current_app.config.get('BASE_URL', 'http://localhost:5000')}/auth/login",
                'dashboard_url': f"{current_app.config.get('BASE_URL', 'http://localhost:5000')}/dashboard",
                'unsubscribe_url': f"{current_app.config.get('BASE_URL', 'http://localhost:5000')}/unsubscribe/{user.id}",
                **context_data
            }
            
            # Рендерим шаблон
            subject = render_template_string(template['subject'], **context)
            html_content = render_template_string(template['template'], **context)
            
            # Создаем сообщение
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@mentora.academy')
            msg['To'] = user.email
            
            # Добавляем HTML контент
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Отправляем email
            self._send_email(msg)
            
            # Логируем отправку
            current_app.logger.info(f"Email notification sent to {user.email}: {notification_type}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error sending email notification: {e}")
            return False
    
    def _send_email(self, msg):
        """Отправка email через SMTP"""
        try:
            # Используем настройки из конфига
            smtp_server = current_app.config.get('MAIL_SERVER', 'localhost')
            smtp_port = current_app.config.get('MAIL_PORT', 587)
            smtp_username = current_app.config.get('MAIL_USERNAME')
            smtp_password = current_app.config.get('MAIL_PASSWORD')
            use_tls = current_app.config.get('MAIL_USE_TLS', True)
            
            # Для разработки используем локальный SMTP
            if smtp_server == 'localhost':
                # Используем Python's built-in SMTP server для тестирования
                with smtplib.SMTP('localhost', 1025) as server:
                    server.send_message(msg)
            else:
                # Продакшн SMTP
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    if use_tls:
                        server.starttls()
                    if smtp_username and smtp_password:
                        server.login(smtp_username, smtp_password)
                    server.send_message(msg)
                    
        except Exception as e:
            current_app.logger.error(f"SMTP error: {e}")
            raise
    
    def send_session_reminder(self, user_id, session_id):
        """Отправка напоминания о занятии"""
        try:
            session = StudySession.query.get(session_id)
            if not session:
                return False
            
            # Получаем данные для контекста
            context = {
                'session_title': f"Изучение {session.domain.name if session.domain else 'материала'}",
                'session_time': session.started_at.strftime('%H:%M') if session.started_at else '09:00',
                'session_duration': session.planned_duration or 2,
                'domain_name': session.domain.name if session.domain else 'Общий материал',
                'overall_progress': round(session.learning_plan.overall_progress or 0),
                'days_to_exam': self._calculate_days_to_exam(session.learning_plan),
                'daily_tip': self._get_daily_tip()
            }
            
            return self.send_email_notification(user_id, 'session_reminder', context)
            
        except Exception as e:
            current_app.logger.error(f"Error sending session reminder: {e}")
            return False
    
    def send_weekly_progress_report(self, user_id, plan_id):
        """Отправка еженедельного отчета"""
        try:
            plan = PersonalLearningPlan.query.get(plan_id)
            if not plan:
                return False
            
            # Получаем данные за неделю
            week_start = datetime.now(timezone.utc) - timedelta(days=7)
            week_sessions = plan.study_sessions.filter(
                StudySession.completed_at >= week_start
            ).all()
            
            # Рассчитываем статистику
            completed_sessions = len([s for s in week_sessions if s.status == 'completed'])
            hours_studied = sum(s.actual_duration or 0 for s in week_sessions if s.status == 'completed')
            questions_answered = sum(s.questions_answered or 0 for s in week_sessions)
            correct_answers = sum(s.correct_answers or 0 for s in week_sessions)
            
            # Прогресс по доменам
            domain_progress = self._get_domain_progress(plan)
            
            # Следующая неделя
            next_week_sessions = self._get_next_week_sessions(plan)
            
            context = {
                'week_number': self._calculate_week_number(plan),
                'completed_sessions': completed_sessions,
                'hours_studied': round(hours_studied / 60, 1),  # Переводим в часы
                'questions_answered': questions_answered,
                'correct_answers': correct_answers,
                'domain_progress': domain_progress,
                'next_week_sessions': next_week_sessions
            }
            
            return self.send_email_notification(user_id, 'weekly_progress', context)
            
        except Exception as e:
            current_app.logger.error(f"Error sending weekly report: {e}")
            return False
    
    def send_exam_reminder(self, user_id, plan_id):
        """Отправка напоминания о экзамене"""
        try:
            plan = PersonalLearningPlan.query.get(plan_id)
            if not plan or not plan.exam_date:
                return False
            
            days_left = (plan.exam_date - datetime.now(timezone.utc).date()).days
            
            if days_left <= 0:
                return False
            
            # Получаем данные готовности
            readiness_data = plan.calculate_readiness()
            
            context = {
                'days_left': days_left,
                'exam_date': plan.exam_date.strftime('%d.%m.%Y'),
                'exam_time': '09:00',  # По умолчанию
                'exam_location': 'Указано в приглашении',
                'readiness_percentage': round(readiness_data.get('readiness_percentage', 0)),
                'readiness_level': readiness_data.get('readiness_level', 'Неизвестно'),
                'recommendations': self._get_exam_recommendations(plan, days_left),
                'study_url': f"{current_app.config.get('BASE_URL', 'http://localhost:5000')}/dashboard/learning-plan/{plan.id}"
            }
            
            return self.send_email_notification(user_id, 'exam_reminder', context)
            
        except Exception as e:
            current_app.logger.error(f"Error sending exam reminder: {e}")
            return False
    
    def _calculate_days_to_exam(self, plan):
        """Рассчитывает дни до экзамена"""
        if not plan or not plan.exam_date:
            return 0
        return (plan.exam_date - datetime.now(timezone.utc).date()).days
    
    def _get_daily_tip(self):
        """Возвращает совет дня"""
        tips = [
            "Попробуйте технику Помодоро: 25 минут учебы, 5 минут отдыха",
            "Повторяйте материал перед сном - это улучшает запоминание",
            "Используйте карточки для запоминания ключевых терминов",
            "Практикуйтесь на реальных клинических случаях",
            "Объясняйте материал другим - это лучший способ понять его самому"
        ]
        import random
        return random.choice(tips)
    
    def _get_domain_progress(self, plan):
        """Получает прогресс по доменам"""
        domain_analysis = plan.get_domain_analysis()
        progress = []
        
        for domain_code, data in domain_analysis.items():
            if data.get('has_data'):
                progress.append({
                    'name': data.get('name', domain_code),
                    'progress': round(data.get('accuracy_percentage', 0)),
                    'target': round(data.get('target_percentage', 80))
                })
        
        return progress[:5]  # Топ-5 доменов
    
    def _get_next_week_sessions(self, plan):
        """Получает занятия на следующую неделю"""
        schedule = plan.get_study_schedule()
        if not schedule or not schedule.get('weekly_schedule'):
            return []
        
        # Берем первую неделю из расписания
        week_data = schedule['weekly_schedule'][0] if schedule['weekly_schedule'] else {}
        sessions = week_data.get('daily_sessions', [])
        
        return [
            {
                'day': session.get('day', 'Понедельник'),
                'title': session.get('title', 'Изучение материала'),
                'duration': session.get('duration', 2)
            }
            for session in sessions[:5]  # Первые 5 занятий
        ]
    
    def _calculate_week_number(self, plan):
        """Рассчитывает номер недели обучения"""
        if not plan.start_date:
            return 1
        
        start_date = plan.start_date
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        weeks_passed = (datetime.now(timezone.utc).date() - start_date).days // 7
        return max(1, weeks_passed + 1)
    
    def _get_exam_recommendations(self, plan, days_left):
        """Получает рекомендации для экзамена"""
        if days_left <= 7:
            return [
                "Повторите ключевые концепции",
                "Пройдите финальную диагностику",
                "Отдохните и выспитесь перед экзаменом"
            ]
        elif days_left <= 14:
            return [
                "Сфокусируйтесь на слабых областях",
                "Практикуйтесь на сложных вопросах",
                "Повторите клинические протоколы"
            ]
        else:
            return [
                "Продолжайте регулярные занятия",
                "Практикуйтесь на промежуточных тестах",
                "Изучайте новые материалы"
            ]

# Глобальный экземпляр системы уведомлений
notification_system = LearningNotificationSystem() 