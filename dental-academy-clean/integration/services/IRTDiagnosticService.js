const DiagnosticSession = require('../models/DiagnosticSession');
const IRTQuestion = require('../models/IRTQuestion');
const Domain = require('../models/Domain');

class IRTDiagnosticService {
  constructor() {
    this.questions = require('../../scripts/unified_system/unified_irt_system.json').questions;
    this.domainsConfig = require('../../scripts/unified_system/domains_config.json');
    this.qualityReport = require('../../scripts/unified_system/quality_report.json');
  }
  
  async startDiagnosticSession(userId, sessionType = 'full_diagnostic', options = {}) {
    try {
      // Проверить активную сессию
      const activeSession = await DiagnosticSession.getActiveSession(userId);
      if (activeSession) {
        throw new Error('У пользователя уже есть активная сессия');
      }
      
      // Создать новую диагностическую сессию
      const session = new DiagnosticSession({
        user_id: userId,
        session_type: sessionType,
        current_ability_estimate: 0.0,
        ability_standard_error: 1.0,
        starting_difficulty: 1.0,
        target_domains: options.target_domains || [],
        max_questions: options.max_questions || 50,
        min_questions: options.min_questions || 20,
        confidence_threshold: options.confidence_threshold || 0.3
      });
      
      await session.save();
      
      // Выбрать стартовые вопросы
      const startingQuestions = await this.selectStartingQuestions(session);
      
      return {
        session_id: session._id,
        first_question: startingQuestions[0],
        total_domains: 30,
        estimated_duration: '45-60 минут',
        session_type: sessionType,
        target_domains: session.target_domains
      };
    } catch (error) {
      throw new Error(`Ошибка при запуске диагностической сессии: ${error.message}`);
    }
  }
  
  async selectStartingQuestions(session) {
    try {
      // Выбрать по 1 вопросу средней сложности из каждого критического домена
      const criticalDomains = this.domainsConfig.domains
        .filter(d => d.is_critical)
        .map(d => d.code);
      
      const startingQuestions = [];
      
      for (const domain of criticalDomains) {
        const domainQuestions = this.questions
          .filter(q => q.domain === domain && q.difficulty_level === 2)
          .sort((a, b) => Math.abs(a.irt_parameters.difficulty - 1.0) - Math.abs(b.irt_parameters.difficulty - 1.0));
        
        if (domainQuestions.length > 0) {
          startingQuestions.push(domainQuestions[0]);
        }
      }
      
      // Если критических доменов недостаточно, добавить вопросы из других доменов
      if (startingQuestions.length < 5) {
        const additionalQuestions = this.questions
          .filter(q => !criticalDomains.includes(q.domain) && q.difficulty_level === 2)
          .sort((a, b) => Math.abs(a.irt_parameters.difficulty - 1.0) - Math.abs(b.irt_parameters.difficulty - 1.0))
          .slice(0, 5 - startingQuestions.length);
        
        startingQuestions.push(...additionalQuestions);
      }
      
      return startingQuestions.slice(0, 5); // Максимум 5 стартовых вопросов
    } catch (error) {
      throw new Error(`Ошибка при выборе стартовых вопросов: ${error.message}`);
    }
  }
  
  async processAnswer(sessionId, questionId, userAnswer, responseTime) {
    try {
      // Получить текущую сессию
      const session = await DiagnosticSession.findById(sessionId);
      if (!session) {
        throw new Error('Сессия не найдена');
      }
      
      if (session.status !== 'in_progress') {
        throw new Error('Сессия уже завершена');
      }
      
      // Найти вопрос
      const question = this.questions.find(q => q.id === questionId);
      if (!question) {
        throw new Error('Вопрос не найден');
      }
      
      // Проверить правильность ответа
      const isCorrect = userAnswer === question.correct_answer_index;
      
      // Обновить IRT оценку способности
      const newAbility = this.updateAbilityEstimate(
        session.current_ability_estimate,
        isCorrect,
        question.irt_parameters
      );
      
      // Добавить ответ в сессию
      session.addAnswer(question, userAnswer, responseTime);
      
      // Обновить текущую оценку
      session.current_ability_estimate = newAbility;
      session.ability_standard_error = this.calculateStandardError(session.questions_answered);
      
      // Обновить последний ответ с новой способностью
      const lastAnswer = session.questions_answered[session.questions_answered.length - 1];
      lastAnswer.ability_after = newAbility;
      
      await session.save();
      
      // Определить следующий вопрос
      const nextQuestion = await this.selectNextQuestion(session);
      
      // Проверить, нужно ли завершить сессию
      const shouldComplete = this.shouldCompleteSession(session);
      
      return {
        is_correct: isCorrect,
        explanation: question.explanation,
        current_ability: newAbility,
        ability_confidence: session.ability_standard_error,
        next_question: nextQuestion,
        session_progress: this.calculateProgress(session),
        should_complete: shouldComplete,
        session_id: session._id
      };
    } catch (error) {
      throw new Error(`Ошибка при обработке ответа: ${error.message}`);
    }
  }
  
