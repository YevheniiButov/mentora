#!/usr/bin/env python3
"""
Advanced script to fix user data by generating domain_abilities from IRT data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, PersonalLearningPlan, DiagnosticSession, DiagnosticResponse, Question, BIGDomain
import logging
from datetime import datetime, timezone
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_domain_abilities_from_irt(session_id: int) -> dict:
    """Generate domain abilities from IRT responses"""
    session = DiagnosticSession.query.get(session_id)
    if not session:
        return {}
    
    # Get all responses for this session
    responses = session.responses.all()
    if not responses:
        return {}
    
    # Group responses by domain
    domain_responses = {}
    for response in responses:
        if response.question and response.question.domain:
            domain = response.question.domain
            if domain not in domain_responses:
                domain_responses[domain] = []
            domain_responses[domain].append({
                'is_correct': response.is_correct,
                'irt_params': {
                    'difficulty': response.question.irt_parameters.difficulty if response.question.irt_parameters else 0.0,
                    'discrimination': response.question.irt_parameters.discrimination if response.question.irt_parameters else 1.0,
                    'guessing': response.question.irt_parameters.guessing if response.question.irt_parameters else 0.0
                }
            })
    
    # Calculate ability for each domain using IRT
    domain_abilities = {}
    for domain, responses in domain_responses.items():
        if len(responses) >= 1:  # Need at least 1 response
            try:
                from utils.irt_engine import IRTEngine
                irt = IRTEngine()
                theta, se = irt.estimate_ability(responses)
                domain_abilities[domain] = theta
                logger.info(f"Domain {domain}: theta={theta:.3f}, SE={se:.3f} ({len(responses)} responses)")
            except Exception as e:
                logger.warning(f"Failed to calculate ability for domain {domain}: {e}")
                # Fallback: use simple proportion
                correct = sum(1 for r in responses if r['is_correct'])
                proportion = correct / len(responses)
                domain_abilities[domain] = 2 * (proportion - 0.5)  # Convert to theta scale
                logger.info(f"Domain {domain}: fallback theta={domain_abilities[domain]:.3f}")
    
    return domain_abilities

def fix_user_data_advanced(user_id: int = 6):
    """Advanced fix for user data"""
    with app.app_context():
        logger.info(f"🔧 Advanced fix for user {user_id}...")
        
        # Get the latest completed diagnostic session with most responses
        latest_session = DiagnosticSession.query.filter_by(
            user_id=user_id,
            status='completed'
        ).order_by(DiagnosticSession.questions_answered.desc()).first()
        
        if not latest_session:
            logger.error("No completed diagnostic session found")
            return
        
        logger.info(f"Using session {latest_session.id} with {latest_session.questions_answered} questions")
        
        # Generate domain abilities from IRT data
        domain_abilities = generate_domain_abilities_from_irt(latest_session.id)
        
        if not domain_abilities:
            logger.error("Could not generate domain abilities")
            return
        
        logger.info(f"Generated abilities for {len(domain_abilities)} domains")
        
        # Get or create learning plan
        learning_plan = PersonalLearningPlan.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if not learning_plan:
            logger.info("Creating new learning plan...")
            learning_plan = PersonalLearningPlan(
                user_id=user_id,
                status='active'
            )
            db.session.add(learning_plan)
        
        # Create proper domain analysis format
        domain_analysis = {}
        for domain, ability in domain_abilities.items():
            domain_analysis[domain] = {
                'current_ability': ability,
                'target_ability': min(ability + 1.0, 3.0),  # Target 1 point higher
                'questions_answered': 0,
                'correct_answers': 0
            }
        
        # Save to learning plan
        learning_plan.set_domain_analysis(domain_analysis)
        
        # Also update session data with domain abilities
        session_data = latest_session.get_session_data()
        session_data['domain_abilities'] = domain_abilities
        latest_session.session_data = json.dumps(session_data)
        
        db.session.commit()
        
        logger.info(f"✅ Fixed domain analysis with {len(domain_analysis)} domains")
        
        # Test if daily plan generation works now
        try:
            from utils.daily_learning_algorithm import DailyLearningAlgorithm
            algorithm = DailyLearningAlgorithm()
            daily_plan = algorithm.generate_daily_plan(user_id)
            logger.info("✅ Daily plan generation successful after fix!")
        except Exception as e:
            logger.error(f"❌ Daily plan generation still fails: {e}")

def clean_duplicate_plans(user_id: int = 6):
    """Clean up duplicate learning plans"""
    with app.app_context():
        logger.info(f"🧹 Cleaning duplicate plans for user {user_id}...")
        
        # Get all active plans
        active_plans = PersonalLearningPlan.query.filter_by(
            user_id=user_id,
            status='active'
        ).all()
        
        if len(active_plans) <= 1:
            logger.info("No duplicate plans to clean")
            return
        
        # Keep the most recent plan, delete others
        plans_to_delete = active_plans[1:]  # Keep first, delete rest
        
        for plan in plans_to_delete:
            logger.info(f"Deleting plan {plan.id}")
            db.session.delete(plan)
        
        db.session.commit()
        logger.info(f"✅ Deleted {len(plans_to_delete)} duplicate plans")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "clean":
            clean_duplicate_plans()
        else:
            fix_user_data_advanced(int(sys.argv[1]))
    else:
        fix_user_data_advanced() 