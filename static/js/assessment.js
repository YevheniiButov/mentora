// ===== ASSESSMENT SYSTEM - JAVASCRIPT FUNCTIONALITY =====
// Адаптировано под существующую систему JavaScript проекта

// ===== UTILITY FUNCTIONS =====
function getCSRFToken() {
    const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    if (token) {
        console.log('CSRF Token: Found');
        return token;
    }
    console.warn('CSRF Token: Not found');
    return null;
}

function getCurrentLanguage() {
    return window.location.pathname.split('/')[1] || 'ru';
}

function getAppConfig() {
    return window.AppConfig || {
        currentLanguage: getCurrentLanguage(),
        csrfToken: getCSRFToken()
    };
}

// ===== API REQUEST HELPER =====
async function makeAssessmentRequest(url, data = {}, options = {}) {
    const defaultOptions = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        credentials: 'same-origin',
        ...options
    };

    console.log(`Making assessment request to: ${url}`);
    
    try {
        const response = await fetch(url, {
            ...defaultOptions,
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            console.error(`Assessment request failed: ${defaultOptions.method} ${url} ${response.status} (${response.statusText})`);
            throw new Error(`HTTP ${response.status}`);
        }
        
        return response.json();
    } catch (error) {
        console.error('Assessment request error:', error);
        throw error;
    }
}

// ===== ASSESSMENT SYSTEM CLASS =====
class AssessmentSystem {
    constructor() {
        this.currentQuestion = 1;
        this.totalQuestions = 50;
        this.selectedAnswers = {};
        this.timeRemaining = 3600; // 60 минут
        this.timerInterval = null;
        this.questionStartTime = null;
        this.autoSaveInterval = null;
        this.retryCount = 0;
        this.maxRetries = 3;
        
        this.init();
    }
    
    init() {
        console.log('🚀 Initializing Assessment System');
        
        this.setupEventListeners();
        this.setupAutoSave();
        this.loadSavedProgress();
        
        // Haptic feedback для мобильных устройств
        if ('vibrate' in navigator) {
            this.enableHapticFeedback();
        }
        
        // Предотвращение случайного закрытия
        this.setupBeforeUnload();
        
        // Accessibility improvements
        this.setupAccessibility();
        
        console.log('✅ Assessment System initialized');
    }
    
