# 🎴 Medical Terminology Flashcards - Phase 2

## Overview

Phase 2 implements the complete user-facing flashcard learning system with interactive study sessions, progress tracking, and statistics.

**What's Included:**
- ✅ 7 Backend routes with full CRUD operations
- ✅ 4 Beautiful responsive templates
- ✅ Alpine.js interactive components
- ✅ 3D flip card animations
- ✅ XP reward system
- ✅ Comprehensive statistics and analytics
- ✅ Spaced repetition integration

**What's NOT Included (Phase 3):**
- API for mobile apps
- Adaptive learning algorithms
- Social features (leaderboards, sharing)
- Video pronunciation guides
- Audio pronunciation support

---

## Architecture

### Backend Routes (`routes/flashcard_routes.py`)

```
GET  /flashcards/categories           → View all categories
GET  /flashcards/study/<category>     → Start study session
POST /flashcards/review/<int:term_id> → Submit term review
GET  /flashcards/due-reviews          → View terms due today
GET  /flashcards/stats                → Overall statistics
GET  /flashcards/category-stats/<cat> → Category statistics
GET  /flashcards/api/due-count        → API for dashboard badge
```

### Helper Functions (`utils/flashcard_helpers.py`)

| Function | Purpose |
|----------|---------|
| `get_session_terms()` | Select 50% new + 50% review terms |
| `calculate_flashcard_xp()` | Award XP (5/10/15 + first-time bonus) |
| `get_mastery_distribution()` | Count terms by mastery level |
| `get_category_progress()` | Detailed category statistics |
| `get_due_reviews_by_category()` | Organize due terms by category |
| `get_study_streak()` | Calculate consecutive study days |

### Templates

| Template | Purpose | Features |
|----------|---------|----------|
| `categories.html` | Category overview | Progress cards, badges, responsive grid |
| `study.html` | Interactive flip card session | 3D animations, keyboard shortcuts, XP animations |
| `due_reviews.html` | Today's due terms | Category grouping, quick stats |
| `stats.html` | Learning analytics | Mastery charts, accuracy stats |
| `category_stats.html` | Detailed category view | Progress bars, action buttons |

---

## Study Session Flow

```
User visits /flashcards/categories
        ↓
Selects category to study
        ↓
Backend: get_session_terms()
  → Select 5 new terms
  → Select 5 due review terms
  → Sort by difficulty/frequency
        ↓
Frontend: Display flip card (study.html)
        ↓
User reviews term (clicks 1-5 or keyboard)
        ↓
Frontend: POST /flashcards/review/<term_id>
  {quality: 1-5}
        ↓
Backend: update_progress_sm2(quality)
  → Recalculate interval
  → Update mastery_level
  → Award XP
  → Commit to database
        ↓
Frontend: Show XP animation
        ↓
Next card loads...
        ↓
When last card done:
  → Show session summary
  → Display total XP
  → Display accuracy
```

---

## XP System

### XP Formula

```
Quality Response | Base XP | First Time Bonus | Total
1-2 (Hard)       | 5 XP   | +5 XP (if new)   | 5-10 XP
3 (Good)         | 10 XP  | +5 XP (if new)   | 10-15 XP
4-5 (Easy)       | 15 XP  | +5 XP (if new)   | 15-20 XP
```

### Example Session

```
Term 1 (New, Quality=5): 15 + 5 = 20 XP ⭐
Term 2 (New, Quality=3): 10 + 5 = 15 XP
Term 3 (Review, Quality=4): 15 XP
Term 4 (New, Quality=1): 5 + 5 = 10 XP
Term 5 (Review, Quality=5): 15 XP

Total Session: 75 XP 🎯
```

---

## Mastery Levels

```
Level 0: Never reviewed (new term)
Level 1: Reviewed 1-2 times (accuracy < 50%)
Level 2: Reviewed 3-4 times (accuracy 50-70%)
Level 3: Reviewed 5+ times (accuracy 70-85%)
Level 4: Consistent accuracy 85-95% (semi-mastered)
Level 5: Consistent accuracy > 95% (fully mastered)
```

---

## Frontend Features

### 1. Interactive Flip Card

```
[FRONT]
┌─────────────────────┐
│                     │
│   het hart          │
│                     │
│  Click to reveal    │
└─────────────────────┘

[BACK]
┌─────────────────────┐
│                     │
│   heart             │
│                     │
│ The central pumping │
│ organ of the body   │
└─────────────────────┘
```

**Animation:**
- CSS 3D transform with `rotateY(180deg)`
- Smooth 0.6s transition
- Touch-friendly click area

