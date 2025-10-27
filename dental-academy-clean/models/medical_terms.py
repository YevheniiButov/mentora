# ========================================
# MEDICAL TERMINOLOGY FLASHCARD SYSTEM
# ========================================

from extensions import db
from datetime import datetime, timezone, timedelta


class MedicalTerm(db.Model):
    """
    Dutch medical term with translations to 8 languages.
    Used for the medical terminology flashcard system.
    """
    __tablename__ = 'medical_term'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Dutch term (source language) - required
    term_nl = db.Column(db.String(200), nullable=False, index=True, unique=True)
    definition_nl = db.Column(db.Text, nullable=True)
    
    # Translations to 8 languages
    term_en = db.Column(db.String(200), nullable=True)  # English
    term_ru = db.Column(db.String(200), nullable=True)  # Russian
    term_uk = db.Column(db.String(200), nullable=True)  # Ukrainian
    term_es = db.Column(db.String(200), nullable=True)  # Spanish
    term_pt = db.Column(db.String(200), nullable=True)  # Portuguese
    term_tr = db.Column(db.String(200), nullable=True)  # Turkish
    term_fa = db.Column(db.String(200), nullable=True)  # Farsi/Persian
    term_ar = db.Column(db.String(200), nullable=True)  # Arabic
    
    # Metadata
    category = db.Column(db.String(50), nullable=False, index=True)  # anatomy, symptoms, diseases, treatments, dental, hospital, communication
    difficulty = db.Column(db.Integer, default=1)  # 1-5 scale
    frequency = db.Column(db.Integer, default=1)  # 1-5 scale (how common)
    
    # Optional audio for pronunciation
    audio_url = db.Column(db.String(500), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user_progress = db.relationship('UserTermProgress', backref='term', cascade='all, delete-orphan', lazy='select')
    
    def __repr__(self):
        return f'<MedicalTerm {self.term_nl}>'
    
    def to_dict(self, lang='en'):
        """Return term translation for specified language"""
        lang_field = f'term_{lang}'
        return {
            'id': self.id,
            'term_nl': self.term_nl,
            'term': getattr(self, lang_field, self.term_en) or self.term_en,
            'definition': self.definition_nl,
            'category': self.category,
            'difficulty': self.difficulty,
            'frequency': self.frequency,
            'audio_url': self.audio_url
        }


class UserTermProgress(db.Model):
    """
    Spaced Repetition progress for individual medical terms.
    Tracks when each user should review each term and their mastery level.
    """
    __tablename__ = 'user_term_progress'
    
    # Primary key & Foreign keys
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    term_id = db.Column(db.Integer, db.ForeignKey('medical_term.id'), nullable=False, index=True)
    
    # SM-2 Spaced Repetition Algorithm parameters
    ease_factor = db.Column(db.Float, default=2.5)  # Start at 2.5, ranges 1.3-2.6
    interval = db.Column(db.Integer, default=1)  # Days until next review
    repetitions = db.Column(db.Integer, default=0)  # Number of successful reviews
    next_review = db.Column(db.DateTime, nullable=False, index=True, default=lambda: datetime.now(timezone.utc))  # When to show next
    
    # Statistics
    times_reviewed = db.Column(db.Integer, default=0)  # Total review attempts
    times_correct = db.Column(db.Integer, default=0)  # Successful answers
    mastery_level = db.Column(db.Integer, default=0)  # 0-5 scale (0=novice, 5=master)
    
    # Response quality from user (1-5 scale used in SM-2)
    last_quality = db.Column(db.Integer, nullable=True)  # Quality of last response (1-5)
    
    # Timestamps
    last_reviewed = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Composite indexes for efficient queries
    __table_args__ = (
        db.Index('ix_user_term_progress_user_next_review', 'user_id', 'next_review'),
        db.Index('ix_user_term_progress_user_term', 'user_id', 'term_id', unique=True),
    )
    
    # Relationships
    user = db.relationship('User', backref='term_progress')
    
    def __repr__(self):
        return f'<UserTermProgress user={self.user_id} term={self.term_id} mastery={self.mastery_level}>'
    
    @property
    def accuracy_rate(self):
        """Calculate accuracy rate as percentage"""
        if self.times_reviewed == 0:
            return 0.0
        return (self.times_correct / self.times_reviewed) * 100
    
    @property
    def is_due(self):
        """Check if this term is due for review"""
        return datetime.now(timezone.utc) >= self.next_review
    
    def update_progress_sm2(self, quality: int):
        """
        Update progress using SM-2 algorithm.
        
        Args:
            quality: User's response quality (1-5)
                     1-2: Failed (will repeat)
                     3-4: Borderline (will repeat sooner)
                     5: Perfect (will show later)
        """
        self.times_reviewed += 1
        self.last_quality = quality
        self.last_reviewed = datetime.now(timezone.utc)
        
        if quality >= 3:  # Correct answer
            self.times_correct += 1
            self.repetitions += 1
            
            # SM-2 algorithm: update ease factor
            self.ease_factor = max(1.3, self.ease_factor + 0.1 - (5 - quality) * 0.08)
            
            # Calculate next interval
            if self.repetitions == 1:
                self.interval = 1
            elif self.repetitions == 2:
                self.interval = 3
            else:
                self.interval = int(self.interval * self.ease_factor)
            
            # Update mastery level
            correct_rate = self.accuracy_rate
            if correct_rate >= 90:
                self.mastery_level = min(5, self.mastery_level + 1)
        else:
            # Failed: reset and repeat sooner
            self.repetitions = 0
            self.ease_factor = max(1.3, self.ease_factor - 0.2)
            self.interval = 1
        
        # Set next review date
        self.next_review = datetime.now(timezone.utc) + timedelta(days=self.interval)
    
    def to_dict(self):
        """Serialize to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'term_id': self.term_id,
            'ease_factor': round(self.ease_factor, 2),
            'interval': self.interval,
            'repetitions': self.repetitions,
            'next_review': self.next_review.isoformat(),
            'times_reviewed': self.times_reviewed,
            'times_correct': self.times_correct,
            'accuracy_rate': round(self.accuracy_rate, 1),
            'mastery_level': self.mastery_level,
            'is_due': self.is_due,
            'last_reviewed': self.last_reviewed.isoformat() if self.last_reviewed else None
        }
