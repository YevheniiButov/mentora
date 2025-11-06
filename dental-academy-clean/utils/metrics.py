#!/usr/bin/env python3
"""
Metrics collection for adaptive learning system
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)

@dataclass
class IRTMetric:
    """Single IRT metric record"""
    timestamp: str
    metric_type: str
    value: float
    metadata: Dict
    user_id: Optional[int] = None
    session_id: Optional[int] = None

class AdaptiveLearningMetrics:
    """Metrics collection for adaptive learning system"""
    
    def __init__(self):
        self.metrics: List[IRTMetric] = []
        self.fallback_usage = []
        self.error_counts = {}
        
    def record_diagnostic_session(self, session_id: int, questions_answered: int, 
                                final_ability: float, final_se: float, user_id: Optional[int] = None):
        """Record diagnostic session metrics"""
        self.metrics.append(IRTMetric(
            timestamp=datetime.now(timezone.utc).isoformat(),
            metric_type='diagnostic_session',
            value=questions_answered,
            metadata={
                'final_ability': final_ability,
                'final_se': final_se,
                'efficiency': questions_answered / max(final_se, 0.1)  # Questions per SE unit
            },
            user_id=user_id,
            session_id=session_id
        ))
        
        logger.info(f"Recorded diagnostic session {session_id}: {questions_answered} questions, ability={final_ability:.3f}, SE={final_se:.3f}")
    
    def record_fallback_usage(self, component: str, reason: str, user_id: Optional[int] = None):
        """Record when fallback logic is used"""
        self.fallback_usage.append({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'component': component,
            'reason': reason,
            'user_id': user_id
        })
        
        logger.warning(f"Fallback used in {component}: {reason}")
    
    def record_error(self, error_type: str, error_message: str, user_id: Optional[int] = None):
        """Record system errors"""
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
        
        self.metrics.append(IRTMetric(
            timestamp=datetime.now(timezone.utc).isoformat(),
            metric_type='error',
            value=1.0,
            metadata={
                'error_type': error_type,
                'error_message': error_message
            },
            user_id=user_id
        ))
        
        logger.error(f"Error recorded: {error_type} - {error_message}")
    
    def record_irt_parameter_validation(self, question_id: int, is_valid: bool, 
                                      difficulty: float, discrimination: float, guessing: float):
        """Record IRT parameter validation results"""
        self.metrics.append(IRTMetric(
            timestamp=datetime.now(timezone.utc).isoformat(),
            metric_type='irt_validation',
            value=1.0 if is_valid else 0.0,
            metadata={
                'question_id': question_id,
                'difficulty': difficulty,
                'discrimination': discrimination,
                'guessing': guessing
            }
        ))
    
    def record_ability_estimation(self, user_id: int, theta: float, se: float, 
                                responses_count: int, iterations: int):
        """Record ability estimation metrics"""
        self.metrics.append(IRTMetric(
            timestamp=datetime.now(timezone.utc).isoformat(),
            metric_type='ability_estimation',
            value=theta,
            metadata={
                'se': se,
                'responses_count': responses_count,
                'iterations': iterations,
                'convergence_rate': responses_count / max(iterations, 1)
            },
            user_id=user_id
        ))
    
    def get_system_health_report(self) -> Dict:
        """Generate system health report"""
        total_metrics = len(self.metrics)
        total_fallbacks = len(self.fallback_usage)
        
        # Calculate fallback rate
        fallback_rate = 0.0
        if total_metrics > 0:
            fallback_rate = total_fallbacks / total_metrics
        
        # Calculate error rate
        error_count = sum(1 for m in self.metrics if m.metric_type == 'error')
        error_rate = error_count / total_metrics if total_metrics > 0 else 0.0
        
        # Calculate IRT validation success rate
        irt_validations = [m for m in self.metrics if m.metric_type == 'irt_validation']
        irt_success_rate = 0.0
        if irt_validations:
            irt_success_rate = sum(m.value for m in irt_validations) / len(irt_validations)
        
        return {
            'total_metrics': total_metrics,
            'fallback_count': total_fallbacks,
            'fallback_rate': fallback_rate,
            'error_count': error_count,
            'error_rate': error_rate,
            'irt_validation_success_rate': irt_success_rate,
            'last_24h_fallbacks': len([f for f in self.fallback_usage 
                                     if (datetime.now(timezone.utc) - datetime.fromisoformat(f['timestamp'])).days < 1]),
            'error_breakdown': self.error_counts
        }
    
    def get_performance_metrics(self, hours: int = 24) -> Dict:
        """Get performance metrics for the last N hours"""
        cutoff_time = datetime.now(timezone.utc).timestamp() - (hours * 3600)
        
        recent_metrics = [
            m for m in self.metrics 
            if datetime.fromisoformat(m.timestamp).timestamp() > cutoff_time
        ]
        
        diagnostic_sessions = [m for m in recent_metrics if m.metric_type == 'diagnostic_session']
        ability_estimations = [m for m in recent_metrics if m.metric_type == 'ability_estimation']
        
        avg_questions_per_session = 0.0
        avg_ability = 0.0
        avg_se = 0.0
        
        if diagnostic_sessions:
            avg_questions_per_session = sum(m.value for m in diagnostic_sessions) / len(diagnostic_sessions)
        
        if ability_estimations:
            avg_ability = sum(m.value for m in ability_estimations) / len(ability_estimations)
            avg_se = sum(m.metadata.get('se', 0) for m in ability_estimations) / len(ability_estimations)
        
        return {
            'period_hours': hours,
            'total_sessions': len(diagnostic_sessions),
            'avg_questions_per_session': avg_questions_per_session,
            'avg_ability': avg_ability,
            'avg_standard_error': avg_se,
            'total_ability_estimations': len(ability_estimations)
        }
    
    def export_metrics(self, filepath: str):
        """Export metrics to JSON file"""
        try:
            export_data = {
                'metrics': [asdict(m) for m in self.metrics],
                'fallback_usage': self.fallback_usage,
                'error_counts': self.error_counts,
                'export_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Metrics exported to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
    
    def clear_old_metrics(self, days: int = 30):
        """Clear metrics older than N days"""
        cutoff_time = datetime.now(timezone.utc).timestamp() - (days * 24 * 3600)
        
        original_count = len(self.metrics)
        self.metrics = [
            m for m in self.metrics 
            if datetime.fromisoformat(m.timestamp).timestamp() > cutoff_time
        ]
        
        cleared_count = original_count - len(self.metrics)
        logger.info(f"Cleared {cleared_count} old metrics (older than {days} days)")

# Global metrics instance
_metrics_instance = None

def get_metrics() -> AdaptiveLearningMetrics:
    """Get global metrics instance"""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = AdaptiveLearningMetrics()
    return _metrics_instance

def record_diagnostic_session(session_id: int, questions_answered: int, 
                            final_ability: float, final_se: float, user_id: Optional[int] = None):
    """Record diagnostic session metrics"""
    get_metrics().record_diagnostic_session(session_id, questions_answered, final_ability, final_se, user_id)

def record_fallback_usage(component: str, reason: str, user_id: Optional[int] = None):
    """Record fallback usage"""
    get_metrics().record_fallback_usage(component, reason, user_id)

def record_error(error_type: str, error_message: str, user_id: Optional[int] = None):
    """Record system error"""
    get_metrics().record_error(error_type, error_message, user_id)

def get_system_health() -> Dict:
    """Get system health report"""
    return get_metrics().get_system_health_report() 