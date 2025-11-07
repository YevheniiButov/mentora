# PROFESSION FILTERING & LANGUAGE GAMES AUDIT REPORT

**Date:** 2025-10-26  
**Auditor:** AI Assistant  
**Application:** Mentora Flask Application

---

## EXECUTIVE SUMMARY

| Component | Status | Notes |
|-----------|--------|-------|
| Profession Filtering | ⚠️ PARTIAL | Model exists, filtering incomplete |
| Memory Game | ✅ WORKING | Full implementation exists |
| Flashcards System | ⚠️ PARTIAL | Content exists, no DB model |
| Language Learning | ❌ MISSING | No vocabulary system |

---

## TASK 1: PROFESSION FILTERING ANALYSIS

### 1.1 Database Schema

✅ **Question Model:**
```python
profession = db.Column(db.String(50), nullable=True, index=True)  # tandarts, apotheker, huisarts, verpleegkundige
```

✅ **User Model:**
```python
profession = db.Column(db.String(50), nullable=True)  # tandarts, apotheker, huisarts, verpleegkundige
```

**Status:** ✅ Schema is ready

---

### 1.2 Question Profession Distribution

**Current State:**
- Total questions analyzed: 640 (from 5 JSON files)
- Questions with profession: **0**
- Questions without profession: **640** (100%)

**Files Checked:**
- `scripts/410_dentist.json` - 320 questions
- `scripts/arts_irt.json` - 200 questions
- `scripts/90_questions_combined.json` - 90 questions
- `scripts/160_2.json` - 320 questions
- `scripts/arts_irt_part2.json` - 200 questions

**⚠️ CRITICAL ISSUE:** All questions have `profession: ""` or missing field

---

### 1.3 Route Filtering Implementation

#### ✅ WORKING: `routes/diagnostic_routes.py`
```python
# Line 152-169
emergency_question = Question.query.filter_by(profession=user_profession).first()
questions = Question.query.filter_by(profession=user_profession).all()
```

**Status:** Profession filtering is implemented for diagnostic

#### ❌ MISSING: `routes/learning_routes.py`
**Status:** No profession filtering found

#### ❌ MISSING: `routes/test_routes.py`
**Status:** No profession filtering found

#### ❌ MISSING: `routes/irt_spaced_routes.py`
**Status:** No profession filtering found

---

### 1.4 User Profession Statistics

**Expected Values:**
- `tandarts` (dentist)
- `huisarts` (GP)
- `apotheker` (pharmacist)
- `verpleegkundige` (nurse)

**Current State:** Users can set profession on registration, but:
- No enforcement
- No migration needed (field already exists)
- Need to populate existing questions

---

## TASK 2: MEMORY GAME ANALYSIS

### 2.1 Game Location & Files

**Files Found:**
```
routes/games_routes.py
templates/games/memory.html
templates/games/base_game.html
static/js/ (game logic)
```

### 2.2 Current Implementation

**Type:** Medical terminology matching game

**Features:**
- ✅ Flip animations (CSS 3D transforms)
- ✅ Match detection
- ✅ Progress tracking
- ✅ Mobile responsive
- ✅ Game statistics display

**Content Source:** Hardcoded in template (Dutch terms)

**Example Card:**
```html
<div class="memory-card">
  <div class="card-front">?</div>
  <div class="card-back">Caries</div>
</div>
```

### 2.3 Integration

**Accessible from:**
- Learning Map (Games tab)
- Direct URL: `/games/memory`

**Gamification:**
- ❌ No XP rewards
- ❌ No progress saving
- ❌ No achievements
- ❌ No streaks

**Spaced Repetition:**
- ❌ Not integrated

---

## TASK 3: FLASHCARDS & MEDICAL TERMS

### 3.1 Database Models

**Current State:**
- ❌ No `Flashcard` model
- ❌ No `MedicalTerm` model
- ❌ No `Translation` model
- ❌ No `UserTermProgress` model

### 3.2 Cards Directory Structure

**Found:** `cards/` directory with 10 folders:
```
cards/
├── anatomy/
├── bit_exam/
├── caries/
├── endodontic/
├── Methodology/
├── pediatric/
├── periodontic/
├── saliva/
├── statistics/
└── virtual_patient/
```

**Content:**
- Total flashcards: ~678
- Format: JSON files
- Structure: `{question: "", answer: "", category: ""}`

**Files:**
- `learning_cards.json`
- `medium_priority_cards.json`
- `high_priority_cards.json`

### 3.3 Flashcard System

**Current State:**
- ✅ Content exists in `/cards/`
- ❌ No routes to serve flashcards
- ❌ No UI component
- ❌ No flip animations
- ❌ No spaced repetition

**Access:** Cards are not accessible in current application

