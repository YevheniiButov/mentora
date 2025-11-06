/**
 * Domain Diagnostic Manager
 * Управление диагностикой по доменам BI-toets
 */

class DomainDiagnosticManager {
    constructor() {
        this.currentSession = null;
        this.currentDomain = null;
        this.domains = [];
        this.init();
    }
    
    async init() {
        await this.loadDomains();
        this.renderDomainSelector();
        this.bindEvents();
    }
    
    async loadDomains() {
        try {
            const response = await fetch('/big-diagnostic/api/domains');
            const data = await response.json();
            
            if (data.success) {
                this.domains = data.domains;
            } else {
                console.error('Failed to load domains:', data.error);
            }
        } catch (error) {
            console.error('Error loading domains:', error);
            showNotification('{{ t("error_loading_domains") }}', 'error');
        }
    }
    
    renderDomainSelector() {
        const container = document.getElementById('domain-selector');
        if (!container) return;
        
        container.innerHTML = this.domains.map(domain => `
            <div class="domain-card" data-domain="${domain.code}">
                <div class="domain-header">
                    <h3>${domain.name}</h3>
                    <span class="domain-weight">{{ t("weight") }}: ${domain.weight}%</span>
                </div>
                <div class="domain-description">
                    ${domain.description || ''}
                </div>
                <div class="domain-stats">
                    <span class="question-count">${domain.question_count} {{ t("questions") }}</span>
                    ${domain.user_stats ? `
                        <span class="user-score">{{ t("average_score") }}: ${domain.user_stats.average_score}%</span>
                    ` : ''}
                </div>
                <div class="domain-actions">
                    <button class="btn-secondary" onclick="domainManager.viewDomainDetails('${domain.code}')">
                        {{ t("details") }}
                    </button>
                    <button class="btn-primary" onclick="domainManager.startDomainDiagnostic('${domain.code}')">
                        {{ t("start_diagnostic") }}
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    bindEvents() {
        // Обработчики событий для интерактивности
        document.addEventListener('click', (e) => {
            if (e.target.matches('.domain-card')) {
                const domainCode = e.target.dataset.domain;
                this.viewDomainDetails(domainCode);
            }
        });
    }
    
    async viewDomainDetails(domainCode) {
        const domain = this.domains.find(d => d.code === domainCode);
        if (!domain) return;
        
        try {
            const response = await fetch(`/big-diagnostic/api/domains/${domainCode}`);
            const data = await response.json();
            
            if (data.success) {
                this.showDomainModal(data.domain);
            } else {
                showNotification('{{ t("error_loading_domain_info") }}', 'error');
            }
        } catch (error) {
            console.error('Error loading domain details:', error);
            showNotification('{{ t("error_connection") }}', 'error');
        }
    }
    
    showDomainModal(domain) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>${domain.name}</h2>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="domain-info">
                        <p class="domain-description">${domain.description}</p>
                        <div class="domain-stats-grid">
                            <div class="stat-item">
                                <span class="stat-label">{{ t("weight") }}:</span>
                                <span class="stat-value">${domain.weight}%</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">{{ t("questions_available") }}:</span>
                                <span class="stat-value">${domain.question_count}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">{{ t("sessions_completed") }}:</span>
                                <span class="stat-value">${domain.user_stats.sessions_completed}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">{{ t("average_score") }}:</span>
                                <span class="stat-value">${domain.user_stats.average_score}%</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="this.closest('.modal-overlay').remove()">
                        {{ t("close") }}
                    </button>
                    <button class="btn-primary" onclick="domainManager.startDomainDiagnostic('${domain.code}'); this.closest('.modal-overlay').remove();">
                        {{ t("start_diagnostic") }}
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
    
    async startDomainDiagnostic(domainCode) {
        const domain = this.domains.find(d => d.code === domainCode);
        if (!domain) return;
        
        this.currentDomain = domain;
        
        // Показать индикатор загрузки
        showLoadingIndicator('{{ t("starting_diagnostic") }}');
        
        try {
            const response = await fetch(`/big-diagnostic/api/domains/${domainCode}/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentSession = data.session_id;
                this.showQuestion(data.question, data.progress);
                hideLoadingIndicator();
            } else {
                hideLoadingIndicator();
                showNotification(data.error || '{{ t("error_starting_diagnostic") }}', 'error');
            }
        } catch (error) {
            hideLoadingIndicator();
            console.error('Error starting domain diagnostic:', error);
            showNotification('{{ t("error_connection") }}', 'error');
        }
    }
    
    showQuestion(question, progress) {
        // Скрыть селектор доменов
        const domainSelector = document.getElementById('domain-selector');
        if (domainSelector) {
            domainSelector.style.display = 'none';
        }
        
        // Показать контейнер вопросов
        const questionContainer = document.getElementById('domain-question-container');
        if (questionContainer) {
            questionContainer.style.display = 'block';
        }
        
        // Использовать существующий QuestionRenderer с адаптацией для доменов
        if (window.QuestionRenderer) {
            const renderer = new QuestionRenderer('domain-diagnostic');
            renderer.render(question, progress, {
                domainName: this.currentDomain.name,
                isDomainDiagnostic: true,
                sessionId: this.currentSession
            });
        } else {
            // Fallback рендеринг
            this.renderQuestionFallback(question, progress);
        }
    }
    
    renderQuestionFallback(question, progress) {
        const container = document.getElementById('domain-question-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="question-header">
                <div class="progress-info">
                    <span class="progress-text">{{ t("question") }} ${progress.current} {{ t("of") }} ${progress.total}</span>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${progress.percentage}%"></div>
                    </div>
                </div>
                <div class="domain-info">
                    <span class="domain-badge">${this.currentDomain.name}</span>
                </div>
            </div>
            
            <div class="question-content">
                <div class="question-text">${question.text}</div>
                
                <div class="question-options">
                    ${question.options.map((option, index) => `
                        <div class="option-item">
                            <input type="radio" name="answer" id="option-${index}" value="${index}">
                            <label for="option-${index}">${option}</label>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div class="question-actions">
                <button class="btn-secondary" onclick="domainManager.showDomainSelector()">
                    {{ t("back_to_domains") }}
                </button>
                <button class="btn-primary" onclick="domainManager.submitAnswer()" id="submit-answer-btn" disabled>
                    {{ t("submit_answer") }}
                </button>
            </div>
        `;
        
        // Добавить обработчики событий
        this.bindQuestionEvents();
    }
    
    bindQuestionEvents() {
        // Обработчик выбора ответа
        const options = document.querySelectorAll('input[name="answer"]');
        const submitBtn = document.getElementById('submit-answer-btn');
        
        options.forEach(option => {
            option.addEventListener('change', () => {
                submitBtn.disabled = false;
            });
        });
    }
    
    async submitAnswer() {
        const selectedOption = document.querySelector('input[name="answer"]:checked');
        if (!selectedOption) {
            showNotification('{{ t("please_select_answer") }}', 'warning');
            return;
        }
        
        const answer = parseInt(selectedOption.value);
        
        try {
            const response = await fetch('/big-diagnostic/submit-answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    session_id: this.currentSession,
                    question_id: this.currentQuestion.id,
                    answer: answer
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                if (data.completed && data.redirect_url) {
                    // Тест завершен, переходим на страницу результатов
                    window.location.href = data.redirect_url;
                } else if (data.session_completed) {
                    this.showResults(data.results);
                } else {
                    this.showQuestion(data.next_question, data.progress);
                }
            } else {
                showNotification(data.error || '{{ t("error_submitting_answer") }}', 'error');
            }
        } catch (error) {
            console.error('Error submitting answer:', error);
            showNotification('{{ t("error_connection") }}', 'error');
        }
    }
    
    showResults(results) {
        const container = document.getElementById('domain-results-container');
        if (!container) return;
        
        container.style.display = 'block';
        container.innerHTML = `
            <div class="results-header">
                <h2>{{ t("diagnostic_completed") }}</h2>
                <p>{{ t("domain") }}: ${this.currentDomain.name}</p>
            </div>
            
            <div class="results-summary">
                <div class="result-stat">
                    <span class="stat-label">{{ t("final_score") }}:</span>
                    <span class="stat-value">${results.final_score}%</span>
                </div>
                <div class="result-stat">
                    <span class="stat-label">{{ t("ability_estimate") }}:</span>
                    <span class="stat-value">${results.ability_estimate.toFixed(2)}</span>
                </div>
                <div class="result-stat">
                    <span class="stat-label">{{ t("questions_answered") }}:</span>
                    <span class="stat-value">${results.questions_answered}</span>
                </div>
            </div>
            
            <div class="results-actions">
                <button class="btn-secondary" onclick="domainManager.showDomainSelector()">
                    {{ t("back_to_domains") }}
                </button>
                <button class="btn-primary" onclick="domainManager.generateLearningPlan()">
                    {{ t("generate_learning_plan") }}
                </button>
            </div>
        `;
    }
    
    showDomainSelector() {
        // Показать селектор доменов
        const domainSelector = document.getElementById('domain-selector');
        if (domainSelector) {
            domainSelector.style.display = 'block';
        }
        
        // Скрыть контейнеры вопросов и результатов
        const questionContainer = document.getElementById('domain-question-container');
        const resultsContainer = document.getElementById('domain-results-container');
        
        if (questionContainer) questionContainer.style.display = 'none';
        if (resultsContainer) resultsContainer.style.display = 'none';
        
        // Сбросить текущую сессию
        this.currentSession = null;
        this.currentDomain = null;
    }
    
    async generateLearningPlan() {
        if (!this.currentSession) return;
        
        try {
            const response = await fetch('/big-diagnostic/generate-learning-plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    session_id: this.currentSession
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Перенаправить на страницу плана обучения
                window.location.href = `/dashboard/learning-plan/${data.plan_id}`;
            } else {
                showNotification(data.error || '{{ t("error_generating_plan") }}', 'error');
            }
        } catch (error) {
            console.error('Error generating learning plan:', error);
            showNotification('{{ t("error_connection") }}', 'error');
        }
    }
}

// Вспомогательные функции
function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
}

function showNotification(message, type = 'info') {
    // Использовать существующую систему уведомлений или создать простую
    if (window.showNotification) {
        window.showNotification(message, type);
    } else {
        alert(message);
    }
}

function showLoadingIndicator(message) {
    // Показать индикатор загрузки
    const loader = document.createElement('div');
    loader.className = 'loading-overlay';
    loader.innerHTML = `
        <div class="loading-content">
            <div class="spinner"></div>
            <p>${message}</p>
        </div>
    `;
    document.body.appendChild(loader);
}

function hideLoadingIndicator() {
    const loader = document.querySelector('.loading-overlay');
    if (loader) {
        loader.remove();
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('domain-diagnostic-page')) {
        window.domainManager = new DomainDiagnosticManager();
    }
}); 