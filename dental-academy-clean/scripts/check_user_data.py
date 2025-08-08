#!/usr/bin/env python3
"""
Script to check user data and diagnose domain_analysis issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, PersonalLearningPlan, DiagnosticSession, DiagnosticResponse
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_user_data(user_id: int = 6):
    """Check user data and diagnose issues"""
    with app.app_context():
        logger.info(f"🔍 Checking data for user {user_id}...")
        
        # Get user
        user = User.query.get(user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            return
        
        logger.info(f"User: {user.email} (ID: {user.id})")
        
        # Check learning plans
        learning_plans = PersonalLearningPlan.query.filter_by(user_id=user_id).all()
        logger.info(f"Learning plans: {len(learning_plans)}")
        
        for plan in learning_plans:
            logger.info(f"  Plan ID: {plan.id}, Status: {plan.status}")
            
            # Check domain analysis
            domain_analysis = plan.get_domain_analysis()
            if domain_analysis:
                logger.info(f"  Domain analysis: {len(domain_analysis)} domains")
                for domain, data in domain_analysis.items():
                    if isinstance(data, dict) and 'current_ability' in data:
                        ability = data.get('current_ability')
                        logger.info(f"    {domain}: ability={ability}")
                    else:
                        logger.warning(f"    {domain}: invalid data format")
            else:
                logger.error(f"  Plan {plan.id}: No domain analysis found!")
        
        # Check diagnostic sessions
        diagnostic_sessions = DiagnosticSession.query.filter_by(user_id=user_id).all()
        logger.info(f"Diagnostic sessions: {len(diagnostic_sessions)}")
        
        for session in diagnostic_sessions:
            logger.info(f"  Session ID: {session.id}, Status: {session.status}, Questions: {session.questions_answered}")
            
            if session.status == 'completed':
                logger.info(f"    Final ability: {session.current_ability}, SE: {session.ability_se}")
                
                # Check responses
                responses = session.responses.all()
                logger.info(f"    Responses: {len(responses)}")
                
                if responses:
                    # Check if responses have IRT data
                    responses_with_irt = sum(1 for r in responses if r.question.irt_parameters)
                    logger.info(f"    Responses with IRT: {responses_with_irt}/{len(responses)}")
        
        # Check if user has any completed diagnostic
        completed_sessions = [s for s in diagnostic_sessions if s.status == 'completed']
        if not completed_sessions:
            logger.error(f"User {user_id} has no completed diagnostic sessions!")
            return
        
        # Check if the latest completed session has proper data
        latest_session = max(completed_sessions, key=lambda s: s.completed_at)
        logger.info(f"Latest completed session: {latest_session.id}")
        
        # Check if session has domain abilities
        session_data = latest_session.get_session_data()
        if 'domain_abilities' in session_data:
            domain_abilities = session_data['domain_abilities']
            logger.info(f"Session domain abilities: {len(domain_abilities)} domains")
            for domain, ability in domain_abilities.items():
                logger.info(f"  {domain}: {ability}")
        else:
            logger.error("Session has no domain_abilities data!")
        
        # Check if we can regenerate domain analysis
        logger.info("\n🔧 Attempting to regenerate domain analysis...")
        try:
            from utils.daily_learning_algorithm import DailyLearningAlgorithm
            algorithm = DailyLearningAlgorithm()
            
            # Try to analyze current abilities
            abilities = algorithm._analyze_current_abilities(user_id)
            logger.info(f"Regenerated abilities: {len(abilities)} domains")
            for domain, ability in abilities.items():
                logger.info(f"  {domain}: {ability}")
            
            # Try to generate daily plan
            daily_plan = algorithm.generate_daily_plan(user_id)
            logger.info("Daily plan generation successful!")
            
        except Exception as e:
            logger.error(f"Failed to regenerate: {e}")

def fix_user_data(user_id: int = 6):
    """Attempt to fix user data issues"""
    with app.app_context():
        logger.info(f"🔧 Attempting to fix data for user {user_id}...")
        
        # Get the latest completed diagnostic session
        latest_session = DiagnosticSession.query.filter_by(
            user_id=user_id,
            status='completed'
        ).order_by(DiagnosticSession.completed_at.desc()).first()
        
        if not latest_session:
            logger.error("No completed diagnostic session found")
            return
        
        # Get or create learning plan
        learning_plan = PersonalLearningPlan.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if not learning_plan:
            logger.info("Creating new learning plan...")
            learning_plan = PersonalLearningPlan(
                user_id=user_id,
                status='active',
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(learning_plan)
        
        # Generate domain analysis from session data
        session_data = latest_session.get_session_data()
        if 'domain_abilities' in session_data:
            domain_abilities = session_data['domain_abilities']
            
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
            db.session.commit()
            
            logger.info(f"Fixed domain analysis with {len(domain_analysis)} domains")
        else:
            logger.error("No domain abilities found in session data")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "fix":
        fix_user_data()
    else:
        check_user_data() 