---

## TASK 4: LANGUAGE SUPPORT

### 4.1 Translation System

**Translation Files:**
```
translations/
├── en.py
├── nl.py (Dutch - primary)
├── ru.py
├── uk.py
├── es.py
├── pt.py
├── tr.py
├── fa.py
└── domain_diagnostic_translations.py
```

**Status:** ✅ 10 languages supported

### 4.2 Medical Terms Translation

**Current State:**
- ❌ No medical terminology translations
- ❌ No multi-language medical terms database
- ⚠️ Memory game has hardcoded Dutch terms only

---

## TASK 5: INTEGRATION POINTS

### 5.1 Individual Plan Tab

**Current State:**
- Games tab exists in Learning Map
- Memory game link present
- No flashcards link
- No vocabulary exercises

### 5.2 Daily Session Structure

**Current Structure:**
1. Questions (practice)
2. Diagnostic (assessment)
3. Games (entertainment)

**Missing:**
- Vocabulary learning
- Flashcard reviews
- Term matching exercises

### 5.3 Gamification

**Existing:**
- Level system (User.level)
- XP system (User.xp)
- Streaks (UserStreak model)

**Missing:**
- XP for games
- XP for flashcards
- Achievements for language learning
- Daily language challenges

---

## PRIORITY ACTION ITEMS

### 🔴 HIGH PRIORITY (Do First)

1. **Assign Profession to Questions** (4-6 hours)
   - Update all 640 questions in JSON files
   - Set profession based on filename/content
   - Run import script to populate DB

2. **Add Profession Filtering to All Routes** (2-3 hours)
   - `routes/learning_routes.py`
   - `routes/test_routes.py`
   - `routes/irt_spaced_routes.py`
   - Use consistent filtering logic

3. **Create Flashcard Routes** (3-4 hours)
   - New route: `/flashcards`
   - Serve cards from `/cards/` directory
   - Add to Individual Plan tab

### 🟡 MEDIUM PRIORITY (Next Sprint)

4. **Create Flashcard DB Model** (2-3 hours)
   - `Flashcard` model
   - `UserFlashcardProgress` model
   - Migration script

5. **Integrate Spaced Repetition for Flashcards** (4-6 hours)
   - Calculate next review date
   - Track difficulty
   - Schedule reviews

6. **Add Gamification to Games** (2-3 hours)
   - XP rewards for memory game
   - Progress tracking
   - Achievements

### 🟢 LOW PRIORITY (Nice to Have)

7. **Create Medical Terms Database** (8-12 hours)
   - Import from cards directory
   - Create `MedicalTerm` model
   - Add translations

8. **Language Learning Dashboard** (6-8 hours)
   - Progress tracking
   - Term mastery visualization
   - Daily goals

---

## EFFORT ESTIMATES

| Task | Hours | Priority |
|------|-------|----------|
| Assign professions to questions | 4-6 | 🔴 HIGH |
| Add profession filtering | 2-3 | 🔴 HIGH |
| Create flashcard routes | 3-4 | 🔴 HIGH |
| Flashcard DB model | 2-3 | 🟡 MEDIUM |
| SR integration flashcards | 4-6 | 🟡 MEDIUM |
| Game gamification | 2-3 | �� MEDIUM |
| Medical terms DB | 8-12 | 🟢 LOW |
| Language dashboard | 6-8 | 🟢 LOW |

**Total High Priority:** 9-13 hours  
**Total All Features:** 31-45 hours

---

## RECOMMENDED QUICK WINS

1. **Fix Question Profession Assignment** (4 hours)
   - Biggest impact
   - Enables filtering
   - Easy to implement

2. **Add Flashcard Route** (3 hours)
   - Use existing `/cards/` content
   - No DB changes needed
   - Immediate value

3. **Add XP to Memory Game** (1 hour)
   - Small code change
   - Improves engagement
   - Uses existing XP system

---

## FILES TO REVIEW

**High Priority:**
- `models.py` (lines 66-73, 1287-1290) - User & Question profession
- `routes/diagnostic_routes.py` (lines 152-169) - Working filter example
- `scripts/*.json` - All question files need profession values

**Medium Priority:**
- `cards/` directory - Existing flashcard content
- `templates/games/memory.html` - Working game UI
- `routes/games_routes.py` - Game routes

**Low Priority:**
- `translations/` - Language system
- `utils/irt_engine.py` - Question selection logic

---

## CONCLUSION

**Current State:** Profession filtering infrastructure exists but is not fully utilized. Memory game works well but lacks gamification. Flashcard content exists but is not accessible. Language learning features are missing.

**Recommended Approach:** Start with high-priority fixes (profession assignment + filtering), then add flashcard routes. This provides immediate value with minimal effort.