  async selectNextQuestion(session) {
    try {
      const answeredQuestions = session.questions_answered.map(q => q.question_id);
      const availableQuestions = this.questions.filter(q => !answeredQuestions.includes(q.id));
      
      if (availableQuestions.length === 0) {
        return null; // Нет доступных вопросов
      }
      
      // Определить домены с недостаточным покрытием
      const domainCoverage = this.analyzeDomainCoverage(session);
      const targetDomains = domainCoverage
        .filter(d => d.questions_answered < d.min_required)
        .map(d => d.domain);
      
      if (targetDomains.length > 0) {
        // Выбрать вопрос из недопокрытого домена
        return this.selectOptimalQuestion(
          availableQuestions.filter(q => targetDomains.includes(q.domain)),
          session.current_ability_estimate
        );
      }
      
      // Выбрать оптимальный вопрос по информации Фишера
      return this.selectOptimalQuestion(availableQuestions, session.current_ability_estimate);
    } catch (error) {
      throw new Error(`Ошибка при выборе следующего вопроса: ${error.message}`);
    }
  }
  
  selectOptimalQuestion(availableQuestions, currentAbility) {
    if (availableQuestions.length === 0) return null;
    
    // Рассчитать информацию Фишера для каждого вопроса
    const questionsWithInfo = availableQuestions.map(question => {
      const fisherInfo = this.fisherInformation(currentAbility, question.irt_parameters);
      return { question, fisherInfo };
    });
    
    // Выбрать вопрос с максимальной информацией
    const optimalQuestion = questionsWithInfo.reduce((best, current) => {
      return current.fisherInfo > best.fisherInfo ? current : best;
    });
    
    return optimalQuestion.question;
  }
  
  updateAbilityEstimate(currentAbility, isCorrect, questionIRT) {
    try {
      // Реализация Maximum Likelihood Estimation для IRT
      // 3PL модель: P(correct) = guessing + (1-guessing) * (1 / (1 + exp(-discrimination * (ability - difficulty))))
      
      const { difficulty, discrimination, guessing } = questionIRT;
      
      // Вероятность правильного ответа при текущей способности
      const probability = guessing + (1 - guessing) / (1 + Math.exp(-discrimination * (currentAbility - difficulty)));
      
      // Обновление оценки (упрощенная версия Newton-Raphson)
      const learningRate = 0.3;
      const error = isCorrect ? (1 - probability) : (0 - probability);
      const update = learningRate * discrimination * error;
      
      return Math.max(-3, Math.min(3, currentAbility + update));
    } catch (error) {
      console.error('Ошибка при обновлении оценки способности:', error);
      return currentAbility; // Возвратить текущую оценку в случае ошибки
    }
  }
  
  calculateStandardError(answeredQuestions) {
    try {
      // Расчет стандартной ошибки на основе информации Фишера
      let totalInformation = 0;
      
      answeredQuestions.forEach(answer => {
        const question = this.questions.find(q => q.id === answer.question_id);
        if (question) {
          const info = this.fisherInformation(answer.ability_after, question.irt_parameters);
          totalInformation += info;
        }
      });
      
      return totalInformation > 0 ? 1 / Math.sqrt(totalInformation) : 1.0;
    } catch (error) {
      console.error('Ошибка при расчете стандартной ошибки:', error);
      return 1.0;
    }
  }
  
  fisherInformation(ability, irtParams) {
    try {
      // Расчет информации Фишера для 3PL модели
      const { difficulty, discrimination, guessing } = irtParams;
      const z = discrimination * (ability - difficulty);
      const p = guessing + (1 - guessing) / (1 + Math.exp(-z));
      
      if (p <= guessing || p >= 1) return 0;
      
      const pStar = (p - guessing) / (1 - guessing);
      const qStar = 1 - pStar;
      const q = 1 - p;
      
      return (discrimination * discrimination * pStar * qStar) / (p * q);
    } catch (error) {
      console.error('Ошибка при расчете информации Фишера:', error);
      return 0;
    }
  }
  
  analyzeDomainCoverage(session) {
    const domainStats = {};
    
    // Инициализировать статистику для всех доменов
    this.domainsConfig.domains.forEach(domain => {
      domainStats[domain.code] = {
        domain: domain.code,
        questions_answered: 0,
        min_required: domain.is_critical ? 3 : 1,
        weight: domain.weight
      };
    });
    
    // Подсчитать ответы по доменам
    session.questions_answered.forEach(answer => {
      if (domainStats[answer.domain]) {
        domainStats[answer.domain].questions_answered += 1;
      }
    });
    
    return Object.values(domainStats);
  }
  
