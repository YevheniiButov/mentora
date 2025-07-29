const fs = require('fs');
const path = require('path');

const analyzeDomains = () => {
  try {
    // Читаем файл с вопросами
    const questionsData = JSON.parse(fs.readFileSync(path.join(__dirname, '../scripts/160_2.json'), 'utf8'));
    
    // Статистика по доменам
    const domainStats = {};
    const domainIRT = {};
    const domainDifficulty = {};
    const domainCategories = {};
    
    // Анализируем каждый вопрос
    questionsData.forEach(question => {
      const domain = question.domain;
      
      // Подсчет вопросов по доменам
      domainStats[domain] = (domainStats[domain] || 0) + 1;
      
      // IRT параметры по доменам
      if (!domainIRT[domain]) {
        domainIRT[domain] = {
          difficulty: [],
          discrimination: [],
          guessing: []
        };
      }
      
      if (question.irt_params) {
        domainIRT[domain].difficulty.push(question.irt_params.difficulty);
        domainIRT[domain].discrimination.push(question.irt_params.discrimination);
        domainIRT[domain].guessing.push(question.irt_params.guessing);
      }
      
      // Уровни сложности по доменам
      if (!domainDifficulty[domain]) {
        domainDifficulty[domain] = { 1: 0, 2: 0, 3: 0 };
      }
      domainDifficulty[domain][question.difficulty_level]++;
      
      // Категории по доменам
      if (!domainCategories[domain]) {
        domainCategories[domain] = new Set();
      }
      domainCategories[domain].add(question.category);
    });
    
    // Вычисляем средние IRT параметры
    const averageIRT = {};
    Object.keys(domainIRT).forEach(domain => {
      const difficulty = domainIRT[domain].difficulty;
      const discrimination = domainIRT[domain].discrimination;
      const guessing = domainIRT[domain].guessing;
      
      averageIRT[domain] = {
        avg_difficulty: difficulty.length > 0 ? (difficulty.reduce((a, b) => a + b, 0) / difficulty.length).toFixed(3) : 0,
        avg_discrimination: discrimination.length > 0 ? (discrimination.reduce((a, b) => a + b, 0) / discrimination.length).toFixed(3) : 0,
        avg_guessing: guessing.length > 0 ? (guessing.reduce((a, b) => a + b, 0) / guessing.length).toFixed(3) : 0,
        min_difficulty: Math.min(...difficulty),
        max_difficulty: Math.max(...difficulty),
        min_discrimination: Math.min(...discrimination),
        max_discrimination: Math.max(...discrimination)
      };
    });
    
    // Преобразуем Set в массивы для JSON
    const domainCategoriesArray = {};
    Object.keys(domainCategories).forEach(domain => {
      domainCategoriesArray[domain] = Array.from(domainCategories[domain]);
    });
    
    // Анализ проблем
    const problems = {
      insufficient_domains: [],
      excessive_domains: [],
      invalid_irt: [],
      duplicate_domains: []
    };
    
    // Домены с недостаточным количеством вопросов
    Object.keys(domainStats).forEach(domain => {
      if (domainStats[domain] < 10) {
        problems.insufficient_domains.push({
          domain: domain,
          count: domainStats[domain],
          needed: 10 - domainStats[domain]
        });
      }
    });
    
    // Домены с избыточным количеством вопросов
    Object.keys(domainStats).forEach(domain => {
      if (domainStats[domain] > 30) {
        problems.excessive_domains.push({
          domain: domain,
          count: domainStats[domain],
          excess: domainStats[domain] - 30
        });
      }
    });
    
    // Проверка IRT параметров
    questionsData.forEach(question => {
      if (question.irt_params) {
        if (question.irt_params.difficulty > 2 || question.irt_params.discrimination < 1) {
          problems.invalid_irt.push({
            id: question.id,
            domain: question.domain,
            difficulty: question.irt_params.difficulty,
            discrimination: question.irt_params.discrimination,
            issue: question.irt_params.difficulty > 2 ? 'difficulty_too_high' : 'discrimination_too_low'
          });
        }
      }
    });
    
    // Поиск дублирующихся доменов
    const potentialDuplicates = {
      'PHARMA': 'FARMACOLOGIE',
      'ETHIEK': 'PROFESSIONAL'
    };
    
    Object.keys(potentialDuplicates).forEach(domain1 => {
      const domain2 = potentialDuplicates[domain1];
      if (domainStats[domain1] && domainStats[domain2]) {
        problems.duplicate_domains.push({
          domain1: domain1,
          domain2: domain2,
          count1: domainStats[domain1],
          count2: domainStats[domain2],
          total: domainStats[domain1] + domainStats[domain2]
        });
      }
    });
    
    // Общая статистика
    const totalQuestions = questionsData.length;
    const totalDomains = Object.keys(domainStats).length;
    const averageQuestionsPerDomain = (totalQuestions / totalDomains).toFixed(2);
    
    const report = {
      summary: {
        total_questions: totalQuestions,
        total_domains: totalDomains,
        average_questions_per_domain: parseFloat(averageQuestionsPerDomain),
        date_analyzed: new Date().toISOString()
      },
      domain_statistics: domainStats,
      domain_irt_averages: averageIRT,
      domain_difficulty_levels: domainDifficulty,
      domain_categories: domainCategoriesArray,
      problems: problems
    };
    
    // Сохраняем отчет
    fs.writeFileSync(path.join(__dirname, 'domain_report.json'), JSON.stringify(report, null, 2));
    
    console.log('✅ Анализ завершен. Результаты сохранены в analysis/domain_report.json');
    
    return report;
    
  } catch (error) {
    console.error('❌ Ошибка при анализе:', error.message);
    return null;
  }
};

// Запускаем анализ
if (require.main === module) {
  analyzeDomains();
}

module.exports = { analyzeDomains }; 