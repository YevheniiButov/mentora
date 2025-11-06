# utils/ielts_generator.py
# IELTS Reading Passage Generator

import re
from typing import Dict, List, Optional

def generate_ielts_prompt(
    topic: str,
    word_count: int = 450,
    band_level: float = 7.0,
    num_paragraphs: int = 3
) -> str:
    """
    Generate a prompt for creating IELTS Academic Reading passage
    
    Args:
        topic: Topic of the passage (e.g., "Ancient Architecture", "Climate Change")
        word_count: Target word count (400-500)
        band_level: IELTS band level (default 7.0)
        num_paragraphs: Number of paragraphs (3 or 4)
    
    Returns:
        Formatted prompt string
    """
    # Validate paragraph count
    if num_paragraphs not in [3, 4]:
        num_paragraphs = 3
    
    # Create paragraph labels
    if num_paragraphs == 3:
        paragraph_labels = "A, B, C"
    else:
        paragraph_labels = "A, B, C, D"
    
    prompt = f"""Create an IELTS Academic Reading passage with the following specifications:

Topic: {topic}
Word count: {word_count} words
IELTS Band level: {band_level}
Structure: {num_paragraphs} paragraphs labeled {paragraph_labels}

Requirements:
- Academic style, neutral tone
- Include facts, statistics, examples
- Complex sentence structures
- Advanced vocabulary appropriate for Band {band_level}
- Cohesive and coherent flow

Format the output as plain text with clear paragraph breaks. Each paragraph should be labeled with its letter (A, B, C, etc.) at the beginning."""
    
    return prompt


def parse_generated_passage(text: str) -> Dict[str, str]:
    """
    Parse generated passage text into structured format
    
    Args:
        text: Generated passage text
    
    Returns:
        Dictionary with 'title', 'text', 'paragraphs' (list), 'word_count'
    """
    # Extract title if present (first line or after "Title:")
    title = ""
    paragraphs = []
    
    lines = text.strip().split('\n')
    
    # Find title
    for i, line in enumerate(lines):
        if line.strip().startswith('Title:'):
            title = line.replace('Title:', '').strip()
            break
        elif i == 0 and not line.strip().startswith(('Paragraph', 'A', 'B', 'C', 'D')):
            title = line.strip()
            break
    
    # Extract paragraphs (labeled A, B, C, D)
    current_paragraph = ""
    current_label = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if line starts with paragraph label
        if re.match(r'^[ABCD]\s*[:\-]?\s*', line, re.IGNORECASE):
            # Save previous paragraph if exists
            if current_paragraph and current_label:
                paragraphs.append({
                    'label': current_label,
                    'text': current_paragraph.strip()
                })
            
            # Extract label and start new paragraph
            match = re.match(r'^([ABCD])', line, re.IGNORECASE)
            if match:
                current_label = match.group(1).upper()
                current_paragraph = re.sub(r'^[ABCD]\s*[:\-]?\s*', '', line, flags=re.IGNORECASE).strip()
        else:
            # Continue current paragraph
            if current_paragraph:
                current_paragraph += " " + line
            elif current_label:
                current_paragraph = line
    
    # Don't forget the last paragraph
    if current_paragraph and current_label:
        paragraphs.append({
            'label': current_label,
            'text': current_paragraph.strip()
        })
    
    # Combine all paragraphs into full text
    full_text = "\n\n".join([p['text'] for p in paragraphs])
    
    # Count words
    word_count = len(full_text.split())
    
    # Generate title from topic if not found
    if not title:
        title = "IELTS Reading Passage"
    
    return {
        'title': title,
        'text': full_text,
        'paragraphs': paragraphs,
        'word_count': word_count
    }


def generate_passage_title_from_topic(topic: str) -> str:
    """
    Generate a suitable title for passage based on topic
    
    Args:
        topic: Topic string
    
    Returns:
        Formatted title
    """
    # Capitalize and format
    title = topic.strip()
    
    # Add "The" if appropriate
    if not title.startswith(('The', 'A', 'An')):
        # Check if it's a specific topic that needs "The"
        if any(keyword in title.lower() for keyword in ['architecture', 'history', 'development', 'impact']):
            title = f"The {title}"
    
    return title


def generate_questions_prompt(
    passage_text: str,
    num_multiple_choice: int = 5,
    num_true_false_ng: int = 3,
    num_fill_blank: int = 4
) -> str:
    """
    Generate a prompt for creating IELTS questions based on passage
    
    Args:
        passage_text: The reading passage text
        num_multiple_choice: Number of multiple choice questions
        num_true_false_ng: Number of True/False/Not Given questions
        num_fill_blank: Number of fill in the blank questions
    
    Returns:
        Formatted prompt string
    """
    prompt = f"""Based on the following IELTS reading passage, create questions in these formats:

Passage:
{passage_text}

Generate:

1. {num_multiple_choice} Multiple Choice questions (A, B, C, D options)

2. {num_true_false_ng} True/False/Not Given statements

3. {num_fill_blank} Fill in the Blank questions (one word or number)

For each question provide:
- Question text
- Correct answer
- Brief explanation why it's correct

Format as JSON:

{{
  "questions": [
    {{
      "type": "multiple_choice",
      "number": 1,
      "text": "...",
      "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
      "correct_answer": "B",
      "explanation": "..."
    }},
    {{
      "type": "true_false_ng",
      "number": 6,
      "text": "...",
      "correct_answer": "TRUE",
      "explanation": "..."
    }},
    {{
      "type": "fill_blank",
      "number": 9,
      "text": "...",
      "correct_answer": "...",
      "explanation": "..."
    }}
  ]
}}

Important:
- Questions should be in order (1, 2, 3, etc.)
- Multiple choice questions should have exactly 4 options (A, B, C, D)
- True/False/Not Given answers should be exactly "TRUE", "FALSE", or "NOT GIVEN"
- Fill in the blank answers should be single words or numbers found in the passage
- All questions must be answerable from the passage text
- Provide clear, concise explanations"""
    
    return prompt

