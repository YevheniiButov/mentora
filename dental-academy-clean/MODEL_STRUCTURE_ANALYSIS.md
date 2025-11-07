# 📋 Model Structure Analysis - Where Are the Flashcard Models?

## Summary

✅ **Models ARE correctly placed and should work**

- ✅ `MedicalTerm` class is in `models.py` (line 6134)
- ✅ `UserTermProgress` class is in `models.py` (line 6188)
- ✅ Import in `routes/flashcard_routes.py` is CORRECT: `from models import MedicalTerm, UserTermProgress, db`

---

## Directory Structure

```
Project Root/
├── models.py                           ✅ Main models file (6283 lines)
│   ├── ... (other models)
│   ├── class MedicalTerm               ✅ LINE 6134
│   └── class UserTermProgress          ✅ LINE 6188
│
├── models/                             ⚠️ Separate directory (created in Phase 1)
│   └── medical_terms.py                (Duplicate/backup copy of models)
│       ├── class MedicalTerm
│       └── class UserTermProgress
│
├── routes/flashcard_routes.py          ✅ Correct import
│   └── from models import MedicalTerm, UserTermProgress
│
└── utils/flashcard_helpers.py          ✅ Correct import
    └── from models import MedicalTerm, UserTermProgress
```

---

## File Locations

### Main File: `models.py`

| Class | Start Line | End Line | Status |
|-------|-----------|----------|--------|
| `MedicalTerm` | 6134 | 6186 | ✅ Complete |
| `UserTermProgress` | 6188 | 6283 | ✅ Complete |

**Key Methods:**
- `UserTermProgress.update_progress_sm2(quality)` - SM-2 algorithm
- `UserTermProgress.accuracy_rate` - Property for calculation
- `UserTermProgress.is_due` - Property for review check

### Alternate File: `models/medical_terms.py`

This is a DUPLICATE/BACKUP of the same models. It exists but is NOT used by the routes.

**Status:** ⚠️ Redundant file (can be deleted)

---

## Import Verification

### In `routes/flashcard_routes.py` (Line 18)
```python
from models import MedicalTerm, UserTermProgress, db
```
✅ **CORRECT** - This will work

### In `utils/flashcard_helpers.py` (Line 7)
```python
from models import MedicalTerm, UserTermProgress, db
```
✅ **CORRECT** - This will work

---

## Why This Works

Flask automatically includes the project root in `sys.path`, so:

1. `from models import X` → looks for `models.py` or `models/__init__.py`
2. Finds `models.py` (272KB file)
3. Loads the classes from it
4. **WORKS** ✅

---

## What Could Go Wrong

### ❌ If imports were like this:
```python
from models.medical_terms import MedicalTerm  # WRONG - models/ has no __init__.py
```

### ⚠️ Current setup works because:
- `models.py` exists as a module
- Both classes are IN `models.py`
- No package structure needed
- Direct imports work fine

---

## Verification Check

To verify the models are accessible:

```python
# This should work:
from models import MedicalTerm, UserTermProgress

# Create instances:
term = MedicalTerm(term_nl="het hart", term_en="heart", category="anatomy")
progress = UserTermProgress(user_id=1, term_id=1)

# Use methods:
progress.update_progress_sm2(5)  # Should work
print(progress.is_due)  # Should work
print(progress.accuracy_rate)  # Should work
```

---

## Redundant Files to Clean Up

### ⚠️ `models/medical_terms.py`

This file exists but is NOT used because:
1. Routes import from `models`, not `models.medical_terms`
2. Flask finds `models.py` first
3. The duplicate causes confusion

**Action:** Can be deleted (backup exists)

---

## Database Tables

Once deployed, these tables will be created:

```sql
CREATE TABLE medical_term (
    id INTEGER PRIMARY KEY,
    term_nl VARCHAR(200) UNIQUE NOT NULL,
    definition_nl TEXT,
    term_en VARCHAR(200),
    term_ru VARCHAR(200),
    term_uk VARCHAR(200),
    term_es VARCHAR(200),
    term_pt VARCHAR(200),
    term_tr VARCHAR(200),
    term_fa VARCHAR(200),
    term_ar VARCHAR(200),
    category VARCHAR(50) NOT NULL,
    difficulty INTEGER DEFAULT 1,
    frequency INTEGER DEFAULT 1,
    audio_url VARCHAR(500),
    created_at DATETIME,
    updated_at DATETIME,
    INDEX(term_nl),
    INDEX(category)
);

CREATE TABLE user_term_progress (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    term_id INTEGER NOT NULL,
    ease_factor FLOAT DEFAULT 2.5,
    interval INTEGER DEFAULT 1,
    repetitions INTEGER DEFAULT 0,
    next_review DATETIME NOT NULL,
    times_reviewed INTEGER DEFAULT 0,
    times_correct INTEGER DEFAULT 0,
    mastery_level INTEGER DEFAULT 0,
    last_quality INTEGER,
    last_reviewed DATETIME,
    created_at DATETIME,
    UNIQUE(user_id, term_id),
    INDEX(user_id, next_review),
    FOREIGN KEY(user_id) REFERENCES user(id),
    FOREIGN KEY(term_id) REFERENCES medical_term(id)
);
```

---

## Deployment Readiness

### ✅ Models are properly structured
### ✅ Imports are correct
### ✅ Database relationships defined
### ⚠️ Redundant `models/medical_terms.py` should be removed (optional)

---

## Summary

**Everything is correctly set up.** The models will work as-is:

1. ✅ Models in `models.py` at end of file
2. ✅ Routes import from `models` correctly
3. ✅ No __init__.py needed (models.py is not a package)
4. ✅ All methods implemented (SM-2 algorithm, properties, etc.)
5. ⚠️ Redundant file exists but doesn't break anything

**Action required:** None - System is ready to test
**Optional cleanup:** Delete `models/medical_terms.py`

