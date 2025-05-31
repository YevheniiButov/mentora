/**
 * Dental Academy - Welcome Mobile JavaScript
 * Современный интерактивный опыт для мобильной welcome страницы
 */

class WelcomeMobileExperience {
    constructor() {
        this.config = {
            animationDuration: 600,
            intersectionThreshold: 0.1,
            counterAnimationDuration: 2000,
            quickTipDelay: 3000,
            parallaxFactor: 0.3
        };
        
        this.state = {
            isVisible: false,
            animationsEnabled: !window.matchMedia('(prefers-reduced-motion: reduce)').matches,
            countersAnimated: new Set(),
            quickTipShown: localStorage.getItem('quickTipShown') === 'true',
            installPromptDeferred: null,
            isOnline: navigator.onLine
        };
        
        this.observers = {
            animation: null,
            counter: null,
            performance: null
        };
        
        this.init();
    }
    
    // ===== ИНИЦИАЛИЗАЦИЯ =====
    async init() {
        console.log('🚀 Initializing Welcome Mobile Experience...');
        
        try {
            // Ожидаем загрузку DOM
            if (document.readyState === 'loading') {
                await new Promise(resolve => document.addEventListener('DOMContentLoaded', resolve));
            }
            
            // Основная инициализация
            this.setupAnimationSystem();
            this.setupCounterAnimations();
            this.setupParallaxEffects();
            this.setupQuickTips();
            this.setupCTATracking();
            this.setupThemeSystem();
            this.setupLanguageSystem();
            this.setupPWAFeatures();
            this.setupPerformanceMonitoring();
            this.setupAccessibilityFeatures();
            this.setupNetworkMonitoring();
            
            // Показать быструю подсказку
            setTimeout(() => this.showQuickTip(), this.config.quickTipDelay);
            
            console.log('✅ Welcome Mobile Experience initialized successfully');
            
        } catch (error) {
            console.error('❌ Error initializing Welcome Mobile Experience:', error);
            this.fallbackInit();
        }
    }
    
    // ===== СИСТЕМА АНИМАЦИЙ =====
    setupAnimationSystem() {
        if (!this.state.animationsEnabled) {
            console.log('⏸️ Animations disabled due to user preference');
            return;
        }
        
        // Настройка Intersection Observer для анимаций появления
        this.observers.animation = new IntersectionObserver(
            this.handleAnimationIntersection.bind(this),
            {
                threshold: this.config.intersectionThreshold,
                rootMargin: '0px 0px -50px 0px'
            }
        );
        
        // Наблюдение за анимируемыми элементами
        const animatedElements = document.querySelectorAll(
            '.fade-in-up, .fade-in-left, .fade-in-right, .fade-in'
        );
        
        animatedElements.forEach((element, index) => {
            // Добавляем задержку для поэтапного появления
            element.style.transitionDelay = `${index * 100}ms`;
            this.observers.animation.observe(element);
        });
        
        console.log(`🎭 Animation system setup complete. Observing ${animatedElements.length} elements`);
    }
    
    handleAnimationIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                this.observers.animation.unobserve(entry.target);
                
