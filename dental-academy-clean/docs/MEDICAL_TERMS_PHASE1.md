# Medical Terminology Flashcard System - Phase 1 Documentation

## Overview

This document describes **Phase 1** of the medical terminology flashcard system for the Mentora Flask application. This phase focuses on database models, migrations, and seed data.

---

## Architecture

### System Goals
- **Dutch Medical Terms**: Learn Dutch medical terminology with translations to 8 languages
- **Spaced Repetition**: SM-2 algorithm for optimized learning
- **Multilingual Support**: Support for EN, RU, UK, ES, PT, TR, FA, AR
- **Progress Tracking**: Per-user mastery levels and learning statistics

### Key Components

```
┌─────────────────────────────────────────┐
│  Medical Term Flashcard System          │
├─────────────────────────────────────────┤
│ Phase 1: Database & Models              │
│  - MedicalTerm (Dictionary)             │
│  - UserTermProgress (SR Tracking)       │
│  - Seed Data (50 basic terms)           │
├─────────────────────────────────────────┤
│ Phase 2: API Endpoints (Coming soon)    │
│  - Get due terms                        │
│  - Submit answer                        │
│  - Get progress                         │
├─────────────────────────────────────────┤
│ Phase 3: Frontend UI (Coming soon)      │
│  - Flashcard interface                  │
│  - Study statistics                     │
│  - Progress charts                      │
└─────────────────────────────────────────┘
```

---

## Phase 1: Database Models

### 1. MedicalTerm Model

**Purpose**: Dictionary of medical terms with translations to 8 languages

**Location**: `models/medical_terms.py`

**Fields**:
```python
class MedicalTerm(db.Model):
    id                      # Primary key
    term_nl                 # Dutch term (indexed, unique)
    definition_nl           # Optional Dutch definition
    
    # Translations (8 languages)
    term_en                 # English
    term_ru                 # Russian
    term_uk                 # Ukrainian
    term_es                 # Spanish
    term_pt                 # Portuguese
    term_tr                 # Turkish
    term_fa                 # Farsi/Persian
    term_ar                 # Arabic
    
    # Metadata
    category                # anatomy, symptoms, diseases, etc.
    difficulty              # 1-5 scale
    frequency               # 1-5 scale (how common the term is)
    audio_url               # Optional pronunciation audio
    
    # Timestamps
    created_at
    updated_at
```

**Methods**:
- `to_dict(lang='en')`: Export term with translation for specified language

**Relationships**:
- One MedicalTerm → Many UserTermProgress

**Indexes**:
- `term_nl` (unique)
- `category`

---

### 2. UserTermProgress Model

**Purpose**: Track each user's spaced repetition progress for each term

**Location**: `models/medical_terms.py`

**Fields**:
```python
class UserTermProgress(db.Model):
    id                      # Primary key
    
    # Foreign keys
    user_id                 # Link to User
    term_id                 # Link to MedicalTerm
    
    # SM-2 Algorithm Parameters
    ease_factor             # 1.3-2.6 (default 2.5)
    interval                # Days until next review
    repetitions             # Count of successful reviews
    next_review             # When to show this term next
    
    # Statistics
    times_reviewed          # Total review attempts
    times_correct           # Successful answers
    mastery_level           # 0-5 (novice to master)
    last_quality            # Quality of last response (1-5)
    
    # Timestamps
    last_reviewed
    created_at
```

**Methods**:
- `update_progress_sm2(quality: int)`: Apply SM-2 algorithm
- `to_dict()`: Export progress as JSON
- `is_due` (property): Check if term is due for review
- `accuracy_rate` (property): Calculate accuracy percentage

**SM-2 Algorithm**:
The model implements the SM-2 (SuperMemo 2) spaced repetition algorithm:

```
On correct answer (quality >= 3):
  - Increase ease_factor
  - Increase repetitions
  - Calculate next interval based on repetitions
  - Update mastery_level if accuracy >= 90%
  
On incorrect answer (quality < 3):
  - Reset repetitions to 0
  - Decrease ease_factor
  - Set interval to 1 (review tomorrow)
  - Decrease mastery_level
```

**Relationships**:
- Many UserTermProgress → One User
- Many UserTermProgress → One MedicalTerm

**Composite Indexes**:
- `(user_id, term_id)` - unique combination
- `(user_id, next_review)` - for finding due reviews efficiently