    setupEventListeners() {
        // Обработчики для опций ответов
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('assessment-option-button')) {
                this.selectOption(e.target);
            }
        });
        
        // Навигация
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.previousQuestion());
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.nextQuestion());
        }
        
        // Горячие клавиши
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardNavigation(e);
        });
        
        // Мобильные жесты
        this.setupMobileGestures();
        
        console.log('✅ Event listeners setup complete');
    }
    
    setupTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }
        
        this.timerInterval = setInterval(() => {
            this.timeRemaining--;
            this.updateTimerDisplay();
            
            // Предупреждения о времени
            if (this.timeRemaining === 600) { // 10 минут
                this.showTimeWarning('У вас осталось 10 минут!', 'warning');
            } else if (this.timeRemaining === 300) { // 5 минут
                this.showTimeWarning('У вас осталось 5 минут!', 'danger');
                this.vibrate([200, 100, 200]);
            } else if (this.timeRemaining <= 0) {
                this.timeUp();
            }
        }, 1000);
        
        console.log('⏰ Timer started');
    }
    
    updateTimerDisplay() {
        const minutes = Math.floor(this.timeRemaining / 60);
        const seconds = this.timeRemaining % 60;
        const display = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        const timerElement = document.getElementById('time-display');
        if (timerElement) {
            timerElement.textContent = display;
        }
        
        // Изменение стиля таймера
        const timer = document.getElementById('timer');
        if (timer) {
            timer.className = 'timer';
            
            if (this.timeRemaining < 300) { // 5 минут
                timer.classList.add('danger');
            } else if (this.timeRemaining < 600) { // 10 минут
                timer.classList.add('warning');
            }
        }
    }
    
    selectOption(optionElement) {
        const questionContainer = optionElement.closest('.question-section') || 
                                optionElement.closest('.question-content');
        
        if (!questionContainer) return;
        
        // Убираем выделение с других опций
        questionContainer.querySelectorAll('.assessment-option-button').forEach(btn => {
            btn.classList.remove('selected');
            btn.setAttribute('aria-pressed', 'false');
        });
        
        // Выделяем выбранную опцию
        optionElement.classList.add('selected');
        optionElement.setAttribute('aria-pressed', 'true');
        
        // Сохраняем ответ
        const optionIndex = parseInt(optionElement.dataset.optionIndex);
        this.selectedAnswers[this.currentQuestion] = optionIndex;
        
        // Активируем кнопку "Далее"
        const nextBtn = document.getElementById('next-btn');
        if (nextBtn) {
            nextBtn.disabled = false;
        }
        
        // Haptic feedback
        this.vibrate(30);
        
        // Сохраняем ответ на сервер
        this.saveAnswer(optionIndex);
        
        // Анимация выбора
        this.animateOptionSelection(optionElement);
    }
    
    async saveAnswer(optionIndex) {
        const questionId = this.getCurrentQuestionId();
        if (!questionId) return;
        
        const timeSpent = this.questionStartTime ? 
            Math.floor((Date.now() - this.questionStartTime) / 1000) : 0;
        
        try {
            const response = await makeAssessmentRequest(
                `/${getCurrentLanguage()}/assessment/answer`,
                {
                    question_id: questionId,
                    answer: optionIndex,
                    time_spent: timeSpent
                }
            );
            
            if (!response.success) {
                console.error('Error saving answer:', response.error);
                this.showNotification('Ошибка сохранения ответа', 'error');
            } else {
                console.log('✅ Answer saved successfully');
            }
        } catch (error) {
            console.error('Error saving answer:', error);
            this.showNotification('Ошибка сети', 'error');
        }
    }
    
    async nextQuestion() {
        if (this.selectedAnswers[this.currentQuestion] === undefined) {
            this.showNotification('Пожалуйста, выберите ответ', 'warning');
            this.vibrate([100, 50, 100]);
            return;
        }
        
        await this.navigateToQuestion('next');
    }
    
    async previousQuestion() {
        await this.navigateToQuestion('previous');
    }
    
    async navigateToQuestion(direction) {
        const btn = direction === 'next' ? 
            document.getElementById('next-btn') : 
            document.getElementById('prev-btn');
        
        if (btn) {
            this.showButtonLoading(btn);
        }
        
        try {
            const response = await makeAssessmentRequest(
                `/${getCurrentLanguage()}/assessment/navigation`,
                {
                    direction: direction,
                    current_question: this.currentQuestion
                }
            );
            
            if (response.success) {
                if (response.action === 'complete') {
                    this.completeAssessment();
                } else {
                    // Плавный переход
                    this.fadeOutAndNavigate(response.redirect_url);
                }
            } else {
                throw new Error(response.error || 'Navigation error');
            }
        } catch (error) {
            console.error('Navigation error:', error);
            this.showNotification('Ошибка навигации', 'error');
            this.vibrate([50, 50, 50]);
        } finally {
            if (btn) {
                this.hideButtonLoading(btn);
            }
        }
    }
    
    completeAssessment() {
        clearInterval(this.timerInterval);
        clearInterval(this.autoSaveInterval);
        
        // Успешная вибрация
        this.vibrate([100, 50, 100, 50, 100]);
        
        // Анимация завершения
        this.showCompletionAnimation();
        
        // Перенаправление через 2 секунды
        setTimeout(() => {
            window.location.href = `/${getCurrentLanguage()}/assessment/complete`;
        }, 2000);
        
        console.log('🎉 Assessment completed');
    }
    
    timeUp() {
        clearInterval(this.timerInterval);
        
        this.showNotification('Время вышло!', 'danger');
        this.vibrate([200, 100, 200, 100, 200]);
        
        // Автоматическое завершение
        setTimeout(() => {
            this.completeAssessment();
        }, 3000);
        
        console.log('⏰ Time up - assessment auto-completed');
    }
    
    setupAutoSave() {
        // Автосохранение каждые 30 секунд
        this.autoSaveInterval = setInterval(() => {
            this.saveProgress();
        }, 30000);
        
        console.log('💾 Auto-save enabled');
    }
    
    saveProgress() {
        const progress = {
            currentQuestion: this.currentQuestion,
            selectedAnswers: this.selectedAnswers,
            timeRemaining: this.timeRemaining,
            timestamp: Date.now()
        };
        
        localStorage.setItem('assessment_progress', JSON.stringify(progress));
        console.log('💾 Progress saved to localStorage');
    }
    
    loadSavedProgress() {
        const saved = localStorage.getItem('assessment_progress');
        if (saved) {
            try {
                const progress = JSON.parse(saved);
                
                // Проверяем актуальность (не старше 2 часов)
                if (Date.now() - progress.timestamp < 7200000) {
                    this.selectedAnswers = progress.selectedAnswers || {};
                    
                    // Восстанавливаем выбранный ответ на текущей странице
                    this.restoreSelectedAnswer();
                    console.log('📂 Saved progress loaded');
                } else {
                    console.log('⏰ Saved progress expired, starting fresh');
                }
            } catch (error) {
                console.error('Error loading progress:', error);
            }
        }
    }
    
    restoreSelectedAnswer() {
        const savedAnswer = this.selectedAnswers[this.currentQuestion];
        if (savedAnswer !== undefined) {
            const optionButton = document.querySelector(
                `.assessment-option-button[data-option-index="${savedAnswer}"]`
            );
            if (optionButton) {
                this.selectOption(optionButton);
            }
        }
    }
    
    handleKeyboardNavigation(event) {
        // Горячие клавиши
        switch(event.key) {
            case '1':
            case '2':
            case '3':
            case '4':
            case '5':
                event.preventDefault();
                const optionIndex = parseInt(event.key) - 1;
                const optionButton = document.querySelector(
                    `.assessment-option-button[data-option-index="${optionIndex}"]`
                );
                if (optionButton) {
                    this.selectOption(optionButton);
                }
                break;
                
            case 'ArrowLeft':
                event.preventDefault();
                this.previousQuestion();
                break;
                
            case 'ArrowRight':
            case 'Enter':
                if (event.key === 'Enter' && event.target.tagName !== 'BUTTON') {
                    event.preventDefault();
                    this.nextQuestion();
                }
                break;
                
            case 'Escape':
                event.preventDefault();
                this.showExitConfirmation();
                break;
        }
    }
    
    setupMobileGestures() {
        let startX = 0;
        let startY = 0;
        
        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        }, { passive: true });
        
        document.addEventListener('touchend', (e) => {
            if (!startX || !startY) return;
            
            const endX = e.changedTouches[0].clientX;
            const endY = e.changedTouches[0].clientY;
            
            const deltaX = endX - startX;
            const deltaY = endY - startY;
            
            // Свайп влево/вправо для навигации
            if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 100) {
                if (deltaX > 0) {
                    // Свайп вправо - предыдущий вопрос
                    this.previousQuestion();
                } else {
                    // Свайп влево - следующий вопрос
                    this.nextQuestion();
                }
            }
        }, { passive: true });
        
        console.log('📱 Mobile gestures enabled');
    }
    
    enableHapticFeedback() {
        // Добавляем haptic feedback для всех интерактивных элементов
        document.querySelectorAll('.assessment-option-button, .btn-assessment').forEach(element => {
            element.addEventListener('touchstart', () => {
                this.vibrate(10);
            }, { passive: true });
        });
        
        console.log('📳 Haptic feedback enabled');
    }
    
    setupBeforeUnload() {
        window.addEventListener('beforeunload', (e) => {
            // Сохраняем прогресс перед закрытием
            this.saveProgress();
            
            // Показываем предупреждение
            e.preventDefault();
            e.returnValue = '';
        });
    }
    
    setupAccessibility() {
        // Улучшения для screen readers
        document.querySelectorAll('.assessment-option-button').forEach((button, index) => {
            button.setAttribute('role', 'radio');
            button.setAttribute('aria-checked', 'false');
            button.setAttribute('tabindex', index === 0 ? '0' : '-1');
        });
        
        // Клавишная навигация по опциям
        document.addEventListener('keydown', (e) => {
            if (e.target.classList.contains('assessment-option-button')) {
                const options = Array.from(document.querySelectorAll('.assessment-option-button'));
                const currentIndex = options.indexOf(e.target);
                
                let newIndex = currentIndex;
                
                switch(e.key) {
                    case 'ArrowDown':
                    case 'ArrowRight':
                        e.preventDefault();
                        newIndex = (currentIndex + 1) % options.length;
                        break;
                    case 'ArrowUp':
                    case 'ArrowLeft':
                        e.preventDefault();
                        newIndex = (currentIndex - 1 + options.length) % options.length;
                        break;
                    case ' ':
                    case 'Enter':
                        e.preventDefault();
                        this.selectOption(e.target);
                        return;
                }
                
                if (newIndex !== currentIndex) {
                    options.forEach((option, i) => {
                        option.setAttribute('tabindex', i === newIndex ? '0' : '-1');
                    });
                    options[newIndex].focus();
                }
            }
        });
        
        console.log('♿ Accessibility features enabled');
    }
    
    // ===== UTILITY METHODS =====
    
    vibrate(pattern) {
        if ('vibrate' in navigator) {
            navigator.vibrate(pattern);
        }
    }
    
    showNotification(message, type = 'info') {
        // Создаем уведомление
        const notification = document.createElement('div');
        notification.className = `assessment-notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="bi bi-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;
        
        // Добавляем в контейнер
        let container = document.querySelector('.notifications-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'notifications-container';
            document.body.appendChild(container);
        }
        
        container.appendChild(notification);
        
        // Анимация появления
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Автоудаление
        setTimeout(() => {
            notification.classList.add('hide');
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }
    
    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'x-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    showButtonLoading(button) {
        button.dataset.originalContent = button.innerHTML;
        button.innerHTML = '<span class="loading-spinner"></span>';
        button.disabled = true;
    }
    
    hideButtonLoading(button) {
        button.innerHTML = button.dataset.originalContent || button.innerHTML;
        button.disabled = false;
    }
    
    fadeOutAndNavigate(url) {
        document.body.style.opacity = '0';
        document.body.style.transition = 'opacity 0.3s ease';
        
        setTimeout(() => {
            window.location.href = url;
        }, 300);
    }
    
    showCompletionAnimation() {
        const overlay = document.createElement('div');
        overlay.className = 'completion-overlay';
        overlay.innerHTML = `
            <div class="completion-content">
                <div class="completion-icon">
                    <i class="bi bi-check-circle"></i>
                </div>
                <h2>Тест завершен!</h2>
                <p>Анализируем ваши результаты...</p>
                <div class="completion-spinner"></div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        
        setTimeout(() => overlay.classList.add('show'), 100);
    }
    
    showTimeWarning(message, type) {
        // Показываем временное предупреждение
        const warning = document.createElement('div');
        warning.className = `time-warning ${type}`;
        warning.innerHTML = `
            <i class="bi bi-clock"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(warning);
        
        setTimeout(() => warning.classList.add('show'), 100);
        setTimeout(() => {
            warning.classList.add('hide');
            setTimeout(() => warning.remove(), 300);
        }, 5000);
    }
    
    showExitConfirmation() {
        if (confirm('Вы уверены, что хотите покинуть тест? Прогресс будет сохранен.')) {
            this.saveProgress();
            window.location.href = `/${getCurrentLanguage()}/assessment/`;
        }
    }
    
    animateOptionSelection(optionElement) {
        optionElement.style.transform = 'scale(1.02)';
        setTimeout(() => {
            optionElement.style.transform = '';
        }, 200);
    }
    
    getCurrentQuestionId() {
        const questionElement = document.querySelector('[data-question-id]');
        return questionElement ? parseInt(questionElement.dataset.questionId) : null;
    }
    
    // Метод для очистки ресурсов
    destroy() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
        }
        console.log('🧹 Assessment System destroyed');
    }
}

// ===== ASSESSMENT RESULTS CLASS =====
class AssessmentResults {
    constructor() {
        this.init();
    }
    
    init() {
        console.log('📊 Initializing Assessment Results');
        this.animateResults();
        this.setupInteractions();
        console.log('✅ Assessment Results initialized');
    }
    
    animateResults() {
        // Анимация кругового прогресса
        setTimeout(() => this.animateScoreCircle(), 500);
        
        // Анимация прогресс-баров категорий
        setTimeout(() => this.animateCategoryBars(), 1000);
        
        // Анимация появления рекомендаций
        setTimeout(() => this.animateRecommendations(), 1500);
    }
    
    animateScoreCircle() {
        const circle = document.querySelector('.score-circle');
        const scoreText = document.querySelector('.score-text');
        
        if (!circle || !scoreText) return;
        
        const targetScore = parseInt(scoreText.textContent);
        let currentScore = 0;
        const increment = targetScore / 50;
        
        const animation = setInterval(() => {
            currentScore += increment;
            if (currentScore >= targetScore) {
                currentScore = targetScore;
                clearInterval(animation);
            }
            
            scoreText.textContent = Math.round(currentScore) + '%';
            
            // Обновляем conic-gradient
            const degrees = (currentScore / 100) * 360;
            circle.style.background = `conic-gradient(
                var(--primary) 0deg,
                var(--primary) ${degrees}deg,
                var(--border-color) ${degrees}deg
            )`;
        }, 50);
    }
    
    animateCategoryBars() {
        const bars = document.querySelectorAll('.category-progress-fill');
        
        bars.forEach((bar, index) => {
            setTimeout(() => {
                const width = bar.dataset.width || bar.style.width;
                bar.style.width = width;
            }, index * 200);
        });
    }
    
    animateRecommendations() {
        const recommendations = document.querySelectorAll('.recommendation-item');
        
        recommendations.forEach((item, index) => {
            setTimeout(() => {
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }
    
    setupInteractions() {
        // Кнопка создания плана
        const createPlanBtn = document.querySelector('.btn-create-plan');
        if (createPlanBtn) {
            createPlanBtn.addEventListener('click', this.createLearningPlan.bind(this));
        }
        
        // Кнопки действий в рекомендациях
        document.querySelectorAll('.recommendation-action').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const moduleId = e.target.dataset.moduleId;
                if (moduleId) {
                    this.startModule(moduleId);
                }
            });
        });
    }
    
    createLearningPlan() {
        const attemptId = this.getAttemptId();
        if (attemptId) {
            window.location.href = `/${getCurrentLanguage()}/assessment/create-plan/${attemptId}`;
        }
    }
    
    startModule(moduleId) {
        window.location.href = `/${getCurrentLanguage()}/modules/${moduleId}`;
    }
    
    getAttemptId() {
        return document.querySelector('[data-attempt-id]')?.dataset.attemptId;
    }
}

// ===== GENERAL ENHANCEMENTS =====
function setupGeneralEnhancements() {
    // Плавные переходы между страницами
    setupPageTransitions();
    
    // Улучшенная обработка форм
    setupFormEnhancements();
    
    // Lazy loading для изображений
    setupLazyLoading();
    
    console.log('🔧 General enhancements applied');
}

function setupPageTransitions() {
    // Анимация загрузки страницы
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.5s ease';
    
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 100);
}

function setupFormEnhancements() {
    // Улучшения для форм оценки
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="loading-spinner me-2"></span>Обработка...';
            }
        });
    });
}

function setupLazyLoading() {
    // Lazy loading для изображений
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    }
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Assessment system initialization started');
    
    // Определяем, какая страница оценки загружена
    if (document.querySelector('.question-section')) {
        // Страница вопроса
        window.assessmentSystem = new AssessmentSystem();
        
        // Запускаем таймер
        window.assessmentSystem.setupTimer();
        window.assessmentSystem.questionStartTime = Date.now();
        
        console.log('📝 Question page initialized');
    } else if (document.querySelector('.results-section')) {
        // Страница результатов
        window.assessmentResults = new AssessmentResults();
        
        console.log('📊 Results page initialized');
    }
    
    // Общие улучшения
    setupGeneralEnhancements();
    
    console.log('✅ Assessment system initialization complete');
});

// ===== EXPORT FOR MODULE SYSTEMS =====
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AssessmentSystem, AssessmentResults };
}

// ===== GLOBAL ACCESS =====
window.AssessmentSystem = AssessmentSystem;
window.AssessmentResults = AssessmentResults; 