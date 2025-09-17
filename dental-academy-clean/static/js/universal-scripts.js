// ===== UNIVERSAL SCRIPTS FROM INDEX.HTML =====
// Все скрипты из оригинального index.html

// ===== CSRF AND REQUEST UTILITIES =====
function getCSRFToken() {
  const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
  if (token) {
    // return token;
  }
  // console.warn('CSRF Token: Not found');
  return null;
}

// ===== AI WIDGET CONTROLLER WITH RETRY SYSTEM =====
const aiWidgetController = {
  retryCounters: {
    examReadiness: 0,
    recommendations: 0,
    progressAnalysis: 0
  },
  maxRetries: 3,
  retryDelay: 2000,
  fallbackMode: false,

  async makeRequest(url, options = {}) {
    const defaultOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      },
      credentials: 'same-origin',
      ...options
    };

    // const response = await fetch(url, defaultOptions);
    
    if (!response.ok) {
      console.error(`

           ${defaultOptions.method} ${url} ${response.status} (${response.statusText})`);
      throw new Error(`HTTP ${response.status}`);
    }
    
    return response.json();
  },

  async retryRequest(requestFn, widgetType) {
    const counter = this.retryCounters[widgetType];
    
    if (counter >= this.maxRetries) {
      console.warn(`Max retries reached for ${widgetType}, switching to fallback mode`);
      this.fallbackMode = true;
      return this.getFallbackData(widgetType);
    }

    try {
      this.retryCounters[widgetType]++;
      await new Promise(resolve => setTimeout(resolve, this.retryDelay * counter));
      return await requestFn();
    } catch (error) {
      console.error(`Retry ${counter + 1} failed for ${widgetType}:`, error);
      return this.retryRequest(requestFn, widgetType);
    }
  },

  getFallbackData(widgetType) {
    const fallbackData = {
      examReadiness: {
        success: true,
        prediction: {
          exam_readiness: 75.0,
          success_probability: 80.0,
          weak_areas: ['Требуется больше практики'],
          recommendations: ['Продолжайте изучение материалов'],
          confidence_level: 'medium',
          fallback_mode: true
        }
      },
      recommendations: {
        success: true,
        recommendations: [
          {
            type: 'module',
            title: 'Рекомендуется изучение',
            description: 'Продолжайте обучение для получения персональных рекомендаций',
            url: `/${window.location.pathname.split('/')[1] || 'ru'}/learning-map`
          }
        ],
        fallback_mode: true
      },
      progressAnalysis: {
        success: true,
        stats: {
          completed_lessons: 0,
          average_score: 0,
          study_time: 0,
          fallback_mode: true
        }
      }
    };

    return fallbackData[widgetType];
  }
};

async function makeAIRequest(url, data = {}, options = {}) {
  return aiWidgetController.makeRequest(url, {
    ...options,
    body: JSON.stringify(data)
  });
}

// ===== EXAM READINESS LOADER WITH RETRY =====
async function loadExamReadiness() {
  const container = document.getElementById('examReadinessContent');
  if (!container) return;
  
  const requestFn = async () => {
    container.innerHTML = getLoadingHTML('Анализируем готовность к экзамену...');
    
    const currentLang = window.location.pathname.split('/')[1] || 'ru';
    const response = await fetch(`/${currentLang}/ai-assistant/predict-exam`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return response.json();
  };

  try {
    let data;
    
    if (aiWidgetController.fallbackMode) {
      data = aiWidgetController.getFallbackData('examReadiness');
    } else {
      try {
        data = await requestFn();
      } catch (error) {
        console.error('Exam readiness error:', error);
        data = await aiWidgetController.retryRequest(requestFn, 'examReadiness');
      }
    }
    
    // if (data.success && data.prediction) {
      renderExamReadiness(data.prediction);
    } else {
      throw new Error(data.error || 'No prediction data');
    }
    
  } catch (error) {
    console.error('Exam readiness error:', error);
    container.innerHTML = `
      <div class="text-center py-4">
        <div class="alert alert-info">
          <h5>📊 Анализ готовности</h5>
          <p>Продолжайте изучение материалов для получения персонального анализа</p>
          <a href="/${window.location.pathname.split('/')[1] || 'ru'}/learning-map" class="btn btn-primary btn-sm">
            Перейти к обучению
          </a>
        </div>
      </div>
    `;
  }
}

