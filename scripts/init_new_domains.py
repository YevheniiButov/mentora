#!/usr/bin/env python3
"""
Initialize new domains for BI-toets system
Adds the new domains: EMERGENCY, SYSTEMIC, PHARMA, INFECTION, SPECIAL, DIAGNOSIS, DUTCH, PROFESSIONAL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import BIGDomain, Question
import json
from datetime import datetime, timezone

def init_new_domains():
    """Initialize new domains in the database"""
    
    print("🔄 Initializing new domains...")
    
    with app.app_context():
        # Initialize all domains using the new method
        BIGDomain.initialize_domains()
        
        # Verify all domains were created
        all_domains = BIGDomain.query.filter_by(is_active=True).all()
        
        print(f"✅ Successfully initialized {len(all_domains)} domains:")
        
        for domain in all_domains:
            questions_count = len(domain.questions) if hasattr(domain, 'questions') else 0
            print(f"  • {domain.code}: {domain.name} ({domain.weight_percentage}%) - {questions_count} questions")
        
        # Auto-assign domains to existing questions
        print("\n🔄 Auto-assigning domains to existing questions...")
        
        questions_without_domain = Question.query.filter_by(big_domain_id=None).all()
        print(f"Found {len(questions_without_domain)} questions without BIG domain assignment")
        
        assigned_count = 0
        for question in questions_without_domain:
            if question.auto_assign_domain():
                assigned_count += 1
        
        db.session.commit()
        print(f"✅ Auto-assigned domains to {assigned_count} questions")
        
        # Show domain statistics
        print("\n📊 Domain Statistics:")
        for domain in all_domains:
            questions_count = len(domain.questions) if hasattr(domain, 'questions') else 0
            print(f"  • {domain.code}: {questions_count} questions")
        
        print("\n🎉 Domain initialization completed successfully!")

def verify_domain_mapping():
    """Verify that questions are properly mapped to domains"""
    
    print("\n🔍 Verifying domain mapping...")
    
    with app.app_context():
        # Check questions without domain mapping
        unmapped_questions = Question.query.filter_by(big_domain_id=None).all()
        
        if unmapped_questions:
            print(f"⚠️  Found {len(unmapped_questions)} questions without domain mapping:")
            for q in unmapped_questions[:5]:  # Show first 5
                print(f"    - Question {q.id}: domain='{q.domain}'")
            if len(unmapped_questions) > 5:
                print(f"    ... and {len(unmapped_questions) - 5} more")
        else:
            print("✅ All questions have domain mapping")
        
        # Check domain distribution
        print("\n📈 Domain Distribution:")
        domains = BIGDomain.query.filter_by(is_active=True).all()
        total_questions = Question.query.count()
        
        for domain in domains:
            questions_count = len(domain.questions) if hasattr(domain, 'questions') else 0
            percentage = (questions_count / total_questions * 100) if total_questions > 0 else 0
            print(f"  • {domain.code}: {questions_count} questions ({percentage:.1f}%)")

if __name__ == "__main__":
    print("🚀 Starting new domain initialization...")
    
    try:
        init_new_domains()
        verify_domain_mapping()
        
        print("\n✅ All operations completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 