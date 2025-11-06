const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const DiagnosticSessionSchema = new Schema({
  user_id: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  
  // Сессия IRT тестирования
  session_type: { 
    type: String, 
    enum: ['full_diagnostic', 'domain_specific', 'adaptive_practice'],
    default: 'full_diagnostic'
  },
  
  // IRT данные
  current_ability_estimate: { type: Number, default: 0 },
  ability_standard_error: { type: Number, default: 1 },
  starting_difficulty: { type: Number, default: 1.0 },
  
  // Прогресс
  questions_answered: [{
    question_id: { type: Number, required: true },
    domain: String,
    user_answer: { type: Number, required: true },
    is_correct: Boolean,
    response_time: Number, // в секундах
    ability_before: Number,
    ability_after: Number,
    question_difficulty: Number,
    timestamp: { type: Date, default: Date.now }
  }],
  
  // Результаты по доменам
  domain_results: [{
    domain: String,
    questions_answered: Number,
    correct_answers: Number,
    avg_difficulty: Number,
    ability_estimate: Number,
    confidence_interval: {
      lower: Number,
      upper: Number
    },
    recommendation: {
      type: String,
      enum: ['study_required', 'practice_recommended', 'proficient', 'advanced']
    }
  }],
  
  // Статус сессии
  status: { 
    type: String, 
    enum: ['in_progress', 'completed', 'abandoned'],
    default: 'in_progress'
  },
  started_at: { type: Date, default: Date.now },
  completed_at: Date,
  total_duration: Number, // в секундах
  
  // Дополнительные метаданные
  target_domains: [String], // Для domain_specific сессий
  max_questions: { type: Number, default: 50 },
  min_questions: { type: Number, default: 20 },
  confidence_threshold: { type: Number, default: 0.3 }, // Для завершения
  
  // Статистика сессии
  session_stats: {
    total_questions: { type: Number, default: 0 },
    correct_answers: { type: Number, default: 0 },
    avg_response_time: Number,
    domain_coverage: Number, // Процент покрытых доменов
    ability_progression: [Number] // История изменения способности
  }
});

// Индексы для оптимизации
DiagnosticSessionSchema.index({ user_id: 1, status: 1 });
DiagnosticSessionSchema.index({ started_at: -1 });
DiagnosticSessionSchema.index({ session_type: 1 });
DiagnosticSessionSchema.index({ 'domain_results.domain': 1 });

// Виртуальные поля
DiagnosticSessionSchema.virtual('accuracy_rate').get(function() {
  if (this.session_stats.total_questions === 0) return 0;
  return this.session_stats.correct_answers / this.session_stats.total_questions;
});

DiagnosticSessionSchema.virtual('session_duration').get(function() {
  if (!this.completed_at) return Date.now() - this.started_at;
  return this.completed_at - this.started_at;
});

DiagnosticSessionSchema.virtual('is_ready_for_completion').get(function() {
  return this.session_stats.total_questions >= this.min_questions &&
         this.ability_standard_error <= this.confidence_threshold;
});

// Методы
DiagnosticSessionSchema.methods.addAnswer = function(questionData, userAnswer, responseTime) {
  const isCorrect = userAnswer === questionData.correct_answer_index;
  
  // Обновить статистику
  this.session_stats.total_questions += 1;
  if (isCorrect) this.session_stats.correct_answers += 1;
  
  // Обновить среднее время ответа
  const currentAvg = this.session_stats.avg_response_time || 0;
  const totalQuestions = this.session_stats.total_questions;
  this.session_stats.avg_response_time = 
    (currentAvg * (totalQuestions - 1) + responseTime) / totalQuestions;
  
  // Добавить ответ
  this.questions_answered.push({
    question_id: questionData.question_id,
    domain: questionData.domain,
    user_answer: userAnswer,
    is_correct: isCorrect,
    response_time: responseTime,
    ability_before: this.current_ability_estimate,
            question_difficulty: questionData.irt_parameters.difficulty
  });
  
  // Обновить способность (будет рассчитана в сервисе)
  this.session_stats.ability_progression.push(this.current_ability_estimate);
};

