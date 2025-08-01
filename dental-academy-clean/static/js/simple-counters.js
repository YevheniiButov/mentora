/* ===== СИСТЕМА ПРОСТЫХ СЧЕТЧИКОВ ===== */
/* static/js/simple-counters.js */

class SimpleCounters {
    constructor() {
        this.counters = new Map();
        this.init();
    }

    init() {
        // Инициализация счетчиков при загрузке страницы
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeCounters();
        });
    }

    initializeCounters() {
        // Находим все элементы с атрибутом data-counter
        const counterElements = document.querySelectorAll('[data-counter]');
        
        counterElements.forEach(element => {
            const id = element.getAttribute('data-counter');
            const target = parseInt(element.getAttribute('data-target')) || 0;
            const duration = parseInt(element.getAttribute('data-duration')) || 2000;
            const format = element.getAttribute('data-format') || 'number';
            
            this.counters.set(id, {
                element,
                target,
                duration,
                format,
                current: 0
            });
            
            // Запускаем анимацию если элемент виден
            this.observeVisibility(id);
        });
    }

    observeVisibility(counterId) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateCounter(counterId);
                    observer.unobserve(entry.target);
                }
            });
        });

        const counter = this.counters.get(counterId);
        if (counter && counter.element) {
            observer.observe(counter.element);
        }
    }

    animateCounter(counterId) {
        const counter = this.counters.get(counterId);
        if (!counter) return;

        const { element, target, duration, format } = counter;
        let startTime = null;
        let current = 0;

        const animate = (currentTime) => {
            if (!startTime) startTime = currentTime;
            const progress = (currentTime - startTime) / duration;

            if (progress < 1) {
                current = Math.floor(target * progress);
                element.textContent = this.formatValue(current, format);
                requestAnimationFrame(animate);
            } else {
                element.textContent = this.formatValue(target, format);
                this.counters.get(counterId).current = target;
            }
        };

        requestAnimationFrame(animate);
    }

    formatValue(value, format) {
        switch (format) {
            case 'percentage':
                return `${value}%`;
            case 'currency':
                return new Intl.NumberFormat('ru-RU', {
                    style: 'currency',
                    currency: 'RUB'
                }).format(value);
            case 'compact':
                return new Intl.NumberFormat('ru-RU', {
                    notation: 'compact',
                    compactDisplay: 'short'
                }).format(value);
            default:
                return new Intl.NumberFormat('ru-RU').format(value);
        }
    }

    // Публичные методы для управления счетчиками
    startCounter(counterId) {
        if (this.counters.has(counterId)) {
            this.animateCounter(counterId);
        }
    }

    updateCounter(counterId, newTarget) {
        const counter = this.counters.get(counterId);
        if (counter) {
            counter.target = newTarget;
            this.animateCounter(counterId);
        }
    }

    resetCounter(counterId) {
        const counter = this.counters.get(counterId);
        if (counter) {
            counter.current = 0;
            counter.element.textContent = this.formatValue(0, counter.format);
        }
    }
}

// Инициализация системы счетчиков
document.addEventListener('DOMContentLoaded', () => {
    window.simpleCounters = new SimpleCounters();
}); 