---

## Database Migration

### Location
`migrations/add_medical_terms_models.sql`

### What It Creates

```sql
CREATE TABLE medical_term (
    id PRIMARY KEY,
    term_nl VARCHAR(200) UNIQUE NOT NULL,
    definition_nl TEXT,
    
    -- 8 language translations
    term_en, term_ru, term_uk, term_es,
    term_pt, term_tr, term_fa, term_ar VARCHAR(200),
    
    -- Metadata
    category VARCHAR(50) NOT NULL,
    difficulty INTEGER DEFAULT 1,
    frequency INTEGER DEFAULT 1,
    audio_url VARCHAR(500),
    
    created_at, updated_at DATETIME
)

CREATE TABLE user_term_progress (
    id PRIMARY KEY,
    user_id INTEGER NOT NULL FK user(id),
    term_id INTEGER NOT NULL FK medical_term(id),
    
    -- SM-2 parameters
    ease_factor FLOAT DEFAULT 2.5,
    interval INTEGER DEFAULT 1,
    repetitions INTEGER DEFAULT 0,
    next_review DATETIME NOT NULL,
    
    -- Statistics
    times_reviewed INTEGER DEFAULT 0,
    times_correct INTEGER DEFAULT 0,
    mastery_level INTEGER DEFAULT 0,
    last_quality INTEGER,
    
    last_reviewed, created_at DATETIME,
    
    UNIQUE(user_id, term_id)
)
```

### How to Run (Phase 2)

```bash
# Generate Flask migration from models
flask db migrate -m "Add medical terms models"

# Review the migration file
cat migrations/versions/xxxx_add_medical_terms_models.py

# Apply migration
flask db upgrade
```

---

## Seed Data

### Location
`scripts/medical_terms_seed.py`

### Structure

The seed file includes **50 basic medical terms** across **5 categories**:

| Category | Terms | Difficulty | Frequency |
|----------|-------|-----------|-----------|
| Anatomy | 10 | 2 | 5 |
| Symptoms | 10 | 1 | 5 |
| Diseases | 10 | 3 | 4 |
| Treatments | 10 | 3 | 4 |
| Dental | 10 | 2 | 5 |

### Example Terms

**Anatomy**:
- het hart (heart)
- de long (lung)
- de maag (stomach)
- de lever (liver)
- ...

**Symptoms**:
- de pijn (pain)
- de koorts (fever)
- de hoest (cough)
- ...

**Dental** (for tandarts users):
- de tand (tooth)
- de kies (molar)
- het tandvlees (gum)
- ...

### How to Run

```bash
# Run seed locally
python scripts/medical_terms_seed.py

# Output:
# ======================================================================
# 🚀 Medical Terminology Seed - Phase 1
# ======================================================================
# 📚 Importing 50 medical terms...
# ✅ Imported: het hart (heart)
# ✅ Imported: de long (lung)
# ...
# ======================================================================
# ✅ SEED COMPLETED SUCCESSFULLY!
#    📊 Imported: 50 terms
#    ⚠️  Errors: 0
#    📚 Total in database: 50
# ======================================================================
```

---

## File Structure

```
project-root/
├── models/
│   └── medical_terms.py          ✨ NEW (Models)
│
├── migrations/
│   └── add_medical_terms_models.sql  ✨ NEW (Migration SQL)
│
├── scripts/
│   └── medical_terms_seed.py     ✨ NEW (Seed data)
│
├── docs/
│   └── MEDICAL_TERMS_PHASE1.md   ✨ THIS FILE
│
└── app.py (needs update - see below)
```

---

## Setup Instructions

### Step 1: Create Models File

File already created: `models/medical_terms.py`

### Step 2: Update app.py

Add imports in your Flask app initialization:

```python
# In app.py or wherever you initialize the app
from models.medical_terms import MedicalTerm, UserTermProgress

# Make sure these are registered with Flask-SQLAlchemy:
# (they should be automatically if using db.Model)
```

### Step 3: Create Database Tables

Choose one method:

**Option A: Flask-SQLAlchemy Migrations (Recommended)**
```bash
flask db init                    # If first time
flask db migrate -m "Add medical terms"
flask db upgrade
```

**Option B: Direct SQL (SQLite)**
```bash
sqlite3 your_database.db < migrations/add_medical_terms_models.sql
```

