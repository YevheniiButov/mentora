#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to generate IRT parameters for existing questions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app
from extensions import db
from models import Question, IRTParameters
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_irt_parameters_for_existing_questions():
    """
    Generate IRT parameters for all existing questions that don't have them
    """
    app_instance = app.app
    
    with app_instance.app_context():
        try:
            # Get all questions without IRT parameters
            questions_without_irt = Question.query.filter(
                ~Question.id.in_(
                    db.session.query(IRTParameters.question_id)
                )
            ).all()
            
            logger.info(f"Found {len(questions_without_irt)} questions without IRT parameters")
            
            generated_count = 0
            error_count = 0
            
            for question in questions_without_irt:
                try:
                    # Auto-generate IRT parameters
                    irt_params = question.auto_generate_irt_parameters()
                    
                    if irt_params:
                        generated_count += 1
                        logger.info(f"Generated IRT parameters for question {question.id}: "
                                  f"a={irt_params.discrimination:.3f}, "
                                  f"b={irt_params.difficulty:.3f}, "
                                  f"c={irt_params.guessing:.3f}")
                    else:
                        error_count += 1
                        logger.error(f"Failed to generate IRT parameters for question {question.id}")
                        
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error generating IRT parameters for question {question.id}: {str(e)}")
                    continue
            
            logger.info(f"IRT parameter generation completed:")
            logger.info(f"  - Successfully generated: {generated_count}")
            logger.info(f"  - Errors: {error_count}")
            logger.info(f"  - Total questions processed: {len(questions_without_irt)}")
            
            return generated_count, error_count
            
        except Exception as e:
            logger.error(f"Error in IRT parameter generation: {str(e)}")
            return 0, 0

def calibrate_irt_parameters_from_responses():
    """
    Calibrate IRT parameters for questions that have enough responses
    """
    app_instance = app.app
    
    with app_instance.app_context():
        try:
            from models import DiagnosticResponse
            
            # Get questions with IRT parameters that have responses with ability_after
            questions_with_responses = db.session.query(
                Question, db.func.count(DiagnosticResponse.id).label('response_count')
            ).join(
                DiagnosticResponse, Question.id == DiagnosticResponse.question_id
            ).join(
                IRTParameters, Question.id == IRTParameters.question_id
            ).filter(
                DiagnosticResponse.ability_after.isnot(None)
            ).group_by(
                Question.id
            ).having(
                db.func.count(DiagnosticResponse.id) >= 5  # Minimum 5 responses for calibration
            ).all()
            
            logger.info(f"Found {len(questions_with_responses)} questions with enough responses for calibration")
            
            calibrated_count = 0
            error_count = 0
            
            for question, response_count in questions_with_responses:
                try:
                    # Get responses for this question
                    responses = DiagnosticResponse.query.filter_by(
                        question_id=question.id
                    ).all()
                    
                    # Prepare response data for calibration
                    response_data = []
                    for response in responses:
                        # Get user ability from session
                        if response.session and response.ability_after is not None:
                            response_data.append({
                                'user_ability': response.ability_after,
                                'is_correct': response.is_correct
                            })
                    
                    if len(response_data) >= 5:
                        # Calibrate parameters
                        success = question.irt_parameters.calibrate_from_responses(response_data)
                        
                        if success:
                            calibrated_count += 1
                            logger.info(f"Calibrated IRT parameters for question {question.id} "
                                      f"using {len(response_data)} responses")
                        else:
                            error_count += 1
                            logger.warning(f"Failed to calibrate IRT parameters for question {question.id}")
                    else:
                        logger.warning(f"Question {question.id} has {len(response_data)} valid responses, "
                                     f"need at least 5 for calibration")
                        
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error calibrating IRT parameters for question {question.id}: {str(e)}")
                    continue
            
            logger.info(f"IRT parameter calibration completed:")
            logger.info(f"  - Successfully calibrated: {calibrated_count}")
            logger.info(f"  - Errors: {error_count}")
            logger.info(f"  - Total questions processed: {len(questions_with_responses)}")
            
            return calibrated_count, error_count
            
        except Exception as e:
            logger.error(f"Error in IRT parameter calibration: {str(e)}")
            return 0, 0

def main():
    """Main function"""
    print("=== IRT Parameter Generation Script ===")
    print()
    
    # Generate IRT parameters for questions without them
    print("1. Generating IRT parameters for questions without them...")
    generated, errors = generate_irt_parameters_for_existing_questions()
    print(f"   Generated: {generated}, Errors: {errors}")
    print()
    
    # Calibrate IRT parameters from responses
    print("2. Calibrating IRT parameters from responses...")
    calibrated, cal_errors = calibrate_irt_parameters_from_responses()
    print(f"   Calibrated: {calibrated}, Errors: {cal_errors}")
    print()
    
    print("=== Script completed ===")

if __name__ == '__main__':
    main() 