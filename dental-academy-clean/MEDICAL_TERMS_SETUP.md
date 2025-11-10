# Medical Terms Flashcard System - Phase 1 Setup Guide

## 🚀 Quick Start

### What's New (Phase 1)

✅ **3 new files created:**
1. `models/medical_terms.py` - Database models (MedicalTerm, UserTermProgress)
2. `migrations/add_medical_terms_models.sql` - SQL migration
3. `scripts/medical_terms_seed.py` - Seed data with 50 basic terms

✅ **Key features:**
- SM-2 spaced repetition algorithm
- 8 language support (EN, RU, UK, ES, PT, TR, FA, AR)
- Per-user mastery tracking
- Efficient database indexes

---

## 📋 Installation Steps

### Step 1: Verify Files Were Created

```bash
# Check files exist
ls -la models/medical_terms.py
ls -la migrations/add_medical_terms_models.sql
ls -la scripts/medical_terms_seed.py
```

### Step 2: Create Database Tables

**Choose ONE option:**

#### Option A: Using Flask-SQLAlchemy (Recommended for Flask app)

```bash
# Generate migration from Python models
cd your-project
flask db migrate -m "Add medical terminology flashcard system"

# Review what was generated
cat migrations/versions/*_add_medical_terminology_flashcard_system.py

# Apply migration
flask db upgrade
```

#### Option B: Direct SQL (SQLite)

```bash
# For local SQLite database
sqlite3 instance/your_database.db < migrations/add_medical_terms_models.sql
```

#### Option C: Direct SQL (PostgreSQL on Render)

```bash
# Via psql (Render Shell)
psql $DATABASE_URL < migrations/add_medical_terms_models.sql
```

### Step 3: Seed Data (50 Basic Terms)

```bash
# Run seed script
python scripts/medical_terms_seed.py

# Expected output:
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

### Step 4: Verify Installation

```python
# Open Python shell
python

# In Python:
from app import create_app
from models.medical_terms import MedicalTerm, UserTermProgress

app = create_app()
with app.app_context():
    # Check tables
    term_count = MedicalTerm.query.count()
    progress_count = UserTermProgress.query.count()
    
    print(f"✅ Medical Terms: {term_count}")
    print(f"✅ User Progress Records: {progress_count}")
    
    # List categories
    terms = MedicalTerm.query.all()
    categories = {}
    for term in terms:
        categories[term.category] = categories.get(term.category, 0) + 1
    
    print(f"✅ Categories: {categories}")
    
    # Show sample term
    sample = MedicalTerm.query.first()
    print(f"✅ Sample: {sample.term_nl} = {sample.term_en}")
```

Expected output:
```
✅ Medical Terms: 50
✅ User Progress Records: 0
✅ Categories: {'anatomy': 10, 'symptoms': 10, 'diseases': 10, 'treatments': 10, 'dental': 10}
✅ Sample: het hart = heart
```

---

## 📚 Model Overview

### MedicalTerm
Dictionary of medical terms with translations to 8 languages

**Key fields:**
- `term_nl`: Dutch term (unique, indexed)
- `term_en`, `term_ru`, `term_uk`, etc.: Translations
- `category`: anatomy, symptoms, diseases, treatments, dental
- `difficulty`: 1-5 scale
- `frequency`: 1-5 scale (how common)

**Usage:**
```python
term = MedicalTerm.query.filter_by(term_nl='het hart').first()
print(f"Dutch: {term.term_nl}")
print(f"English: {term.term_en}")
print(f"Category: {term.category}")
```

### UserTermProgress
Tracks each user's spaced repetition progress for each term

**Key fields:**
- `user_id`, `term_id`: Foreign keys
- `ease_factor`: SM-2 difficulty factor (1.3-2.6)
- `interval`: Days until next review
- `repetitions`: Number of successful reviews
- `next_review`: When to show this term next
- `times_reviewed`, `times_correct`: Statistics
- `mastery_level`: 0-5 (novice to master)

**Key methods:**
```python
# Get user's progress for a term
progress = UserTermProgress.query.filter_by(
    user_id=user_id,
    term_id=term_id
).first()

# Check if term is due for review
if progress.is_due:
    # Show this term to user
    pass

