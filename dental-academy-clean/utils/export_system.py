#!/usr/bin/env python3
"""
Система экспорта расписания обучения
"""

import json
from datetime import datetime, timedelta, timezone
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from models import User, PersonalLearningPlan, StudySession, BIGDomain

class LearningPlanExporter:
    """Система экспорта планов обучения"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Настройка пользовательских стилей для PDF"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1d4ed8')
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#6C5CE7')
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=6
        )
        
        self.highlight_style = ParagraphStyle(
            'CustomHighlight',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=6,
            textColor=colors.HexColor('#22c55e'),
            fontName='Helvetica-Bold'
        )
    
    def export_to_ical(self, plan_id, user_id):
        """Экспорт плана обучения в формат iCal"""
        try:
            plan = PersonalLearningPlan.query.get(plan_id)
            if not plan or plan.user_id != user_id:
                return None
            
            # Получаем расписание занятий
            study_sessions = plan.study_sessions.filter_by(status='planned').all()
            
            # Создаем iCal контент
            ical_content = self._generate_ical_content(plan, study_sessions)
            
            return ical_content
            
        except Exception as e:
            print(f"Error exporting to iCal: {e}")
            return None
    
    def _generate_ical_content(self, plan, study_sessions):
        """Генерирует iCal контент"""
        now = datetime.now(timezone.utc)
        
        ical_lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Mentora Academy//Learning Plan//RU",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            f"X-WR-CALNAME:Mentora Academy - План обучения",
            f"X-WR-CALDESC:План подготовки к BIG экзамену",
        ]
        
        # Добавляем занятия
        for session in study_sessions:
            if session.started_at:
                event_lines = self._create_ical_event(session, plan)
                ical_lines.extend(event_lines)
        
        # Добавляем экзамен если есть
        if plan.exam_date:
            exam_lines = self._create_ical_exam_event(plan)
            ical_lines.extend(exam_lines)
        
        ical_lines.append("END:VCALENDAR")
        
        return "\r\n".join(ical_lines)
    
    def _create_ical_event(self, session, plan):
        """Создает iCal событие для занятия"""
        start_time = session.started_at
        end_time = start_time + timedelta(hours=session.planned_duration or 2)
        
        # Форматируем время для iCal
        start_str = start_time.strftime("%Y%m%dT%H%M%SZ")
        end_str = end_time.strftime("%Y%m%dT%H%M%SZ")
        created_str = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        
        # Создаем уникальный ID
        event_id = f"mentora-session-{session.id}@mentora.academy"
        
        # Описание занятия
        domain_name = session.domain.name if session.domain else "Общий материал"
        description = f"Изучение: {domain_name}\n"
        description += f"Тип: {session.session_type}\n"
        description += f"Длительность: {session.planned_duration or 2} часа\n"
        description += f"Прогресс плана: {plan.overall_progress or 0}%"
        
        # Локация (виртуальная)
        location = "Mentora Academy - Онлайн платформа"
        
        return [
            "BEGIN:VEVENT",
            f"UID:{event_id}",
            f"DTSTAMP:{created_str}",
            f"DTSTART:{start_str}",
            f"DTEND:{end_str}",
            f"SUMMARY:📚 {session.session_type.title()} - {domain_name}",
            f"DESCRIPTION:{description}",
            f"LOCATION:{location}",
            "CATEGORIES:EDUCATION,STUDY",
            "PRIORITY:3",
            "STATUS:CONFIRMED",
            "SEQUENCE:0",
            "END:VEVENT"
        ]
    
    def _create_ical_exam_event(self, plan):
        """Создает iCal событие для экзамена"""
        exam_date = plan.exam_date
        start_time = datetime.combine(exam_date, datetime.min.time().replace(hour=9, minute=0))
        start_time = start_time.replace(tzinfo=timezone.utc)
        end_time = start_time + timedelta(hours=4)  # 4 часа на экзамен
        
        start_str = start_time.strftime("%Y%m%dT%H%M%SZ")
        end_str = end_time.strftime("%Y%m%dT%H%M%SZ")
        created_str = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        
        event_id = f"mentora-exam-{plan.id}@mentora.academy"
        
        description = "BIG экзамен - Финальная проверка знаний\n"
        description += f"Готовность: {plan.overall_progress or 0}%\n"
        description += "Не забудьте взять документы и прибыть заранее!"
        
        return [
            "BEGIN:VEVENT",
            f"UID:{event_id}",
            f"DTSTAMP:{created_str}",
            f"DTSTART:{start_str}",
            f"DTEND:{end_str}",
            "SUMMARY:⚠️ BIG ЭКЗАМЕН",
            f"DESCRIPTION:{description}",
            "LOCATION:Указано в приглашении",
            "CATEGORIES:EXAM,IMPORTANT",
            "PRIORITY:1",
            "STATUS:CONFIRMED",
            "SEQUENCE:0",
            "END:VEVENT"
        ]
    
    def export_to_pdf(self, plan_id, user_id):
        """Экспорт плана обучения в PDF"""
        try:
            plan = PersonalLearningPlan.query.get(plan_id)
            if not plan or plan.user_id != user_id:
                return None
            
            user = User.query.get(user_id)
            study_sessions = plan.study_sessions.all()
            
            # Создаем PDF документ
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
            
            # Собираем элементы документа
            story = []
            
            # Заголовок
            story.append(Paragraph("MENTORA", self.title_style))
            story.append(Paragraph("Персональный план обучения", self.heading_style))
            story.append(Spacer(1, 20))
            
            # Информация о пользователе
            story.extend(self._create_user_info_section(user, plan))
            story.append(Spacer(1, 20))
            
            # Общая статистика
            story.extend(self._create_statistics_section(plan))
            story.append(Spacer(1, 20))
            
            # Анализ доменов
            story.extend(self._create_domain_analysis_section(plan))
            story.append(Spacer(1, 20))
            
            # Расписание занятий
            story.extend(self._create_schedule_section(study_sessions))
            story.append(Spacer(1, 20))
            
            # Цели обучения
            story.extend(self._create_goals_section(plan))
            story.append(Spacer(1, 20))
            
            # Рекомендации
            story.extend(self._create_recommendations_section(plan))
            
            # Строим PDF
            doc.build(story)
            
            # Получаем содержимое
            pdf_content = buffer.getvalue()
            buffer.close()
            
            return pdf_content
            
        except Exception as e:
            print(f"Error exporting to PDF: {e}")
            return None
    
    def _create_user_info_section(self, user, plan):
        """Создает секцию с информацией о пользователе"""
        elements = []
        
        elements.append(Paragraph("Информация о студенте", self.heading_style))
        
        user_info = [
            ["Имя:", user.first_name or user.username or "Не указано"],
            ["Email:", user.email or "Не указано"],
            ["Дата создания плана:", plan.last_updated.strftime("%d.%m.%Y") if plan.last_updated else "Не указано"],
            ["Дата экзамена:", plan.exam_date.strftime("%d.%m.%Y") if plan.exam_date else "Не указано"],
            ["Статус плана:", plan.status.title()]
        ]
        
        user_table = Table(user_info, colWidths=[2*inch, 4*inch])
        user_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(user_table)
        return elements
    
    def _create_statistics_section(self, plan):
        """Создает секцию со статистикой"""
        elements = []
        
        elements.append(Paragraph("Общая статистика", self.heading_style))
        
        # Рассчитываем статистику
        total_sessions = plan.study_sessions.count()
        completed_sessions = plan.study_sessions.filter_by(status='completed').count()
        upcoming_sessions = plan.study_sessions.filter_by(status='planned').count()
        
        days_to_exam = 0
        if plan.exam_date:
            days_to_exam = (plan.exam_date - datetime.now(timezone.utc).date()).days
        
        stats_info = [
            ["Общий прогресс:", f"{plan.overall_progress or 0}%"],
            ["Всего занятий:", str(total_sessions)],
            ["Завершено:", str(completed_sessions)],
            ["Запланировано:", str(upcoming_sessions)],
            ["Дней до экзамена:", str(max(0, days_to_exam))],
            ["Текущая способность:", f"{plan.current_ability:.3f}" if plan.current_ability else "Не рассчитано"]
        ]
        
        stats_table = Table(stats_info, colWidths=[2*inch, 4*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(stats_table)
        return elements
    
    def _create_domain_analysis_section(self, plan):
        """Создает секцию с анализом доменов"""
        elements = []
        
        elements.append(Paragraph("Анализ по доменам", self.heading_style))
        
        domain_analysis = plan.get_domain_analysis()
        if not domain_analysis:
            elements.append(Paragraph("Данные по доменам недоступны", self.normal_style))
            return elements
        
        # Создаем таблицу доменов
        domain_data = [["Домен", "Прогресс", "Цель", "Статус"]]
        
        for domain_code, data in domain_analysis.items():
            if data.get('has_data'):
                progress = data.get('accuracy_percentage', 0)
                target = data.get('target_percentage', 80)
                status = "✅ Хорошо" if progress >= target else "⚠️ Требует внимания"
                
                domain_data.append([
                    data.get('name', domain_code),
                    f"{progress:.1f}%",
                    f"{target}%",
                    status
                ])
        
        if len(domain_data) > 1:  # Есть данные кроме заголовка
            domain_table = Table(domain_data, colWidths=[2*inch, 1*inch, 1*inch, 2*inch])
            domain_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6C5CE7')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            elements.append(domain_table)
        else:
            elements.append(Paragraph("Нет данных по доменам", self.normal_style))
        
        return elements
    
    def _create_schedule_section(self, study_sessions):
        """Создает секцию с расписанием"""
        elements = []
        
        elements.append(Paragraph("Расписание занятий", self.heading_style))
        
        if not study_sessions:
            elements.append(Paragraph("Расписание занятий не создано", self.normal_style))
            return elements
        
        # Группируем занятия по неделям
        schedule_data = [["Дата", "Время", "Тип", "Домен", "Длительность", "Статус"]]
        
        for session in study_sessions[:20]:  # Ограничиваем первыми 20 занятиями
            date_str = session.started_at.strftime("%d.%m.%Y") if session.started_at else "Не указано"
            time_str = session.started_at.strftime("%H:%M") if session.started_at else "Не указано"
            domain_name = session.domain.name if session.domain else "Общий материал"
            duration = f"{session.planned_duration or 2}ч" if session.planned_duration else "2ч"
            
            schedule_data.append([
                date_str,
                time_str,
                session.session_type.title(),
                domain_name,
                duration,
                session.status.title()
            ])
        
        schedule_table = Table(schedule_data, colWidths=[1*inch, 0.8*inch, 1*inch, 1.5*inch, 0.8*inch, 1*inch])
        schedule_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1d4ed8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(schedule_table)
        
        if len(study_sessions) > 20:
            elements.append(Paragraph(f"... и еще {len(study_sessions) - 20} занятий", self.normal_style))
        
        return elements
    
    def _create_goals_section(self, plan):
        """Создает секцию с целями обучения"""
        elements = []
        
        elements.append(Paragraph("Цели обучения", self.heading_style))
        
        weak_domains = plan.get_weak_domain_names()
        if weak_domains:
            elements.append(Paragraph("Слабые области для улучшения:", self.normal_style))
            for domain in weak_domains[:5]:  # Топ-5 слабых областей
                elements.append(Paragraph(f"• {domain}", self.normal_style))
        else:
            elements.append(Paragraph("Все области изучены на хорошем уровне", self.highlight_style))
        
        elements.append(Spacer(1, 10))
        
        # Общие цели
        elements.append(Paragraph("Общие цели:", self.normal_style))
        elements.append(Paragraph("• Подготовиться к BIG экзамену", self.normal_style))
        elements.append(Paragraph("• Улучшить знания в слабых областях", self.normal_style))
        elements.append(Paragraph("• Достичь 80% готовности", self.normal_style))
        
        return elements
    
    def _create_recommendations_section(self, plan):
        """Создает секцию с рекомендациями"""
        elements = []
        
        elements.append(Paragraph("Рекомендации", self.heading_style))
        
        recommendations = [
            "Регулярно занимайтесь по расписанию",
            "Фокусируйтесь на слабых областях",
            "Проходите промежуточные тесты",
            "Практикуйтесь на клинических случаях",
            "Повторяйте материал перед сном"
        ]
        
        for rec in recommendations:
            elements.append(Paragraph(f"• {rec}", self.normal_style))
        
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Удачи в обучении!", self.highlight_style))
        
        return elements

# Глобальный экземпляр экспортера
exporter = LearningPlanExporter() 