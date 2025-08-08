#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze answer options (0,1,2,3,4) for user with 130 questions
Check how many correct answers were under index 1 (which corresponds to option B)
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

def analyze_answer_options_fixed(user_id=2):
    """Analyze answer options for specific user (using correct format)"""
    
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
                
                # Analyze answer options (0,1,2,3,4)
                answer_stats = {
                    '0': {'total': 0, 'correct': 0, 'incorrect': 0, 'letter': 'A'},
                    '1': {'total': 0, 'correct': 0, 'incorrect': 0, 'letter': 'B'},
                    '2': {'total': 0, 'correct': 0, 'incorrect': 0, 'letter': 'C'},
                    '3': {'total': 0, 'correct': 0, 'incorrect': 0, 'letter': 'D'},
                    '4': {'total': 0, 'correct': 0, 'incorrect': 0, 'letter': 'E'}
                }
                
                # Analyze each response
                for response in responses:
                    selected_answer = response.selected_answer
                    is_correct = response.is_correct
                    
                    if selected_answer in answer_stats:
                        answer_stats[selected_answer]['total'] += 1
                        if is_correct:
                            answer_stats[selected_answer]['correct'] += 1
                        else:
                            answer_stats[selected_answer]['incorrect'] += 1
                
                # Print statistics for this session
                logger.info(f"\nAnswer option statistics for session {session.id}:")
                for option, stats in answer_stats.items():
                    if stats['total'] > 0:
                        accuracy = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
                        logger.info(f"  Option {option} ({stats['letter']}):")
                        logger.info(f"    Total answers: {stats['total']}")
                        logger.info(f"    Correct: {stats['correct']}")
                        logger.info(f"    Incorrect: {stats['incorrect']}")
                        logger.info(f"    Accuracy: {accuracy:.2%}")
                    else:
                        logger.info(f"  Option {option} ({stats['letter']}): No answers")
                
                # Special focus on option 1 (B)
                b_stats = answer_stats['1']
                if b_stats['total'] > 0:
                    b_accuracy = b_stats['correct'] / b_stats['total']
                    logger.info(f"\n🎯 Option 1 (B) Summary for session {session.id}:")
                    logger.info(f"  Total B answers: {b_stats['total']}")
                    logger.info(f"  Correct B answers: {b_stats['correct']}")
                    logger.info(f"  B accuracy: {b_accuracy:.2%}")
                else:
                    logger.info(f"\n🎯 Option 1 (B): No answers in session {session.id}")
            
            # Overall statistics across all sessions
            logger.info(f"\n=== OVERALL STATISTICS ===")
            
            all_responses = DiagnosticResponse.query.join(DiagnosticSession).filter(
                DiagnosticSession.user_id == user_id,
                DiagnosticSession.status == 'completed'
            ).all()
            
            logger.info(f"Total responses across all sessions: {len(all_responses)}")
            
            overall_stats = {
                '0': {'total': 0, 'correct': 0, 'incorrect': 0, 'letter': 'A'},
                '1': {'total': 0, 'correct': 0, 'incorrect': 0, 'letter': 'B'},
                '2': {'total': 0, 'correct': 0, 'incorrect': 0, 'letter': 'C'},
                '3': {'total': 0, 'correct': 0, 'incorrect': 0, 'letter': 'D'},
                '4': {'total': 0, 'correct': 0, 'incorrect': 0, 'letter': 'E'}
            }
            
            for response in all_responses:
                selected_answer = response.selected_answer
                is_correct = response.is_correct
                
                if selected_answer in overall_stats:
                    overall_stats[selected_answer]['total'] += 1
                    if is_correct:
                        overall_stats[selected_answer]['correct'] += 1
                    else:
                        overall_stats[selected_answer]['incorrect'] += 1
            
            logger.info(f"\nOverall answer option statistics:")
            for option, stats in overall_stats.items():
                if stats['total'] > 0:
                    accuracy = stats['correct'] / stats['total']
                    logger.info(f"  Option {option} ({stats['letter']}): {stats['correct']}/{stats['total']} correct ({accuracy:.2%})")
                else:
                    logger.info(f"  Option {option} ({stats['letter']}): No answers")
            
            # Final B summary
            b_overall = overall_stats['1']
            if b_overall['total'] > 0:
                b_overall_accuracy = b_overall['correct'] / b_overall['total']
                logger.info(f"\n🎯 FINAL OPTION 1 (B) SUMMARY:")
                logger.info(f"  Total B answers: {b_overall['total']}")
                logger.info(f"  Correct B answers: {b_overall['correct']}")
                logger.info(f"  B accuracy: {b_overall_accuracy:.2%}")
            else:
                logger.info(f"\n🎯 FINAL OPTION 1 (B) SUMMARY: No B answers found")
            
            # Check session with 130 questions specifically
            logger.info(f"\n=== SESSION WITH 130 QUESTIONS ===")
            session_130 = DiagnosticSession.query.filter_by(
                user_id=user_id,
                questions_answered=130,
                status='completed'
            ).first()
            
            if session_130:
                logger.info(f"Found session {session_130.id} with 130 questions")
                logger.info(f"Completed: {session_130.completed_at}")
                logger.info(f"Correct: {session_130.correct_answers}")
                logger.info(f"Accuracy: {session_130.get_accuracy():.2%}")
                
                responses_130 = session_130.responses.all()
                logger.info(f"Total responses: {len(responses_130)}")
                
                # Analyze 130-question session specifically
                stats_130 = {
                    '0': {'total': 0, 'correct': 0, 'incorrect': 0, 'letter': 'A'},
                    '1': {'total': 0, 'correct': 0, 'incorrect': 0, 'letter': 'B'},
                    '2': {'total': 0, 'correct': 0, 'incorrect': 0, 'letter': 'C'},
                    '3': {'total': 0, 'correct': 0, 'incorrect': 0, 'letter': 'D'},
                    '4': {'total': 0, 'correct': 0, 'incorrect': 0, 'letter': 'E'}
                }
                
                for response in responses_130:
                    selected_answer = response.selected_answer
                    is_correct = response.is_correct
                    
                    if selected_answer in stats_130:
                        stats_130[selected_answer]['total'] += 1
                        if is_correct:
                            stats_130[selected_answer]['correct'] += 1
                        else:
                            stats_130[selected_answer]['incorrect'] += 1
                
                logger.info(f"\n130-question session answer statistics:")
                for option, stats in stats_130.items():
                    if stats['total'] > 0:
                        accuracy = stats['correct'] / stats['total']
                        logger.info(f"  Option {option} ({stats['letter']}): {stats['correct']}/{stats['total']} correct ({accuracy:.2%})")
                    else:
                        logger.info(f"  Option {option} ({stats['letter']}): No answers")
                
                # B summary for 130-question session
                b_130 = stats_130['1']
                if b_130['total'] > 0:
                    b_130_accuracy = b_130['correct'] / b_130['total']
                    logger.info(f"\n🎯 OPTION 1 (B) IN 130-QUESTION SESSION:")
                    logger.info(f"  Total B answers: {b_130['total']}")
                    logger.info(f"  Correct B answers: {b_130['correct']}")
                    logger.info(f"  B accuracy: {b_130_accuracy:.2%}")
                else:
                    logger.info(f"\n🎯 OPTION 1 (B) IN 130-QUESTION SESSION: No B answers")
            else:
                logger.info("No session with exactly 130 questions found")
            
            return {
                'user': user,
                'sessions': sessions,
                'overall_stats': overall_stats,
                'session_130': session_130
            }
            
        except Exception as e:
            logger.error(f"Error analyzing answer options: {e}", exc_info=True)
            return None

def main():
    """Main function"""
    logger.info("Analyzing answer options for user with 130 questions (FIXED)...")
    
    # Analyze user ID 2 (Jan van der Berg)
    result = analyze_answer_options_fixed(2)
    
    if result:
        logger.info("Analysis completed successfully!")
    else:
        logger.error("Analysis failed!")

if __name__ == '__main__':
    main() 