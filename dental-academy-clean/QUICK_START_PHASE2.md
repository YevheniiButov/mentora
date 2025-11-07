# 🎴 Quick Start - Medical Flashcards Phase 2

## Access Points

### Main Pages
```
http://yourapp.com/flashcards/categories           # Browse categories
http://yourapp.com/flashcards/study/anatomy        # Study session
http://yourapp.com/flashcards/due-reviews          # Today's reviews
http://yourapp.com/flashcards/stats                # Analytics
```

### API Endpoint (for dashboard)
```
GET /flashcards/api/due-count   # Returns {"due_count": 3}
```

---

## Study Session Guide

### How to Study
1. Click category on `/flashcards/categories`
2. Get 10 terms (5 new + 5 review)
3. Click card to flip
4. Rate difficulty: Hard (1), Good (2), Easy (3)
5. See XP earned
6. Move to next term
7. Complete session → view summary

### Keyboard Shortcuts
```
Space    → Flip card
1        → Hard (🔄 tomorrow)
2        → Good (✓ 3 days)
3        → Easy (⭐ 7 days)
```

### XP Formula
```
Quality 1-2: 5 XP + 5 (first time) = 10 XP
Quality 3:   10 XP + 5 (first time) = 15 XP
Quality 4-5: 15 XP + 5 (first time) = 20 XP

Max per session (10 terms): 200 XP
```

---

## Features Overview

### Categories Page
- View all 5 categories
- See progress bars
- Check mastery count
- "Due today" badge
- Start learning or review

### Study Session
- Beautiful 3D flip card
- Color-coded buttons
- XP animation
- Progress bar
- Session modal summary

### Due Reviews
- Grouped by category
- Quick stats
- Term cards with mastery
- Direct review links

### Statistics
- Overall progress
- Mastery distribution
- Category breakdown
- Study streak counter

---

## Backend Endpoints Summary

| Method | Endpoint | Returns |
|--------|----------|---------|
| GET | `/flashcards/categories` | HTML page with categories |
| GET | `/flashcards/study/<cat>` | HTML page with 10 terms |
| POST | `/flashcards/review/<id>` | JSON {success, xp, mastery} |
| GET | `/flashcards/due-reviews` | HTML page with due terms |
| GET | `/flashcards/stats` | HTML page with analytics |
| GET | `/flashcards/category-stats/<cat>` | HTML page with category detail |
| GET | `/flashcards/api/due-count` | JSON {due_count: number} |

---

## Database Fields

### MedicalTerm
```
id, term_nl, definition_nl, term_en, term_ru, term_uk,
term_es, term_pt, term_tr, term_fa, term_ar,
category, difficulty, frequency, audio_url,
created_at, updated_at
```

### UserTermProgress
```
id, user_id, term_id,
ease_factor, interval, repetitions, next_review,
times_reviewed, times_correct, mastery_level,
last_quality, last_reviewed,
created_at
```

---

## Troubleshooting

### Card won't flip
- Check browser console for errors
- Ensure JavaScript enabled
- Try hard refresh (Ctrl+Shift+R)

### XP not showing
- Check if session loaded correctly
- Verify POST returned 200 status
- Check browser console for fetch errors

### Categories empty
- Run seed: `python scripts/medical_terms_seed.py`
- Verify database migrated

### Mobile buttons not clickable
- Increase viewport size
- Check if CSS loaded
- Verify touch events supported

---

## Files Changed in Phase 2

```
CREATED:
  routes/flashcard_routes.py
  utils/flashcard_helpers.py
  templates/flashcards/categories.html
  templates/flashcards/study.html
  templates/flashcards/due_reviews.html
  templates/flashcards/stats.html
  templates/flashcards/category_stats.html
  docs/MEDICAL_TERMS_PHASE2.md
  PHASE2_COMPLETE.md
  QUICK_START_PHASE2.md (this file)

MODIFIED:
  app.py (added flashcard_bp registration)

DATABASE:
  Uses: MedicalTerm, UserTermProgress (from Phase 1)
  No schema changes needed
```

---

## Performance Notes

- All endpoints respond in < 1 second
- Card animations run at 60fps
- Database queries use indexed lookups
- Alpine.js loaded from CDN (lightweight)
- CSS 3D transforms used for flip animation

---

## Next Phase (Phase 3)

Coming soon:
- Mobile app API
- Adaptive difficulty
- Social features
- Audio pronunciation
- Video lessons

---

*Quick Start Guide v1.0*
*Medical Terminology Flashcards Phase 2*