DiagnosticSessionSchema.methods.updateDomainResults = function() {
  // Группировать ответы по доменам
  const domainAnswers = {};
  
  this.questions_answered.forEach(answer => {
    if (!domainAnswers[answer.domain]) {
      domainAnswers[answer.domain] = {
        questions: [],
        correct: 0,
        total: 0,
        difficulties: []
      };
    }
    
    domainAnswers[answer.domain].questions.push(answer);
    domainAnswers[answer.domain].total += 1;
    if (answer.is_correct) domainAnswers[answer.domain].correct += 1;
    domainAnswers[answer.domain].difficulties.push(answer.question_difficulty);
  });
  
  // Обновить результаты по доменам
  this.domain_results = Object.entries(domainAnswers).map(([domain, data]) => {
    const avgDifficulty = data.difficulties.reduce((a, b) => a + b, 0) / data.difficulties.length;
    const accuracy = data.correct / data.total;
    
    // Рассчитать оценку способности для домена
    const domainAbility = this.calculateDomainAbility(data.questions);
    
    return {
      domain,
      questions_answered: data.total,
      correct_answers: data.correct,
      avg_difficulty: avgDifficulty,
      ability_estimate: domainAbility.ability,
      confidence_interval: {
        lower: domainAbility.ability - domainAbility.confidence,
        upper: domainAbility.ability + domainAbility.confidence
      },
      recommendation: this.getRecommendation(domainAbility.ability, accuracy)
    };
  });
};

DiagnosticSessionSchema.methods.calculateDomainAbility = function(domainAnswers) {
  if (domainAnswers.length === 0) {
    return { ability: 0, confidence: 1.0 };
  }
  
  // Упрощенный расчет способности для домена
  let totalAbility = 0;
  let totalWeight = 0;
  
  domainAnswers.forEach(answer => {
    const weight = 1 / (1 + answer.response_time / 60);
    totalAbility += answer.ability_after * weight;
    totalWeight += weight;
  });
  
  return {
    ability: totalWeight > 0 ? totalAbility / totalWeight : 0,
    confidence: Math.min(1.0, 1 / Math.sqrt(domainAnswers.length))
  };
};

DiagnosticSessionSchema.methods.getRecommendation = function(ability, accuracy) {
  if (ability >= 1.5 && accuracy >= 0.8) return 'advanced';
  if (ability >= 0.5 && accuracy >= 0.6) return 'proficient';
  if (ability >= -0.5 && accuracy >= 0.4) return 'practice_recommended';
  return 'study_required';
};

DiagnosticSessionSchema.methods.completeSession = function() {
  this.status = 'completed';
  this.completed_at = new Date();
  this.total_duration = this.session_duration;
  this.updateDomainResults();
};

// Статические методы
DiagnosticSessionSchema.statics.getActiveSession = function(userId) {
  return this.findOne({ 
    user_id: userId, 
    status: 'in_progress' 
  }).sort({ started_at: -1 });
};

DiagnosticSessionSchema.statics.getUserSessions = function(userId, limit = 10) {
  return this.find({ user_id: userId })
    .sort({ started_at: -1 })
    .limit(limit);
};

DiagnosticSessionSchema.statics.getSessionStats = function() {
  return this.aggregate([
    {
      $group: {
        _id: '$session_type',
        total_sessions: { $sum: 1 },
        completed_sessions: {
          $sum: { $cond: [{ $eq: ['$status', 'completed'] }, 1, 0] }
        },
        avg_duration: { $avg: '$total_duration' },
        avg_questions: { $avg: '$session_stats.total_questions' },
        avg_accuracy: {
          $avg: {
            $divide: ['$session_stats.correct_answers', '$session_stats.total_questions']
          }
        }
      }
    }
  ]);
};

// Middleware для обновления времени
DiagnosticSessionSchema.pre('save', function(next) {
  if (this.isModified('questions_answered')) {
    this.updateDomainResults();
  }
  next();
});

module.exports = mongoose.model('DiagnosticSession', DiagnosticSessionSchema); 