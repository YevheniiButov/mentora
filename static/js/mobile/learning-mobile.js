// JavaScript для мобильного обучения
// Вставьте сюда код для обучения 

// ===== МОБИЛЬНОЕ ОБУЧЕНИЕ =====
class MobileLearningController {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupSubjectCards();
        this.setupProgressAnimations();
        this.setupQuickActions();
        this.setupAchievements();
        this.setupRecommendations();
    }
    
    setupSubjectCards() {
        const subjectCards = document.querySelectorAll('.subject-card');
        
        subjectCards.forEach(card => {
            card.addEventListener('click', (e) => {
                if (!e.target.closest('.subject-action')) {
                    const link = card.querySelector('.subject-action.primary');
                    if (link) {
                        window.location.href = link.href;
                    }
                }
            });
            
            // Анимация при скролле
            this.observeElement(card, 'animate-in');
        });
    }
    
    setupProgressAnimations() {
        const progressBars = document.querySelectorAll('.progress-fill');
        
        progressBars.forEach(bar => {
            this.observeElement(bar, () => {
                const percentage = bar.getAttribute('data-percentage') || '0';
                bar.style.width = percentage + '%';
            });
        });
    }
    
    setupQuickActions() {
        const quickActions = document.querySelectorAll('.quick-action');
        
        quickActions.forEach(action => {
            action.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Показываем индикатор загрузки
                action.style.opacity = '0.7';
                action.style.pointerEvents = 'none';
                
                // Перенаправляем
                setTimeout(() => {
                    window.location.href = action.href;
                }, 300);
            });
        });
    }
    
    setupAchievements() {
        const achievements = document.querySelectorAll('.achievement-item.earned');
        
        achievements.forEach((achievement, index) => {
            setTimeout(() => {
                achievement.style.animation = 'achievementGlow 2s ease-in-out infinite';
            }, index * 200);
        });
    }
    
    setupRecommendations() {
        const recommendations = document.querySelectorAll('.recommendation-item');
        
        recommendations.forEach(item => {
            item.addEventListener('click', () => {
                const link = item.getAttribute('data-link');
                if (link) {
                    window.location.href = link;
                }
            });
        });
    }
    
    observeElement(element, callback) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    if (typeof callback === 'string') {
                        entry.target.classList.add(callback);
                    } else {
                        callback();
                    }
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        observer.observe(element);
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    window.mobileLearning = new MobileLearningController();
}); 