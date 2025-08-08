#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug response format in database
Check how answers are actually stored
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models import DiagnosticSession, DiagnosticResponse, Question, User
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_response_format(user_id=2):
    """Debug how responses are stored in database"""
    
    with app.app_context():
        try:
            logger.info(f"=== Debugging Response Format for User {user_id} ===")
            
            # Get user
            user = User.query.get(user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return
            
            logger.info(f"User: {user.email} ({user.full_name})")
            
            # Get latest session with responses
            latest_session = DiagnosticSession.query.filter_by(
                user_id=user_id,
                status='completed'
            ).order_by(DiagnosticSession.completed_at.desc()).first()
            
            if not latest_session:
                logger.error("No completed sessions found")
                return
            
            logger.info(f"Latest session: {latest_session.id}")
            logger.info(f"Questions answered: {latest_session.questions_answered}")
            logger.info(f"Correct answers: {latest_session.correct_answers}")
            
            # Get first few responses to analyze format
            responses = latest_session.responses.limit(5).all()
            
            logger.info(f"\nAnalyzing {len(responses)} responses:")
            
            for i, response in enumerate(responses):
                logger.info(f"\n--- Response {i+1} ---")
                logger.info(f"Response ID: {response.id}")
                logger.info(f"Question ID: {response.question_id}")
                logger.info(f"Selected answer: '{response.selected_answer}'")
                logger.info(f"Is correct: {response.is_correct}")
                logger.info(f"Response time: {response.response_time}")
                
                # Get question details
                question = response.question
                if question:
                    logger.info(f"Question text: {question.text[:100]}...")
                    logger.info(f"Question options: {question.options}")
                    logger.info(f"Correct answer text: '{question.correct_answer_text}'")
                    logger.info(f"Correct answer index: {question.correct_answer_index}")
                    
                    # Check if options is JSON or list
                    if isinstance(question.options, str):
                        try:
                            options_parsed = json.loads(question.options)
                            logger.info(f"Options parsed: {options_parsed}")
                        except:
                            logger.info(f"Options not valid JSON: {question.options}")
                    else:
                        logger.info(f"Options type: {type(question.options)}")
                        logger.info(f"Options: {question.options}")
                    
                    # Check if selected answer matches any option
                    if question.options:
                        options = question.options if isinstance(question.options, list) else json.loads(question.options)
                        for j, option in enumerate(options):
                            if option == response.selected_answer:
                                logger.info(f"Selected answer matches option {j} (letter {chr(65+j)})")
                                break
                        else:
                            logger.info(f"Selected answer '{response.selected_answer}' does not match any option")
                else:
                    logger.info("Question not found")
            
            # Check all unique selected answers
            logger.info(f"\n=== ALL UNIQUE SELECTED ANSWERS ===")
            
            all_responses = DiagnosticResponse.query.join(DiagnosticSession).filter(
                DiagnosticSession.user_id == user_id,
                DiagnosticSession.status == 'completed'
            ).all()
            
            unique_answers = set()
            for response in all_responses:
                unique_answers.add(response.selected_answer)
            
            logger.info(f"Total responses: {len(all_responses)}")
            logger.info(f"Unique selected answers: {len(unique_answers)}")
            logger.info(f"Unique answers: {sorted(list(unique_answers))}")
            
            # Check if answers are stored as A, B, C, D
            letter_answers = [ans for ans in unique_answers if ans in ['A', 'B', 'C', 'D']]
            logger.info(f"Letter answers (A,B,C,D): {letter_answers}")
            
            # Check if answers are stored as 0, 1, 2, 3
            number_answers = [ans for ans in unique_answers if ans in ['0', '1', '2', '3']]
            logger.info(f"Number answers (0,1,2,3): {number_answers}")
            
            # Check if answers are stored as full text
            text_answers = [ans for ans in unique_answers if len(ans) > 10]
            logger.info(f"Text answers (long): {len(text_answers)}")
            if text_answers:
                logger.info(f"Sample text answers: {text_answers[:3]}")
            
            return {
                'user': user,
                'session': latest_session,
                'responses': responses,
                'unique_answers': unique_answers,
                'letter_answers': letter_answers,
                'number_answers': number_answers,
                'text_answers': text_answers
            }
            
        except Exception as e:
            logger.error(f"Error debugging response format: {e}", exc_info=True)
            return None

def main():
    """Main function"""
    logger.info("Debugging response format...")
    
    result = debug_response_format(2)
    
    if result:
        logger.info("Debug completed successfully!")
    else:
        logger.error("Debug failed!")

if __name__ == '__main__':
    main() 