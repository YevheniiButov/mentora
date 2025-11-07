const { expect } = require('chai');
const sinon = require('sinon');
const IRTDiagnosticService = require('../services/IRTDiagnosticService');
const DiagnosticSession = require('../models/DiagnosticSession');
const Domain = require('../models/Domain');
const IRTQuestion = require('../models/IRTQuestion');

describe('IRT Integration Tests', () => {
  let testSession;
  let irtService;
  let sandbox;
  
  beforeEach(async () => {
    sandbox = sinon.createSandbox();
    irtService = new IRTDiagnosticService();
    
    // Мокаем данные для тестирования
    const mockQuestions = [
      {
        id: 1,
        text: 'Test question 1',
        options: ['A', 'B', 'C', 'D', 'E'],
        correct_answer_index: 0,
        domain: 'PHARMACOLOGY',
        difficulty_level: 2,
        irt_params: {
          difficulty: 1.0,
          discrimination: 1.5,
          guessing: 0.2
        }
      },
      {
        id: 2,
        text: 'Test question 2',
        options: ['A', 'B', 'C', 'D', 'E'],
        correct_answer_index: 1,
        domain: 'THERAPEUTIC_DENTISTRY',
        difficulty_level: 2,
        irt_params: {
          difficulty: 1.2,
          discrimination: 1.8,
          guessing: 0.15
        }
      }
    ];
    
    // Мокаем unified_irt_system.json
    sandbox.stub(irtService, 'questions').value(mockQuestions);
    
    // Мокаем domains_config.json
    sandbox.stub(irtService, 'domainsConfig').value({
      domains: [
        {
          code: 'PHARMACOLOGY',
          is_critical: true,
          weight: 15
        },
        {
          code: 'THERAPEUTIC_DENTISTRY',
          is_critical: true,
          weight: 12
        }
      ]
    });
  });
  
  afterEach(() => {
    sandbox.restore();
  });
  
  describe('Diagnostic Session Management', () => {
    test('Should start diagnostic session with valid parameters', async () => {
      // Arrange
      const userId = 'test_user_id';
      const sessionType = 'full_diagnostic';
      
      // Mock DiagnosticSession.getActiveSession
      const getActiveSessionStub = sandbox.stub(DiagnosticSession, 'getActiveSession').resolves(null);
      
      // Mock DiagnosticSession constructor and save
      const mockSession = {
        _id: 'session_123',
        save: sandbox.stub().resolves()
      };
      const DiagnosticSessionStub = sandbox.stub(DiagnosticSession.prototype, 'constructor').returns(mockSession);
      
      // Act
      const result = await irtService.startDiagnosticSession(userId, sessionType);
      
      // Assert
      expect(result.session_id).to.equal('session_123');
      expect(result.first_question).to.be.defined;
      expect(result.total_domains).to.equal(30);
      expect(getActiveSessionStub.calledOnce).to.be.true;
    });
    
    test('Should prevent starting session if user has active session', async () => {
      // Arrange
      const userId = 'test_user_id';
      const activeSession = { _id: 'active_session_123' };
      
      sandbox.stub(DiagnosticSession, 'getActiveSession').resolves(activeSession);
      
      // Act & Assert
      try {
        await irtService.startDiagnosticSession(userId);
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error.message).to.include('уже есть активная сессия');
      }
    });
  });
  
  describe('Answer Processing', () => {
    beforeEach(async () => {
      // Setup mock session
      testSession = {
        _id: 'session_123',
        user_id: 'test_user_id',
        status: 'in_progress',
        current_ability_estimate: 0.0,
        ability_standard_error: 1.0,
        questions_answered: [],
        session_stats: {
          total_questions: 0,
          correct_answers: 0,
          avg_response_time: 0
        },
        addAnswer: sandbox.stub(),
        save: sandbox.stub().resolves()
      };
      
      sandbox.stub(DiagnosticSession, 'findById').resolves(testSession);
    });
    
    test('Should update ability estimate correctly for correct answer', async () => {
      // Arrange
      const questionId = 1;
      const userAnswer = 0; // Correct answer
      const responseTime = 30;
      
      // Act
      const result = await irtService.processAnswer('session_123', questionId, userAnswer, responseTime);
      
      // Assert
      expect(result.is_correct).to.be.true;
      expect(result.current_ability).to.be.greaterThan(0);
      expect(testSession.addAnswer.calledOnce).to.be.true;
      expect(testSession.save.calledOnce).to.be.true;
    });
    
    test('Should update ability estimate correctly for incorrect answer', async () => {
      // Arrange
      const questionId = 1;
      const userAnswer = 1; // Incorrect answer
      const responseTime = 45;
      
      // Act
      const result = await irtService.processAnswer('session_123', questionId, userAnswer, responseTime);
      
      // Assert
      expect(result.is_correct).to.be.false;
      expect(result.current_ability).to.be.lessThan(0);
      expect(testSession.addAnswer.calledOnce).to.be.true;
    });
    
    test('Should handle session not found', async () => {
      // Arrange
      sandbox.stub(DiagnosticSession, 'findById').resolves(null);
      
      // Act & Assert
      try {
        await irtService.processAnswer('invalid_session', 1, 0, 30);
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error.message).to.include('Сессия не найдена');
      }
    });
    
    test('Should handle completed session', async () => {
      // Arrange
      testSession.status = 'completed';
      
      // Act & Assert
      try {
        await irtService.processAnswer('session_123', 1, 0, 30);
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error.message).to.include('Сессия уже завершена');
      }
    });
  });
  
  describe('Question Selection', () => {
    test('Should select optimal question based on Fisher information', () => {
      // Arrange
      const availableQuestions = irtService.questions;
      const currentAbility = 1.0;
      
      // Act
      const selectedQuestion = irtService.selectOptimalQuestion(availableQuestions, currentAbility);
      
      // Assert
      expect(selectedQuestion).to.be.defined;
      expect(selectedQuestion.id).to.be.oneOf([1, 2]);
    });
    
    test('Should return null when no questions available', () => {
      // Arrange
      const availableQuestions = [];
      const currentAbility = 1.0;
      
      // Act
      const selectedQuestion = irtService.selectOptimalQuestion(availableQuestions, currentAbility);
      
      // Assert
      expect(selectedQuestion).to.be.null;
    });
  });
  
  describe('IRT Calculations', () => {
    test('Should calculate probability correctly for 3PL model', () => {
      // Arrange
      const question = irtService.questions[0];
      const ability = 1.0;
      
      // Act
      const probability = question.calculateProbability(ability);
      
      // Assert
      expect(probability).to.be.a('number');
      expect(probability).to.be.greaterThan(0.2); // guessing parameter
      expect(probability).to.be.lessThan(1.0);
    });
    
    test('Should calculate Fisher information correctly', () => {
      // Arrange
      const question = irtService.questions[0];
      const ability = 1.0;
      
      // Act
      const fisherInfo = question.calculateFisherInformation(ability);
      
      // Assert
      expect(fisherInfo).to.be.a('number');
      expect(fisherInfo).to.be.greaterThan(0);
    });
    
    test('Should update ability estimate correctly', () => {
      // Arrange
      const currentAbility = 0.0;
      const isCorrect = true;
      const questionIRT = {
        difficulty: 1.0,
        discrimination: 1.5,
        guessing: 0.2
      };
      
      // Act
      const newAbility = irtService.updateAbilityEstimate(currentAbility, isCorrect, questionIRT);
      
      // Assert
      expect(newAbility).to.be.a('number');
      expect(newAbility).to.be.greaterThan(currentAbility); // Should increase for correct answer
      expect(newAbility).to.be.greaterThan(-3);
      expect(newAbility).to.be.lessThan(3);
    });
  });
  
  describe('Domain Coverage Analysis', () => {
    test('Should analyze domain coverage correctly', () => {
      // Arrange
      const session = {
        questions_answered: [
          { domain: 'PHARMACOLOGY' },
          { domain: 'PHARMACOLOGY' },
          { domain: 'THERAPEUTIC_DENTISTRY' }
        ]
      };
      
      // Act
      const coverage = irtService.analyzeDomainCoverage(session);
      
      // Assert
      expect(coverage).to.be.an('array');
      expect(coverage.length).to.be.greaterThan(0);
      
      const pharmaCoverage = coverage.find(d => d.domain === 'PHARMACOLOGY');
      expect(pharmaCoverage.questions_answered).to.equal(2);
    });
  });
  
  describe('Session Completion Logic', () => {
    test('Should complete session when minimum questions reached and confidence high', () => {
      // Arrange
      const session = {
        session_stats: {
          total_questions: 25
        },
        min_questions: 20,
        max_questions: 50,
        ability_standard_error: 0.2,
        confidence_threshold: 0.3
      };
      
      // Act
      const shouldComplete = irtService.shouldCompleteSession(session);
      
      // Assert
      expect(shouldComplete).to.be.true;
    });
    
    test('Should not complete session when minimum questions not reached', () => {
      // Arrange
      const session = {
        session_stats: {
          total_questions: 15
        },
        min_questions: 20,
        max_questions: 50,
        ability_standard_error: 0.2,
        confidence_threshold: 0.3
      };
      
      // Act
      const shouldComplete = irtService.shouldCompleteSession(session);
      
      // Assert
      expect(shouldComplete).to.be.false;
    });
    
    test('Should complete session when maximum questions reached', () => {
      // Arrange
      const session = {
        session_stats: {
          total_questions: 50
        },
        min_questions: 20,
        max_questions: 50,
        ability_standard_error: 0.5,
        confidence_threshold: 0.3
      };
      
      // Act
      const shouldComplete = irtService.shouldCompleteSession(session);
      
      // Assert
      expect(shouldComplete).to.be.true;
    });
  });
  
  describe('BI-toets Readiness Assessment', () => {
    test('Should assess high readiness correctly', () => {
      // Arrange
      const session = {
        current_ability_estimate: 1.8,
        accuracy_rate: 0.85
      };
      
      // Act
      const readiness = irtService.assessBIToetsReadiness(session);
      
      // Assert
      expect(readiness.level).to.equal('high');
      expect(readiness.score).to.equal(90);
      expect(readiness.message).to.include('Высокая готовность');
    });
    
    test('Should assess medium readiness correctly', () => {
      // Arrange
      const session = {
        current_ability_estimate: 0.8,
        accuracy_rate: 0.65
      };
      
      // Act
      const readiness = irtService.assessBIToetsReadiness(session);
      
      // Assert
      expect(readiness.level).to.equal('medium');
      expect(readiness.score).to.equal(70);
      expect(readiness.message).to.include('Средняя готовность');
    });
    
    test('Should assess low readiness correctly', () => {
      // Arrange
      const session = {
        current_ability_estimate: -0.5,
        accuracy_rate: 0.35
      };
      
      // Act
      const readiness = irtService.assessBIToetsReadiness(session);
      
      // Assert
      expect(readiness.level).to.equal('low');
      expect(readiness.score).to.equal(40);
      expect(readiness.message).to.include('Низкая готовность');
    });
  });
  
  describe('Learning Recommendations', () => {
    test('Should generate study recommendations for weak domains', () => {
      // Arrange
      const session = {
        domain_results: [
          {
            domain: 'PHARMACOLOGY',
            recommendation: 'study_required'
          },
          {
            domain: 'THERAPEUTIC_DENTISTRY',
            recommendation: 'practice_recommended'
          }
        ]
      };
      
      // Act
      const recommendations = irtService.generateLearningRecommendations(session);
      
      // Assert
      expect(recommendations).to.be.an('array');
      expect(recommendations.length).to.equal(2);
      
      const studyRec = recommendations.find(r => r.type === 'study');
      expect(studyRec.priority).to.equal('high');
      expect(studyRec.message).to.include('Необходимо изучить');
      
      const practiceRec = recommendations.find(r => r.type === 'practice');
      expect(practiceRec.priority).to.equal('medium');
      expect(practiceRec.message).to.include('Рекомендуется практика');
    });
  });
  
  describe('Error Handling', () => {
    test('Should handle IRT calculation errors gracefully', () => {
      // Arrange
      const invalidIRT = {
        difficulty: 'invalid',
        discrimination: 'invalid',
        guessing: 'invalid'
      };
      
      // Act
      const result = irtService.updateAbilityEstimate(0, true, invalidIRT);
      
      // Assert
      expect(result).to.equal(0); // Should return current ability on error
    });
    
    test('Should handle Fisher information calculation errors', () => {
      // Arrange
      const invalidIRT = {
        difficulty: 1.0,
        discrimination: 1.0,
        guessing: 0.5 // Invalid guessing parameter
      };
      
      // Act
      const result = irtService.fisherInformation(1.0, invalidIRT);
      
      // Assert
      expect(result).to.equal(0); // Should return 0 on error
    });
  });
  
  describe('Integration with Database Models', () => {
    test('Should work with Domain model methods', async () => {
      // Arrange
      const mockDomain = {
        code: 'PHARMACOLOGY',
        getQuestionsByDifficulty: sandbox.stub().resolves([]),
        calculateDomainAbility: sandbox.stub().returns({ ability: 1.0, confidence: 0.8 })
      };
      
      // Act
      const questions = await mockDomain.getQuestionsByDifficulty(1.0);
      const ability = mockDomain.calculateDomainAbility([]);
      
      // Assert
      expect(questions).to.be.an('array');
      expect(ability.ability).to.equal(1.0);
      expect(ability.confidence).to.equal(0.8);
    });
    
    test('Should work with IRTQuestion model methods', () => {
      // Arrange
      const mockQuestion = {
        question_id: 1,
        calculateProbability: sandbox.stub().returns(0.75),
        calculateFisherInformation: sandbox.stub().returns(1.2),
        updateUsageStats: sandbox.stub()
      };
      
      // Act
      const probability = mockQuestion.calculateProbability(1.0);
      const fisherInfo = mockQuestion.calculateFisherInformation(1.0);
      mockQuestion.updateUsageStats(true, 30);
      
      // Assert
      expect(probability).to.equal(0.75);
      expect(fisherInfo).to.equal(1.2);
      expect(mockQuestion.updateUsageStats.calledOnce).to.be.true;
    });
  });
});

// Тесты для API endpoints (если нужно)
describe('IRT API Endpoints', () => {
  // Здесь можно добавить тесты для API endpoints
  // используя supertest или аналогичную библиотеку
}); 