                // Запуск дополнительных эффектов
                this.triggerEnhancedEffects(entry.target);
            }
        });
    }
    
    triggerEnhancedEffects(element) {
        // Проверяем, есть ли у элемента специальные эффекты
        if (element.classList.contains('feature-card')) {
            this.enhanceFeatureCard(element);
        } else if (element.classList.contains('stat-card')) {
            this.enhanceStatCard(element);
        } else if (element.classList.contains('testimonial-card')) {
            this.enhanceTestimonialCard(element);
        }
    }
    
    enhanceFeatureCard(card) {
        const icon = card.querySelector('.feature-icon');
        if (icon) {
            setTimeout(() => {
                icon.style.transform = 'scale(1.1) rotate(5deg)';
                setTimeout(() => {
                    icon.style.transform = 'scale(1) rotate(0deg)';
                }, 200);
            }, 300);
        }
    }
    
    enhanceStatCard(card) {
        const number = card.querySelector('.stat-number');
        if (number && number.dataset.count) {
            setTimeout(() => {
                this.animateStatCounter(number);
            }, 200);
        }
    }
    
    enhanceTestimonialCard(card) {
        const avatar = card.querySelector('.author-avatar');
        if (avatar) {
            setTimeout(() => {
                avatar.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    avatar.style.transform = 'scale(1)';
                }, 300);
            }, 400);
        }
    }
    
    // ===== АНИМАЦИЯ СЧЕТЧИКОВ =====
    setupCounterAnimations() {
        this.observers.counter = new IntersectionObserver(
            this.handleCounterIntersection.bind(this),
            { threshold: 0.5 }
        );
        
        const counters = document.querySelectorAll('[data-count]');
        counters.forEach(counter => {
            this.observers.counter.observe(counter);
        });
    }
    
    handleCounterIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                const countId = element.dataset.count;
                
                if (!this.state.countersAnimated.has(countId)) {
                    this.animateStatCounter(element);
                    this.state.countersAnimated.add(countId);
                    this.observers.counter.unobserve(element);
                }
            }
        });
    }
    
    animateStatCounter(element) {
        const target = parseInt(element.dataset.count);
        const duration = this.config.counterAnimationDuration;
        const start = Date.now();
        
        // Определяем тип счетчика по контексту
        const label = element.parentElement.querySelector('.stat-label');
        const isPercentage = label && label.textContent.toLowerCase().includes('rate');
        const isThousands = target >= 1000;
        
        const updateCounter = () => {
            const now = Date.now();
            const progress = Math.min((now - start) / duration, 1);
            
            // Easing function (ease out cubic)
            const easeOutCubic = 1 - Math.pow(1 - progress, 3);
            const current = Math.floor(easeOutCubic * target);
            
            // Форматируем число в зависимости от типа
            if (isPercentage) {
                element.textContent = current + '%';
            } else if (isThousands) {
                element.textContent = (current / 1000).toFixed(1) + 'K';
            } else {
                element.textContent = current.toLocaleString();
            }
            
            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            } else {
                // Финальное форматирование
                if (isPercentage) {
                    element.textContent = target + '%';
                } else if (isThousands) {
                    element.textContent = (target / 1000).toFixed(1) + 'K';
                } else {
                    element.textContent = target.toLocaleString();
                }
                
                // Добавляем пульсацию в конце
                this.addCounterPulse(element);
            }
        };
        
        updateCounter();
    }
    
    addCounterPulse(element) {
        element.style.transform = 'scale(1.1)';
        element.style.transition = 'transform 0.2s ease';
        
        setTimeout(() => {
            element.style.transform = 'scale(1)';
        }, 200);
    }
    
    // ===== ПАРАЛЛАКС ЭФФЕКТЫ =====
    setupParallaxEffects() {
        if (!this.state.animationsEnabled) return;
        
        let ticking = false;
        
        const updateParallax = () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -this.config.parallaxFactor;
            
            // Параллакс для летающих орбов
            const orbs = document.querySelectorAll('.orb');
            orbs.forEach((orb, index) => {
                const speed = 0.3 + (index * 0.1);
                const yOffset = rate * speed;
                orb.style.transform = `translateY(${yOffset}px)`;
            });
            
            // Параллакс для hero контента
            const heroContent = document.querySelector('.hero-content');
            if (heroContent) {
                const heroOffset = scrolled * 0.1;
                heroContent.style.transform = `translateY(${heroOffset}px)`;
            }
            
            ticking = false;
        };
        
        const handleScroll = () => {
            if (!ticking) {
                requestAnimationFrame(updateParallax);
                ticking = true;
            }
        };
        
        window.addEventListener('scroll', handleScroll, { passive: true });
    }
    
    // ===== БЫСТРЫЕ ПОДСКАЗКИ =====
    setupQuickTips() {
        // Глобальные функции для управления подсказками
        window.showQuickTip = () => this.showQuickTip();
        window.closeQuickTip = () => this.closeQuickTip();
    }
    
    showQuickTip() {
        if (this.state.quickTipShown) return;
        
        const tip = document.getElementById('quickTip');
        if (!tip) return;
        
        // Проверяем, не в PWA ли мы уже
        const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
        const isIOSInstalled = window.navigator.standalone;
        
        if (isStandalone || isIOSInstalled) {
            return; // Не показываем подсказку если уже установлено
        }
        
        tip.classList.add('show');
        
        // Автоматически скрываем через 10 секунд
        setTimeout(() => {
            this.closeQuickTip();
        }, 10000);
    }
    
    closeQuickTip() {
        const tip = document.getElementById('quickTip');
        if (tip) {
            tip.classList.remove('show');
            this.state.quickTipShown = true;
            localStorage.setItem('quickTipShown', 'true');
        }
    }
    
    // ===== ОТСЛЕЖИВАНИЕ CTA =====
    setupCTATracking() {
        const ctaButtons = document.querySelectorAll('.cta-button, .final-cta-button');
        
        ctaButtons.forEach(button => {
            button.addEventListener('click', (event) => {
                this.handleCTAClick(button, event);
            });
            
            // Добавляем hover эффекты для десктопа
            if (window.matchMedia('(hover: hover)').matches) {
                this.addHoverEffects(button);
            }
        });
    }
    
    handleCTAClick(button, event) {
        const buttonText = button.querySelector('span')?.textContent || button.textContent;
        const section = this.getButtonSection(button);
        const href = button.href;
        
        console.log(`🎯 CTA Clicked:`, {
            text: buttonText,
            section: section,
            href: href
        });
        
        // Добавляем визуальный эффект клика
        this.addRippleEffect(button, event);
        
        // Отправляем аналитику
        this.trackCTAClick(buttonText, section, href);
        
        // Добавляем небольшую задержку для анимации
        if (href && !event.defaultPrevented) {
            event.preventDefault();
            setTimeout(() => {
                window.location.href = href;
            }, 150);
        }
    }
    
    addRippleEffect(button, event) {
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        const ripple = document.createElement('div');
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.5);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple-animation 0.6s linear;
            pointer-events: none;
            z-index: 1000;
        `;
        
        // Добавляем стили анимации если их еще нет
        if (!document.getElementById('ripple-styles')) {
            const style = document.createElement('style');
            style.id = 'ripple-styles';
            style.textContent = `
                @keyframes ripple-animation {
                    to {
                        transform: scale(4);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    }
    
    addHoverEffects(button) {
        button.addEventListener('mouseenter', () => {
            if (this.state.animationsEnabled) {
                button.style.transform = 'translateY(-2px) scale(1.02)';
            }
        });
        
        button.addEventListener('mouseleave', () => {
            if (this.state.animationsEnabled) {
                button.style.transform = 'translateY(0) scale(1)';
            }
        });
    }
    
    getButtonSection(button) {
        const section = button.closest('section');
        if (!section) return 'unknown';
        
        if (section.classList.contains('hero-section')) return 'hero';
        if (section.classList.contains('final-cta-section')) return 'final-cta';
        if (section.classList.contains('features-section')) return 'features';
        
        return 'unknown';
    }
    
    trackCTAClick(buttonText, section, href) {
        // Google Analytics
        if (typeof gtag !== 'undefined') {
            gtag('event', 'cta_click', {
                'button_text': buttonText,
                'section': section,
                'destination': href
            });
        }
        
        // Собственная аналитика
        if (typeof window.analytics !== 'undefined') {
            window.analytics.track('CTA Clicked', {
                buttonText,
                section,
                href,
                timestamp: Date.now(),
                userAgent: navigator.userAgent
            });
        }
    }
    
    // ===== СИСТЕМА ТЕМ =====
    setupThemeSystem() {
        const themeToggle = document.getElementById('mobile-theme-toggle');
        if (!themeToggle) return;
        
        // Инициализация темы
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.applyTheme(savedTheme);
        
        // Обработчик переключения темы
        themeToggle.addEventListener('click', () => {
            this.toggleTheme();
        });
        
        // Слушаем системные изменения темы
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                this.applyTheme(e.matches ? 'dark' : 'light');
            }
        });
    }
    
    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        this.applyTheme(newTheme);
        localStorage.setItem('theme', newTheme);
        
        // Показываем уведомление
        this.showToast(
            newTheme === 'dark' ? '🌙 Dark theme enabled' : '☀️ Light theme enabled',
            'success'
        );
    }
    
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        document.body.setAttribute('data-theme', theme);
        
        // Обновляем иконку кнопки
        const themeIcon = document.querySelector('.theme-icon');
        if (themeIcon) {
            themeIcon.className = `bi bi-${theme === 'dark' ? 'sun' : 'moon'} theme-icon`;
        }
        
        // Обновляем meta theme-color
        const metaTheme = document.querySelector('meta[name="theme-color"]');
        if (metaTheme) {
            metaTheme.content = theme === 'dark' ? '#1f2937' : '#667eea';
        }
    }
    
    // ===== ЯЗЫКОВАЯ СИСТЕМА =====
    setupLanguageSystem() {
        const languageToggle = document.getElementById('mobile-language-toggle');
        const languageDropdown = document.getElementById('mobile-language-dropdown');
        
        if (!languageToggle || !languageDropdown) return;
        
        // Открытие/закрытие dropdown
        languageToggle.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.toggleLanguageDropdown();
        });
        
        // Закрытие при клике вне
        document.addEventListener('click', (e) => {
            if (!languageToggle.contains(e.target) && !languageDropdown.contains(e.target)) {
                this.closeLanguageDropdown();
            }
        });
        
        // Обработка выбора языка
        const languageOptions = languageDropdown.querySelectorAll('.mobile-language-option');
        languageOptions.forEach(option => {
            option.addEventListener('click', (e) => {
                this.handleLanguageSelection(option, e);
            });
        });
    }
    
    toggleLanguageDropdown() {
        const dropdown = document.getElementById('mobile-language-dropdown');
        dropdown.classList.toggle('show');
    }
    
    closeLanguageDropdown() {
        const dropdown = document.getElementById('mobile-language-dropdown');
        dropdown.classList.remove('show');
    }
    
    handleLanguageSelection(option, event) {
        if (option.classList.contains('active')) {
            event.preventDefault();
            return;
        }
        
        // Показываем индикатор загрузки
        option.style.opacity = '0.7';
        option.style.pointerEvents = 'none';
        
        const loadingSpinner = document.createElement('i');
        loadingSpinner.className = 'bi bi-arrow-clockwise';
        loadingSpinner.style.animation = 'spin 1s linear infinite';
        option.appendChild(loadingSpinner);
        
        // Показываем уведомление
        this.showToast('🌍 Changing language...', 'info', 2000);
        
        // Добавляем стили для анимации
        if (!document.getElementById('spin-animation')) {
            const style = document.createElement('style');
            style.id = 'spin-animation';
            style.textContent = `
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    // ===== PWA ФУНКЦИИ =====
    setupPWAFeatures() {
        // Обработка события beforeinstallprompt
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.state.installPromptDeferred = e;
            console.log('📱 PWA install prompt available');
        });
        
        // Обработка установки
        window.addEventListener('appinstalled', () => {
            console.log('📱 PWA installed successfully');
            this.showToast('🎉 App installed successfully!', 'success');
            this.state.installPromptDeferred = null;
        });
        
        // Проверяем, запущены ли мы как PWA
        if (window.matchMedia('(display-mode: standalone)').matches) {
            console.log('📱 Running as PWA');
            document.body.classList.add('pwa-mode');
        }
    }
    
    // ===== МОНИТОРИНГ ПРОИЗВОДИТЕЛЬНОСТИ =====
    setupPerformanceMonitoring() {
        // Web Vitals мониторинг
        if ('PerformanceObserver' in window) {
            this.monitorLCP();
            this.monitorFID();
            this.monitorCLS();
        }
        
        // Мониторинг загрузки страницы
        window.addEventListener('load', () => {
            this.measurePageLoadPerformance();
        });
    }
    
    monitorLCP() {
        new PerformanceObserver((entryList) => {
            const entries = entryList.getEntries();
            const lastEntry = entries[entries.length - 1];
            console.log('📊 LCP:', lastEntry.startTime.toFixed(2) + 'ms');
            this.reportMetric('LCP', lastEntry.startTime);
        }).observe({ type: 'largest-contentful-paint', buffered: true });
    }
    
    monitorFID() {
        new PerformanceObserver((entryList) => {
            const entries = entryList.getEntries();
            const firstInput = entries[0];
            const fid = firstInput.processingStart - firstInput.startTime;
            console.log('📊 FID:', fid.toFixed(2) + 'ms');
            this.reportMetric('FID', fid);
        }).observe({ type: 'first-input', buffered: true });
    }
    
    monitorCLS() {
        let clsValue = 0;
        new PerformanceObserver((entryList) => {
            for (const entry of entryList.getEntries()) {
                if (!entry.hadRecentInput) {
                    clsValue += entry.value;
                }
            }
            console.log('📊 CLS:', clsValue.toFixed(4));
            this.reportMetric('CLS', clsValue);
        }).observe({ type: 'layout-shift', buffered: true });
    }
    
    measurePageLoadPerformance() {
        const navigation = performance.getEntriesByType('navigation')[0];
        const loadTime = navigation.loadEventEnd - navigation.loadEventStart;
        
        console.log('📊 Page Load Performance:', {
            'DNS Lookup': (navigation.domainLookupEnd - navigation.domainLookupStart).toFixed(2) + 'ms',
            'TCP Connection': (navigation.connectEnd - navigation.connectStart).toFixed(2) + 'ms',
            'Server Response': (navigation.responseEnd - navigation.requestStart).toFixed(2) + 'ms',
            'DOM Processing': (navigation.domContentLoadedEventEnd - navigation.responseEnd).toFixed(2) + 'ms',
            'Total Load Time': loadTime.toFixed(2) + 'ms'
        });
    }
    
    reportMetric(name, value) {
        // Отправляем метрики на сервер для анализа
        if (navigator.sendBeacon) {
            const data = {
                metric: name,
                value: value,
                url: window.location.pathname,
                userAgent: navigator.userAgent,
                timestamp: Date.now()
            };
            
            navigator.sendBeacon('/api/performance-metrics', JSON.stringify(data));
        }
    }
    
    // ===== ВОЗМОЖНОСТИ ДОСТУПНОСТИ =====
    setupAccessibilityFeatures() {
        // Управление с клавиатуры
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardNavigation(e);
        });
        
        // Высокий контраст
        if (window.matchMedia('(prefers-contrast: high)').matches) {
            document.body.classList.add('high-contrast');
        }
        
        // Уведомления для скринридеров
        this.setupScreenReaderAnnouncements();
    }
    
    handleKeyboardNavigation(e) {
        // Escape закрывает модальные окна
        if (e.key === 'Escape') {
            this.closeLanguageDropdown();
            this.closeQuickTip();
        }
        
        // Alt + L открывает языковое меню
        if (e.altKey && e.key.toLowerCase() === 'l') {
            e.preventDefault();
            this.toggleLanguageDropdown();
        }
        
        // Alt + T переключает тему
        if (e.altKey && e.key.toLowerCase() === 't') {
            e.preventDefault();
            this.toggleTheme();
        }
    }
    
    setupScreenReaderAnnouncements() {
        // Создаем live region для объявлений
        const liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'sr-only';
        liveRegion.id = 'screen-reader-announcements';
        document.body.appendChild(liveRegion);
    }
    
    announceToScreenReader(message, priority = 'polite') {
        const liveRegion = document.getElementById('screen-reader-announcements');
        if (liveRegion) {
            liveRegion.setAttribute('aria-live', priority);
            liveRegion.textContent = message;
            
            // Очищаем после объявления
            setTimeout(() => {
                liveRegion.textContent = '';
            }, 1000);
        }
    }
    
    // ===== МОНИТОРИНГ СЕТИ =====
    setupNetworkMonitoring() {
        // Отслеживание статуса сети
        window.addEventListener('online', () => {
            this.state.isOnline = true;
            this.showToast('🌐 Back online', 'success');
            console.log('🌐 Network: Online');
        });
        
        window.addEventListener('offline', () => {
            this.state.isOnline = false;
            this.showToast('📴 You\'re offline', 'warning');
            console.log('📴 Network: Offline');
        });
        
        // Мониторинг качества соединения
        if ('connection' in navigator) {
            const connection = navigator.connection;
            console.log('📡 Network Info:', {
                effectiveType: connection.effectiveType,
                downlink: connection.downlink,
                rtt: connection.rtt
            });
            
            connection.addEventListener('change', () => {
                console.log('📡 Network changed:', connection.effectiveType);
            });
        }
    }
    
    // ===== УВЕДОМЛЕНИЯ =====
    showToast(message, type = 'info', duration = 3000) {
        // Удаляем существующие уведомления
        const existingToasts = document.querySelectorAll('.welcome-toast');
        existingToasts.forEach(toast => toast.remove());
        
        // Создаем новое уведомление
        const toast = document.createElement('div');
        toast.className = `welcome-toast welcome-toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-icon">${this.getToastIcon(type)}</span>
                <span class="toast-message">${message}</span>
            </div>
        `;
        
        // Стили уведомления
        toast.style.cssText = `
            position: fixed;
            top: calc(var(--header-height) + 1rem);
            left: 1rem;
            right: 1rem;
            max-width: 350px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            z-index: 1000;
            transform: translateY(-100px);
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border-left: 4px solid ${this.getToastColor(type)};
        `;
        
        document.body.appendChild(toast);
        
        // Анимация появления
        requestAnimationFrame(() => {
            toast.style.transform = 'translateY(0)';
            toast.style.opacity = '1';
        });
        
        // Автоматическое скрытие
        if (duration > 0) {
            setTimeout(() => {
                toast.style.transform = 'translateY(-100px)';
                toast.style.opacity = '0';
                setTimeout(() => {
                    if (toast.parentNode) {
                        toast.parentNode.removeChild(toast);
                    }
                }, 300);
            }, duration);
        }
        
        // Объявляем для скринридеров
        this.announceToScreenReader(message);
    }
    
    getToastIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    }
    
    getToastColor(type) {
        const colors = {
            success: '#22c55e',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };
        return colors[type] || colors.info;
    }
    
    // ===== РЕЗЕРВНАЯ ИНИЦИАЛИЗАЦИЯ =====
    fallbackInit() {
        console.warn('🆘 Using fallback initialization');
        
        // Минимальная функциональность
        try {
            // Основные обработчики событий
            const ctaButtons = document.querySelectorAll('.cta-button, .final-cta-button');
            ctaButtons.forEach(button => {
                button.addEventListener('click', () => {
                    console.log('CTA clicked (fallback)');
                });
            });
            
            // Языковое меню
            const languageToggle = document.getElementById('mobile-language-toggle');
            const languageDropdown = document.getElementById('mobile-language-dropdown');
            
            if (languageToggle && languageDropdown) {
                languageToggle.addEventListener('click', (e) => {
                    e.preventDefault();
                    languageDropdown.classList.toggle('show');
                });
            }
            
            console.log('✅ Fallback initialization complete');
            
        } catch (error) {
            console.error('❌ Fallback initialization failed:', error);
        }
    }
    
    // ===== ОЧИСТКА =====
    destroy() {
        // Очищаем observers
        Object.values(this.observers).forEach(observer => {
            if (observer && typeof observer.disconnect === 'function') {
                observer.disconnect();
            }
        });
        
        // Удаляем глобальные функции
        delete window.showQuickTip;
        delete window.closeQuickTip;
        
        console.log('🧹 Welcome Mobile Experience destroyed');
    }
}

// ===== ИНИЦИАЛИЗАЦИЯ =====
document.addEventListener('DOMContentLoaded', () => {
    // Создаем глобальный экземпляр
    window.welcomeMobile = new WelcomeMobileExperience();
    
    // Дополнительные глобальные стили
    if (!document.getElementById('welcome-mobile-dynamic-styles')) {
        const style = document.createElement('style');
        style.id = 'welcome-mobile-dynamic-styles';
        style.textContent = `
            .toast-content {
                display: flex;
                align-items: center;
                gap: 0.75rem;
            }
            
            .toast-icon {
                font-size: 1.2rem;
                flex-shrink: 0;
            }
            
            .toast-message {
                flex: 1;
                font-weight: 500;
                color: #374151;
            }
            
            .sr-only {
                position: absolute;
                width: 1px;
                height: 1px;
                padding: 0;
                margin: -1px;
                overflow: hidden;
                clip: rect(0, 0, 0, 0);
                white-space: nowrap;
                border: 0;
            }
            
            .high-contrast .cta-button,
            .high-contrast .feature-card,
            .high-contrast .stat-card {
                border: 2px solid currentColor !important;
            }
            
            .pwa-mode .quick-tip {
                display: none !important;
            }
            
            @media (prefers-reduced-motion: reduce) {
                * {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                }
            }
        `;
        document.head.appendChild(style);
    }
});

// ===== ЭКСПОРТ ДЛЯ МОДУЛЬНОГО ИСПОЛЬЗОВАНИЯ =====
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WelcomeMobileExperience;
}

// ===== ГЛОБАЛЬНАЯ СОВМЕСТИМОСТЬ =====
window.WelcomeMobileExperience = WelcomeMobileExperience;