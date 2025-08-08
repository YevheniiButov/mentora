#!/usr/bin/env python3
"""
Script to check IRT parameters integrity
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Question, IRTParameters, BIGDomain
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_irt_integrity():
    """Check integrity of IRT parameters in database"""
    with app.app_context():
        logger.info("🔍 Starting IRT parameters integrity check...")
        
        # Получить все вопросы
        questions = Question.query.all()
        logger.info(f"📊 Total questions in database: {len(questions)}")
        
        # Проверить IRT параметры
        questions_with_irt = 0
        questions_without_irt = 0
        invalid_irt = 0
        invalid_questions = []
        
        for question in questions:
            if question.irt_parameters:
                questions_with_irt += 1
                
                # Проверить валидность параметров
                try:
                    question.irt_parameters.validate_parameters()
                except ValueError as e:
                    invalid_irt += 1
                    invalid_questions.append({
                        'id': question.id,
                        'error': str(e),
                        'difficulty': question.irt_parameters.difficulty,
                        'discrimination': question.irt_parameters.discrimination,
                        'guessing': question.irt_parameters.guessing
                    })
                    logger.error(f"❌ Question {question.id}: Invalid IRT parameters - {e}")
            else:
                questions_without_irt += 1
                logger.warning(f"⚠️ Question {question.id}: Missing IRT parameters")
        
        logger.info(f"✅ Questions with IRT: {questions_with_irt}")
        logger.info(f"⚠️ Questions without IRT: {questions_without_irt}")
        logger.info(f"❌ Questions with invalid IRT: {invalid_irt}")
        
        # Проверить диапазоны параметров
        if questions_with_irt > 0:
            difficulties = [q.irt_parameters.difficulty for q in questions if q.irt_parameters]
            discriminations = [q.irt_parameters.discrimination for q in questions if q.irt_parameters]
            guessings = [q.irt_parameters.guessing for q in questions if q.irt_parameters]
            
            logger.info(f"📈 Difficulty range: {min(difficulties):.3f} to {max(difficulties):.3f}")
            logger.info(f"📈 Discrimination range: {min(discriminations):.3f} to {max(discriminations):.3f}")
            logger.info(f"📈 Guessing range: {min(guessings):.3f} to {max(guessings):.3f}")
            
            # Проверить распределение по доменам
            logger.info("\n🏷️ Distribution by domains:")
            domains = db.session.query(Question.domain, db.func.count(Question.id)).group_by(Question.domain).all()
            for domain, count in domains:
                domain_questions = Question.query.filter_by(domain=domain).all()
                domain_with_irt = sum(1 for q in domain_questions if q.irt_parameters)
                logger.info(f"   {domain}: {count} total, {domain_with_irt} with IRT ({domain_with_irt/count*100:.1f}%)")
        
        # Проверить связь с BIGDomain
        logger.info("\n🔗 Checking BIGDomain relationships:")
        big_domains = BIGDomain.query.all()
        for domain in big_domains:
            domain_questions = Question.query.filter_by(big_domain_id=domain.id).all()
            domain_with_irt = sum(1 for q in domain_questions if q.irt_parameters)
            logger.info(f"   {domain.code} ({domain.name}): {len(domain_questions)} questions, {domain_with_irt} with IRT")
        
        # Показать детали невалидных вопросов
        if invalid_questions:
            logger.info("\n❌ Invalid IRT parameters details:")
            for invalid in invalid_questions[:10]:  # Показать первые 10
                logger.info(f"   Question {invalid['id']}: {invalid['error']}")
                logger.info(f"     Values: difficulty={invalid['difficulty']}, discrimination={invalid['discrimination']}, guessing={invalid['guessing']}")
            if len(invalid_questions) > 10:
                logger.info(f"   ... and {len(invalid_questions) - 10} more")
        
        # Общая статистика
        total_questions = len(questions)
        coverage_percentage = (questions_with_irt / total_questions * 100) if total_questions > 0 else 0
        valid_percentage = ((questions_with_irt - invalid_irt) / total_questions * 100) if total_questions > 0 else 0
        
        logger.info(f"\n📊 SUMMARY:")
        logger.info(f"   Total questions: {total_questions}")
        logger.info(f"   IRT coverage: {coverage_percentage:.1f}%")
        logger.info(f"   Valid IRT: {valid_percentage:.1f}%")
        
        if questions_without_irt > 0:
            logger.warning(f"⚠️ {questions_without_irt} questions missing IRT parameters")
        if invalid_irt > 0:
            logger.error(f"❌ {invalid_irt} questions have invalid IRT parameters")
        
        return {
            'total_questions': total_questions,
            'questions_with_irt': questions_with_irt,
            'questions_without_irt': questions_without_irt,
            'invalid_irt': invalid_irt,
            'coverage_percentage': coverage_percentage,
            'valid_percentage': valid_percentage,
            'invalid_questions': invalid_questions
        }

def check_irt_usage_in_diagnostic():
    """Check how IRT parameters are used in diagnostic sessions"""
    with app.app_context():
        logger.info("\n🔍 Checking IRT usage in diagnostic sessions...")
        
        from models import DiagnosticSession, DiagnosticResponse
        
        # Получить последние диагностические сессии
        recent_sessions = DiagnosticSession.query.filter_by(
            status='completed'
        ).order_by(DiagnosticSession.completed_at.desc()).limit(10).all()
        
        logger.info(f"📊 Found {len(recent_sessions)} recent completed diagnostic sessions")
        
        for session in recent_sessions:
            responses = session.responses.all()
            responses_with_irt = 0
            responses_without_irt = 0
            
            for response in responses:
                if response.question.irt_parameters:
                    responses_with_irt += 1
                else:
                    responses_without_irt += 1
            
            total_responses = len(responses)
            irt_usage_percentage = (responses_with_irt / total_responses * 100) if total_responses > 0 else 0
            
            logger.info(f"   Session {session.id}: {total_responses} responses, {responses_with_irt} with IRT ({irt_usage_percentage:.1f}%)")

if __name__ == "__main__":
    try:
        results = check_irt_integrity()
        check_irt_usage_in_diagnostic()
        
        if results['questions_without_irt'] > 0 or results['invalid_irt'] > 0:
            logger.warning("⚠️ Issues found with IRT parameters!")
            sys.exit(1)
        else:
            logger.info("✅ All IRT parameters are valid!")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"❌ Error during integrity check: {e}")
        sys.exit(1) 