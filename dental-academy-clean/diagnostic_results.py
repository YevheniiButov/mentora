#!/usr/bin/env python3
"""
Система результатов диагностики БЕЗ обучающих компонентов
Только численные оценки, процентили и статистика
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from sqlalchemy import func, and_

from extensions import db
from models import (
    DiagnosticSession, DiagnosticResponse, Question, 
    Specialty, SpecialtyDomain, DiagnosticResult
)

logger = logging.getLogger(__name__)


class DiagnosticResults:
    """Результаты диагностики БЕЗ обучающих компонентов"""
    
    def __init__(self, session: DiagnosticSession):
        self.session = session
        self.specialty = session.specialty
        self.responses = session.responses.all()
    
    def generate_comprehensive_report(self) -> Dict:
        """Генерировать полный отчет диагностики"""
        try:
            report = {
                # Основные метрики IRT
                'theta_score': self.session.current_ability,
                'standard_error': self.session.ability_se,
                'confidence_interval': self._calculate_confidence_interval(),
                
                # Процентильный ранг
                'percentile_rank': self._calculate_percentile_rank(),
                'peer_comparison': self._get_peer_comparison(),
                
                # Статистика по категориям
                'category_scores': self._calculate_category_scores(),
                'domain_analysis': self._analyze_domain_performance(),
                
                # Метрики качества
                'total_questions': self.session.questions_answered,
                'correct_answers': self.session.correct_answers,
                'accuracy': self.session.get_accuracy(),
                'response_time_analysis': self._analyze_response_times(),
                
                # Временные метки
                'session_duration': self._calculate_session_duration(),
                'completed_at': self.session.completed_at.isoformat() if self.session.completed_at else None,
                
                # Метаданные
                'specialty': self.specialty.to_dict(),
                'session_type': self.session.session_type,
                'assessment_mode': self.session.assessment_mode,
                
                # НЕ ВКЛЮЧАЕМ:
                # - learning_plan
                # - recommendations
                # - study_suggestions
                # - improvement_areas
                # - next_steps
            }
            
            logger.info(f"Generated diagnostic report for session {self.session.id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating diagnostic report: {str(e)}")
            return self._get_error_report()
    
    def _calculate_confidence_interval(self, confidence_level: float = 0.95) -> Dict:
        """Рассчитать доверительный интервал для theta"""
        try:
            from scipy import stats
            
            # 95% доверительный интервал
            z_score = stats.norm.ppf((1 + confidence_level) / 2)
            margin_of_error = z_score * self.session.ability_se
            
            return {
                'level': confidence_level,
                'lower': self.session.current_ability - margin_of_error,
                'upper': self.session.current_ability + margin_of_error,
                'margin_of_error': margin_of_error
            }
            
        except Exception as e:
            logger.error(f"Error calculating confidence interval: {str(e)}")
            return {
                'level': confidence_level,
                'lower': None,
                'upper': None,
                'margin_of_error': None
            }
    
    def _calculate_percentile_rank(self) -> float:
        """Рассчитать процентильный ранг среди коллег"""
        try:
            # Получаем все завершенные сессии той же специальности
            peer_sessions = DiagnosticSession.query.filter(
                and_(
                    DiagnosticSession.specialty_id == self.session.specialty_id,
                    DiagnosticSession.status == 'completed',
                    DiagnosticSession.id != self.session.id
                )
            ).all()
            
            if not peer_sessions:
                # Если нет других сессий, возвращаем 50 (средний)
                return 50.0
            
            # Получаем способности коллег
            peer_abilities = [s.current_ability for s in peer_sessions if s.current_ability is not None]
            user_ability = self.session.current_ability
            
            if not peer_abilities:
                return 50.0
            
            # Рассчитываем процентиль
            below_count = sum(1 for ability in peer_abilities if ability < user_ability)
            percentile = (below_count / len(peer_abilities)) * 100
            
            return round(percentile, 1)
            
        except Exception as e:
            logger.error(f"Error calculating percentile rank: {str(e)}")
            return 50.0
    
    def _get_peer_comparison(self) -> Dict:
        """Получить сравнение с коллегами"""
        try:
            # Статистика по коллегам
            peer_stats = db.session.query(
                func.avg(DiagnosticSession.current_ability).label('avg_ability'),
                func.stddev(DiagnosticSession.current_ability).label('std_ability'),
                func.count(DiagnosticSession.id).label('total_sessions')
            ).filter(
                and_(
                    DiagnosticSession.specialty_id == self.session.specialty_id,
                    DiagnosticSession.status == 'completed',
                    DiagnosticSession.id != self.session.id
                )
            ).first()
            
            if not peer_stats or peer_stats.total_sessions == 0:
                return {
                    'peer_count': 0,
                    'peer_average': None,
                    'peer_std': None,
                    'user_vs_peer': None
                }
            
            user_ability = self.session.current_ability
            peer_avg = peer_stats.avg_ability
            peer_std = peer_stats.std_ability or 0
            
            # Рассчитываем z-score
            if peer_std > 0:
                z_score = (user_ability - peer_avg) / peer_std
            else:
                z_score = 0
            
            return {
                'peer_count': peer_stats.total_sessions,
                'peer_average': round(peer_avg, 3),
                'peer_std': round(peer_std, 3),
                'user_vs_peer': {
                    'z_score': round(z_score, 2),
                    'description': self._get_z_score_description(z_score)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting peer comparison: {str(e)}")
            return {
                'peer_count': 0,
                'peer_average': None,
                'peer_std': None,
                'user_vs_peer': None
            }
    
    def _get_z_score_description(self, z_score: float) -> str:
        """Получить описание z-score"""
        if z_score >= 2.0:
            return "Significantly above average"
        elif z_score >= 1.0:
            return "Above average"
        elif z_score >= -1.0:
            return "Average"
        elif z_score >= -2.0:
            return "Below average"
        else:
            return "Significantly below average"
    
    def _calculate_category_scores(self) -> Dict:
        """Рассчитать оценки по категориям"""
        try:
            category_scores = {}
            
            for response in self.responses:
                question = response.question
                if not question.specialty_domain:
                    continue
                
                category = question.specialty_domain.category
                
                if category not in category_scores:
                    category_scores[category] = {
                        'correct': 0,
                        'total': 0,
                        'accuracy': 0.0,
                        'avg_response_time': 0.0,
                        'questions': []
                    }
                
                category_scores[category]['total'] += 1
                category_scores[category]['questions'].append({
                    'question_id': question.id,
                    'is_correct': response.is_correct,
                    'response_time': response.response_time
                })
                
                if response.is_correct:
                    category_scores[category]['correct'] += 1
            
            # Рассчитываем точность и среднее время ответа
            for category in category_scores:
                total = category_scores[category]['total']
                correct = category_scores[category]['correct']
                category_scores[category]['accuracy'] = (correct / total) * 100 if total > 0 else 0
                
                # Среднее время ответа
                response_times = [q['response_time'] for q in category_scores[category]['questions'] 
                                if q['response_time'] is not None]
                if response_times:
                    category_scores[category]['avg_response_time'] = sum(response_times) / len(response_times)
                
                # Удаляем детали вопросов из результата
                del category_scores[category]['questions']
            
            return category_scores
            
        except Exception as e:
            logger.error(f"Error calculating category scores: {str(e)}")
            return {}
    
    def _analyze_domain_performance(self) -> Dict:
        """Анализ производительности по доменам"""
        try:
            domain_analysis = {}
            
            for response in self.responses:
                question = response.question
                if not question.specialty_domain:
                    continue
                
                domain_code = question.specialty_domain.domain_code
                domain_name = question.specialty_domain.domain_name
                
                if domain_code not in domain_analysis:
                    domain_analysis[domain_code] = {
                        'domain_name': domain_name,
                        'category': question.specialty_domain.category,
                        'is_critical': question.specialty_domain.is_critical,
                        'correct': 0,
                        'total': 0,
                        'accuracy': 0.0,
                        'avg_response_time': 0.0,
                        'difficulty_levels': {}
                    }
                
                domain_analysis[domain_code]['total'] += 1
                
                if response.is_correct:
                    domain_analysis[domain_code]['correct'] += 1
                
                # Анализ по уровням сложности
                difficulty = question.difficulty_level
                if difficulty not in domain_analysis[domain_code]['difficulty_levels']:
                    domain_analysis[domain_code]['difficulty_levels'][difficulty] = {
                        'correct': 0,
                        'total': 0
                    }
                
                domain_analysis[domain_code]['difficulty_levels'][difficulty]['total'] += 1
                if response.is_correct:
                    domain_analysis[domain_code]['difficulty_levels'][difficulty]['correct'] += 1
            
            # Рассчитываем итоговые метрики
            for domain_code in domain_analysis:
                domain = domain_analysis[domain_code]
                total = domain['total']
                correct = domain['correct']
                domain['accuracy'] = (correct / total) * 100 if total > 0 else 0
                
                # Среднее время ответа
                response_times = [r.response_time for r in self.responses 
                                if r.question.specialty_domain and 
                                r.question.specialty_domain.domain_code == domain_code and
                                r.response_time is not None]
                if response_times:
                    domain['avg_response_time'] = sum(response_times) / len(response_times)
                
                # Рассчитываем точность по уровням сложности
                for difficulty in domain['difficulty_levels']:
                    diff_data = domain['difficulty_levels'][difficulty]
                    diff_data['accuracy'] = (diff_data['correct'] / diff_data['total']) * 100 if diff_data['total'] > 0 else 0
            
            return domain_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing domain performance: {str(e)}")
            return {}
    
    def _analyze_response_times(self) -> Dict:
        """Анализ времени ответов"""
        try:
            response_times = [r.response_time for r in self.responses if r.response_time is not None]
            
            if not response_times:
                return {
                    'avg_time': None,
                    'median_time': None,
                    'min_time': None,
                    'max_time': None,
                    'total_time': None
                }
            
            response_times.sort()
            n = len(response_times)
            
            return {
                'avg_time': round(sum(response_times) / n, 2),
                'median_time': round(response_times[n // 2], 2),
                'min_time': round(min(response_times), 2),
                'max_time': round(max(response_times), 2),
                'total_time': round(sum(response_times), 2),
                'count': n
            }
            
        except Exception as e:
            logger.error(f"Error analyzing response times: {str(e)}")
            return {
                'avg_time': None,
                'median_time': None,
                'min_time': None,
                'max_time': None,
                'total_time': None
            }
    
    def _calculate_session_duration(self) -> Optional[int]:
        """Рассчитать длительность сессии в секундах"""
        try:
            if self.session.completed_at and self.session.started_at:
                duration = (self.session.completed_at - self.session.started_at).total_seconds()
                return int(duration)
            return None
            
        except Exception as e:
            logger.error(f"Error calculating session duration: {str(e)}")
            return None
    
    def _get_error_report(self) -> Dict:
        """Получить отчет об ошибке"""
        return {
            'error': True,
            'message': 'Failed to generate diagnostic report',
            'session_id': self.session.id,
            'specialty': self.specialty.to_dict() if self.specialty else None
        }
    
    def save_results(self) -> Optional[DiagnosticResult]:
        """Сохранить результаты в базе данных"""
        try:
            # Проверяем, не сохранены ли уже результаты
            existing_result = DiagnosticResult.query.filter_by(session_id=self.session.id).first()
            if existing_result:
                logger.warning(f"Results already exist for session {self.session.id}")
                return existing_result
            
            # Генерируем отчет
            report = self.generate_comprehensive_report()
            
            if report.get('error'):
                logger.error(f"Cannot save results due to error in report generation")
                return None
            
            # Создаем запись результатов
            result = DiagnosticResult(
                session_id=self.session.id,
                user_id=self.session.user_id,
                specialty_id=self.session.specialty_id,
                theta_score=report['theta_score'],
                standard_error=report['standard_error'],
                confidence_interval_lower=report['confidence_interval']['lower'],
                confidence_interval_upper=report['confidence_interval']['upper'],
                percentile_rank=report['percentile_rank'],
                total_questions=report['total_questions'],
                correct_answers=report['correct_answers'],
                accuracy=report['accuracy'],
                avg_response_time=report['response_time_analysis']['avg_time'],
                category_scores=json.dumps(report['category_scores']),
                domain_analysis=json.dumps(report['domain_analysis']),
                session_duration=report['session_duration'],
                completed_at=self.session.completed_at or datetime.now(timezone.utc)
            )
            
            db.session.add(result)
            db.session.commit()
            
            logger.info(f"Saved diagnostic results for session {self.session.id}")
            return result
            
        except Exception as e:
            logger.error(f"Error saving diagnostic results: {str(e)}")
            db.session.rollback()
            return None


class ResultsComparison:
    """Сравнение результатов между сессиями"""
    
    def __init__(self, user_id: int, specialty_id: int):
        self.user_id = user_id
        self.specialty_id = specialty_id
    
    def get_user_progress(self) -> Dict:
        """Получить прогресс пользователя"""
        try:
            # Получаем все результаты пользователя по специальности
            results = DiagnosticResult.query.filter(
                and_(
                    DiagnosticResult.user_id == self.user_id,
                    DiagnosticResult.specialty_id == self.specialty_id
                )
            ).order_by(DiagnosticResult.completed_at.desc()).all()
            
            if not results:
                return {
                    'total_sessions': 0,
                    'progress': [],
                    'improvement': None
                }
            
            # Анализируем прогресс
            progress = []
            for i, result in enumerate(results):
                progress.append({
                    'session_number': len(results) - i,
                    'date': result.completed_at.isoformat(),
                    'theta_score': result.theta_score,
                    'percentile_rank': result.percentile_rank,
                    'accuracy': result.accuracy,
                    'total_questions': result.total_questions
                })
            
            # Рассчитываем улучшение
            improvement = None
            if len(results) >= 2:
                latest = results[0]
                previous = results[1]
                
                improvement = {
                    'theta_change': latest.theta_score - previous.theta_score,
                    'percentile_change': latest.percentile_rank - previous.percentile_rank,
                    'accuracy_change': latest.accuracy - previous.accuracy,
                    'time_between_sessions': (latest.completed_at - previous.completed_at).days
                }
            
            return {
                'total_sessions': len(results),
                'progress': progress,
                'improvement': improvement,
                'latest_result': results[0].to_dict() if results else None
            }
            
        except Exception as e:
            logger.error(f"Error getting user progress: {str(e)}")
            return {
                'total_sessions': 0,
                'progress': [],
                'improvement': None
            }
    
    def get_specialty_statistics(self) -> Dict:
        """Получить статистику по специальности"""
        try:
            # Общая статистика по специальности
            stats = db.session.query(
                func.count(DiagnosticResult.id).label('total_sessions'),
                func.avg(DiagnosticResult.theta_score).label('avg_theta'),
                func.stddev(DiagnosticResult.theta_score).label('std_theta'),
                func.avg(DiagnosticResult.accuracy).label('avg_accuracy'),
                func.count(func.distinct(DiagnosticResult.user_id)).label('unique_users')
            ).filter(
                DiagnosticResult.specialty_id == self.specialty_id
            ).first()
            
            return {
                'total_sessions': stats.total_sessions or 0,
                'unique_users': stats.unique_users or 0,
                'average_theta': round(stats.avg_theta, 3) if stats.avg_theta else None,
                'theta_std': round(stats.std_theta, 3) if stats.std_theta else None,
                'average_accuracy': round(stats.avg_accuracy, 1) if stats.avg_accuracy else None
            }
            
        except Exception as e:
            logger.error(f"Error getting specialty statistics: {str(e)}")
            return {
                'total_sessions': 0,
                'unique_users': 0,
                'average_theta': None,
                'theta_std': None,
                'average_accuracy': None
            }