// ===== RECOMMENDATIONS LOADER WITH RETRY AND TYPE CHECKING =====
async function loadRecommendations() {
  const container = document.getElementById('recommendationsContent');
  if (!container) return;
  
  const requestFn = async () => {
    container.innerHTML = getLoadingHTML('Подбираем рекомендации...');
    
    const currentLang = window.location.pathname.split('/')[1] || 'ru';
    return await makeAIRequest(`/${currentLang}/ai-assistant/recommend-content`, {
      limit: 3
    });
  };

  try {
    let data;
    
    if (aiWidgetController.fallbackMode) {
      data = aiWidgetController.getFallbackData('recommendations');
    } else {
      try {
        data = await requestFn();
      } catch (error) {
        console.error('Recommendations error:', error);
        data = await aiWidgetController.retryRequest(requestFn, 'recommendations');
      }
    }
    
    // if (data.success && data.recommendations) {
      renderRecommendations(data.recommendations);
    } else {
      throw new Error(data.error || 'No recommendations data');
    }
    
  } catch (error) {
    console.error('Recommendations error:', error);
    container.innerHTML = `
      <div class="text-center py-3">
        <div class="alert alert-info">
          <h6>💡 Персональные рекомендации</h6>
          <p>Рекомендации появятся после изучения первых материалов</p>
          <a href="/${window.location.pathname.split('/')[1] || 'ru'}/learning-map" class="btn btn-outline-primary btn-sm">
            Начать обучение
          </a>
        </div>
      </div>
    `;
  }
}

