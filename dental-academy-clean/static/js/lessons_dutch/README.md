# Dutch Reading Lessons

This directory contains Dutch reading comprehension lessons in JavaScript format.

## File naming convention:
- `lesson_001.js` - First lesson
- `lesson_002.js` - Second lesson
- etc.

## Lesson structure:
Each lesson should export an object with:
- `id`: unique lesson ID
- `title`: lesson title in Dutch
- `text`: full text of the passage
- `category`: category (e.g., 'medisch', 'algemeen', 'wetenschap')
- `difficulty`: 1-5 (1=easiest, 5=hardest)
- `imageUrl`: optional image URL
- `questions`: array of question objects with:
  - `id`: question ID
  - `question`: question text
  - `type`: 'multiple_choice', 'true_false', 'fill_blank', etc.
  - `options`: array of option objects with:
    - `id`: option ID (A, B, C, D)
    - `text`: option text
    - `correct`: boolean
    - `explanation`: explanation (optional)

## Example:
```javascript
export const lesson_001 = {
  id: 'lesson_001',
  title: 'De Geschiedenis van de Geneeskunde',
  text: `Lorem ipsum...`,
  category: 'medisch',
  difficulty: 3,
  imageUrl: '/static/images/dutch/medicine_history.jpg',
  questions: [
    {
      id: 'q1',
      question: 'Wat is het hoofdonderwerp van deze tekst?',
      type: 'multiple_choice',
      options: [
        { id: 'A', text: 'Moderne chirurgie', correct: false },
        { id: 'B', text: 'Geschiedenis van de geneeskunde', correct: true, explanation: 'De tekst beschrijft...' },
        { id: 'C', text: 'Tandheelkunde', correct: false },
        { id: 'D', text: 'Farmacie', correct: false }
      ]
    }
  ]
};
```

## Notes:
- All text should be in Dutch
- Questions should test reading comprehension
- Difficulty should be appropriate for medical students learning Dutch
- Images should be relevant to the topic