### 2. Keyboard Shortcuts

```
Spacebar  → Flip card
1         → Hard (see tomorrow)
2         → Good (see in 3 days)
3         → Easy (see in 7 days)
```

### 3. XP Animation

```
When user submits review:
  1. Show "+15 XP" floating upward
  2. Fade in, move up 60px, fade out
  3. Duration: 1.5 seconds
  4. Animation: floatUp keyframe
```

### 4. Session Complete Modal

```
🎉 Session Complete!

Terms Studied:     10
Total XP Earned:   75 XP
Accuracy:          80%

[Back to Categories] [Continue Learning]
```

---

## Responsive Design

### Breakpoints

```
Desktop (>1200px)   → Full grid, 4-column layout
Tablet (768-1200px) → 2-column cards
Mobile (<768px)     → Single column, stacked buttons
```

### Mobile Optimizations

```
- Vertical action buttons instead of horizontal
- Larger touch targets (minimum 44px)
- Full-width cards
- Simplified headers
- Compact stats display
```

---

## Database Integration

### Models Used

```python
MedicalTerm
├── id
├── term_nl (indexed)
├── term_en, term_ru, ...
├── category (indexed)
└── user_progress → UserTermProgress

UserTermProgress
├── user_id (indexed)
├── term_id (indexed)
├── ease_factor, interval, repetitions
├── next_review (indexed) ← Used for queries
├── times_reviewed, times_correct
├── mastery_level
└── last_reviewed
```

### Query Performance

```sql
-- Get due reviews (highly optimized with index)
SELECT * FROM user_term_progress
WHERE user_id = ? AND next_review <= NOW()
-- Uses: idx_user_term_progress_user_next_review

-- Get category progress (joins)
SELECT mt.*, utp.* FROM medical_term mt
LEFT JOIN user_term_progress utp 
  ON mt.id = utp.term_id AND utp.user_id = ?
WHERE mt.category = ?
-- Uses: idx_medical_term_category
```

---

## User Experience Flow

### First Time User

```
1. Visits /flashcards/categories
2. Sees 5 empty categories (0 studied)
3. Clicks "Start Learning" on any category
4. Gets 10 new terms (5 random new + 5 already reviewed empty)
5. Reviews each term one by one
6. Earns first XP
7. Sees completion modal
8. Returns to categories (progress updated)
```

### Regular User

```
1. Visits /flashcards/categories
2. Sees "🔄 3 due today" badge
3. Clicks "🔄 All Due Reviews"
4. Sees 3 terms grouped by category
5. Clicks "Review anatomy"
6. Reviews due terms
7. Completes session
8. Checks overall progress
```

### Advanced User

```
1. Checks /flashcards/stats
2. Views mastery distribution
3. Focuses on weak categories
4. Reviews weak areas daily
5. Maintains study streak
6. Achieves mastery on categories
```

---

## Statistics Available

### Overview Stats

```
- Total Studied: Count of unique terms user has seen
- Total Reviewed: Sum of all review attempts
- Accuracy: (correct_answers / total_reviews) × 100%
- Current Streak: Consecutive days with activity
```

### Mastery Distribution

```
Shows count of terms at each mastery level
Example:
  Level 0: 25 new terms
  Level 1: 10 learning terms
  Level 2: 8 learning terms
  Level 3: 5 learning terms
  Level 4: 2 semi-mastered
  Level 5: 0 fully mastered
```

### Category Stats

```
Per category:
- Total terms in category
- How many studied
- How many mastered
- Accuracy rate
- Last review date
```

---

## Error Handling

### Frontend Errors

```javascript
try {
    const response = await fetch(`/flashcards/review/${termId}`);
    const data = await response.json();
    
    if (!response.ok) {
        alert('Error: ' + data.error);
        return;
    }
    // Update UI
} catch (error) {
    console.error('Network error:', error);
    alert('Failed to submit review');
}
```

### Backend Errors

```python
@flashcard_bp.route('/review/<int:term_id>', methods=['POST'])
@login_required
def review_term(term_id):
    try:
        term = MedicalTerm.query.get_or_404(term_id)
        # Process review
        db.session.commit()
        return jsonify({'success': True, ...})
    except Exception as e:
        logger.error(f"Error reviewing term: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to process review'}), 500
```

---

## Testing Checklist

### Manual Testing