// ===== PROGRESS ANALYSIS LOADER WITH RETRY =====
async function loadProgressAnalysis() {
  const container = document.getElementById('progressAnalysisContent');
  if (!container) return;
  
  const requestFn = async () => {
    container.innerHTML = getLoadingHTML('Анализируем слабые области...');
    
    const currentLang = window.location.pathname.split('/')[1] || 'ru';
    const response = await fetch(`/${currentLang}/dashboard/api/progress-stats`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return response.json();
  };

  try {
    let data;
    
    if (aiWidgetController.fallbackMode) {
      data = aiWidgetController.getFallbackData('progressAnalysis');
    } else {
      try {
        data = await requestFn();
      } catch (error) {
        console.error('Progress analysis error:', error);
        data = await aiWidgetController.retryRequest(requestFn, 'progressAnalysis');
      }
    }
    
    if (data.success) {
      renderProgressAnalysis(data.stats);
    } else {
      throw new Error('No progress data');
    }
    
  } catch (error) {
    console.error('Progress analysis error:', error);
    container.innerHTML = `
      <div class="text-center py-3">
        <div class="alert alert-info">
          <h6>📈 Анализ прогресса</h6>
          <p>Детальный анализ появится после прохождения уроков</p>
          <div class="progress mt-3">
            <div class="progress-bar" role="progressbar" style="width: 0%">0%</div>
          </div>
        </div>
      </div>
    `;
  }
}

// ===== MINI CHAT FUNCTIONS =====
function toggleMiniChat() {
  const body = document.getElementById('miniChatBody');
  const toggle = document.getElementById('miniChatToggle');
  
  if (!body || !toggle) return;
  
  if (body.style.display === 'none' || !body.style.display) {
    body.style.display = 'block';
    toggle.className = 'bi bi-chevron-up';
  } else {
    body.style.display = 'none';
    toggle.className = 'bi bi-chevron-down';
  }
}

async function sendMiniChatMessage() {
  const input = document.getElementById('miniChatInput');
  const messages = document.getElementById('miniChatMessages');
  
  if (!input || !messages) return;
  
  const message = input.value.trim();
  if (!message) return;
  
  // Добавляем сообщение пользователя
  const userMessage = document.createElement('div');
  userMessage.className = 'user-message';
  userMessage.textContent = message;
  messages.appendChild(userMessage);
  
  input.value = '';
  messages.scrollTop = messages.scrollHeight;
  
  try {
    const currentLang = window.location.pathname.split('/')[1] || 'ru';
    const data = await makeAIRequest(`/${currentLang}/ai-assistant/chat`, {
      message: message,
      mini_chat: true 
    });
    
    if (data.success && data.response) {
      const aiMessage = document.createElement('div');
      aiMessage.className = 'ai-message';
      aiMessage.innerHTML = `<i class="bi bi-robot"></i><span>${data.response}</span>`;
      messages.appendChild(aiMessage);
    } else {
      throw new Error(data.error || 'No response from AI');
    }
    
  } catch (error) {
    console.error('Mini chat error:', error);
    const errorMessage = document.createElement('div');
    errorMessage.className = 'ai-message error';
    errorMessage.innerHTML = `<i class="bi bi-exclamation-triangle"></i><span>AI временно недоступен</span>`;
    messages.appendChild(errorMessage);
  }
  
  messages.scrollTop = messages.scrollHeight;
}

// ===== UTILITY FUNCTIONS =====
function getLoadingHTML(text) {
  return `
    <div class="loading-state text-center py-3">
      <div class="spinner-border spinner-border-sm text-primary mb-2" role="status"></div>
      <div class="loading-text">${text}</div>
    </div>
  `;
}

function renderExamReadiness(prediction) {
  const container = document.getElementById('examReadinessContent');
  if (!container) return;

  const readiness = prediction.exam_readiness || 0;
  const weakAreas = prediction.weak_areas || [];
  const fallbackMode = prediction.fallback_mode || false;

  container.innerHTML = `
    <div class="text-center">
      ${fallbackMode ? '<div class="badge badge-info mb-2">Автономный режим</div>' : ''}
      <div class="success-probability-circle ${readiness > 70 ? 'success-high' : readiness > 40 ? 'success-medium' : 'success-low'}">
        ${readiness}%
      </div>
      <h6 class="mb-3">Готовность к экзамену</h6>
      ${weakAreas.length > 0 ? `
        <div class="weak-areas mt-3">
          <h6>Области для улучшения:</h6>
          <div class="weak-areas-list">
            ${weakAreas.map(area => `<span class="badge badge-outline-warning">${area}</span>`).join('')}
          </div>
        </div>
      ` : ''}
    </div>
  `;
}

// ===== PROTECTED RECOMMENDATIONS RENDERER =====
function renderRecommendations(recommendations) {
  const container = document.getElementById('recommendationsContent');
  if (!container) return;

  // ЗАЩИЩЕННАЯ ПРОВЕРКА ТИПОВ ДАННЫХ
  let safeRecommendations = [];
  
  try {
    // Проверяем что recommendations существует и является массивом
    if (Array.isArray(recommendations)) {
      safeRecommendations = recommendations;
      // } else if (recommendations && typeof recommendations === 'object') {
      // Если это объект, пытаемся извлечь массив
      if (Array.isArray(recommendations.recommendations)) {
        safeRecommendations = recommendations.recommendations;
      } else if (Array.isArray(recommendations.data)) {
        safeRecommendations = recommendations.data;
      } else {
        // Создаем массив из одного элемента
        safeRecommendations = [recommendations];
      }
    } else {
      // Если данные некорректны, создаем fallback рекомендацию  
      console.warn('Invalid recommendations data, using fallback');
      safeRecommendations = [{
        type: 'fallback',
        title: 'Продолжайте обучение',
        description: 'Персональные рекомендации появятся после изучения материалов',
        url: `/${window.location.pathname.split('/')[1] || 'ru'}/learning-map`
      }];
    }
  } catch (error) {
    console.error('Error processing recommendations:', error);
    safeRecommendations = [{
      type: 'error',
      title: 'Рекомендации временно недоступны',
      description: 'Попробуйте обновить страницу',
      url: '#'
    }];
  }

  // Безопасный рендеринг с проверкой каждого поля
  container.innerHTML = safeRecommendations.map(rec => {
    const title = rec?.title || 'Без названия';
    const description = rec?.description || 'Описание недоступно';
    const type = rec?.type || 'general';
    const url = rec?.url || '#';
    
    return `
      <div class="recommendation-item">
        <div class="recommendation-header">
          <h6>${title}</h6>
          <span class="badge badge-primary">${type}</span>
        </div>
        <p class="recommendation-description">${description}</p>
        <a href="${url}" class="btn btn-sm btn-outline-primary">Изучить</a>
      </div>
    `;
  }).join('');
}

function renderProgressAnalysis(stats) {
  const container = document.getElementById('progressAnalysisContent');
  if (!container) return;

  const fallbackMode = stats?.fallback_mode || false;

  container.innerHTML = `
    <div class="progress-stats">
      ${fallbackMode ? '<div class="badge badge-info mb-2">Автономный режим</div>' : ''}
      <div class="stat-item">
        <div class="stat-label">Пройдено уроков</div>
        <div class="stat-value">${stats?.completed_lessons || 0}</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">Средний балл</div>
        <div class="stat-value">${stats?.average_score || 0}%</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">Время обучения</div>
        <div class="stat-value">${stats?.study_time || 0}ч</div>
      </div>
    </div>
  `;
}

// ===== DOM CONTENT LOADED INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
  // Initialize smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const href = this.getAttribute('href');
      
      // Проверяем, что href не просто '#'
      if (href === '#') return;
      
      const target = document.querySelector(href);
      if (target) {
        const headerHeight = document.querySelector('.modern-header')?.offsetHeight || 70;
        const targetPosition = target.offsetTop - headerHeight - 20;
        
        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });
      }
    });
  });

  // Reduce animations on mobile for better performance
  if (window.innerWidth <= 768) {
    document.documentElement.classList.add('mobile-optimized');
  }
  
  // Animate elements on scroll
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-visible');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);
  
  // Observe all elements with data-animate attribute
  document.querySelectorAll('[data-animate]').forEach(el => {
    observer.observe(el);
  });
  
  // Initialize AI Widgets for authenticated users
  if (typeof initializeAIWidgets !== 'undefined') {
    initializeAIWidgets();
  }
  
  // Initialize AI Widgets immediately if they exist
  if (document.getElementById('examReadinessWidget')) {
    initializeAIWidgets();
  }
});

