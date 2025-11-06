# utils/ielts_prompt_template.py
# IELTS Prompt Template for AI Generation

IELTS_PROMPT_TEMPLATE = """Create an IELTS Academic Reading passage with the following specifications:

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


def format_ielts_prompt(
    topic: str,
    word_count: int = 450,
    band_level: float = 7.0,
    num_paragraphs: int = 3
) -> str:
    """
    Format IELTS prompt with given parameters
    
    Args:
        topic: Topic of the passage
        word_count: Target word count (400-500)
        band_level: IELTS band level
        num_paragraphs: Number of paragraphs (3 or 4)
    
    Returns:
        Formatted prompt string
    """
    # Validate and adjust
    if num_paragraphs not in [3, 4]:
        num_paragraphs = 3
    
    # Create paragraph labels
    if num_paragraphs == 3:
        paragraph_labels = "A, B, C"
    else:
        paragraph_labels = "A, B, C, D"
    
    return IELTS_PROMPT_TEMPLATE.format(
        topic=topic,
        word_count=word_count,
        band_level=band_level,
        num_paragraphs=num_paragraphs,
        paragraph_labels=paragraph_labels
    )


# Example topics for IELTS passages
IELTS_TOPICS = [
    "Ancient Architecture",
    "Climate Change",
    "Artificial Intelligence",
    "Renewable Energy",
    "Medical Research",
    "Space Exploration",
    "Ocean Conservation",
    "Urban Planning",
    "Educational Technology",
    "Cultural Heritage",
    "Sustainable Development",
    "Neuroscience",
    "Archaeology",
    "Environmental Science",
    "Social Psychology"
]


# Prompt for generating questions
QUESTIONS_GENERATION_PROMPT = """Based on the following IELTS reading passage, create questions in these formats:

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


def format_questions_prompt(
    passage_text: str,
    num_multiple_choice: int = 5,
    num_true_false_ng: int = 3,
    num_fill_blank: int = 4
) -> str:
    """
    Format questions generation prompt
    
    Args:
        passage_text: The reading passage text
        num_multiple_choice: Number of multiple choice questions
        num_true_false_ng: Number of True/False/Not Given questions
        num_fill_blank: Number of fill in the blank questions
    
    Returns:
        Formatted prompt string
    """
    return QUESTIONS_GENERATION_PROMPT.format(
        passage_text=passage_text,
        num_multiple_choice=num_multiple_choice,
        num_true_false_ng=num_true_false_ng,
        num_fill_blank=num_fill_blank
    )