**Option C: Direct SQL (PostgreSQL on Render)**
```bash
psql $DATABASE_URL < migrations/add_medical_terms_models.sql
```

### Step 4: Seed Data

```bash
python scripts/medical_terms_seed.py
```

### Step 5: Verify

```python
# In Python shell
from app import create_app
from models.medical_terms import MedicalTerm, UserTermProgress

app = create_app()
with app.app_context():
    print(f"Medical Terms: {MedicalTerm.query.count()}")
    print(f"User Progress: {UserTermProgress.query.count()}")
    
    # List all categories
    terms = MedicalTerm.query.all()
    categories = set(t.category for t in terms)
    print(f"Categories: {categories}")
```

---

## Key Design Decisions

### 1. Spaced Repetition Algorithm
- **Choice**: SM-2 (SuperMemo 2)
- **Why**: Proven effective, simple to implement, well-documented
- **Alternative**: SM-18 (more complex but newer)

### 2. Language Storage
- **Choice**: Direct columns (term_en, term_ru, etc.)
- **Why**: Simple queries, good for small number of languages
- **Alternative**: JSON field (more flexible but slower queries)

### 3. Composite Index (user_id, term_id)
- **Unique constraint**: Ensures one progress record per user-term pair
- **Performance**: Prevents duplicate reviews

### 4. Mastery Levels (0-5)
- **0**: Novice (learning)
- **1-3**: Intermediate
- **4-5**: Master (learned)

### 5. Default Values
- **ease_factor**: 2.5 (SM-2 standard)
- **interval**: 1 day (review tomorrow by default)
- **difficulty/frequency**: 1-5 scale

---

## Testing

### Unit Test Example

```python
def test_medical_term_creation():
    """Test creating a medical term"""
    term = MedicalTerm(
        term_nl='het hart',
        term_en='heart',
        category='anatomy',
        difficulty=2,
        frequency=5
    )
    db.session.add(term)
    db.session.commit()
    
    assert term.id is not None
    assert term.term_nl == 'het hart'
    
def test_sm2_algorithm():
    """Test SM-2 spaced repetition algorithm"""
    progress = UserTermProgress(
        user_id=1,
        term_id=1
    )
    
    # Simulate correct answers
    progress.update_progress_sm2(5)  # Perfect
    assert progress.repetitions == 1
    assert progress.interval >= 1
    
    progress.update_progress_sm2(5)
    assert progress.repetitions == 2
    assert progress.interval == 3  # SM-2 rule: 3 days after 2nd success
    
def test_accuracy_calculation():
    """Test accuracy rate calculation"""
    progress = UserTermProgress(
        user_id=1,
        term_id=1,
        times_reviewed=10,
        times_correct=8
    )
    assert progress.accuracy_rate == 80.0
```

---

## Performance Considerations

### Queries

**Get terms due for review**:
```python
# Efficient: Uses index on (user_id, next_review)
due_terms = UserTermProgress.query.filter(
    UserTermProgress.user_id == user_id,
    UserTermProgress.next_review <= datetime.now()
).all()
```

**Get user's progress for term**:
```python
# Efficient: Uses unique index on (user_id, term_id)
progress = UserTermProgress.query.filter_by(
    user_id=user_id,
    term_id=term_id
).first()
```

### Database Size
- 50 basic terms: ~5 KB
- Per user (1000 users): ~500 KB (if all terms learned)
- Total (1000 users): ~5 MB

---

## Next Steps (Phase 2-3)

### Phase 2: API Endpoints
- `GET /api/medical-terms/due` - Get terms due for review
- `POST /api/medical-terms/answer` - Submit answer
- `GET /api/medical-terms/progress` - Get user progress
- `GET /api/medical-terms/categories` - List categories

### Phase 3: Frontend UI
- Flashcard component (flip animation)
- Study session interface
- Progress statistics dashboard
- Category filtering

### Phase 4: Advanced Features
- Audio pronunciation
- Mnemonic hints
- Learning statistics
- Integration with learning path

---

## Support

For questions or issues:
1. Check this documentation
2. Review model code in `models/medical_terms.py`
3. Check seed data in `scripts/medical_terms_seed.py`
4. Open an issue on GitHub

---

**Status**: ✅ Phase 1 - Database & Models Complete
**Last Updated**: 2025-10-27
**Next Phase**: Phase 2 - API Endpoints (TBD)




