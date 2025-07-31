/**
 * Achievement Integration for Learning Planner
 * Handles achievement notifications and progress tracking
 */

class AchievementIntegration {
    constructor() {
        this.achievements = [];
        this.progress = {};
        this.init();
    }
    
    async init() {
        // Загружаем достижения пользователя
        await this.loadUserAchievements();
        
        // Загружаем прогресс по достижениям
        await this.loadAchievementProgress();
        
        // Отображаем достижения
        this.displayAchievements();
        
        // Отображаем прогресс
        this.displayProgress();
    }
    
    async loadUserAchievements() {
        try {
            const response = await fetch('/api/user-achievements');
            if (response.ok) {
                this.achievements = await response.json();
            }
        } catch (error) {
            console.error('Error loading achievements:', error);
        }
    }
    
    async loadAchievementProgress() {
        try {
            const response = await fetch('/api/achievement-progress');
            if (response.ok) {
                this.progress = await response.json();
            }
        } catch (error) {
            console.error('Error loading progress:', error);
        }
    }
    
    displayAchievements() {
        const container = document.getElementById('achievements-container');
        if (!container) return;
        
        if (this.achievements.length === 0) {
            container.innerHTML = `
                <div class="no-achievements">
                    <i class="fas fa-trophy" style="font-size: 48px; color: #ccc; margin-bottom: 16px;"></i>
                    <p>Пока нет достижений. Продолжайте обучение!</p>
                </div>
            `;
            return;
        }
        
        const achievementsHTML = this.achievements.map(achievement => `
            <div class="achievement-card" style="
                background: white; 
                border-radius: 12px; 
                padding: 16px; 
                margin-bottom: 12px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border-left: 4px solid var(--${achievement.badge_color || 'primary'}-color);
            ">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div class="achievement-icon" style="
                        width: 48px; 
                        height: 48px; 
                        border-radius: 50%; 
                        background: linear-gradient(135deg, var(--${achievement.badge_color || 'primary'}-color), var(--${achievement.badge_color || 'primary'}-color-dark));
                        display: flex; 
                        align-items: center; 
                        justify-content: center; 
                        color: white;
                        font-size: 20px;
                    ">
                        <i class="fas fa-${achievement.icon}"></i>
                    </div>
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 4px 0; color: var(--text-color);">${achievement.name}</h4>
                        <p style="margin: 0; color: var(--text-muted); font-size: 14px;">${achievement.description}</p>
                        <small style="color: var(--text-muted);">Получено: ${achievement.earned_at}</small>
                    </div>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = achievementsHTML;
    }
    
    displayProgress() {
        const container = document.getElementById('achievement-progress');
        if (!container) return;
        
        const progressItems = [
            {
                name: 'Планы обучения',
                current: this.progress.plans_created || 0,
                target: 1,
                icon: 'calendar-check',
                color: 'primary'
            },
            {
                name: 'Дни подряд',
                current: this.progress.consecutive_days || 0,
                target: 30,
                icon: 'calendar-week',
                color: 'success'
            },
            {
                name: 'Достигнутые цели',
                current: this.progress.goals_achieved || 0,
                target: 5,
                icon: 'target',
                color: 'info'
            },
            {
                name: 'Готовность к экзамену',
                current: this.progress.readiness_percentage || 0,
                target: 80,
                icon: 'graduation-cap',
                color: 'danger'
            },
            {
                name: 'Часы обучения',
                current: this.progress.total_study_hours || 0,
                target: 100,
                icon: 'clock',
                color: 'secondary'
            }
        ];
        
        const progressHTML = progressItems.map(item => {
            const percentage = Math.min(100, (item.current / item.target) * 100);
            return `
                <div class="progress-item" style="margin-bottom: 16px;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <i class="fas fa-${item.icon}" style="color: var(--${item.color}-color); width: 16px;"></i>
                        <span style="font-weight: 600; color: var(--text-color);">${item.name}</span>
                        <span style="margin-left: auto; font-size: 14px; color: var(--text-muted);">
                            ${item.current}/${item.target}
                        </span>
                    </div>
                    <div class="progress-bar" style="
                        background: #e5e7eb; 
                        height: 8px; 
                        border-radius: 4px; 
                        overflow: hidden;
                    ">
                        <div class="progress-fill" style="
                            background: var(--${item.color}-color); 
                            height: 100%; 
                            width: ${percentage}%; 
                            transition: width 0.3s ease;
                        "></div>
                    </div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = progressHTML;
    }
    
    showAchievementNotification(achievement) {
        // Показываем уведомление о новом достижении
        if (window.notificationSystem) {
            window.notificationSystem.showCustomNotification(
                `🏆 Новое достижение: ${achievement.name}`,
                achievement.description,
                {
                    icon: '/static/images/medal.svg',
                    tag: 'achievement',
                    requireInteraction: true,
                    duration: 8000
                }
            );
        }
        
        // Показываем модальное окно с достижением
        this.showAchievementModal(achievement);
    }
    
    showAchievementModal(achievement) {
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed; 
            top: 0; 
            left: 0; 
            width: 100%; 
            height: 100%; 
            background: rgba(0,0,0,0.8); 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            z-index: 1000;
            animation: fadeIn 0.3s ease-out;
        `;
        
        modal.innerHTML = `
            <div style="
                background: white; 
                border-radius: 20px; 
                padding: 40px; 
                max-width: 500px; 
                width: 90%; 
                text-align: center;
                animation: scaleIn 0.3s ease-out;
            ">
                <div style="
                    width: 120px; 
                    height: 120px; 
                    border-radius: 50%; 
                    background: linear-gradient(135deg, var(--${achievement.badge_color || 'primary'}-color), var(--${achievement.badge_color || 'primary'}-color-dark));
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    margin: 0 auto 24px;
                    font-size: 48px;
                    color: white;
                    animation: bounce 1s ease-out;
                ">
                    <i class="fas fa-${achievement.icon}"></i>
                </div>
                
                <h2 style="margin: 0 0 16px 0; color: var(--text-color);">🏆 ${achievement.name}</h2>
                <p style="margin: 0 0 24px 0; color: var(--text-muted); font-size: 16px; line-height: 1.5;">
                    ${achievement.description}
                </p>
                
                <button onclick="this.closest('.achievement-modal').remove()" style="
                    background: var(--${achievement.badge_color || 'primary'}-color); 
                    color: white; 
                    border: none; 
                    padding: 12px 24px; 
                    border-radius: 8px; 
                    font-size: 16px; 
                    cursor: pointer;
                    transition: background 0.2s;
                ">
                    Отлично!
                </button>
            </div>
        `;
        
        modal.className = 'achievement-modal';
        document.body.appendChild(modal);
        
        // Автоматически закрываем через 5 секунд
        setTimeout(() => {
            if (modal.parentNode) {
                modal.remove();
            }
        }, 5000);
    }
    
    async checkForNewAchievements() {
        try {
            const response = await fetch('/api/check-achievements', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                
                if (result.new_achievements && result.new_achievements.length > 0) {
                    // Показываем уведомления о новых достижениях
                    for (const achievement of result.new_achievements) {
                        this.showAchievementNotification(achievement);
                    }
                    
                    // Обновляем список достижений
                    await this.loadUserAchievements();
                    this.displayAchievements();
                }
                
                // Обновляем прогресс
                await this.loadAchievementProgress();
                this.displayProgress();
            }
        } catch (error) {
            console.error('Error checking achievements:', error);
        }
    }
    
    // Методы для интеграции с планировщиком
    onPlanCreated() {
        // Проверяем достижения после создания плана
        setTimeout(() => {
            this.checkForNewAchievements();
        }, 1000);
    }
    
    onSessionCompleted() {
        // Проверяем достижения после завершения занятия
        setTimeout(() => {
            this.checkForNewAchievements();
        }, 1000);
    }
    
    onProgressUpdated() {
        // Проверяем достижения после обновления прогресса
        setTimeout(() => {
            this.checkForNewAchievements();
        }, 1000);
    }
}

// Глобальный экземпляр интеграции достижений
let achievementIntegration;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    achievementIntegration = new AchievementIntegration();
    
    // Интегрируем с планировщиком
    if (window.learningPlan) {
        window.learningPlan.onPlanCreated = () => {
            achievementIntegration.onPlanCreated();
        };
        
        window.learningPlan.onSessionCompleted = () => {
            achievementIntegration.onSessionCompleted();
        };
        
        window.learningPlan.onProgressUpdated = () => {
            achievementIntegration.onProgressUpdated();
        };
    }
});

// Добавляем CSS анимации
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes scaleIn {
        from { transform: scale(0.8); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-20px); }
        60% { transform: translateY(-10px); }
    }
    
    .achievement-card {
        transition: transform 0.2s ease;
    }
    
    .achievement-card:hover {
        transform: translateY(-2px);
    }
    
    .progress-fill {
        transition: width 0.3s ease;
    }
`;
document.head.appendChild(style);

// Экспорт для использования в других модулях
window.AchievementIntegration = AchievementIntegration; 