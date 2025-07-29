const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const DomainSchema = new Schema({
  // Основные поля
  code: { 
    type: String, 
    required: true, 
    unique: true,
    enum: [
      // Все 30 доменов из domains_config.json
      'PHARMACOLOGY', 'THERAPEUTIC_DENTISTRY', 'SURGICAL_DENTISTRY',
      'PROSTHODONTICS', 'PEDIATRIC_DENTISTRY', 'PERIODONTOLOGY',
      'ORTHODONTICS', 'PREVENTIVE_DENTISTRY', 'ANATOMY',
      'PHYSIOLOGY', 'PATHOLOGY', 'RADIOLOGY', 'MICROBIOLOGY',
      'MATERIALS_SCIENCE', 'GENERAL_MEDICINE', 'EMERGENCY_MEDICINE',
      'SYSTEMIC_DISEASES', 'INFECTIOUS_DISEASES', 'SPECIAL_CASES',
      'DUTCH_DENTISTRY', 'DIAGNOSTICS', 'ETHICS_NL',
      'PROFESSIONAL_ETHICS', 'STATISTICS', 'RESEARCH_METHOD',
      'TREATMENT_PLANNING', 'COMMUNICATION', 'PRACTICAL_THEORY',
      'SPECIAL_DIAGNOSTICS', 'CLINICAL_SKILLS', 'PATIENT_MANAGEMENT'
    ]
  },
  
  // Многоязычные названия
  name: { type: String, required: true },
  name_en: { type: String, required: true },
  name_nl: { type: String, required: true },
  name_ru: { type: String },
  
  // Метаданные
  weight: { type: Number, required: true, min: 0, max: 20 },
  category: { 
    type: String, 
    enum: ['THEORETICAL', 'METHODOLOGY', 'PRACTICAL', 'CLINICAL'],
    required: true 
  },
  exam_type: {
    type: String,
    enum: ['multiple_choice', 'open_book', 'case_study', 'interview_case'],
    required: true
  },
  is_critical: { type: Boolean, default: false },
  
  // IRT статистика
  question_count: { type: Number, required: true },
  avg_difficulty: { type: Number, min: 0, max: 2 },
  avg_discrimination: { type: Number, min: 1, max: 3 },
  
  // Связи
  irt_questions: [{ type: Schema.Types.ObjectId, ref: 'IRTQuestion' }],
  learning_cards: [{ type: Schema.Types.ObjectId, ref: 'LearningCard' }],
  
  // Метаинформация  
  created_from: [String], // ['PHARMA', 'FARMACOLOGIE'] для объединенных
  migration_notes: String,
  last_updated: { type: Date, default: Date.now }
});

// Индексы для оптимизации
DomainSchema.index({ code: 1 });
DomainSchema.index({ category: 1 });
DomainSchema.index({ is_critical: 1 });
DomainSchema.index({ weight: -1 });

// Виртуальные поля
DomainSchema.virtual('difficulty_distribution').get(function() {
  if (this.avg_difficulty < 0.7) return 'easy';
  if (this.avg_difficulty < 1.3) return 'medium';
  return 'hard';
});

DomainSchema.virtual('bi_toets_weight').get(function() {
  // Вес в процентах для BI-toets
  return Math.round((this.weight / 100) * 100);
});

// Методы
DomainSchema.methods.getQuestionsByDifficulty = function(difficulty) {
  return this.model('IRTQuestion').find({
    domain: this.code,
    'irt_params.difficulty': {
      $gte: difficulty - 0.2,
      $lte: difficulty + 0.2
    }
  });
};

DomainSchema.methods.calculateDomainAbility = function(userAnswers) {
  // Расчет способности пользователя в данном домене
  const domainAnswers = userAnswers.filter(a => a.domain === this.code);
  if (domainAnswers.length === 0) return { ability: 0, confidence: 1.0 };
  
  let totalAbility = 0;
  let totalWeight = 0;
  
  domainAnswers.forEach(answer => {
    const question = answer.question;
    const weight = 1 / (1 + answer.response_time / 60); // Вес на основе времени ответа
    totalAbility += answer.ability_after * weight;
    totalWeight += weight;
  });
  
  return {
    ability: totalWeight > 0 ? totalAbility / totalWeight : 0,
    confidence: Math.min(1.0, 1 / Math.sqrt(domainAnswers.length))
  };
};

// Статические методы
DomainSchema.statics.getCriticalDomains = function() {
  return this.find({ is_critical: true }).sort({ weight: -1 });
};

DomainSchema.statics.getDomainsByCategory = function(category) {
  return this.find({ category }).sort({ weight: -1 });
};

DomainSchema.statics.getDomainDistribution = function() {
  return this.aggregate([
    {
      $group: {
        _id: '$category',
        domains: { $push: '$$ROOT' },
        total_weight: { $sum: '$weight' },
        avg_difficulty: { $avg: '$avg_difficulty' }
      }
    },
    {
      $project: {
        category: '$_id',
        domains: 1,
        total_weight: 1,
        avg_difficulty: 1,
        domain_count: { $size: '$domains' }
      }
    }
  ]);
};

module.exports = mongoose.model('Domain', DomainSchema); 