// ===== ADDITIONAL AI FUNCTIONS =====
function getAreaDisplayName(area) {
  const areaNames = {
    'oral_pathology': 'Патология полости рта',
    'endodontics': 'Эндодонтия',
    'periodontics': 'Пародонтология',
    'prosthetics': 'Протезирование',
    'surgery': 'Хирургия',
    'radiology': 'Рентгенология'
  };
  return areaNames[area] || area;
}

async function loadProgressAnalytics() {
  const container = document.getElementById('progressAnalyticsContent');
  if (!container) {
    console.warn('progressAnalyticsContent container not found');
    return;
  }
  
  try {
    container.innerHTML = getLoadingHTML('Анализируем слабые области...');
    
    const currentLang = window.location.pathname.split('/')[1] || 'ru';
    
    const response = await fetch(`/${currentLang}/ai-assistant/progress-stats`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    
    if (data.success) {
      renderProgressAnalytics(data.stats);
    } else {
      throw new Error('No progress data');
    }
    
  } catch (error) {
    console.error('Progress analysis error:', error);
    container.innerHTML = `
      <div class="text-center py-3">
        <div class="alert alert-info">
          <h6>📈 Анализ прогресса</h6>
          <p>Детальный анализ появится после прохождения уроков и тестов</p>
          <div class="progress mt-3">
            <div class="progress-bar" role="progressbar" style="width: 0%">0%</div>
          </div>
        </div>
      </div>
    `;
  }
}

function renderProgressAnalytics(analytics) {
  const container = document.getElementById('progressAnalyticsContent');
  if (!container) return;
  
  container.innerHTML = `
    <div class="analytics-metric">
      <span class="metric-label">Регулярность обучения</span>
      <span class="metric-value">
        ${Math.round((analytics.study_consistency || 0) * 100)}%
        <span class="metric-trend trend-up">↑</span>
      </span>
    </div>
    <div class="analytics-metric">
      <span class="metric-label">Среднее время сессии</span>
      <span class="metric-value">${analytics.avg_session_time || 0} мин</span>
    </div>
    <div class="analytics-metric">
      <span class="metric-label">Слабые области</span>
      <span class="metric-value">${(analytics.weak_areas || []).length}</span>
    </div>
  `;
}

// ===== AI WIDGETS INITIALIZATION WITH STAGGERED LOADING =====
function initializeAIWidgets() {
  // // Загружаем виджеты с задержкой для лучшей производительности
  setTimeout(() => {
    // Load exam readiness if widget exists
    if (document.getElementById('examReadinessContent')) {
      loadExamReadiness();
    }
  }, 100);
  
  setTimeout(() => {
    // Load recommendations if widget exists
    if (document.getElementById('recommendationsContent')) {
      loadRecommendations();
    }
  }, 300);
  
  setTimeout(() => {
    // Load progress analysis if widget exists
    if (document.getElementById('progressAnalysisContent')) {
      loadProgressAnalysis();
    }
  }, 500);
  
  setTimeout(() => {
    // Load progress analytics if widget exists
    if (document.getElementById('progressAnalyticsContent')) {
      loadProgressAnalytics();
    }
  }, 700);
}

// ===== ANIMATIONS AND EFFECTS =====
const additionalStyles = `
.loading-state {
  min-height: 80px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.success-probability-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 18px;
  color: white;
  margin: 0 auto 15px;
  position: relative;
}

.success-high {
  background: linear-gradient(135deg, #28a745, #20c997);
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
}

.success-medium {
  background: linear-gradient(135deg, #ffc107, #fd7e14);
  box-shadow: 0 4px 15px rgba(255, 193, 7, 0.3);
}

.success-low {
  background: linear-gradient(135deg, #dc3545, #e83e8c);
  box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3);
}

.recommendation-item {
  border: 1px solid var(--border-color, #e9ecef);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 10px;
  background: var(--card-bg, #fff);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.recommendation-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.recommendation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.recommendation-header h6 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.recommendation-description {
  font-size: 12px;
  color: var(--text-muted, #6c757d);
  margin-bottom: 10px;
  line-height: 1.4;
}

.progress-stats {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color, #e9ecef);
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  font-size: 12px;
  color: var(--text-muted, #6c757d);
}

.stat-value {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary, #333);
}

.weak-areas-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  justify-content: center;
}

.weak-areas-list .badge {
  font-size: 10px;
  padding: 4px 8px;
}

.analytics-metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-color, #e9ecef);
}

.analytics-metric:last-child {
  border-bottom: none;
}

.metric-label {
  font-size: 12px;
  color: var(--text-muted, #6c757d);
}

.metric-value {
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.metric-trend {
  font-size: 12px;
}

.trend-up {
  color: #28a745;
}

.trend-down {
  color: #dc3545;
}

@media (max-width: 768px) {
  .success-probability-circle {
    width: 60px;
    height: 60px;
    font-size: 14px;
  }
  
  .recommendation-item {
    padding: 10px;
  }
  
  .recommendation-header h6 {
    font-size: 13px;
  }
  
  .recommendation-description {
    font-size: 11px;
  }
}
`;

// Добавляем стили
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet); 