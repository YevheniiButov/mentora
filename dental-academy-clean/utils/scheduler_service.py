#!/usr/bin/env python3
"""
Adaptive Diagnostic Scheduler Service

This service manages adaptive scheduling of diagnostic reassessments
based on user progress, learning patterns, and exam readiness.
"""

import logging
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

from models import PersonalLearningPlan, User, StudySession, DiagnosticSession
from extensions import db

logger = logging.getLogger(__name__)


class ReassessmentPriority(Enum):
    """Priority levels for diagnostic reassessment"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ReassessmentRecommendation:
    """Recommendation for diagnostic reassessment"""
    user_id: int
    plan_id: int
    priority: ReassessmentPriority
    recommended_date: date
    reason: str
    confidence: float
    estimated_days_needed: int
    current_ability: float
    target_ability: float
    weak_domains_count: int
    last_diagnostic_date: Optional[date]
    study_activity_score: float


class AdaptiveDiagnosticScheduler:
    """
    Adaptive scheduler for diagnostic reassessments
    
    Features:
    - Adaptive intervals based on user progress
    - Priority-based scheduling
    - Integration with email/push notifications
    - Admin monitoring capabilities
    """
    
    def __init__(self):
        self.min_interval_days = 7
        self.max_interval_days = 90
        self.default_interval_days = 21
        
        # Priority thresholds
        self.priority_thresholds = {
            ReassessmentPriority.LOW: 0.3,
            ReassessmentPriority.MEDIUM: 0.5,
            ReassessmentPriority.HIGH: 0.7,
            ReassessmentPriority.CRITICAL: 0.9
        }
    
    def calculate_adaptive_interval(self, user_id: int, plan: PersonalLearningPlan) -> int:
        """
        Calculate adaptive interval for diagnostic reassessment
        
        Args:
            user_id: User ID
            plan: Personal learning plan
            
        Returns:
            Recommended interval in days
        """
        try:
            # Base factors
            base_interval = self.default_interval_days
            
            # Factor 1: Progress towards target
            progress_factor = self._calculate_progress_factor(plan)
            
            # Factor 2: Study activity
            activity_factor = self._calculate_activity_factor(user_id, plan)
            
            # Factor 3: Weak domains urgency
            urgency_factor = self._calculate_urgency_factor(plan)
            
            # Factor 4: Exam proximity
            exam_factor = self._calculate_exam_proximity_factor(plan)
            
            # Factor 5: Learning consistency
            consistency_factor = self._calculate_consistency_factor(user_id, plan)
            
            # Calculate adaptive interval
            adaptive_interval = base_interval * progress_factor * activity_factor * urgency_factor * exam_factor * consistency_factor
            
            # Ensure within bounds
            adaptive_interval = max(self.min_interval_days, min(self.max_interval_days, int(adaptive_interval)))
            
            logger.info(f"User {user_id}: Adaptive interval calculated: {adaptive_interval} days "
                       f"(progress: {progress_factor:.2f}, activity: {activity_factor:.2f}, "
                       f"urgency: {urgency_factor:.2f}, exam: {exam_factor:.2f}, consistency: {consistency_factor:.2f})")
            
            return adaptive_interval
            
        except Exception as e:
            logger.error(f"Error calculating adaptive interval for user {user_id}: {str(e)}")
            return self.default_interval_days
    
    def _calculate_progress_factor(self, plan: PersonalLearningPlan) -> float:
        """Calculate interval factor based on progress towards target"""
        if plan.target_ability <= 0:
            return 1.0
        
        progress_ratio = plan.current_ability / plan.target_ability
        
        if progress_ratio >= 1.0:
            # Already at or above target - longer interval
            return 1.5
        elif progress_ratio >= 0.8:
            # Close to target - standard interval
            return 1.0
        elif progress_ratio >= 0.6:
            # Moderate progress - shorter interval
            return 0.8
        else:
            # Low progress - much shorter interval
            return 0.6
    
    def _calculate_activity_factor(self, user_id: int, plan: PersonalLearningPlan) -> float:
        """Calculate interval factor based on study activity"""
        try:
            # Get recent study sessions (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_sessions = StudySession.query.filter(
                StudySession.learning_plan_id == plan.id,
                StudySession.completed_at >= thirty_days_ago,
                StudySession.status == 'completed'
            ).all()
            
            if not recent_sessions:
                return 0.7  # No activity - shorter interval
            
            # Calculate activity score
            total_time = sum(s.actual_duration or 0 for s in recent_sessions)
            session_count = len(recent_sessions)
            
            # Normalize to 0-1 scale
            time_score = min(1.0, total_time / (plan.study_hours_per_week * 60 * 4))  # 4 weeks
            session_score = min(1.0, session_count / 20)  # 20 sessions per month target
            
            activity_score = (time_score + session_score) / 2
            
            # Convert to interval factor
            if activity_score >= 0.8:
                return 1.2  # High activity - longer interval
            elif activity_score >= 0.5:
                return 1.0  # Moderate activity - standard interval
            else:
                return 0.8  # Low activity - shorter interval
                
        except Exception as e:
            logger.error(f"Error calculating activity factor: {str(e)}")
            return 1.0
    
    def _calculate_urgency_factor(self, plan: PersonalLearningPlan) -> float:
        """Calculate interval factor based on weak domains urgency"""
        try:
            weak_domains = plan.get_weak_domains()
            weak_count = len(weak_domains)
            
            if weak_count == 0:
                return 1.3  # No weak domains - longer interval
            elif weak_count <= 2:
                return 1.0  # Few weak domains - standard interval
            elif weak_count <= 5:
                return 0.8  # Several weak domains - shorter interval
            else:
                return 0.6  # Many weak domains - much shorter interval
                
        except Exception as e:
            logger.error(f"Error calculating urgency factor: {str(e)}")
            return 1.0
    
    def _calculate_exam_proximity_factor(self, plan: PersonalLearningPlan) -> float:
        """Calculate interval factor based on exam proximity"""
        if not plan.exam_date:
            return 1.0
        
        days_to_exam = (plan.exam_date - date.today()).days
        
        if days_to_exam <= 30:
            return 0.5  # Very close to exam - much shorter interval
        elif days_to_exam <= 60:
            return 0.7  # Close to exam - shorter interval
        elif days_to_exam <= 120:
            return 0.9  # Moderate time to exam - slightly shorter interval
        else:
            return 1.0  # Far from exam - standard interval
    
    def _calculate_consistency_factor(self, user_id: int, plan: PersonalLearningPlan) -> float:
        """Calculate interval factor based on learning consistency"""
        try:
            # Get study sessions over last 90 days
            ninety_days_ago = datetime.now() - timedelta(days=90)
            sessions = StudySession.query.filter(
                StudySession.learning_plan_id == plan.id,
                StudySession.completed_at >= ninety_days_ago,
                StudySession.status == 'completed'
            ).order_by(StudySession.completed_at).all()
            
            if len(sessions) < 5:
                return 0.8  # Not enough data - shorter interval
            
            # Calculate consistency (regular intervals between sessions)
            intervals = []
            for i in range(1, len(sessions)):
                interval = (sessions[i].completed_at - sessions[i-1].completed_at).days
                intervals.append(interval)
            
            if not intervals:
                return 1.0
            
            # Calculate coefficient of variation (lower = more consistent)
            mean_interval = sum(intervals) / len(intervals)
            variance = sum((x - mean_interval) ** 2 for x in intervals) / len(intervals)
            std_dev = variance ** 0.5
            cv = std_dev / mean_interval if mean_interval > 0 else 1.0
            
            # Convert to factor (lower CV = higher consistency = longer interval)
            if cv <= 0.3:
                return 1.2  # Very consistent - longer interval
            elif cv <= 0.6:
                return 1.0  # Moderately consistent - standard interval
            else:
                return 0.8  # Inconsistent - shorter interval
                
        except Exception as e:
            logger.error(f"Error calculating consistency factor: {str(e)}")
            return 1.0
    
    def get_reassessment_recommendations(self, limit: int = 100) -> List[ReassessmentRecommendation]:
        """
        Get recommendations for diagnostic reassessments
        
        Args:
            limit: Maximum number of recommendations to return
            
        Returns:
            List of reassessment recommendations
        """
        recommendations = []
        
        try:
            # Get all active learning plans
            active_plans = PersonalLearningPlan.query.filter_by(status='active').all()
            
            for plan in active_plans:
                try:
                    recommendation = self._create_recommendation(plan)
                    if recommendation:
                        recommendations.append(recommendation)
                except Exception as e:
                    logger.error(f"Error creating recommendation for plan {plan.id}: {str(e)}")
                    continue
            
            # Sort by priority and date
            recommendations.sort(key=lambda r: (r.priority.value, r.recommended_date))
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error getting reassessment recommendations: {str(e)}")
            return []
    
    def _create_recommendation(self, plan: PersonalLearningPlan) -> Optional[ReassessmentRecommendation]:
        """Create recommendation for a specific plan"""
        try:
            user = User.query.get(plan.user_id)
            if not user:
                return None
            
            # Calculate adaptive interval
            adaptive_interval = self.calculate_adaptive_interval(plan.user_id, plan)
            
            # Get last diagnostic date
            last_diagnostic = DiagnosticSession.query.filter_by(
                user_id=plan.user_id,
                status='completed'
            ).order_by(DiagnosticSession.completed_at.desc()).first()
            
            last_diagnostic_date = last_diagnostic.completed_at.date() if last_diagnostic else None
            
            # Calculate recommended date
            base_date = last_diagnostic_date or plan.start_date or date.today()
            recommended_date = base_date + timedelta(days=adaptive_interval)
            
            # Calculate priority
            priority = self._calculate_priority(plan, adaptive_interval, last_diagnostic_date)
            
            # Calculate confidence
            confidence = self._calculate_confidence(plan, adaptive_interval)
            
            # Get weak domains count
            weak_domains = plan.get_weak_domains()
            weak_domains_count = len(weak_domains)
            
            # Calculate study activity score
            activity_score = self._calculate_activity_score(plan.user_id, plan)
            
            # Create recommendation
            recommendation = ReassessmentRecommendation(
                user_id=plan.user_id,
                plan_id=plan.id,
                priority=priority,
                recommended_date=recommended_date,
                reason=self._generate_reason(plan, priority, adaptive_interval),
                confidence=confidence,
                estimated_days_needed=adaptive_interval,
                current_ability=plan.current_ability,
                target_ability=plan.target_ability,
                weak_domains_count=weak_domains_count,
                last_diagnostic_date=last_diagnostic_date,
                study_activity_score=activity_score
            )
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error creating recommendation for plan {plan.id}: {str(e)}")
            return None
    
    def _calculate_priority(self, plan: PersonalLearningPlan, interval: int, last_diagnostic_date: Optional[date]) -> ReassessmentPriority:
        """Calculate priority for reassessment"""
        # Base priority on interval length
        if interval <= 10:
            return ReassessmentPriority.CRITICAL
        elif interval <= 21:
            return ReassessmentPriority.HIGH
        elif interval <= 35:
            return ReassessmentPriority.MEDIUM
        else:
            return ReassessmentPriority.LOW
    
    def _calculate_confidence(self, plan: PersonalLearningPlan, interval: int) -> float:
        """Calculate confidence in recommendation"""
        # Base confidence on data quality
        confidence = 0.7  # Base confidence
        
        # Adjust based on plan completeness
        if plan.domain_analysis:
            confidence += 0.1
        
        if plan.weak_domains:
            confidence += 0.1
        
        if plan.exam_date:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _calculate_activity_score(self, user_id: int, plan: PersonalLearningPlan) -> float:
        """Calculate study activity score"""
        try:
            # Get recent study sessions
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_sessions = StudySession.query.filter(
                StudySession.learning_plan_id == plan.id,
                StudySession.completed_at >= thirty_days_ago,
                StudySession.status == 'completed'
            ).all()
            
            if not recent_sessions:
                return 0.0
            
            total_time = sum(s.actual_duration or 0 for s in recent_sessions)
            target_time = plan.study_hours_per_week * 60 * 4  # 4 weeks
            
            return min(1.0, total_time / target_time) if target_time > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating activity score: {str(e)}")
            return 0.0
    
    def _generate_reason(self, plan: PersonalLearningPlan, priority: ReassessmentPriority, interval: int) -> str:
        """Generate human-readable reason for recommendation"""
        reasons = []
        
        if priority == ReassessmentPriority.CRITICAL:
            reasons.append("Critical reassessment needed")
        elif priority == ReassessmentPriority.HIGH:
            reasons.append("High priority reassessment")
        
        if plan.current_ability < plan.target_ability * 0.8:
            reasons.append("Below target progress")
        
        weak_domains = plan.get_weak_domains()
        if len(weak_domains) > 3:
            reasons.append(f"{len(weak_domains)} weak domains identified")
        
        if plan.exam_date and (plan.exam_date - date.today()).days <= 60:
            reasons.append("Exam approaching")
        
        if not reasons:
            reasons.append("Regular progress check")
        
        return "; ".join(reasons)
    
    def update_plan_schedule(self, plan_id: int) -> bool:
        """
        Update diagnostic schedule for a specific plan
        
        Args:
            plan_id: Learning plan ID
            
        Returns:
            Success status
        """
        try:
            plan = PersonalLearningPlan.query.get(plan_id)
            if not plan:
                logger.error(f"Plan {plan_id} not found")
                return False
            
            # Calculate new adaptive interval
            adaptive_interval = self.calculate_adaptive_interval(plan.user_id, plan)
            
            # Update next diagnostic date
            plan.set_next_diagnostic_date(adaptive_interval)
            
            logger.info(f"Updated diagnostic schedule for plan {plan_id}: {adaptive_interval} days")
            return True
            
        except Exception as e:
            logger.error(f"Error updating plan schedule {plan_id}: {str(e)}")
            return False
    
    def get_overdue_reassessments(self) -> List[Dict]:
        """
        Get list of overdue diagnostic reassessments
        
        Returns:
            List of overdue reassessments
        """
        overdue = []
        
        try:
            today = date.today()
            
            # Get plans with overdue diagnostic dates
            overdue_plans = PersonalLearningPlan.query.filter(
                PersonalLearningPlan.status == 'active',
                PersonalLearningPlan.next_diagnostic_date <= today,
                PersonalLearningPlan.diagnostic_reminder_sent == False
            ).all()
            
            for plan in overdue_plans:
                overdue_days = (today - plan.next_diagnostic_date).days
                
                overdue.append({
                    'user_id': plan.user_id,
                    'plan_id': plan.id,
                    'overdue_days': overdue_days,
                    'current_ability': plan.current_ability,
                    'target_ability': plan.target_ability,
                    'weak_domains': plan.get_weak_domains(),
                    'next_diagnostic_date': plan.next_diagnostic_date.isoformat()
                })
            
            return overdue
            
        except Exception as e:
            logger.error(f"Error getting overdue reassessments: {str(e)}")
            return []
    
    def mark_reminder_sent(self, plan_id: int) -> bool:
        """
        Mark diagnostic reminder as sent
        
        Args:
            plan_id: Learning plan ID
            
        Returns:
            Success status
        """
        try:
            plan = PersonalLearningPlan.query.get(plan_id)
            if not plan:
                return False
            
            plan.diagnostic_reminder_sent = True
            db.session.commit()
            
            logger.info(f"Marked reminder sent for plan {plan_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error marking reminder sent for plan {plan_id}: {str(e)}")
            return False


# Global scheduler instance
scheduler = AdaptiveDiagnosticScheduler()


def get_scheduler() -> AdaptiveDiagnosticScheduler:
    """Get global scheduler instance"""
    return scheduler


def run_daily_scheduler_check():
    """
    Daily background task to check for diagnostic reassessments
    
    This function should be called by a cron job or scheduler
    """
    try:
        logger.info("Starting daily diagnostic scheduler check")
        
        # Get overdue reassessments
        overdue = scheduler.get_overdue_reassessments()
        
        if overdue:
            logger.info(f"Found {len(overdue)} overdue diagnostic reassessments")
            
            # Send email/push notifications
            for item in overdue:
                logger.info(f"User {item['user_id']}: {item['overdue_days']} days overdue")
                send_diagnostic_reminder(item)
        
        # Get recommendations for upcoming reassessments
        recommendations = scheduler.get_reassessment_recommendations(limit=50)
        
        if recommendations:
            logger.info(f"Generated {len(recommendations)} reassessment recommendations")
            
            # Update plans with new schedules
            for rec in recommendations:
                if rec.priority in [ReassessmentPriority.HIGH, ReassessmentPriority.CRITICAL]:
                    scheduler.update_plan_schedule(rec.plan_id)
                    logger.info(f"Updated schedule for plan {rec.plan_id} with priority {rec.priority.value}")
        
        logger.info("Daily diagnostic scheduler check completed")
        
    except Exception as e:
        logger.error(f"Error in daily scheduler check: {str(e)}")


def send_diagnostic_reminder(overdue_item: Dict):
    """
    Send diagnostic reminder to user
    
    Args:
        overdue_item: Overdue reassessment item
    """
    try:
        from flask import current_app
        from models import User
        
        user_id = overdue_item['user_id']
        overdue_days = overdue_item['overdue_days']
        
        # Get user
        user = User.query.get(user_id)
        if not user or not user.email:
            logger.warning(f"User {user_id} not found or has no email")
            return
        
        # Send email notification
        try:
            from utils.email_service import send_email_confirmation
            
            # Create reminder email content
            subject = f"Напоминание о диагностическом тестировании - {overdue_days} дней просрочки"
            message = f"""
            Добрый день, {user.first_name}!
            
            Это напоминание о том, что ваше диагностическое тестирование просрочено на {overdue_days} дней.
            
            Пожалуйста, пройдите диагностику для продолжения обучения:
            https://bigmentor.nl/dashboard/diagnostic
            
            С уважением,
            Команда Mentora
            """
            
            # Send email using existing email service
            email_sent = send_email_confirmation(user, message)
            
            if email_sent:
                logger.info(f"Diagnostic reminder email sent to user {user_id}")
            else:
                logger.warning(f"Failed to send diagnostic reminder email to user {user_id}")
                
        except Exception as email_error:
            logger.error(f"Error sending diagnostic reminder email: {str(email_error)}")
        
        # Mark reminder as sent
        scheduler.mark_reminder_sent(overdue_item['plan_id'])
        logger.info(f"Diagnostic reminder sent to user {user_id} for plan {overdue_item['plan_id']}")
        
    except Exception as e:
        logger.error(f"Error sending diagnostic reminder: {str(e)}")


# Export diagnostic_scheduler for backward compatibility
diagnostic_scheduler = scheduler 