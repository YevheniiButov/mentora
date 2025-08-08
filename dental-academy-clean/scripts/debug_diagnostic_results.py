#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script for IRT diagnostic results showing 0 for all domains
Analyzes the issue and provides detailed diagnostics
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models import Question, IRTParameters, TestAttempt, DiagnosticResponse, DiagnosticSession, User
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_user_diagnostic_session(user_id):
    """Analyze diagnostic session for specific user"""
    
    with app.app_context():
        try:
            logger.info(f"=== Analyzing Diagnostic Session for User {user_id} ===")
            
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
                
                # Check IRT parameters for questions in this domain
                irt_params_found = 0
                irt_params_missing = 0
                
                for response in domain_resp_list:
                    question = response.question
                    if question.irt_parameters:
                        irt_params_found += 1
                    else:
                        irt_params_missing += 1
                
                logger.info(f"  IRT parameters: {irt_params_found} found, {irt_params_missing} missing")
            
            # Test IRT engine calculation
            from utils.irt_engine import IRTEngine
            irt_engine = IRTEngine(latest_session)
            
            # Get domain abilities
            domain_abilities = irt_engine.get_domain_abilities()
            logger.info(f"\nDomain abilities from IRT engine:")
            for domain_code, ability in domain_abilities.items():
                logger.info(f"  {domain_code}: {ability}")
            
            # Get detailed statistics
            domain_stats = irt_engine.get_domain_detailed_statistics()
            logger.info(f"\nDetailed domain statistics:")
            for domain_code, stats in domain_stats.items():
                if stats['has_data']:
                    logger.info(f"  {domain_code}: {stats['accuracy_percentage']}% accuracy")
                else:
                    logger.info(f"  {domain_code}: No data")
            
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
                'domain_stats': domain_stats,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error analyzing diagnostic session: {e}", exc_info=True)
            return None

def check_irt_parameters():
    """Check IRT parameters for questions"""
    
    with app.app_context():
        try:
            logger.info("\n=== Checking IRT Parameters ===")
            
            # Count questions with and without IRT parameters
            total_questions = Question.query.count()
            questions_with_irt = Question.query.join(IRTParameters).count()
            questions_without_irt = total_questions - questions_with_irt
            
            logger.info(f"Total questions: {total_questions}")
            logger.info(f"Questions with IRT parameters: {questions_with_irt}")
            logger.info(f"Questions without IRT parameters: {questions_without_irt}")
            
            # Check by domain
            from models import BIGDomain
            domains = BIGDomain.query.all()
            
            for domain in domains:
                domain_questions = Question.query.filter_by(big_domain_id=domain.id).count()
                domain_questions_with_irt = Question.query.join(IRTParameters).filter_by(big_domain_id=domain.id).count()
                
                logger.info(f"Domain {domain.code} ({domain.name}): {domain_questions_with_irt}/{domain_questions} questions have IRT parameters")
            
            # Check sample IRT parameters
            sample_irt = IRTParameters.query.first()
            if sample_irt:
                logger.info(f"Sample IRT parameters:")
                logger.info(f"  Difficulty: {sample_irt.difficulty}")
                logger.info(f"  Discrimination: {sample_irt.discrimination}")
                logger.info(f"  Guessing: {sample_irt.guessing}")
            else:
                logger.warning("No IRT parameters found in database")
            
        except Exception as e:
            logger.error(f"Error checking IRT parameters: {e}", exc_info=True)

def test_irt_calculation():
    """Test IRT calculation with sample data"""
    
    with app.app_context():
        try:
            logger.info("\n=== Testing IRT Calculation ===")
            
            from utils.irt_engine import IRTEngine
            
            # Create a mock session for testing
            mock_session = type('MockSession', (), {
                'id': 999,
                'questions_answered': 10,
                'correct_answers': 7,
                'current_ability': 0.5,
                'ability_se': 0.3,
                'responses': type('MockResponses', (), {
                    'all': lambda: []
                })()
            })()
            
            irt_engine = IRTEngine(mock_session)
            
            # Test domain abilities calculation
            domain_abilities = irt_engine.get_domain_abilities()
            logger.info(f"Mock domain abilities: {domain_abilities}")
            
            # Test detailed statistics
            domain_stats = irt_engine.get_domain_detailed_statistics()
            logger.info(f"Mock domain stats keys: {list(domain_stats.keys())}")
            
            # Test ability conversion
            readiness = irt_engine.convert_irt_ability_to_readiness_percentage(0.5)
            performance = irt_engine.convert_irt_ability_to_performance_percentage(0.5)
            
            logger.info(f"Ability 0.5 -> Readiness: {readiness:.1f}%, Performance: {performance:.1f}%")
            
        except Exception as e:
            logger.error(f"Error testing IRT calculation: {e}", exc_info=True)

def check_database_consistency():
    """Check database consistency for diagnostic data"""
    
    with app.app_context():
        try:
            logger.info("\n=== Checking Database Consistency ===")
            
            # Check diagnostic sessions
            total_sessions = DiagnosticSession.query.count()
            completed_sessions = DiagnosticSession.query.filter_by(status='completed').count()
            active_sessions = DiagnosticSession.query.filter_by(status='active').count()
            
            logger.info(f"Total diagnostic sessions: {total_sessions}")
            logger.info(f"Completed sessions: {completed_sessions}")
            logger.info(f"Active sessions: {active_sessions}")
            
            # Check diagnostic responses
            total_responses = DiagnosticResponse.query.count()
            correct_responses = DiagnosticResponse.query.filter_by(is_correct=True).count()
            incorrect_responses = DiagnosticResponse.query.filter_by(is_correct=False).count()
            
            logger.info(f"Total diagnostic responses: {total_responses}")
            logger.info(f"Correct responses: {correct_responses}")
            logger.info(f"Incorrect responses: {incorrect_responses}")
            
            # Check for orphaned responses
            orphaned_responses = DiagnosticResponse.query.outerjoin(DiagnosticSession).filter(
                DiagnosticSession.id.is_(None)
            ).count()
            
            logger.info(f"Orphaned responses: {orphaned_responses}")
            
            # Check for responses without questions
            responses_without_questions = DiagnosticResponse.query.outerjoin(Question).filter(
                Question.id.is_(None)
            ).count()
            
            logger.info(f"Responses without questions: {responses_without_questions}")
            
        except Exception as e:
            logger.error(f"Error checking database consistency: {e}", exc_info=True)

def main():
    """Main diagnostic function"""
    logger.info("Starting IRT diagnostic results analysis...")
    
    # Check database consistency
    check_database_consistency()
    
    # Check IRT parameters
    check_irt_parameters()
    
    # Test IRT calculation
    test_irt_calculation()
    
    # Analyze specific user (you can change the user_id)
    user_id = 1  # Change this to the user ID you want to analyze
    analyze_user_diagnostic_session(user_id)
    
    logger.info("Analysis completed!")

if __name__ == '__main__':
    main() 