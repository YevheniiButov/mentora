#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find user who completed diagnostic with 130 questions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models import DiagnosticSession, User
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_user_with_130_questions():
    """Find user who completed diagnostic with 130 questions"""
    
    with app.app_context():
        try:
            logger.info("=== Finding User with 130 Questions ===")
            
            # Find sessions with 130 questions
            sessions_130 = DiagnosticSession.query.filter_by(
                questions_answered=130,
                status='completed'
            ).all()
            
            logger.info(f"Found {len(sessions_130)} sessions with 130 questions")
            
            for session in sessions_130:
                user = session.user
                logger.info(f"\nSession {session.id}:")
                logger.info(f"  User: {user.email} ({user.full_name})")
                logger.info(f"  User ID: {user.id}")
                logger.info(f"  Completed: {session.completed_at}")
                logger.info(f"  Questions: {session.questions_answered}")
                logger.info(f"  Correct: {session.correct_answers}")
                logger.info(f"  Accuracy: {session.get_accuracy():.2%}")
                logger.info(f"  Current ability: {session.current_ability}")
                logger.info(f"  Ability SE: {session.ability_se}")
                
                # Analyze this session
                analyze_user_diagnostic_session(user.id)
                
                return user.id
            
            # If no 130-question sessions, find sessions with most questions
            max_questions_session = DiagnosticSession.query.filter_by(
                status='completed'
            ).order_by(DiagnosticSession.questions_answered.desc()).first()
            
            if max_questions_session:
                logger.info(f"\nNo 130-question sessions found. Max questions: {max_questions_session.questions_answered}")
                logger.info(f"Session {max_questions_session.id} by user {max_questions_session.user_id}")
                
                user = max_questions_session.user
                logger.info(f"User: {user.email} ({user.full_name})")
                logger.info(f"User ID: {user.id}")
                
                # Analyze this session
                analyze_user_diagnostic_session(user.id)
                
                return user.id
            
            logger.warning("No completed diagnostic sessions found")
            return None
            
        except Exception as e:
            logger.error(f"Error finding user: {e}", exc_info=True)
            return None

def analyze_user_diagnostic_session(user_id):
    """Analyze diagnostic session for specific user"""
    
    with app.app_context():
        try:
            logger.info(f"\n=== Analyzing Diagnostic Session for User {user_id} ===")
            
            # Get user's latest diagnostic session
            user = User.query.get(user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return
            
            logger.info(f"User: {user.email} ({user.full_name})")
            
            # Get latest completed diagnostic session
            latest_session = DiagnosticSession.query.filter_by(
                user_id=user_id,
                status='completed'
            ).order_by(DiagnosticSession.completed_at.desc()).first()
            
            if not latest_session:
                logger.error(f"No completed diagnostic session found for user {user_id}")
                return
            
            logger.info(f"Latest session: {latest_session.id} (completed: {latest_session.completed_at})")
            logger.info(f"Questions answered: {latest_session.questions_answered}")
            logger.info(f"Correct answers: {latest_session.correct_answers}")
            logger.info(f"Accuracy: {latest_session.get_accuracy():.2%}")
            logger.info(f"Current ability: {latest_session.current_ability}")
            logger.info(f"Ability SE: {latest_session.ability_se}")
            
            # Get all responses for this session
            responses = latest_session.responses.all()
            logger.info(f"Total responses: {len(responses)}")
            
            if not responses:
                logger.error("No responses found in session")
                return
            
            # Analyze responses by domain
            domain_responses = {}
            for response in responses:
                question = response.question
                if hasattr(question, 'big_domain') and question.big_domain:
                    domain_code = question.big_domain.code
                    if domain_code not in domain_responses:
                        domain_responses[domain_code] = []
                    domain_responses[domain_code].append(response)
            
            logger.info(f"Domains with responses: {list(domain_responses.keys())}")
            
            # Analyze each domain
            for domain_code, domain_resp_list in domain_responses.items():
                correct_count = sum(1 for resp in domain_resp_list if resp.is_correct)
                total_count = len(domain_resp_list)
                accuracy = correct_count / total_count if total_count > 0 else 0
                
                logger.info(f"\nDomain {domain_code}:")
                logger.info(f"  Questions: {total_count}")
                logger.info(f"  Correct: {correct_count}")
                logger.info(f"  Accuracy: {accuracy:.2%}")
            
            # Test IRT engine calculation
            from utils.irt_engine import IRTEngine
            irt_engine = IRTEngine(latest_session)
            
            # Get domain abilities
            domain_abilities = irt_engine.get_domain_abilities()
            logger.info(f"\nDomain abilities from IRT engine:")
            for domain_code, ability in domain_abilities.items():
                if ability is not None:
                    logger.info(f"  {domain_code}: {ability:.3f} ({ability*100:.1f}%)")
                else:
                    logger.info(f"  {domain_code}: None")
            
            # Test generate_results method
            results = latest_session.generate_results()
            logger.info(f"\nGenerated results:")
            logger.info(f"  Final ability: {results.get('final_ability')}")
            logger.info(f"  Readiness percentage: {results.get('readiness_percentage')}%")
            logger.info(f"  Performance percentage: {results.get('performance_percentage')}%")
            
            domain_abilities_result = results.get('domain_abilities', {})
            logger.info(f"  Domain abilities in results:")
            for domain_code, ability in domain_abilities_result.items():
                if ability is not None:
                    logger.info(f"    {domain_code}: {ability:.3f} ({ability*100:.1f}%)")
                else:
                    logger.info(f"    {domain_code}: None")
            
            return {
                'session': latest_session,
                'responses': responses,
                'domain_responses': domain_responses,
                'domain_abilities': domain_abilities,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error analyzing diagnostic session: {e}", exc_info=True)
            return None

def main():
    """Main function"""
    logger.info("Finding user with 130 questions...")
    
    user_id = find_user_with_130_questions()
    
    if user_id:
        logger.info(f"Found user ID: {user_id}")
        logger.info("Run the debug script with this user ID to analyze the issue")
    else:
        logger.info("No user with 130 questions found")

if __name__ == '__main__':
    main() 