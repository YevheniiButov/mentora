// Enhanced Virtual Patient Results JavaScript
/**
 * Enhanced JavaScript для современной системы виртуальных пациентов
 * Включает анимации, геймификацию и интерактивные эффекты
 */

class EnhancedVirtualPatientResults {
    constructor() {
        this.chart = null;
        this.animationObserver = null;
        this.particles = [];
        this.isInitialized = false;
        this.tooltip = null;
        this.init();
    }

    /**
     * Инициализация системы
     */
    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeAll());
        } else {
            this.initializeAll();
        }
    }

    /**
     * Инициализация всех компонентов
     */
    initializeAll() {
        try {
            console.log('🚀 Initializing Enhanced Virtual Patient Results...');
            
            this.createParticleSystem();
            this.initializeScrollAnimations();
            this.createCompetencyChart();
            this.animateCounters();
            this.initializeTooltips();
            this.setupInteractiveEffects();
            this.animateProgressBars();
            this.initializeGamificationEffects();
            
            this.isInitialized = true;
            console.log('✅ Enhanced Virtual Patient Results initialized successfully!');
            
            // Показываем уведомление об успешной загрузке
            this.showNotification(window.t('system_loaded', window.lang) + ' 🎉', 'success');
            
        } catch (error) {
            console.error('❌ Error initializing Enhanced Virtual Patient Results:', error);
            this.showNotification(window.t('system_load_error', window.lang), 'error');
        }
    }

    /**
     * Создает систему частиц для фонового эффекта
     */
    createParticleSystem() {
        // Создаем контейнер для частиц, если его нет
        let particleContainer = document.querySelector('.particle-container');
        if (!particleContainer) {
            particleContainer = document.createElement('div');
            particleContainer.className = 'particle-container';
            document.body.appendChild(particleContainer);
        }

        // Создаем частицы
        for (let i = 0; i < 5; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.top = `${Math.random() * 100}%`;
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.animationDelay = `${Math.random() * 20}s`;
            particleContainer.appendChild(particle);
            this.particles.push(particle);
        }
    }

    /**
     * Инициализация анимаций при скролле
     */
    initializeScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        this.animationObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    
                    // Специальные анимации для разных типов элементов
                    if (entry.target.classList.contains('metric-card')) {
                        this.animateMetricCard(entry.target);
                    }
                    
                    if (entry.target.classList.contains('reward-card')) {
                        this.animateRewardCard(entry.target);
                    }
                }
            });
        }, observerOptions);

        // Добавляем наблюдение за элементами
        const elementsToAnimate = document.querySelectorAll(
            '.performance-overview, .metric-card, .reward-card, .competency-analysis, .decision-timeline'
        );
        
        elementsToAnimate.forEach(el => {
            el.classList.add('scroll-reveal');
            this.animationObserver.observe(el);
        });
    }

    /**
     * Получает данные компетенций с улучшенной обработкой
     */
    getCompetencyData() {
        let empathyScore = 50;
        let clinicalScore = 50;
        let communicationScore = 50;

        // Читаем данные из HTML структуры
        const competencyMetrics = document.querySelectorAll('.competency-metric');
        
        competencyMetrics.forEach(metric => {
            const nameElement = metric.querySelector('.competency-name');
            const scoreElement = metric.querySelector('.competency-score');
            
            if (nameElement && scoreElement) {
                const name = nameElement.textContent.toLowerCase();
                const scoreText = scoreElement.textContent.replace(/[^\d]/g, '');
                const score = parseInt(scoreText) || 50;
                
                // Масштабируем значения для лучшей визуализации
                const scaledScore = Math.max(score, 15);
                
                if (name.includes('эмпатия') || name.includes('емпатія') || name.includes('empathy')) {
                    empathyScore = scaledScore;
                } else if (name.includes('клинические') || name.includes('клінічні') || name.includes('clinical')) {
                    clinicalScore = scaledScore;
                } else if (name.includes('коммуникация') || name.includes('комунікація') || name.includes('communication')) {
                    communicationScore = scaledScore;
                }
            }
        });

        const efficiencyScore = this.calculateEfficiency();
        const decisionScore = this.calculateDecisionQuality();

        const data = {
            empathy: empathyScore,
            clinical: clinicalScore,
            communication: communicationScore,
            efficiency: efficiencyScore,
            decision: decisionScore
        };

        console.log('📊 Competency data for chart:', data);
        return data;
    }

    /**
     * Расчет эффективности на основе времени
     */
    calculateEfficiency() {
        const timeElements = document.querySelectorAll('.metric-value');
        let timeSpent = 360; // По умолчанию 6 минут

        timeElements.forEach(element => {
            const parent = element.closest('.metric-card');
            if (parent) {
                const label = parent.querySelector('.metric-label');
                if (label && label.textContent.includes(window.t('scenario_time', window.lang))) {
                    const timeText = element.textContent;
                    const minutes = parseInt(timeText);
                    if (!isNaN(minutes)) {
                        timeSpent = minutes * 60;
                    }
                }
            }
        });

        // Расчет эффективности: чем меньше времени, тем выше эффективность
        if (timeSpent < 300) return 90;      // Менее 5 минут - отлично
        if (timeSpent < 600) return 75;      // Менее 10 минут - хорошо
        if (timeSpent < 900) return 60;      // Менее 15 минут - удовлетворительно
        if (timeSpent < 1200) return 45;     // Менее 20 минут - ниже среднего
        return 30;                           // Более 20 минут - медленно
    }

    /**
     * Расчет качества решений
     */
    calculateDecisionQuality() {
        const scoreDisplay = document.querySelector('.score-value');
        if (scoreDisplay) {
            const scoreText = scoreDisplay.textContent;
            const scoreParts = scoreText.split('/');
            if (scoreParts.length === 2) {
                const totalScore = parseInt(scoreParts[0]);
                const maxScore = parseInt(scoreParts[1]);
                const percentage = maxScore > 0 ? (totalScore / maxScore) * 100 : 0;
                return Math.max(0, Math.min(100, Math.round(percentage)));
            }
        }
        return 50;
    }

    /**
     * Создает современную радарную диаграмму компетенций
     */
    createCompetencyChart() {
        const ctx = document.getElementById('competencyChart');
        
        if (!ctx) {
            console.warn('⚠️ Competency chart canvas not found');
            return;
        }
        
        if (typeof Chart === 'undefined') {
            console.error('❌ Chart.js not available');
            return;
        }
        
        const data = this.getCompetencyData();

        // Уничтожаем предыдущий график
        if (this.chart) {
            this.chart.destroy();
        }

        try {
            this.chart = new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: [
                        window.t('empathy', window.lang),
                        window.t('clinical_skills', window.lang),
                        window.t('communication', window.lang),
                        window.t('efficiency', window.lang),
                        window.t('decision_quality', window.lang)
                    ],
                    datasets: [{
                        label: window.t('your_results', window.lang),
                        data: [
                            data.empathy,
                            data.clinical,
                            data.communication,
                            data.efficiency,
                            data.decision
                        ],
                        backgroundColor: 'rgba(102, 126, 234, 0.2)',
                        borderColor: 'rgba(102, 126, 234, 1)',
                        pointBackgroundColor: 'rgba(102, 126, 234, 1)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgba(102, 126, 234, 1)'
                    }]
                },
                options: {
                    scales: {
                        r: {
                            angleLines: {
                                display: true
                            },
                            suggestedMin: 0,
                            suggestedMax: 100
                        }
                    }
                }
            });
        } catch (error) {
            console.error('❌ Error creating competency chart:', error);
        }
    }

    /**
     * Анимация счетчиков с улучшенными эффектами
     */
    animateCounters() {
        const counters = document.querySelectorAll('.metric-value, .reward-value, .score-value');
        
        counters.forEach((counter, index) => {
            // Задержка для каскадного эффекта
            setTimeout(() => {
                this.animateCounter(counter);
            }, index * 200);
        });
    }

    /**
     * Анимирует отдельный счетчик
     */
    animateCounter(element) {
        const text = element.textContent;
        const numbers = text.match(/\d+/g);
        
        if (!numbers) return;
        
        const target = parseInt(numbers[0]);
        const duration = 2000;
        const steps = 60;
        const increment = target / steps;
        const stepDuration = duration / steps;
        
        let current = 0;
        element.style.transform = 'scale(1.1)';
        
        const timer = setInterval(() => {
            current += increment;
            const displayValue = Math.min(Math.ceil(current), target);
            
            // Сохраняем оригинальный формат
            const newText = text.replace(/\d+/, displayValue);
            element.textContent = newText;
            
            // Добавляем пульсацию на важных значениях
            if (displayValue === target) {
                element.style.transform = 'scale(1)';
                element.style.transition = 'transform 0.3s ease';
                clearInterval(timer);
                
                // Финальная анимация
                setTimeout(() => {
                    element.style.transform = 'scale(1.05)';
                    setTimeout(() => {
                        element.style.transform = 'scale(1)';
                    }, 150);
                }, 100);
            }
        }, stepDuration);
    }

    /**
     * Инициализация всплывающих подсказок
     */
    initializeTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        
        tooltipElements.forEach(element => {
            element.classList.add('tooltip');
            
            element.addEventListener('mouseenter', (e) => {
                this.showTooltip(e.target);
            });
            
            element.addEventListener('mouseleave', (e) => {
                this.hideTooltip();
            });
        });
    }

    /**
     * Настройка интерактивных эффектов
     */
    setupInteractiveEffects() {
        // Магнитный эффект для кнопок и карточек
        const interactiveElements = document.querySelectorAll(
            '.metric-card, .reward-card, .competency-metric, .decision-score'
        );
        
        interactiveElements.forEach(element => {
            element.classList.add('magnetic-hover');
            
            element.addEventListener('mouseenter', (e) => {
                this.addInteractiveGlow(e.target);
            });
            
            element.addEventListener('mouseleave', (e) => {
                this.removeInteractiveGlow(e.target);
            });
        });

        // Ripple эффект для кликабельных элементов
        const clickableElements = document.querySelectorAll('.metric-card, .reward-card');
        clickableElements.forEach(element => {
            element.classList.add('button-ripple');
        });
    }

    /**
     * Анимация прогресс-баров
     */
    animateProgressBars() {
        const progressBars = document.querySelectorAll('.progress-fill');
        
        progressBars.forEach((bar, index) => {
            setTimeout(() => {
                const width = bar.style.width || '0%';
                bar.style.width = '0%';
                bar.style.transition = 'width 2s cubic-bezier(0.4, 0.0, 0.2, 1)';
                
                requestAnimationFrame(() => {
                    bar.style.width = width;
                });
            }, index * 300);
        });
    }

    /**
     * Инициализация эффектов геймификации
     */
    initializeGamificationEffects() {
        // Анимация появления наград
        const rewardCards = document.querySelectorAll('.reward-card');
        rewardCards.forEach((card, index) => {
            setTimeout(() => {
                card.style.transform = 'translateY(0) scale(1)';
                card.style.opacity = '1';
            }, index * 150);
        });

        // Добавляем обработчики для наград
        rewardCards.forEach(card => {
            card.addEventListener('click', () => {
                this.celebrateReward(card);
            });
        });

        // Анимация круговой диаграммы счета
        this.animateScoreCircle();
    }

    /**
     * Анимация кругового индикатора счета
     */
    animateScoreCircle() {
        const progressRing = document.querySelector('.progress-ring');
        const scoreValue = document.querySelector('.score-value');
        
        if (!progressRing || !scoreValue) return;
        
        const scoreText = scoreValue.textContent;
        const scoreParts = scoreText.split('/');
        
        if (scoreParts.length === 2) {
            const current = parseInt(scoreParts[0]);
            const max = parseInt(scoreParts[1]);
            const percentage = (current / max) * 100;
            
            // Радиус окружности
            const radius = 52;
            const circumference = 2 * Math.PI * radius;
            
            // Устанавливаем stroke-dasharray
            progressRing.style.strokeDasharray = circumference;
            progressRing.style.strokeDashoffset = circumference;
            
            // Анимируем
            setTimeout(() => {
                const offset = circumference - (percentage / 100) * circumference;
                progressRing.style.transition = 'stroke-dashoffset 2s cubic-bezier(0.4, 0.0, 0.2, 1)';
                progressRing.style.strokeDashoffset = offset;
            }, 500);
        }
    }

    /**
     * Анимация метрических карточек
     */
    animateMetricCard(card) {
        card.style.transform = 'translateY(20px)';
        card.style.opacity = '0';
        
        requestAnimationFrame(() => {
            card.style.transition = 'all 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
            card.style.transform = 'translateY(0)';
            card.style.opacity = '1';
        });
    }

    /**
     * Анимация карточек наград
     */
    animateRewardCard(card) {
        card.style.transform = 'scale(0.8) rotate(-5deg)';
        card.style.opacity = '0';
        
        requestAnimationFrame(() => {
            card.style.transition = 'all 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
            card.style.transform = 'scale(1) rotate(0deg)';
            card.style.opacity = '1';
        });
    }

    /**
     * Добавляет интерактивное свечение
     */
    addInteractiveGlow(element) {
        element.classList.add('interactive-glow');
    }

    /**
     * Убирает интерактивное свечение
     */
    removeInteractiveGlow(element) {
        element.classList.remove('interactive-glow');
    }

    /**
     * Празднование получения награды
     */
    celebrateReward(rewardCard) {
        // Создаем элемент празднования
        const celebration = document.createElement('div');
        celebration.className = 'achievement-celebration';
        document.body.appendChild(celebration);
        
        // Анимация карточки
        rewardCard.style.transform = 'scale(1.1)';
        rewardCard.style.transition = 'transform 0.3s ease';
        
        setTimeout(() => {
            rewardCard.style.transform = 'scale(1)';
        }, 300);
        
        // Удаляем элемент празднования
        setTimeout(() => {
            if (celebration.parentNode) {
                celebration.parentNode.removeChild(celebration);
            }
        }, 2000);
        
        this.showNotification(window.t('reward_received', window.lang) + ' 🏆', 'success');
    }

    /**
     * Показ уведомлений
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            transition: all 0.3s ease;
            transform: translateX(100%);
        `;
        
        // Стили в зависимости от типа
        if (type === 'success') {
            notification.style.background = 'linear-gradient(135deg, #10b981, #059669)';
        } else if (type === 'error') {
            notification.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
        } else {
            notification.style.background = 'linear-gradient(135deg, #3b82f6, #2563eb)';
        }
        
        document.body.appendChild(notification);
        
        // Показываем уведомление
        requestAnimationFrame(() => {
            notification.style.transform = 'translateX(0)';
        });
        
        // Скрываем через 3 секунды
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    /**
     * Обновляет диаграмму с новыми данными
     */
    updateChart() {
        if (this.chart) {
            const data = this.getCompetencyData();
            this.chart.data.datasets[0].data = [
                data.empathy,
                data.clinical,
                data.communication,
                data.efficiency,
                data.decision
            ];
            this.chart.update('active');
        }
    }

    /**
     * Добавляет эффекты печати
     */
    setupPrintEffects() {
        window.addEventListener('beforeprint', () => {
            // Останавливаем анимации перед печатью
            document.body.style.animation = 'none';
            const animatedElements = document.querySelectorAll('*');
            animatedElements.forEach(el => {
                el.style.animation = 'none';
                el.style.transition = 'none';
            });
        });
    }

    /**
     * Уничтожение системы (для очистки ресурсов)
     */
    destroy() {
        if (this.animationObserver) {
            this.animationObserver.disconnect();
        }
        
        if (this.chart) {
            this.chart.destroy();
        }
        
        // Удаляем частицы
        this.particles.forEach(particle => {
            if (particle.parentNode) {
                particle.parentNode.removeChild(particle);
            }
        });
        
        console.log('🧹 Enhanced Virtual Patient Results destroyed');
    }

    /**
     * Показывает всплывающую подсказку
     */
    showTooltip(element) {
        const tooltipText = element.getAttribute('data-tooltip');
        if (!tooltipText) return;

        // Создаем элемент подсказки, если его еще нет
        if (!this.tooltip) {
            this.tooltip = document.createElement('div');
            this.tooltip.className = 'tooltip-content';
            document.body.appendChild(this.tooltip);
        }

        // Устанавливаем текст и позицию
        this.tooltip.textContent = tooltipText;
        this.tooltip.style.display = 'block';

        // Позиционируем подсказку
        const rect = element.getBoundingClientRect();
        const tooltipRect = this.tooltip.getBoundingClientRect();

        this.tooltip.style.left = `${rect.left + (rect.width / 2) - (tooltipRect.width / 2)}px`;
        this.tooltip.style.top = `${rect.bottom + 10}px`;

        // Добавляем класс для анимации
        this.tooltip.classList.add('tooltip-visible');
    }

    /**
     * Скрывает всплывающую подсказку
     */
    hideTooltip() {
        if (this.tooltip) {
            this.tooltip.classList.remove('tooltip-visible');
            setTimeout(() => {
                if (this.tooltip) {
                    this.tooltip.style.display = 'none';
                }
            }, 200);
        }
    }
}

// Инициализация системы
const enhancedVpResults = new EnhancedVirtualPatientResults();

// Экспорт для использования в других скриптах
window.EnhancedVirtualPatientResults = EnhancedVirtualPatientResults;
window.vpResults = enhancedVpResults;

// Обработка ошибок
window.addEventListener('error', (e) => {
    console.error('🚨 Global error in Virtual Patient Results:', e.error);
});

// Оптимизация производительности
if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
        // Выполняем не критические операции когда браузер свободен
        enhancedVpResults.setupPrintEffects();
    });
}