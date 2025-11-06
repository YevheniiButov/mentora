# scripts/load_ielts_passage.py
# Script to load IELTS passage and questions into database

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import EnglishPassage, EnglishQuestion


def load_passage_with_questions(
    title: str,
    text: str,
    category: str = "general",
    difficulty: int = 7,
    word_count: int = None,
    questions_data: list = None
):
    """
    Load passage and questions into database
    
    Args:
        title: Passage title
        text: Passage text
        category: Passage category
        difficulty: IELTS band level (default 7)
        word_count: Word count (calculated if None)
        questions_data: List of question dictionaries
    
    Returns:
        Created passage object
    """
    with app.app_context():
        # Calculate word count if not provided
        if word_count is None:
            word_count = len(text.split())
        
        # Create passage
        passage = EnglishPassage(
            title=title,
            text=text,
            category=category,
            difficulty=difficulty,
            word_count=word_count
        )
        
        db.session.add(passage)
        db.session.flush()
        
        # Add questions if provided
        if questions_data:
            for q_data in questions_data:
                # Handle options - convert dict to JSON string if needed
                options = q_data.get('options', {})
                if isinstance(options, dict):
                    options = json.dumps(options)
                elif options is None:
                    options = None
                
                question = EnglishQuestion(
                    passage_id=passage.id,
                    question_number=q_data.get('number', q_data.get('question_number')),
                    question_type=q_data.get('type', q_data.get('question_type')),
                    question_text=q_data.get('text', q_data.get('question_text')),
                    correct_answer=q_data.get('correct_answer'),
                    options=options,
                    explanation=q_data.get('explanation')
                )
                
                db.session.add(question)
        
        db.session.commit()
        
        print(f"✅ Added passage '{passage.title}' (ID: {passage.id})")
        if questions_data:
            print(f"   Added {len(questions_data)} questions")
        else:
            print(f"   No questions added")
        
        return passage


def load_from_json(json_file_path: str):
    """
    Load passage and questions from JSON file
    
    JSON format:
    {
        "title": "...",
        "text": "...",
        "category": "...",
        "difficulty": 7,
        "word_count": 450,
        "questions": [
            {
                "type": "multiple_choice",
                "number": 1,
                "text": "...",
                "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
                "correct_answer": "B",
                "explanation": "..."
            },
            ...
        ]
    }
    """
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return load_passage_with_questions(
        title=data.get('title'),
        text=data.get('text'),
        category=data.get('category', 'general'),
        difficulty=data.get('difficulty', 7),
        word_count=data.get('word_count'),
        questions_data=data.get('questions', [])
    )


# Example usage
if __name__ == '__main__':
    # Example 1: Manual input
    passage_text = """
    Paragraph A
    The evolution of urban planning has been a continuous process throughout human history...
    
    Paragraph B
    Modern urban planning emerged in the 19th century as cities grew rapidly...
    
    Paragraph C
    Today, sustainable development principles guide urban planning...
    """
    
    questions_data = [
        {
            "type": "multiple_choice",
            "number": 1,
            "text": "According to the passage, when did modern urban planning emerge?",
            "options": {"A": "18th century", "B": "19th century", "C": "20th century", "D": "21st century"},
            "correct_answer": "B",
            "explanation": "Paragraph B explicitly states that modern urban planning emerged in the 19th century."
        },
        {
            "type": "true_false_ng",
            "number": 2,
            "text": "Urban planning has been a continuous process throughout human history.",
            "correct_answer": "TRUE",
            "explanation": "Paragraph A states that 'The evolution of urban planning has been a continuous process throughout human history'."
        },
        {
            "type": "fill_blank",
            "number": 3,
            "text": "Today, urban planning is guided by _______ development principles.",
            "correct_answer": "sustainable",
            "explanation": "Paragraph C states that 'sustainable development principles guide urban planning'."
        }
    ]
    
    # Uncomment to use:
    # load_passage_with_questions(
    #     title="The Evolution of Urban Planning",
    #     text=passage_text.strip(),
    #     category="architecture",
    #     difficulty=7,
    #     word_count=450,
    #     questions_data=questions_data
    # )
    
    # Example 2: Load from JSON file
    # load_from_json('ielts_passage.json')
    
    print("\n📝 Usage:")
    print("1. Import and use load_passage_with_questions() function")
    print("2. Or use load_from_json() to load from JSON file")
    print("\nExample:")
    print("""
    from scripts.load_ielts_passage import load_passage_with_questions
    
    load_passage_with_questions(
        title="Your Passage Title",
        text="Your passage text here...",
        category="science",
        difficulty=7,
        questions_data=[
            {
                "type": "multiple_choice",
                "number": 1,
                "text": "Question text?",
                "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
                "correct_answer": "B",
                "explanation": "Explanation..."
            }
        ]
    )
    """)


