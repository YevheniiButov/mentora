/**
 * Унифицированная система обновления статистики
 * Автоматически обновляет статистику на всех страницах после завершения уроков
 */

class UnifiedStatsManager {
    constructor() {
        this.currentLang = document.documentElement.lang || 'ru';
        this.updateInterval = null;
        this.isUpdating = false;
        this.init();
    }

    init() {
        // Инициализируем обновление статистики
        this.setupEventListeners();
        this.setupAutoRefresh();
        
        console.log('✅ UnifiedStatsManager инициализирован');
    }

    setupEventListeners() {
        // Слушаем события завершения уроков
        document.addEventListener('lessonCompleted', (e) => {
            this.updateStats();
        });

        // Слушаем события сохранения прогресса
        document.addEventListener('progressSaved', (e) => {
            this.updateStats();
        });

        // Слушаем клики по кнопкам завершения урока
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="complete-lesson"], .complete-lesson-btn, .mark-completed')) {
                setTimeout(() => this.updateStats(), 1000);
            }
        });

        // Слушаем AJAX запросы на завершение урока
        this.interceptAjaxRequests();
    }

    interceptAjaxRequests() {
        // Перехватываем AJAX запросы для отслеживания завершения уроков
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const response = await originalFetch(...args);
            
            // Проверяем, является ли это запросом завершения урока
            const url = args[0];
            if (typeof url === 'string' && (
                url.includes('/mark-completed') ||
                url.includes('/save-progress') ||
                url.includes('/complete')
            )) {
                // Если запрос успешен, обновляем статистику
                if (response.ok) {
                    setTimeout(() => this.updateStats(), 500);
                }
            }
            
            return response;
        };
    }

    setupAutoRefresh() {
        // Автоматическое обновление статистики каждые 30 секунд
        this.updateInterval = setInterval(() => {
            if (!this.isUpdating) {
                this.updateStats(true); // silent update
            }
        }, 30000);
    }

    async updateStats(silent = false) {
        if (this.isUpdating) {
            console.log('🔄 Обновление статистики уже выполняется...');
            return;
        }

        this.isUpdating = true;

        try {
            if (!silent) {
                console.log('🔄 Обновление статистики...');
            }

            const response = await fetch(`/${this.currentLang}/api/update-stats`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.success) {
                this.updateUIWithStats(data.stats);
                
                if (!silent) {
                    console.log('✅ Статистика обновлена:', data.stats);
                    this.showSuccessMessage('Статистика обновлена');
                }
            } else {
                throw new Error(data.message || 'Неизвестная ошибка');
            }

        } catch (error) {
            console.error('❌ Ошибка обновления статистики:', error);
            
            if (!silent) {
                this.showErrorMessage(`Ошибка обновления статистики: ${error.message}`);
            }
        } finally {
            this.isUpdating = false;
        }
    }

    updateUIWithStats(stats) {
        // Обновляем все элементы статистики на странице
        
        // 1. Общий прогресс
        this.updateProgressElements(stats.overall_progress);
        
        // 2. Количество завершенных уроков
        this.updateCompletedLessons(stats.completed_lessons);
        
        // 3. Общее время обучения
        this.updateTimeSpent(stats.total_time_spent);
        
        // 4. Дни активности
        this.updateActiveDays(stats.active_days);
        
        // 5. Уровень и опыт
        this.updateLevelAndExperience(stats.level, stats.experience_points, stats.next_level_progress);
        
        // 6. Анимация обновления
        this.animateStatsUpdate();
    }

    updateProgressElements(progress) {
        // Обновляем все элементы с общим прогрессом
        const progressElements = document.querySelectorAll('[data-stat="overall-progress"], .overall-progress, .progress-percentage');
        
        progressElements.forEach(element => {
            const oldValue = element.textContent;
            const newValue = `${progress}%`;
            
            if (oldValue !== newValue) {
                // Анимация изменения значения
                this.animateValueChange(element, oldValue, newValue);
            }
        });

        // Обновляем прогресс-бары
        const progressBars = document.querySelectorAll('.progress-bar, .circular-progress');
        progressBars.forEach(bar => {
            const progressCircle = bar.querySelector('.progress-circle');
            if (progressCircle) {
                const circumference = 2 * Math.PI * 45; // радиус 45
                const offset = circumference - (progress / 100) * circumference;
                progressCircle.style.strokeDashoffset = offset;
            }
        });
    }

    updateCompletedLessons(completed) {
        const elements = document.querySelectorAll('[data-stat="completed-lessons"], .completed-lessons');
        elements.forEach(element => {
            const oldValue = element.textContent;
            const newValue = completed.toString();
            
            if (oldValue !== newValue) {
                this.animateValueChange(element, oldValue, newValue);
            }
        });
    }

    updateTimeSpent(timeSpent) {
        const elements = document.querySelectorAll('[data-stat="time-spent"], .time-spent');
        elements.forEach(element => {
            const oldValue = element.textContent;
            const newValue = `${timeSpent} мин`;
            
            if (oldValue !== newValue) {
                this.animateValueChange(element, oldValue, newValue);
            }
        });
    }

    updateActiveDays(days) {
        const elements = document.querySelectorAll('[data-stat="active-days"], .active-days');
        elements.forEach(element => {
            const oldValue = element.textContent;
            const newValue = days.toString();
            
            if (oldValue !== newValue) {
                this.animateValueChange(element, oldValue, newValue);
            }
        });
    }

    updateLevelAndExperience(level, experience, nextLevelProgress) {
        // Обновляем уровень
        const levelElements = document.querySelectorAll('[data-stat="level"], .user-level');
        levelElements.forEach(element => {
            element.textContent = level;
        });

        // Обновляем опыт
        const expElements = document.querySelectorAll('[data-stat="experience"], .experience-points');
        expElements.forEach(element => {
            element.textContent = experience;
        });

        // Обновляем прогресс до следующего уровня
        const nextLevelElements = document.querySelectorAll('[data-stat="next-level-progress"], .next-level-progress');
        nextLevelElements.forEach(element => {
            element.textContent = `${nextLevelProgress}%`;
        });
    }

    animateValueChange(element, oldValue, newValue) {
        // Простая анимация изменения значения
        element.style.transition = 'all 0.3s ease';
        element.style.transform = 'scale(1.1)';
        element.style.color = '#28a745';
        
        setTimeout(() => {
            element.textContent = newValue;
            element.style.transform = 'scale(1)';
            element.style.color = '';
        }, 150);
    }

    animateStatsUpdate() {
        // Анимация обновления статистики
        const statsContainer = document.querySelector('.stats-container, .progress-stats');
        if (statsContainer) {
            statsContainer.style.transition = 'all 0.3s ease';
            statsContainer.style.boxShadow = '0 0 20px rgba(40, 167, 69, 0.3)';
            
            setTimeout(() => {
                statsContainer.style.boxShadow = '';
            }, 300);
        }
    }

    showSuccessMessage(message) {
        // Показываем уведомление об успешном обновлении
        const notification = document.createElement('div');
        notification.className = 'stats-notification success';
        notification.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    showErrorMessage(message) {
        // Показываем уведомление об ошибке
        const notification = document.createElement('div');
        notification.className = 'stats-notification error';
        notification.innerHTML = `
            <i class="fas fa-exclamation-circle"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    // Публичные методы для внешнего использования
    refresh() {
        this.updateStats();
    }

    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.unifiedStatsManager = new UnifiedStatsManager();
});

// Экспорт для использования в других модулях
window.UnifiedStatsManager = UnifiedStatsManager; 