# Record user's answer (quality 1-5)
progress.update_progress_sm2(quality=5)  # Perfect answer
db.session.commit()

# Export as JSON
data = progress.to_dict()
```

---

## 🔄 Spaced Repetition Algorithm (SM-2)

The system implements the SuperMemo 2 algorithm:

**When user answers correctly (quality >= 3):**
- Increase ease_factor by 0.1
- Increase repetitions
- Calculate next interval based on repetitions:
  - 1st success: review in 1 day
  - 2nd success: review in 3 days
  - 3rd+ success: review_days = previous_interval × ease_factor
- Update mastery_level if accuracy >= 90%

**When user answers incorrectly (quality < 3):**
- Reset repetitions to 0
- Decrease ease_factor by 0.2 (min 1.3)
- Set interval to 1 (review tomorrow)

---

## 📁 File Structure

```
project/
├── models/
│   └── medical_terms.py              # ✨ NEW: Database models
│       ├── MedicalTerm               # Medical term dictionary
│       └── UserTermProgress          # User's SR progress
│
├── migrations/
│   ├── add_medical_terms_models.sql  # ✨ NEW: SQL migration
│   └── versions/
│       └── ...existing migrations
│
├── scripts/
│   ├── medical_terms_seed.py         # ✨ NEW: Seed data
│   └── ...other scripts
│
├── docs/
│   └── MEDICAL_TERMS_PHASE1.md       # ✨ NEW: Detailed docs
│
├── MEDICAL_TERMS_SETUP.md            # ✨ NEW: This file
├── app.py                            # Your Flask app
└── extensions.py                     # Database setup (db, etc.)
```

---

## ✅ Validation Checklist

Before using the system, verify:

- [ ] Models file created: `models/medical_terms.py`
- [ ] Migration file created: `migrations/add_medical_terms_models.sql`
- [ ] Seed file created: `scripts/medical_terms_seed.py`
- [ ] Database tables created (run migration)
- [ ] Seed data loaded (50 terms in database)
- [ ] Can query MedicalTerm and UserTermProgress
- [ ] Sample query returns correct data
- [ ] SM-2 algorithm methods work

---

## 🐛 Troubleshooting

### "No module named 'models.medical_terms'"

**Solution:**
```python
# Make sure models/ has __init__.py
touch models/__init__.py

# Or import directly from file
from models.medical_terms import MedicalTerm, UserTermProgress
```

### "Column does not exist" error

**Solution:**
- Make sure migration was run: `flask db upgrade`
- Check database: `sqlite3 your.db ".tables"` (SQLite)
- Check: `\dt` in psql (PostgreSQL)

### Seed script doesn't run

**Solution:**
```bash
# Make script executable
chmod +x scripts/medical_terms_seed.py

# Run with explicit Python
python scripts/medical_terms_seed.py

# Check for import errors
python -c "from models.medical_terms import MedicalTerm"
```

### "Foreign key constraint failed"

**Solution:**
- Ensure User table exists before loading seed data
- Seed script only creates MedicalTerm, not UserTermProgress relationships

---

## 🔗 Integration Points (Phase 2+)

These will be implemented in future phases:

**API Endpoints:**
- `GET /api/medical-terms/due` - Get terms due for review
- `POST /api/medical-terms/answer` - Submit answer
- `GET /api/medical-terms/progress` - Get user progress

**Frontend UI:**
- Flashcard component
- Study session interface
- Progress dashboard

---

## 📞 Support

For detailed information, see:
- `docs/MEDICAL_TERMS_PHASE1.md` - Full documentation
- `models/medical_terms.py` - Code with comments
- `scripts/medical_terms_seed.py` - Seed implementation

---

## 🎯 Next Steps

1. ✅ Follow setup steps above
2. ✅ Verify installation
3. ✅ (Optional) Add more terms to seed
4. 🔲 Phase 2: Create API endpoints
5. 🔲 Phase 3: Build frontend UI
6. 🔲 Phase 4: Advanced features (audio, hints, etc.)

---

**Phase 1 Status**: ✅ Complete  
**Created**: 2025-10-27  
**Database**: SQLite (local) or PostgreSQL (production)






