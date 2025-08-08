#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for diagnostic results fix
Tests the fix for None values in domain abilities
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

def test_diagnostic_fix(user_id=2):
    """Test the fix for diagnostic results"""
    
    with app.app_context():
        try:
            logger.info(f"=== Testing Diagnostic Fix for User {user_id} ===")
            
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
            
            # Test IRT engine calculation
            from utils.irt_engine import IRTEngine
            irt_engine = IRTEngine(latest_session)
            
            # Get domain abilities
            domain_abilities = irt_engine.get_domain_abilities()
            logger.info(f"\nDomain abilities from IRT engine (FIXED):")
            none_count = 0
            zero_count = 0
            for domain_code, ability in domain_abilities.items():
                if ability is None:
                    logger.info(f"  {domain_code}: None (PROBLEM!)")
                    none_count += 1
                elif ability == 0.0:
                    logger.info(f"  {domain_code}: 0.000 (0.0%) - FIXED")
                    zero_count += 1
                else:
                    logger.info(f"  {domain_code}: {ability:.3f} ({ability*100:.1f}%)")
            
            logger.info(f"\nSummary:")
            logger.info(f"  Domains with None: {none_count}")
            logger.info(f"  Domains with 0.0: {zero_count}")
            logger.info(f"  Total domains: {len(domain_abilities)}")
            
            # Test generate_results method
            results = latest_session.generate_results()
            logger.info(f"\nGenerated results (FIXED):")
            logger.info(f"  Final ability: {results.get('final_ability')}")
            logger.info(f"  Readiness percentage: {results.get('readiness_percentage')}%")
            logger.info(f"  Performance percentage: {results.get('performance_percentage')}%")
            
            domain_abilities_result = results.get('domain_abilities', {})
            logger.info(f"  Domain abilities in results (FIXED):")
            none_count_result = 0
            zero_count_result = 0
            for domain_code, ability in domain_abilities_result.items():
                if ability is None:
                    logger.info(f"    {domain_code}: None (PROBLEM!)")
                    none_count_result += 1
                elif ability == 0.0:
                    logger.info(f"    {domain_code}: 0.000 (0.0%) - FIXED")
                    zero_count_result += 1
                else:
                    logger.info(f"    {domain_code}: {ability:.3f} ({ability*100:.1f}%)")
            
            logger.info(f"\nResults Summary:")
            logger.info(f"  Domains with None: {none_count_result}")
            logger.info(f"  Domains with 0.0: {zero_count_result}")
            logger.info(f"  Total domains: {len(domain_abilities_result)}")
            
            # Check if fix is successful
            if none_count == 0 and none_count_result == 0:
                logger.info("✅ FIX SUCCESSFUL: No None values found!")
            else:
                logger.error("❌ FIX FAILED: Still found None values!")
            
            return {
                'domain_abilities': domain_abilities,
                'results': results,
                'none_count': none_count,
                'zero_count': zero_count,
                'none_count_result': none_count_result,
                'zero_count_result': zero_count_result
            }
            
        except Exception as e:
            logger.error(f"Error testing diagnostic fix: {e}", exc_info=True)
            return None

def test_multiple_users():
    """Test the fix for multiple users"""
    
    with app.app_context():
        try:
            logger.info("\n=== Testing Multiple Users ===")
            
            # Get all users with completed diagnostic sessions
            completed_sessions = DiagnosticSession.query.filter_by(status='completed').all()
            user_ids = list(set([session.user_id for session in completed_sessions]))
            
            logger.info(f"Found {len(user_ids)} users with completed diagnostic sessions")
            
            # Test first 5 users
            for i, user_id in enumerate(user_ids[:5]):
                logger.info(f"\n--- Testing User {i+1}/{min(5, len(user_ids))} ---")
                test_diagnostic_fix(user_id)
            
        except Exception as e:
            logger.error(f"Error testing multiple users: {e}", exc_info=True)

def main():
    """Main test function"""
    logger.info("Testing diagnostic results fix...")
    
    # Test the specific user with 130 questions
    test_diagnostic_fix(2)
    
    # Test multiple users
    test_multiple_users()
    
    logger.info("Test completed!")

if __name__ == '__main__':
    main() 