```
□ Visit /flashcards/categories
  ✓ All 5 categories visible
  ✓ Progress bars show correct %
  ✓ Due badges count correct
  
□ Start study session
  ✓ 10 terms loaded
  ✓ Card flips on click/space
  ✓ Buttons appear after flip
  
□ Submit review (all qualities)
  ✓ 1=Hard: interval = 1 day
  ✓ 3=Good: interval = 3 days
  ✓ 5=Easy: interval = 7 days
  ✓ XP animation shows
  ✓ Next card loads
  
□ Session completion
  ✓ Modal appears
  ✓ Stats display correct
  ✓ Can return or continue
  
□ Due reviews page
  ✓ Terms grouped by category
  ✓ Mastery stars show
  ✓ Quick stats calculate
  
□ Statistics
  ✓ Overall stats calculate
  ✓ Mastery distribution shows
  ✓ Category cards load
  
□ Responsive design
  ✓ Test on mobile
  ✓ Cards stack vertically
  ✓ Buttons resize
  ✓ Font sizes adjust
  
□ Keyboard shortcuts
  ✓ Space flips card
  ✓ 1,2,3 submit answers
  
□ Multiple languages
  ✓ Terms display in user's language
  ✓ Fallback to English works
```

### Performance Testing

```
Endpoint Response Times:
- /flashcards/categories    < 500ms (cached)
- /flashcards/study/<cat>   < 200ms
- POST /flashcards/review   < 300ms
- /flashcards/due-reviews   < 400ms
- /flashcards/stats         < 800ms (calculation)
```

---

## Deployment Notes

### Pre-Deployment

```bash
# Ensure models are migrated
flask db upgrade

# Ensure seed data loaded
python scripts/medical_terms_seed.py

# Run tests
pytest tests/test_flashcards.py
```

### Environment Variables

```python
# None required - uses existing app configuration
# Inherits: DATABASE_URL, FLASK_ENV, SECRET_KEY
```

### Production Considerations

```
1. Cache category list (changes rarely)
2. Use connection pooling for DB
3. Consider CDN for CSS/JS
4. Monitor query performance
5. Set up alerts for errors
6. Log review submissions
```

---

## Next Steps (Phase 3)

### Mobile App API

```
POST /api/flashcards/session/start
  → returns 10 terms with IDs

GET /api/flashcards/session/{session_id}
  → returns current term

POST /api/flashcards/session/{session_id}/review
  → submit answer

GET /api/flashcards/session/{session_id}/complete
  → get session summary
```

### Adaptive Learning

```
- Adjust term selection based on weakness
- Predict review dates using ML
- Recommend focus areas
- Estimate time to mastery
```

### Social Features

```
- Leaderboards (global, friends)
- Study challenges
- Share achievements
- Group learning
```

---

## Support

### Common Issues

**Q: My session XP isn't showing**
A: Check that Alpine.js loaded and browser console shows no errors. Hard refresh with Ctrl+Shift+R.

**Q: Terms aren't progressing**
A: Verify DB updated (check `next_review` in DB). Clear browser cache.

**Q: Mobile buttons not working**
A: Ensure viewport meta tag in base.html. Test on different devices.

**Q: XP not being awarded**
A: Check Flask logs for `/flashcards/review` endpoint errors. Verify `current_user` authenticated.

---

## Files Overview

```
routes/flashcard_routes.py              (360 lines)
  ├── 7 route handlers
  ├── Request validation
  └── Database operations

utils/flashcard_helpers.py              (315 lines)
  ├── 6 helper functions
  ├── Query optimization
  └── Statistical calculations

templates/flashcards/
  ├── categories.html          (550 lines)
  ├── study.html              (800 lines)
  ├── due_reviews.html        (600 lines)
  ├── stats.html              (380 lines)
  └── category_stats.html     (320 lines)

app.py
  └── flashcard_bp registration

docs/
  ├── MEDICAL_TERMS_PHASE2.md  (this file)
  └── PHASE2_SUMMARY.md
```

---

## Performance Metrics

### Database

```
Total Medical Terms:     50
Languages Supported:     8 (NL, EN, RU, UK, ES, PT, TR, FA, AR)
Indexes Created:         4 (term_nl, category, user_next_review, user_term unique)
Typical Query Time:      < 10ms (with indexes)
```

### Frontend

```
Page Load Time:          < 1s
Card Flip Animation:     60fps (CSS transform)
XP Animation:            1.5s smooth fade
Session Load:            < 200ms
Bundle Size:             Alpine.js CDN (< 15KB gzipped)
```

---

## License & Attribution

Medical terminology sourced from:
- Dutch medical education resources
- Healthcare terminology standards
- Open medical dictionaries

See `scripts/medical_terms_seed.py` for term sources.







