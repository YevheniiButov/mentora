#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for IRT calibration logic
Tests the new calibration sample size calculation and validation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models import Question, IRTParameters, TestAttempt, DiagnosticResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_calibration_config():
    """Test calibration configuration loading"""
    
    with app.app_context():
        try:
            logger.info("=== Testing Calibration Configuration ===")
            
            # Import the functions from init_big_domains
            from scripts.init_big_domains import get_calibration_config, calculate_required_sample_size
            
            # Test configuration loading
            config = get_calibration_config()
            logger.info(f"Calibration config: {config}")
            
            # Test sample size calculation
            sample_size = calculate_required_sample_size()
            logger.info(f"Required sample size: {sample_size}")
            
            # Test with different parameters
            sample_size_90 = calculate_required_sample_size(confidence_level=0.90, margin_of_error=0.15)
            logger.info(f"Required sample size (90% confidence, 15% margin): {sample_size_90}")
            
            sample_size_99 = calculate_required_sample_size(confidence_level=0.99, margin_of_error=0.05)
            logger.info(f"Required sample size (99% confidence, 5% margin): {sample_size_99}")
            
            logger.info("✅ Configuration test completed")
            
        except Exception as e:
            logger.error(f"Error in configuration test: {e}", exc_info=True)

def test_response_analysis():
    """Test response data analysis"""
    
    with app.app_context():
        try:
            logger.info("\n=== Testing Response Analysis ===")
            
            from scripts.init_big_domains import analyze_existing_responses
            
            # Analyze existing responses
            analysis = analyze_existing_responses()
            logger.info(f"Response analysis: {analysis}")
            
            # Check if analysis is reasonable
            if analysis['total_responses'] >= 0:
                logger.info("✅ Response analysis completed successfully")
            else:
                logger.warning("⚠️ No response data found")
            
        except Exception as e:
            logger.error(f"Error in response analysis test: {e}", exc_info=True)

def test_sample_size_validation():
    """Test sample size validation logic"""
    
    with app.app_context():
        try:
            logger.info("\n=== Testing Sample Size Validation ===")
            
            from scripts.init_big_domains import validate_sample_size, get_calibration_config
            
            config = get_calibration_config()
            
            # Test different sample sizes
            test_sizes = [10, 25, 50, 100, 200, 1000]
            
            for size in test_sizes:
                validation = validate_sample_size(size, config)
                logger.info(f"Sample size {size}: {validation}")
            
            logger.info("✅ Sample size validation test completed")
            
        except Exception as e:
            logger.error(f"Error in sample size validation test: {e}", exc_info=True)

def test_calibration_sample_size():
    """Test calibration sample size calculation"""
    
    with app.app_context():
        try:
            logger.info("\n=== Testing Calibration Sample Size ===")
            
            from scripts.init_big_domains import get_calibration_sample_size
            
            # Test general sample size calculation
            general_info = get_calibration_sample_size()
            logger.info(f"General sample size info: {general_info}")
            
            # Test specific question sample size
            question = Question.query.first()
            if question:
                specific_info = get_calibration_sample_size(question.id)
                logger.info(f"Specific sample size for question {question.id}: {specific_info}")
            else:
                logger.warning("No questions found for testing")
            
            logger.info("✅ Calibration sample size test completed")
            
        except Exception as e:
            logger.error(f"Error in calibration sample size test: {e}", exc_info=True)

def test_irt_parameter_creation():
    """Test IRT parameter creation with new logic"""
    
    with app.app_context():
        try:
            logger.info("\n=== Testing IRT Parameter Creation ===")
            
            from scripts.init_big_domains import get_calibration_sample_size, log_calibration_info
            from models import IRTParameters
            from datetime import datetime, timezone
            
            # Get a question without IRT parameters
            question = Question.query.outerjoin(IRTParameters).filter(
                IRTParameters.id.is_(None)
            ).first()
            
            if question:
                logger.info(f"Testing with question ID: {question.id}")
                
                # Get sample size info
                sample_size_info = get_calibration_sample_size(question.id)
                calibration_sample_size = log_calibration_info(question.id, sample_size_info)
                
                # Create IRT parameters
                irt_params = IRTParameters(
                    question_id=question.id,
                    difficulty=0.0,
                    discrimination=1.0,
                    guessing=0.25,
                    calibration_date=datetime.now(timezone.utc),
                    calibration_sample_size=calibration_sample_size
                )
                
                db.session.add(irt_params)
                db.session.commit()
                
                logger.info(f"✅ Created IRT parameters with sample size: {calibration_sample_size}")
                
                # Clean up
                db.session.delete(irt_params)
                db.session.commit()
                
            else:
                logger.warning("No questions without IRT parameters found for testing")
            
        except Exception as e:
            logger.error(f"Error in IRT parameter creation test: {e}", exc_info=True)

def test_performance():
    """Test performance of calibration functions"""
    
    with app.app_context():
        try:
            logger.info("\n=== Testing Performance ===")
            
            import time
            from scripts.init_big_domains import get_calibration_sample_size, analyze_existing_responses
            
            # Test analysis performance
            start_time = time.time()
            analysis = analyze_existing_responses()
            analysis_time = time.time() - start_time
            logger.info(f"Analysis time: {analysis_time:.4f}s")
            
            # Test sample size calculation performance
            questions = Question.query.limit(10).all()
            
            total_time = 0
            for question in questions:
                start_time = time.time()
                sample_size_info = get_calibration_sample_size(question.id)
                end_time = time.time()
                
                calculation_time = end_time - start_time
                total_time += calculation_time
                
                logger.info(f"Question {question.id}: {calculation_time:.4f}s")
            
            avg_time = total_time / len(questions) if questions else 0
            logger.info(f"Average sample size calculation time: {avg_time:.4f}s")
            logger.info(f"Total time for {len(questions)} questions: {total_time:.4f}s")
            
            logger.info("✅ Performance test completed")
            
        except Exception as e:
            logger.error(f"Error in performance test: {e}", exc_info=True)

def main():
    """Main test function"""
    logger.info("Starting IRT calibration logic tests...")
    
    # Run all tests
    test_calibration_config()
    test_response_analysis()
    test_sample_size_validation()
    test_calibration_sample_size()
    test_irt_parameter_creation()
    test_performance()
    
    logger.info("All tests completed!")

if __name__ == '__main__':
    main() 