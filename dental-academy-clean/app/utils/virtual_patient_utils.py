#!/usr/bin/env python3
"""
Утилиты для работы с виртуальными пациентами в ежедневных сессиях
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app import db
from models import VirtualPatientScenario, VirtualPatientAttempt, User


class VirtualPatientSelector:
    """Класс для выбора виртуальных пациентов для ежедневных сессий"""
    
    @staticmethod
    def get_daily_scenario(user: User) -> Optional[VirtualPatientScenario]:
        """
        Получить сценарий виртуального пациента для ежедневной сессии
        
        Args:
            user: Пользователь
            
        Returns:
            VirtualPatientScenario или None
        """
        try:
            # Получаем все доступные сценарии для специальности пользователя
            available_scenarios = VirtualPatientScenario.query.filter(
                VirtualPatientScenario.specialty == user.specialty,
                VirtualPatientScenario.is_published == True
            ).all()
            
            if not available_scenarios:
                return None
            
            # Фильтруем сценарии, которые доступны для пользователя
            available_for_user = [
                scenario for scenario in available_scenarios
                if scenario.is_available_for_user(user)
            ]
            
            if not available_for_user:
                # Если нет доступных сценариев, выбираем случайный
                return random.choice(available_scenarios)
            
            # Выбираем случайный из доступных
            selected_scenario = random.choice(available_for_user)
            
            # Отмечаем как сыгранный
            selected_scenario.mark_played()
            
            return selected_scenario
            
        except Exception as e:
            print(f"Error getting daily scenario: {e}")
            return None
    
    @staticmethod
    def get_scenario_by_keywords(user: User, keywords: List[str]) -> Optional[VirtualPatientScenario]:
        """
        Получить сценарий по ключевым словам
        
        Args:
            user: Пользователь
            keywords: Список ключевых слов
            
        Returns:
            VirtualPatientScenario или None
        """
        try:
            # Поиск по ключевым словам
            scenarios = VirtualPatientScenario.query.filter(
                VirtualPatientScenario.specialty == user.specialty,
                VirtualPatientScenario.is_published == True
            ).all()
            
            # Фильтруем по ключевым словам
            matching_scenarios = []
            for scenario in scenarios:
                scenario_keywords = scenario.keywords_list
                if any(keyword.lower() in [kw.lower() for kw in scenario_keywords] for keyword in keywords):
                    matching_scenarios.append(scenario)
            
            if not matching_scenarios:
                return None
            
            # Выбираем случайный из подходящих
            selected_scenario = random.choice(matching_scenarios)
            selected_scenario.mark_played()
            
            return selected_scenario
            
        except Exception as e:
            print(f"Error getting scenario by keywords: {e}")
            return None
    
    @staticmethod
    def get_user_statistics(user: User) -> Dict:
        """
        Получить статистику пользователя по виртуальным пациентам
        
        Args:
            user: Пользователь
            
        Returns:
            Словарь со статистикой
        """
        try:
            # Общее количество попыток
            total_attempts = VirtualPatientAttempt.query.filter_by(user_id=user.id).count()
            
            # Завершенные попытки
            completed_attempts = VirtualPatientAttempt.query.filter_by(
                user_id=user.id, 
                completed=True
            ).count()
            
            # Средний балл
            avg_score = db.session.query(db.func.avg(VirtualPatientAttempt.score)).filter(
                VirtualPatientAttempt.user_id == user.id,
                VirtualPatientAttempt.completed == True
            ).scalar() or 0
            
            # Лучший балл
            best_score = db.session.query(db.func.max(VirtualPatientAttempt.score)).filter(
                VirtualPatientAttempt.user_id == user.id,
                VirtualPatientAttempt.completed == True
            ).scalar() or 0
            
            # Количество уникальных сценариев
            unique_scenarios = db.session.query(db.func.count(db.func.distinct(
                VirtualPatientAttempt.scenario_id
            ))).filter(VirtualPatientAttempt.user_id == user.id).scalar() or 0
            
            # Попытки за последние 7 дней
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_attempts = VirtualPatientAttempt.query.filter(
                VirtualPatientAttempt.user_id == user.id,
                VirtualPatientAttempt.started_at >= week_ago
            ).count()
            
            return {
                'total_attempts': total_attempts,
                'completed_attempts': completed_attempts,
                'completion_rate': (completed_attempts / total_attempts * 100) if total_attempts > 0 else 0,
                'average_score': round(float(avg_score), 2),
                'best_score': best_score,
                'unique_scenarios': unique_scenarios,
                'recent_attempts': recent_attempts
            }
            
        except Exception as e:
            print(f"Error getting user statistics: {e}")
            return {
                'total_attempts': 0,
                'completed_attempts': 0,
                'completion_rate': 0,
                'average_score': 0,
                'best_score': 0,
                'unique_scenarios': 0,
                'recent_attempts': 0
            }


class VirtualPatientSessionManager:
    """Менеджер сессий виртуальных пациентов"""
    
    @staticmethod
    def start_attempt(user: User, scenario_id: int) -> Optional[VirtualPatientAttempt]:
        """
        Начать новую попытку прохождения сценария
        
        Args:
            user: Пользователь
            scenario_id: ID сценария
            
        Returns:
            VirtualPatientAttempt или None
        """
        try:
            scenario = VirtualPatientScenario.query.get(scenario_id)
            if not scenario:
                return None
            
            # Проверяем доступность сценария
            if not scenario.is_available_for_user(user):
                return None
            
            # Создаем новую попытку
            attempt = VirtualPatientAttempt(
                user_id=user.id,
                scenario_id=scenario_id,
                max_score=scenario.max_score,
                started_at=datetime.utcnow()
            )
            
            db.session.add(attempt)
            db.session.commit()
            
            return attempt
            
        except Exception as e:
            print(f"Error starting attempt: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def complete_attempt(attempt_id: int, score: int, time_spent: float, 
                        dialogue_history: List[Dict] = None) -> bool:
        """
        Завершить попытку прохождения
        
        Args:
            attempt_id: ID попытки
            score: Полученный балл
            time_spent: Время в минутах
            dialogue_history: История диалога
            
        Returns:
            True если успешно
        """
        try:
            attempt = VirtualPatientAttempt.query.get(attempt_id)
            if not attempt:
                return False
            
            attempt.score = score
            attempt.completed = True
            attempt.time_spent = time_spent
            attempt.completed_at = datetime.utcnow()
            
            if dialogue_history:
                attempt.dialogue_history = json.dumps(dialogue_history)
            
            db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"Error completing attempt: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def add_fill_in_answer(attempt_id: int, node_id: str, answer: str) -> bool:
        """
        Добавить ответ на вопрос с заполнением пропусков
        
        Args:
            attempt_id: ID попытки
            node_id: ID узла диалога
            answer: Ответ пользователя
            
        Returns:
            True если успешно
        """
        try:
            attempt = VirtualPatientAttempt.query.get(attempt_id)
            if not attempt:
                return False
            
            attempt.add_fill_in_answer(node_id, answer)
            db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"Error adding fill-in answer: {e}")
            db.session.rollback()
            return False


class VirtualPatientDailyIntegration:
    """Интеграция виртуальных пациентов в ежедневные сессии"""
    
    @staticmethod
    def get_daily_vp_session(user: User) -> Dict:
        """
        Получить данные для ежедневной сессии с виртуальным пациентом
        
        Args:
            user: Пользователь
            
        Returns:
            Словарь с данными сессии
        """
        try:
            # Получаем сценарий для дня
            scenario = VirtualPatientSelector.get_daily_scenario(user)
            
            if not scenario:
                return {
                    'available': False,
                    'message': 'No virtual patient scenarios available for your specialty'
                }
            
            # Получаем статистику пользователя
            stats = VirtualPatientSelector.get_user_statistics(user)
            
            return {
                'available': True,
                'scenario': {
                    'id': scenario.id,
                    'title': scenario.title,
                    'description': scenario.description,
                    'difficulty': scenario.difficulty,
                    'max_score': scenario.max_score,
                    'keywords': scenario.keywords_list
                },
                'user_stats': stats,
                'session_type': 'virtual_patient'
            }
            
        except Exception as e:
            print(f"Error getting daily VP session: {e}")
            return {
                'available': False,
                'message': 'Error loading virtual patient session'
            }
    
    @staticmethod
    def integrate_with_daily_learning(user: User, existing_sessions: List[Dict]) -> List[Dict]:
        """
        Интегрировать виртуальных пациентов в существующие ежедневные сессии
        
        Args:
            user: Пользователь
            existing_sessions: Существующие сессии
            
        Returns:
            Обновленный список сессий
        """
        try:
            # Получаем данные для виртуального пациента
            vp_session = VirtualPatientDailyIntegration.get_daily_vp_session(user)
            
            if vp_session['available']:
                # Добавляем сессию с виртуальным пациентом
                vp_session_data = {
                    'id': f"vp_{vp_session['scenario']['id']}",
                    'type': 'virtual_patient',
                    'title': f"Virtual Patient: {vp_session['scenario']['title']}",
                    'description': vp_session['scenario']['description'],
                    'difficulty': vp_session['scenario']['difficulty'],
                    'estimated_duration': 15,  # минут
                    'scenario_id': vp_session['scenario']['id'],
                    'max_score': vp_session['scenario']['max_score'],
                    'keywords': vp_session['scenario']['keywords'],
                    'status': 'ready'
                }
                
                existing_sessions.append(vp_session_data)
            
            return existing_sessions
            
        except Exception as e:
            print(f"Error integrating VP with daily learning: {e}")
            return existing_sessions







