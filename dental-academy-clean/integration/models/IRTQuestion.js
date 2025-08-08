const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const IRTQuestionSchema = new Schema({
  // Основные поля из unified_irt_system.json
  question_id: { type: Number, required: true, unique: true }, // 1-410
  text: { type: String, required: true },
  options: [{ type: String, required: true }], // Exactly 5 options
  correct_answer_index: { type: Number, required: true, min: 0, max: 4 },
  correct_answer_text: { type: String, required: true },
  explanation: { type: String, required: true },
  
  // Классификация
  domain: { 
    type: String, 
    required: true,
    ref: 'Domain'
  },
  category: { type: String, required: true },
  tags: [String],
  difficulty_level: { type: Number, required: true, min: 1, max: 3 },
  
  // IRT параметры
  irt_params: {
    difficulty: { type: Number, required: true, min: 0, max: 2 },
    discrimination: { type: Number, required: true, min: 1, max: 3 },
    guessing: { type: Number, required: true, min: 0.1, max: 0.3 }
  },
  
  // Метаданные
  image_url: String,
  language: { type: String, default: 'nl' },
  source: { type: String, enum: ['original', 'new_domain', 'migrated'] },
  quality_score: Number,
  
  // Статистика использования
  usage_stats: {
    times_presented: { type: Number, default: 0 },
    times_correct: { type: Number, default: 0 },
    avg_response_time: Number,
    last_used: Date
  },
  
  // Связи
  domain_ref: { type: Schema.Types.ObjectId, ref: 'Domain' },
  
  // Метаинформация
  created_at: { type: Date, default: Date.now },
  updated_at: { type: Date, default: Date.now }
});

// Индексы для оптимизации
IRTQuestionSchema.index({ question_id: 1 });
IRTQuestionSchema.index({ domain: 1 });
IRTQuestionSchema.index({ difficulty_level: 1 });
IRTQuestionSchema.index({ 'irt_params.difficulty': 1 });
IRTQuestionSchema.index({ 'irt_params.discrimination': 1 });
IRTQuestionSchema.index({ tags: 1 });

// Виртуальные поля
IRTQuestionSchema.virtual('correctness_rate').get(function() {
  if (this.usage_stats.times_presented === 0) return 0;
  return this.usage_stats.times_correct / this.usage_stats.times_presented;
});

IRTQuestionSchema.virtual('difficulty_category').get(function() {
      const diff = this.irt_parameters.difficulty;
  if (diff < 0.7) return 'easy';
  if (diff < 1.3) return 'medium';
  return 'hard';
});

IRTQuestionSchema.virtual('discrimination_category').get(function() {
      const disc = this.irt_parameters.discrimination;
  if (disc < 1.5) return 'low';
  if (disc < 2.5) return 'medium';
  return 'high';
});

// Методы
IRTQuestionSchema.methods.calculateProbability = function(ability) {
  // 3PL модель: P(correct) = guessing + (1-guessing) * (1 / (1 + exp(-discrimination * (ability - difficulty))))
  const { difficulty, discrimination, guessing } = this.irt_parameters;
  const z = discrimination * (ability - difficulty);
  return guessing + (1 - guessing) / (1 + Math.exp(-z));
};

IRTQuestionSchema.methods.calculateFisherInformation = function(ability) {
  // Расчет информации Фишера для 3PL модели
  const { difficulty, discrimination, guessing } = this.irt_parameters;
  const z = discrimination * (ability - difficulty);
  const p = this.calculateProbability(ability);
  
  if (p <= guessing || p >= 1) return 0;
  
  const pStar = (p - guessing) / (1 - guessing);
  const qStar = 1 - pStar;
  const q = 1 - p;
  
  return (discrimination * discrimination * pStar * qStar) / (p * q);
};

IRTQuestionSchema.methods.updateUsageStats = function(isCorrect, responseTime) {
  this.usage_stats.times_presented += 1;
  if (isCorrect) this.usage_stats.times_correct += 1;
  
  // Обновить среднее время ответа
  const currentAvg = this.usage_stats.avg_response_time || 0;
  const totalPresented = this.usage_stats.times_presented;
  this.usage_stats.avg_response_time = 
    (currentAvg * (totalPresented - 1) + responseTime) / totalPresented;
  
  this.usage_stats.last_used = new Date();
  this.updated_at = new Date();
};

IRTQuestionSchema.methods.getOptimalDifficulty = function(currentAbility) {
  // Оптимальная сложность для максимальной информации
  return currentAbility;
};

// Статические методы
IRTQuestionSchema.statics.getQuestionsByDomain = function(domain, limit = 10) {
  return this.find({ domain })
    .sort({ 'irt_parameters.difficulty': 1 })
    .limit(limit);
};

IRTQuestionSchema.statics.getQuestionsByDifficulty = function(minDiff, maxDiff, limit = 20) {
  return this.find({
    'irt_parameters.difficulty': { $gte: minDiff, $lte: maxDiff }
  })
  .sort({ 'irt_parameters.discrimination': -1 })
  .limit(limit);
};

IRTQuestionSchema.statics.getUnusedQuestions = function(usedIds, domain = null) {
  const query = { question_id: { $nin: usedIds } };
  if (domain) query.domain = domain;
  
  return this.find(query)
    .sort({ 'usage_stats.times_presented': 1, 'irt_parameters.discrimination': -1 });
};

IRTQuestionSchema.statics.getHighQualityQuestions = function(domain = null, limit = 50) {
  const query = {
    'irt_parameters.discrimination': { $gte: 1.5 },
    'irt_parameters.difficulty': { $gte: 0.3, $lte: 1.7 }
  };
  if (domain) query.domain = domain;
  
  return this.find(query)
    .sort({ 'irt_params.discrimination': -1 })
    .limit(limit);
};

IRTQuestionSchema.statics.getQuestionStats = function() {
  return this.aggregate([
    {
      $group: {
        _id: '$domain',
        total_questions: { $sum: 1 },
        avg_difficulty: { $avg: '$irt_parameters.difficulty' },
        avg_discrimination: { $avg: '$irt_parameters.discrimination' },
        avg_guessing: { $avg: '$irt_parameters.guessing' },
        total_usage: { $sum: '$usage_stats.times_presented' },
        avg_correctness: {
          $avg: {
            $cond: [
              { $eq: ['$usage_stats.times_presented', 0] },
              0,
              { $divide: ['$usage_stats.times_correct', '$usage_stats.times_presented'] }
            ]
          }
        }
      }
    },
    {
      $sort: { total_questions: -1 }
    }
  ]);
};

// Middleware для обновления времени
IRTQuestionSchema.pre('save', function(next) {
  this.updated_at = new Date();
  next();
});

module.exports = mongoose.model('IRTQuestion', IRTQuestionSchema); 