  calculateProgress(session) {
    const totalQuestions = session.session_stats.total_questions;
    const maxQuestions = session.max_questions;
    const minQuestions = session.min_questions;
    
    return {
      questions_answered: totalQuestions,
      max_questions: maxQuestions,
      min_questions: minQuestions,
      progress_percentage: Math.min(100, (totalQuestions / maxQuestions) * 100),
      confidence_level: 1 - session.ability_standard_error,
      domain_coverage: this.calculateDomainCoveragePercentage(session)
    };
  }
  
  calculateDomainCoveragePercentage(session) {
    const domainCoverage = this.analyzeDomainCoverage(session);
    const coveredDomains = domainCoverage.filter(d => d.questions_answered >= d.min_required).length;
    const totalDomains = domainCoverage.length;
    
    return Math.round((coveredDomains / totalDomains) * 100);
  }
  
  shouldCompleteSession(session) {
    // Проверить минимальное количество вопросов
    if (session.session_stats.total_questions < session.min_questions) {
      return false;
    }
    
    // Проверить максимальное количество вопросов
    if (session.session_stats.total_questions >= session.max_questions) {
      return true;
    }
    
    // Проверить уровень уверенности
    if (session.ability_standard_error <= session.confidence_threshold) {
      return true;
    }
    
    // Проверить покрытие доменов
    const domainCoverage = this.calculateDomainCoveragePercentage(session);
    if (domainCoverage >= 80) {
      return true;
    }
    
    return false;
  }
  
  async completeSession(sessionId) {
    try {
      const session = await DiagnosticSession.findById(sessionId);
      if (!session) {
        throw new Error('Сессия не найдена');
      }
      
      session.completeSession();
      await session.save();
      
      return {
        session_id: session._id,
        final_ability: session.current_ability_estimate,
        final_confidence: session.ability_standard_error,
        total_questions: session.session_stats.total_questions,
        accuracy_rate: session.accuracy_rate,
        domain_results: session.domain_results,
        total_duration: session.total_duration
      };
    } catch (error) {
      throw new Error(`Ошибка при завершении сессии: ${error.message}`);
    }
  }
  
  async getSessionResults(sessionId) {
    try {
      const session = await DiagnosticSession.findById(sessionId);
      if (!session) {
        throw new Error('Сессия не найдена');
      }
      
      if (session.status !== 'completed') {
        throw new Error('Сессия не завершена');
      }
      
      return {
        session_id: session._id,
        overall_ability: session.current_ability_estimate,
        ability_confidence: session.ability_standard_error,
        domain_results: session.domain_results,
        total_questions: session.session_stats.total_questions,
        accuracy_rate: session.accuracy_rate,
        total_duration: session.total_duration,
        bi_toets_readiness: this.assessBIToetsReadiness(session),
        learning_recommendations: this.generateLearningRecommendations(session)
      };
    } catch (error) {
      throw new Error(`Ошибка при получении результатов: ${error.message}`);
    }
  }
  
  assessBIToetsReadiness(session) {
    const overallAbility = session.current_ability_estimate;
    const accuracyRate = session.accuracy_rate;
    
    if (overallAbility >= 1.5 && accuracyRate >= 0.8) {
      return {
        level: 'high',
        score: 90,
        message: 'Высокая готовность к BI-toets',
        confidence: 'high'
      };
    } else if (overallAbility >= 0.5 && accuracyRate >= 0.6) {
      return {
        level: 'medium',
        score: 70,
        message: 'Средняя готовность - требуется дополнительная подготовка',
        confidence: 'medium'
      };
    } else {
      return {
        level: 'low',
        score: 40,
        message: 'Низкая готовность - необходимо интенсивное обучение',
        confidence: 'low'
      };
    }
  }
  
  generateLearningRecommendations(session) {
    const recommendations = [];
    
    // Анализ результатов по доменам
    session.domain_results.forEach(domainResult => {
      if (domainResult.recommendation === 'study_required') {
        recommendations.push({
          type: 'study',
          domain: domainResult.domain,
          priority: 'high',
          message: `Необходимо изучить основы ${domainResult.domain}`,
          suggested_resources: this.getSuggestedResources(domainResult.domain)
        });
      } else if (domainResult.recommendation === 'practice_recommended') {
        recommendations.push({
          type: 'practice',
          domain: domainResult.domain,
          priority: 'medium',
          message: `Рекомендуется практика в области ${domainResult.domain}`,
          suggested_resources: this.getSuggestedResources(domainResult.domain)
        });
      }
    });
    
    return recommendations;
  }
  
  getSuggestedResources(domain) {
    // Заглушка для получения рекомендуемых ресурсов
    return [
      'Соответствующие учебные материалы',
      'Практические задания',
      'Клинические случаи'
    ];
  }
}

module.exports = IRTDiagnosticService; 