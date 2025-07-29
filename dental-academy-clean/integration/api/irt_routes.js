const express = require('express');
const router = express.Router();
const IRTDiagnosticService = require('../services/IRTDiagnosticService');
const DiagnosticSession = require('../models/DiagnosticSession');

// Middleware для проверки аутентификации
const requireAuth = (req, res, next) => {
  if (!req.user) {
    return res.status(401).json({ 
      success: false, 
      message: 'Требуется аутентификация' 
    });
  }
  next();
};

// Начать диагностическую сессию
router.post('/diagnostic/start', requireAuth, async (req, res) => {
  try {
    const { session_type, target_domains, max_questions, min_questions, confidence_threshold } = req.body;
    const userId = req.user.id;
    
    const irtService = new IRTDiagnosticService();
    
    const session = await irtService.startDiagnosticSession(userId, session_type, {
      target_domains,
      max_questions,
      min_questions,
      confidence_threshold
    });
    
    res.json({
      success: true,
      data: session,
      message: 'Диагностическая сессия начата'
    });
  } catch (error) {
    console.error('Ошибка при запуске диагностики:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// Отправить ответ на вопрос
router.post('/diagnostic/answer', requireAuth, async (req, res) => {
  try {
    const { session_id, question_id, user_answer, response_time } = req.body;
    const userId = req.user.id;
    
    // Проверить, что сессия принадлежит пользователю
    const session = await DiagnosticSession.findById(session_id);
    if (!session || session.user_id.toString() !== userId) {
      return res.status(403).json({
        success: false,
        message: 'Доступ запрещен'
      });
    }
    
    const irtService = new IRTDiagnosticService();
    const result = await irtService.processAnswer(session_id, question_id, user_answer, response_time);
    
    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('Ошибка при обработке ответа:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// Завершить диагностическую сессию
router.post('/diagnostic/complete', requireAuth, async (req, res) => {
  try {
    const { session_id } = req.body;
    const userId = req.user.id;
    
    // Проверить, что сессия принадлежит пользователю
    const session = await DiagnosticSession.findById(session_id);
    if (!session || session.user_id.toString() !== userId) {
      return res.status(403).json({
        success: false,
        message: 'Доступ запрещен'
      });
    }
    
    const irtService = new IRTDiagnosticService();
    const result = await irtService.completeSession(session_id);
    
    res.json({
      success: true,
      data: result,
      message: 'Диагностическая сессия завершена'
    });
  } catch (error) {
    console.error('Ошибка при завершении сессии:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// Получить результаты диагностики
router.get('/diagnostic/results/:session_id', requireAuth, async (req, res) => {
  try {
    const { session_id } = req.params;
    const userId = req.user.id;
    
    const session = await DiagnosticSession.findById(session_id);
    if (!session || session.user_id.toString() !== userId) {
      return res.status(403).json({
        success: false,
        message: 'Доступ запрещен'
      });
    }
    
    if (session.status !== 'completed') {
      return res.status(404).json({ 
        success: false, 
        message: 'Сессия не найдена или не завершена' 
      });
    }
    
    const irtService = new IRTDiagnosticService();
    const results = await irtService.getSessionResults(session_id);
    
    res.json({
      success: true,
      data: results
    });
  } catch (error) {
    console.error('Ошибка при получении результатов:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// Получить активную сессию пользователя
router.get('/diagnostic/active', requireAuth, async (req, res) => {
  try {
    const userId = req.user.id;
    const activeSession = await DiagnosticSession.getActiveSession(userId);
    
    if (!activeSession) {
      return res.json({
        success: true,
        data: null,
        message: 'Активная сессия не найдена'
      });
    }
    
    res.json({
      success: true,
      data: {
        session_id: activeSession._id,
        session_type: activeSession.session_type,
        current_ability: activeSession.current_ability_estimate,
        questions_answered: activeSession.session_stats.total_questions,
        started_at: activeSession.started_at,
        progress: {
          questions_answered: activeSession.session_stats.total_questions,
          max_questions: activeSession.max_questions,
          progress_percentage: Math.min(100, (activeSession.session_stats.total_questions / activeSession.max_questions) * 100)
        }
      }
    });
  } catch (error) {
    console.error('Ошибка при получении активной сессии:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// Получить историю сессий пользователя
router.get('/diagnostic/history', requireAuth, async (req, res) => {
  try {
    const userId = req.user.id;
    const { limit = 10, page = 1 } = req.query;
    
    const sessions = await DiagnosticSession.getUserSessions(userId, parseInt(limit));
    
    res.json({
      success: true,
      data: {
        sessions: sessions.map(session => ({
          session_id: session._id,
          session_type: session.session_type,
          status: session.status,
          started_at: session.started_at,
          completed_at: session.completed_at,
          total_questions: session.session_stats.total_questions,
          accuracy_rate: session.accuracy_rate,
          final_ability: session.current_ability_estimate,
          total_duration: session.total_duration
        })),
        total: sessions.length,
        page: parseInt(page),
        limit: parseInt(limit)
      }
    });
  } catch (error) {
    console.error('Ошибка при получении истории сессий:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// Получить статистику IRT системы
router.get('/system/stats', async (req, res) => {
  try {
    const qualityReport = require('../../scripts/unified_system/quality_report.json');
    const domainsConfig = require('../../scripts/unified_system/domains_config.json');
    
    // Получить статистику сессий
    const sessionStats = await DiagnosticSession.getSessionStats();
    
    res.json({
      success: true,
      data: {
        total_questions: 410,
        total_domains: 30,
        quality_score: qualityReport.overall_score,
        categories: domainsConfig.categories,
        version: '2.0',
        session_statistics: sessionStats,
        system_health: {
          status: 'healthy',
          last_updated: new Date().toISOString(),
          uptime: process.uptime()
        }
      }
    });
  } catch (error) {
    console.error('Ошибка при получении статистики системы:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// Получить информацию о доменах
router.get('/domains', async (req, res) => {
  try {
    const domainsConfig = require('../../scripts/unified_system/domains_config.json');
    
    res.json({
      success: true,
      data: {
        domains: domainsConfig.domains,
        categories: domainsConfig.categories,
        total_domains: domainsConfig.total_domains
      }
    });
  } catch (error) {
    console.error('Ошибка при получении информации о доменах:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// Получить вопросы по домену
router.get('/questions/domain/:domain', requireAuth, async (req, res) => {
  try {
    const { domain } = req.params;
    const { limit = 10, difficulty = null } = req.query;
    
    const irtService = new IRTDiagnosticService();
    const domainQuestions = irtService.questions.filter(q => q.domain === domain);
    
    let filteredQuestions = domainQuestions;
    
    if (difficulty) {
      filteredQuestions = domainQuestions.filter(q => 
        q.difficulty_level === parseInt(difficulty)
      );
    }
    
    const limitedQuestions = filteredQuestions
      .sort((a, b) => a.irt_params.difficulty - b.irt_params.difficulty)
      .slice(0, parseInt(limit))
      .map(q => ({
        id: q.id,
        text: q.text,
        options: q.options,
        domain: q.domain,
        difficulty_level: q.difficulty_level,
        irt_params: q.irt_params,
        tags: q.tags
      }));
    
    res.json({
      success: true,
      data: {
        domain,
        questions: limitedQuestions,
        total_questions: domainQuestions.length,
        filtered_count: limitedQuestions.length
      }
    });
  } catch (error) {
    console.error('Ошибка при получении вопросов по домену:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// Получить прогресс пользователя по доменам
router.get('/user/progress', requireAuth, async (req, res) => {
  try {
    const userId = req.user.id;
    
    // Получить все завершенные сессии пользователя
    const completedSessions = await DiagnosticSession.find({
      user_id: userId,
      status: 'completed'
    }).sort({ completed_at: -1 });
    
    // Агрегировать прогресс по доменам
    const domainProgress = {};
    
    completedSessions.forEach(session => {
      session.domain_results.forEach(domainResult => {
        if (!domainProgress[domainResult.domain]) {
          domainProgress[domainResult.domain] = {
            domain: domainResult.domain,
            total_questions: 0,
            correct_answers: 0,
            avg_ability: 0,
            sessions_count: 0,
            last_updated: null
          };
        }
        
        const progress = domainProgress[domainResult.domain];
        progress.total_questions += domainResult.questions_answered;
        progress.correct_answers += domainResult.correct_answers;
        progress.avg_ability = (progress.avg_ability * progress.sessions_count + domainResult.ability_estimate) / (progress.sessions_count + 1);
        progress.sessions_count += 1;
        progress.last_updated = session.completed_at;
      });
    });
    
    // Рассчитать точность для каждого домена
    Object.values(domainProgress).forEach(progress => {
      progress.accuracy_rate = progress.total_questions > 0 ? 
        progress.correct_answers / progress.total_questions : 0;
    });
    
    res.json({
      success: true,
      data: {
        user_id: userId,
        domain_progress: Object.values(domainProgress),
        total_sessions: completedSessions.length,
        overall_progress: {
          total_questions: Object.values(domainProgress).reduce((sum, p) => sum + p.total_questions, 0),
          avg_accuracy: Object.values(domainProgress).reduce((sum, p) => sum + p.accuracy_rate, 0) / Object.keys(domainProgress).length
        }
      }
    });
  } catch (error) {
    console.error('Ошибка при получении прогресса пользователя:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

module.exports = router; 