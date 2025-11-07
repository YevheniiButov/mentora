# 🌍 Multilingual Support for Medical Flashcards

## Supported Languages

The flashcard system now supports **8 languages**:

| Code | Language | Script | Status |
|------|----------|--------|--------|
| en | English | Latin | ✅ Base (Fallback) |
| uk | Ukrainian | Cyrillic | ✅ Complete |
| ru | Russian | Cyrillic | ✅ Complete |
| es | Spanish | Latin | ✅ Complete |
| pt | Portuguese | Latin | ✅ Complete |
| tr | Turkish | Latin | ✅ Complete |
| fa | Farsi (Persian) | Arabic | ✅ Complete |
| ar | Arabic | Arabic | ✅ Complete |

## How It Works

### 1. User Language Setting
User sets their language in application settings:
- Profile page: Select from dropdown
- Stored in `user.language` field in database

### 2. Flashcard Translation System
When displaying a term:

```python
# In routes/flashcard_routes.py
user_lang = current_user.language or 'en'
term_translated = getattr(term, f'term_{user_lang}', None) or term.term_en
```

### 3. Display Logic
- **Exact match found**: Shows translation in user's language ✓
- **Translation missing**: Falls back to English ✓
- **User language not set**: Defaults to English ✓

## Database Schema

Each term has 8 translation columns:

```python
class MedicalTerm(db.Model):
    term_en = db.Column(db.String(200))  # English (base)
    term_uk = db.Column(db.String(200))  # Ukrainian
    term_ru = db.Column(db.String(200))  # Russian
    term_es = db.Column(db.String(200))  # Spanish
    term_pt = db.Column(db.String(200))  # Portuguese
    term_tr = db.Column(db.String(200))  # Turkish
    term_fa = db.Column(db.String(200))  # Farsi
    term_ar = db.Column(db.String(200))  # Arabic
```

## Translation Coverage

**50 core medical terms** translated to all 8 languages:

### Anatomy (10 terms)
- Heart, Lung, Stomach, Liver, Kidney, Brain, Throat, Blood Vessel, Muscle, Bone

### Symptoms (10 terms)
- Pain, Fever, Cough, Diarrhea, Nausea, Headache, Fatigue, Vomiting, Dizziness, Shortness of Breath

### Diseases (10 terms)
- Flu, Diabetes, Cancer, Hypertension, Pneumonia, Eczema, Asthma, Arthritis, Stroke, Heart Attack

### Treatments (10 terms)
- Treatment, Medicine, Pill, Injection, Operation, Antibiotic, Ointment, Physical Therapy, Radiotherapy, Surgery

### Dental (10 terms)
- Tooth, Molar, Incisor, Gum, Cavity, Periodontitis, Toothbrush, Toothpaste, Filling, Crown

**Total: 50 × 8 languages = 400 translations**

## Example Term: "Pain"

| Language | Translation |
|----------|-------------|
| English | pain |
| Ukrainian | біль |
| Russian | боль |
| Spanish | dolor |
| Portuguese | dor |
| Turkish | ağrı |
| Farsi | درد |
| Arabic | الألم |

## Adding New Translations

To add a new language or expand translations:

1. **Add column to MedicalTerm model:**
   ```python
   term_xx = db.Column(db.String(200), nullable=True)
   ```

2. **Create migration:**
   ```bash
   flask db migrate -m "Add term_xx translations"
   flask db upgrade
   ```

3. **Create seed script or update terms:**
   ```python
   term = MedicalTerm.query.filter_by(term_nl='example').first()
   term.term_xx = 'translation'
   db.session.commit()
   ```

## Testing Multilingual Support

1. **Set user language to Ukrainian:**
   - Go to profile settings
   - Select "Українська"
   - Save

2. **Open flashcards:**
   - Navigate to `/flashcards/study/dental`
   - Terms now display in Ukrainian:
     - зуб (tooth)
     - коренний зуб (molar)
     - карієс (cavity)

3. **Switch language:**
   - Change language in profile
   - Refresh page
   - Terms update to new language

## Future Improvements

- [ ] Add more medical terms (100+)
- [ ] Add translations for all categories
- [ ] Support for additional languages
- [ ] RTL (Right-to-Left) support for Arabic/Farsi
- [ ] Language-specific sorting/collation

## Performance Notes

- Translations stored in same table (no extra queries)
- Fallback to English is fast (simple `or` operation)
- No caching needed (direct column access)

## Accessibility

- All terms have English fallback
- Supports multiple scripts (Latin, Cyrillic, Arabic)
- RTL languages partially supported

---

**Last Updated**: October 27, 2025
**Maintenance**: Keep translations aligned with base terms (English)
