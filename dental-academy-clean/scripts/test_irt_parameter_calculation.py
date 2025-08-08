#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for IRT parameter calculation in Question model
Tests the new calculate_default_irt_params() method
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models import Question, IRTParameters, TestAttempt, DiagnosticResponse, User
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_irt_parameter_calculation():
    """Test the new IRT parameter calculation functionality"""
    
    with app.app_context():
        try:
            logger.info("=== Testing IRT Parameter Calculation ===")
            
            # Get a sample question
            question = Question.query.first()
            if not question:
                logger.error("No questions found in database")
                return
            
            logger.info(f"Testing with question ID: {question.id}")
            logger.info(f"Question domain: {question.domain}")
            logger.info(f"Question type: {question.question_type}")
            
            # Test 1: Check if IRT parameters exist
            logger.info("\n--- Test 1: Check existing IRT parameters ---")
            if question.irt_parameters:
                logger.info(f"Existing IRT parameters: difficulty={question.irt_parameters.difficulty}, "
                           f"discrimination={question.irt_parameters.discrimination}, "
                           f"guessing={question.irt_parameters.guessing}")
            else:
                logger.info("No existing IRT parameters found")
            
            # Test 2: Test property access with calculation
            logger.info("\n--- Test 2: Test property access with calculation ---")
            difficulty = question.irt_difficulty
            discrimination = question.irt_discrimination
            guessing = question.irt_guessing
            
            logger.info(f"Calculated difficulty: {difficulty}")
            logger.info(f"Calculated discrimination: {discrimination}")
            logger.info(f"Calculated guessing: {guessing}")
            
            # Test 3: Test direct calculation method
            logger.info("\n--- Test 3: Test direct calculation method ---")
            calculated_params = question.calculate_default_irt_params()
            
            if calculated_params:
                logger.info(f"Calculated parameters: {calculated_params}")
                logger.info(f"Source: {calculated_params.get('source')}")
                logger.info(f"Sample size: {calculated_params.get('sample_size')}")
            else:
                logger.warning("No parameters could be calculated")
            
            # Test 4: Test response statistics
            logger.info("\n--- Test 4: Test response statistics ---")
            response_stats = question._get_response_statistics()
            logger.info(f"Response statistics: {response_stats}")
            
            # Test 5: Test domain averages
            logger.info("\n--- Test 5: Test domain averages ---")
            domain_params = question._get_domain_average_params()
            logger.info(f"Domain average parameters: {domain_params}")
            
            # Test 6: Test with questions from different domains
            logger.info("\n--- Test 6: Test with different domains ---")
            domains = db.session.query(Question.domain).distinct().limit(5).all()
            
            for (domain,) in domains:
                domain_question = Question.query.filter_by(domain=domain).first()
                if domain_question:
                    params = domain_question.calculate_default_irt_params()
                    logger.info(f"Domain {domain}: {params}")
            
            logger.info("\n=== Test completed successfully ===")
            
        except Exception as e:
            logger.error(f"Error during testing: {str(e)}", exc_info=True)

def test_irt_parameter_validation():
    """Test IRT parameter validation"""
    
    with app.app_context():
        try:
            logger.info("\n=== Testing IRT Parameter Validation ===")
            
            # Test with a question that has IRT parameters
            question_with_params = Question.query.join(IRTParameters).first()
            
            if question_with_params:
                logger.info(f"Testing validation with question ID: {question_with_params.id}")
                
                try:
                    question_with_params.validate_irt_parameters()
                    logger.info("✅ IRT parameters validation passed")
                except ValueError as e:
                    logger.error(f"❌ IRT parameters validation failed: {e}")
            
            # Test with a question without IRT parameters
            question_without_params = Question.query.outerjoin(IRTParameters).filter(
                IRTParameters.id.is_(None)
            ).first()
            
            if question_without_params:
                logger.info(f"Testing validation with question ID: {question_without_params.id} (no IRT params)")
                
                try:
                    question_without_params.validate_irt_parameters()
                    logger.error("❌ Validation should have failed for question without IRT parameters")
                except ValueError as e:
                    logger.info(f"✅ Correctly caught validation error: {e}")
            
            logger.info("=== Validation test completed ===")
            
        except Exception as e:
            logger.error(f"Error during validation testing: {str(e)}", exc_info=True)

def test_performance():
    """Test performance of IRT parameter calculation"""
    
    with app.app_context():
        try:
            logger.info("\n=== Testing Performance ===")
            
            import time
            
            # Test calculation time for multiple questions
            questions = Question.query.limit(10).all()
            
            total_time = 0
            calculated_count = 0
            
            for question in questions:
                start_time = time.time()
                params = question.calculate_default_irt_params()
                end_time = time.time()
                
                calculation_time = end_time - start_time
                total_time += calculation_time
                
                if params:
                    calculated_count += 1
                
                logger.info(f"Question {question.id}: {calculation_time:.4f}s")
            
            avg_time = total_time / len(questions) if questions else 0
            logger.info(f"\nPerformance summary:")
            logger.info(f"Total questions tested: {len(questions)}")
            logger.info(f"Questions with calculated parameters: {calculated_count}")
            logger.info(f"Average calculation time: {avg_time:.4f}s")
            logger.info(f"Total calculation time: {total_time:.4f}s")
            
            logger.info("=== Performance test completed ===")
            
        except Exception as e:
            logger.error(f"Error during performance testing: {str(e)}", exc_info=True)

def main():
    """Main test function"""
    logger.info("Starting IRT parameter calculation tests...")
    
    # Run all tests
    test_irt_parameter_calculation()
    test_irt_parameter_validation()
    test_performance()
    
    logger.info("All tests completed!")

if __name__ == '__main__':
    main() 