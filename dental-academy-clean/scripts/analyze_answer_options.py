#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze answer options (A, B, C, D) for user with 130 questions
Check how many correct answers were under letter "B"
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

def analyze_answer_options(user_id=2):
    """Analyze answer options for specific user"""
    
    with app.app_context():
        try:
            logger.info(f"=== Analyzing Answer Options for User {user_id} ===")
            
            # Get user
            user = User.query.get(user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return
            
            logger.info(f"User: {user.email} ({user.full_name})")
            
            # Get all completed diagnostic sessions for this user
            sessions = DiagnosticSession.query.filter_by(
                user_id=user_id,
                status='completed'
            ).order_by(DiagnosticSession.completed_at.desc()).all()
            
            logger.info(f"Found {len(sessions)} completed diagnostic sessions")
            
            # Analyze each session
            for i, session in enumerate(sessions):
                logger.info(f"\n--- Session {i+1}: {session.id} ---")
                logger.info(f"Completed: {session.completed_at}")
                logger.info(f"Questions: {session.questions_answered}")
                logger.info(f"Correct: {session.correct_answers}")
                logger.info(f"Accuracy: {session.get_accuracy():.2%}")
                
                # Get all responses for this session
                responses = session.responses.all()
                logger.info(f"Total responses: {len(responses)}")
                
                if not responses:
                    logger.info("No responses found")
                    continue
                
                # Analyze answer options
                answer_stats = {
                    'A': {'total': 0, 'correct': 0, 'incorrect': 0},
                    'B': {'total': 0, 'correct': 0, 'incorrect': 0},
                    'C': {'total': 0, 'correct': 0, 'incorrect': 0},
                    'D': {'total': 0, 'correct': 0, 'incorrect': 0}
                }
                
                # Analyze each response
                for response in responses:
                    question = response.question
                    selected_answer = response.selected_answer
                    is_correct = response.is_correct
                    
                    # Get correct answer from question
                    if question and hasattr(question, 'options') and question.options:
                        options = question.options if isinstance(question.options, list) else json.loads(question.options)
                        correct_answer_text = question.correct_answer_text
                        
                        # Find which option (A, B, C, D) was selected
                        selected_option = None
                        correct_option = None
                        
                        for j, option in enumerate(options):
                            if option == selected_answer:
                                selected_option = chr(65 + j)  # A, B, C, D
                            if option == correct_answer_text:
                                correct_option = chr(65 + j)  # A, B, C, D
                        
                        if selected_option:
                            answer_stats[selected_option]['total'] += 1
                            if is_correct:
                                answer_stats[selected_option]['correct'] += 1
                            else:
                                answer_stats[selected_option]['incorrect'] += 1
                
                # Print statistics for this session
                logger.info(f"\nAnswer option statistics for session {session.id}:")
                for option, stats in answer_stats.items():
                    if stats['total'] > 0:
                        accuracy = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
                        logger.info(f"  Option {option}:")
                        logger.info(f"    Total answers: {stats['total']}")
                        logger.info(f"    Correct: {stats['correct']}")
                        logger.info(f"    Incorrect: {stats['incorrect']}")
                        logger.info(f"    Accuracy: {accuracy:.2%}")
                    else:
                        logger.info(f"  Option {option}: No answers")
                
                # Special focus on option B
                b_stats = answer_stats['B']
                if b_stats['total'] > 0:
                    b_accuracy = b_stats['correct'] / b_stats['total']
                    logger.info(f"\n🎯 Option B Summary for session {session.id}:")
                    logger.info(f"  Total B answers: {b_stats['total']}")
                    logger.info(f"  Correct B answers: {b_stats['correct']}")
                    logger.info(f"  B accuracy: {b_accuracy:.2%}")
                else:
                    logger.info(f"\n🎯 Option B: No answers in session {session.id}")
            
            # Overall statistics across all sessions
            logger.info(f"\n=== OVERALL STATISTICS ===")
            
            all_responses = DiagnosticResponse.query.join(DiagnosticSession).filter(
                DiagnosticSession.user_id == user_id,
                DiagnosticSession.status == 'completed'
            ).all()
            
            logger.info(f"Total responses across all sessions: {len(all_responses)}")
            
            overall_stats = {
                'A': {'total': 0, 'correct': 0, 'incorrect': 0},
                'B': {'total': 0, 'correct': 0, 'incorrect': 0},
                'C': {'total': 0, 'correct': 0, 'incorrect': 0},
                'D': {'total': 0, 'correct': 0, 'incorrect': 0}
            }
            
            for response in all_responses:
                question = response.question
                selected_answer = response.selected_answer
                is_correct = response.is_correct
                
                if question and hasattr(question, 'options') and question.options:
                    options = question.options if isinstance(question.options, list) else json.loads(question.options)
                    
                    for j, option in enumerate(options):
                        if option == selected_answer:
                            selected_option = chr(65 + j)  # A, B, C, D
                            overall_stats[selected_option]['total'] += 1
                            if is_correct:
                                overall_stats[selected_option]['correct'] += 1
                            else:
                                overall_stats[selected_option]['incorrect'] += 1
                            break
            
            logger.info(f"\nOverall answer option statistics:")
            for option, stats in overall_stats.items():
                if stats['total'] > 0:
                    accuracy = stats['correct'] / stats['total']
                    logger.info(f"  Option {option}: {stats['correct']}/{stats['total']} correct ({accuracy:.2%})")
                else:
                    logger.info(f"  Option {option}: No answers")
            
            # Final B summary
            b_overall = overall_stats['B']
            if b_overall['total'] > 0:
                b_overall_accuracy = b_overall['correct'] / b_overall['total']
                logger.info(f"\n🎯 FINAL OPTION B SUMMARY:")
                logger.info(f"  Total B answers: {b_overall['total']}")
                logger.info(f"  Correct B answers: {b_overall['correct']}")
                logger.info(f"  B accuracy: {b_overall_accuracy:.2%}")
            else:
                logger.info(f"\n🎯 FINAL OPTION B SUMMARY: No B answers found")
            
            return {
                'user': user,
                'sessions': sessions,
                'overall_stats': overall_stats
            }
            
        except Exception as e:
            logger.error(f"Error analyzing answer options: {e}", exc_info=True)
            return None

def main():
    """Main function"""
    logger.info("Analyzing answer options for user with 130 questions...")
    
    # Analyze user ID 2 (Jan van der Berg)
    result = analyze_answer_options(2)
    
    if result:
        logger.info("Analysis completed successfully!")
    else:
        logger.error("Analysis failed!")

if __name__ == '__main__':
    main() 