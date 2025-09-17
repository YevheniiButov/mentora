/**
 * Diagnostic Type Selector
 * Управление выбором типа диагностики и взаимодействием с сервером
 */

class DiagnosticTypeSelector {
    constructor() {
        this.selectedType = null;
        this.isLoading = false;

        this.init();
    }

    init() {
        this.bindEvents();
        this.setupAnimations();
    }

    bindEvents() {
        // Обработка выбора типа диагностики
        document.querySelectorAll('.diagnostic-type-card').forEach(card => {
            card.addEventListener('click', (e) => this.handleTypeSelection(e));
        });

        // Обработка кнопки "Начать диагностику"
        const startButton = document.getElementById('start-diagnostic');
        if (startButton) {
            startButton.addEventListener('click', (e) => this.handleStartDiagnostic(e));
        }

        // Обработка клавиатуры
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    }

    setupAnimations() {
        // Добавляем анимации появления карточек
        const cards = document.querySelectorAll('.diagnostic-type-card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.3s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    handleTypeSelection(event) {
        const card = event.currentTarget;
        const type = card.dataset.type;

        // Убираем выделение со всех карточек
        document.querySelectorAll('.diagnostic-type-card').forEach(c => {
            c.classList.remove('selected');
        });

        // Выделяем выбранную карточку
        card.classList.add('selected');
        this.selectedType = type;

        // Активируем кнопку
        this.updateStartButton();
        
        // Добавляем тактильную обратную связь
        this.addHapticFeedback();
    }

    updateStartButton() {
        const startButton = document.getElementById('start-diagnostic');
        if (!startButton) return;

        if (this.selectedType) {
            startButton.disabled = false;
            startButton.textContent = `Начать ${this.getTypeDisplayName(this.selectedType)}`;
            startButton.classList.add('btn-pulse');
        } else {
            startButton.disabled = true;
            startButton.textContent = 'Начать диагностику';
            startButton.classList.remove('btn-pulse');
        }
    }

    getTypeDisplayName(type) {
        const names = {
            'readiness': 'полную диагностику',
            'express': 'быструю диагностику',
            'preliminary': 'стандартную диагностику'
        };
        return names[type] || 'диагностику';
    }

    async handleStartDiagnostic(event) {
        event.preventDefault();
        
        if (!this.selectedType || this.isLoading) return;

        this.isLoading = true;
        this.showLoading();

        try {
            const response = await this.sendStartRequest();
            await this.handleStartResponse(response);
        } catch (error) {
            console.error('Error starting diagnostic:', error);
            this.showErrorModal('Произошла ошибка при запуске диагностики');
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }

    async sendStartRequest() {

        // Получаем CSRF токен из мета-тега
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        
        const response = await fetch('/big-diagnostic/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken || ''
            },
            body: JSON.stringify({
                diagnostic_type: this.selectedType
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    async handleStartResponse(data) {
        if (data.success) {
            // Переходим к диагностике
            this.redirectToDiagnostic(data.redirect_url);
        } else if (data.error === 'active_session') {
            // Показываем модальное окно с активной сессией
            this.showActiveSessionModal(data.session_info);
        } else {
            // Показываем ошибку
            this.showErrorModal(data.message || 'Произошла ошибка при запуске диагностики');
        }
    }

    showActiveSessionModal(sessionInfo) {
        const isSameType = this.selectedType === sessionInfo.diagnostic_type;

        const content = this.createActiveSessionContent(sessionInfo);
        const actions = [
            {
                text: 'Продолжить',
                className: 'modal-btn modal-btn-primary',
                onclick: () => {
                    hideModal();
                    this.redirectToDiagnostic(`/big-diagnostic/question/${sessionInfo.id}`);
                }
            },
            {
                text: 'Перезапустить',
                className: 'modal-btn modal-btn-warning',
                onclick: () => {
                    hideModal();
                    this.restartSession();
                }
            },
            {
                text: 'Отмена',
                className: 'modal-btn modal-btn-secondary',
                onclick: hideModal
            }
        ];
        
        // Проверяем, есть ли выбранный тип и отличается ли он от текущей сессии
        if (!isSameType && this.selectedType) {

            actions.unshift({
                text: 'Начать выбранную диагностику',
                className: 'modal-btn modal-btn-primary',
                onclick: () => {
                    hideModal();
                    this.terminateAndStartNewSession();
                }
            });
        } else {

        }
        
        showModal('Активная сессия', content, actions);
    }

    createActiveSessionContent(sessionInfo) {
        const progress = sessionInfo.progress || 0;
        const startDate = new Date(sessionInfo.created_at).toLocaleString();
        
        return `
            <div class="active-session-info">
                <div class="session-summary">
                    <h4>У вас уже есть активная сессия диагностики:</h4>
                    <div class="session-details">
                        <div class="detail-item">
                            <span class="detail-label">Тип:</span>
                            <span class="detail-value">${this.getTypeDisplayName(sessionInfo.diagnostic_type)}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Прогресс:</span>
                            <span class="detail-value">${progress}%</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Начата:</span>
                            <span class="detail-value">${startDate}</span>
                        </div>
                    </div>
                </div>
                <div class="session-actions">
                    <p>Что вы хотите сделать?</p>
                </div>
            </div>
        `;
    }

    async restartSession() {
        this.showLoading();
        
        try {
            const response = await fetch('/big-diagnostic/restart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();
            
            if (data.success) {
                this.redirectToDiagnostic(data.redirect_url);
            } else {
                this.showErrorModal(data.message || 'Ошибка при перезапуске сессии');
            }
        } catch (error) {
            console.error('Error restarting session:', error);
            this.showErrorModal('Ошибка при перезапуске сессии');
        } finally {
            this.hideLoading();
        }
    }

    async terminateAndStartNewSession() {
        // Завершаем текущую сессию и запускаем новую с выбранным типом
        this.showLoading();
        try {
            await fetch('/big-diagnostic/session/terminate', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
            // После завершения — стартуем новую
            const response = await this.sendStartRequest();
            await this.handleStartResponse(response);
        } catch (error) {
            this.showErrorModal('Ошибка при запуске новой диагностики');
        } finally {
            this.hideLoading();
        }
    }

    showErrorModal(message) {
        showModal('Ошибка', `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${message}</p>
            </div>
        `, [
            { text: 'OK', className: 'modal-btn modal-btn-primary', onclick: hideModal }
        ]);
    }

    redirectToDiagnostic(url) {
        // Добавляем анимацию перехода
        document.body.style.opacity = '0';
        document.body.style.transition = 'opacity 0.3s ease';
        
        setTimeout(() => {
            window.location.href = url;
        }, 300);
    }

    handleKeyboard(event) {
        // Обработка клавиши Enter для запуска диагностики
        if (event.key === 'Enter' && this.selectedType && !this.isLoading) {
            const startButton = document.getElementById('start-diagnostic');
            if (startButton && !startButton.disabled) {
                startButton.click();
            }
        }

        // Обработка стрелок для навигации по карточкам
        if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
            this.navigateCards(event.key);
        }
    }

    navigateCards(direction) {
        const cards = Array.from(document.querySelectorAll('.diagnostic-type-card'));
        const currentIndex = cards.findIndex(card => card.classList.contains('selected'));
        
        let nextIndex;
        if (direction === 'ArrowLeft') {
            nextIndex = currentIndex > 0 ? currentIndex - 1 : cards.length - 1;
        } else {
            nextIndex = currentIndex < cards.length - 1 ? currentIndex + 1 : 0;
        }

        cards[nextIndex].click();
        cards[nextIndex].focus();
    }

    addHapticFeedback() {
        // Добавляем тактильную обратную связь (если поддерживается)
        if ('vibrate' in navigator) {
            navigator.vibrate(50);
        }
    }

    showLoading() {
        if (typeof showLoading === 'function') {
            showLoading();
        } else {
            const overlay = document.getElementById('loading-overlay');
            if (overlay) {
                overlay.style.display = 'flex';
            }
        }
    }

    hideLoading() {
        if (typeof hideLoading === 'function') {
            hideLoading();
        } else {
            const overlay = document.getElementById('loading-overlay');
            if (overlay) {
                overlay.style.display = 'none';
            }
        }
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем, что мы на странице выбора типа диагностики
    if (document.querySelector('.diagnostic-type-selector')) {
        new DiagnosticTypeSelector();
    }
});

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DiagnosticTypeSelector;
} 