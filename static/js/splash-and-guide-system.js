/* ===== ФИНАЛЬНАЯ МУЛЬТИЯЗЫЧНАЯ СИСТЕМА СПЛЕШСКРИНА И ГАЙДОВ ===== */
/* static/js/splash-and-guide-system.js */

class SplashAndGuideSystem {
    constructor() {
        // Получаем текущий язык из window или HTML атрибута
        this.currentLanguage = window.currentLanguage || 
                              document.documentElement.lang || 
                              'en';
        
        // Инициализируем переводы
        this.translations = {};
        this.translationsLoaded = false;
        
        // Состояние пользователя
        this.userStatus = {
            isNewUser: true,
            shouldShowSplash: true,
            shouldShowGuide: true
        };
        
        // Настройки
        this.splashDuration = 3500; // Длительность сплеш-экрана
        this.guideDuration = 10000; // Время показа гайда
        
        // Флаги состояния
        this.isInitialized = false;
        this.splashShown = false;
        this.guideShown = false;
        
        this.init();
    }

    async init() {
        try {
            // Загружаем переводы и статус пользователя параллельно
            await Promise.all([
                this.loadTranslations(),
                this.loadUserStatus()
            ]);
            
            this.isInitialized = true;
            
            // Показываем сплеш-экран если нужно
            if (this.shouldShowContent()) {
                this.showSplashScreen();
            }
            
            console.log('🎬 Splash and Guide System initialized successfully');
            
        } catch (error) {
            console.error('❌ Error initializing Splash and Guide System:', error);
            // Используем fallback функциональность
            this.setFallbackMode();
        }
    }

    shouldShowContent() {
        return window.location.pathname.includes('/learning-map') && 
               this.userStatus.shouldShowSplash && 
               !this.splashShown &&
               this.userStatus.isNewUser;
    }

    async loadTranslations() {
        try {
            const response = await fetch(`/api/splash-guide-translations?lang=${this.currentLanguage}`);
            if (response.ok) {
                this.translations = await response.json();
                this.translationsLoaded = true;
                console.log('✅ Translations loaded successfully');
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.warn('⚠️ Could not load translations from API, using fallback');
            this.setFallbackTranslations();
        }
    }

    async loadUserStatus() {
        try {
            const response = await fetch('/api/user-onboarding-status');
            if (response.ok) {
                this.userStatus = await response.json();
                console.log('✅ User status loaded:', this.userStatus);
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.warn('⚠️ Could not load user status, using defaults');
            // Используем localStorage как fallback
            this.userStatus = {
                isNewUser: !localStorage.getItem('dental_academy_visited'),
                shouldShowSplash: !localStorage.getItem('dental_academy_visited'),
                shouldShowGuide: !localStorage.getItem('dental_academy_guide_completed'),
                currentLanguage: this.currentLanguage
            };
        }
    }

    setFallbackMode() {
        this.setFallbackTranslations();
        this.userStatus = {
            isNewUser: !localStorage.getItem('dental_academy_visited'),
            shouldShowSplash: !localStorage.getItem('dental_academy_visited'),
            shouldShowGuide: !localStorage.getItem('dental_academy_guide_completed'),
            currentLanguage: this.currentLanguage
        };
        this.isInitialized = true;
        
        if (this.shouldShowContent()) {
            this.showSplashScreen();
        }
    }

    setFallbackTranslations() {
        this.translations = {
            [this.currentLanguage]: {
                'splash': {
                    'loading_steps': this.currentLanguage === 'ru' ? [
                        'Инициализация системы обучения...',
                        'Загрузка учебных материалов...',
                        'Подготовка интерактивных элементов...',
                        'Почти готово...',
                        'Добро пожаловать!'
                    ] : [
                        'Initializing learning system...',
                        'Loading study materials...',
                        'Preparing interactive elements...',
                        'Almost ready...',
                        'Welcome!'
                    ],
                    'quotes': this.currentLanguage === 'ru' ? [
                        "Каждый шаг в обучении приближает вас к мечте стать отличным стоматологом"
                    ] : [
                        "Every step in learning brings you closer to your dream of becoming an excellent dentist"
                    ]
                },
                'guide': {
                    'welcome_title': this.currentLanguage === 'ru' ? 
                        '🎓 Добро пожаловать в Dental Academy!' : 
                        '🎓 Welcome to Dental Academy!',
                    'welcome_subtitle': this.currentLanguage === 'ru' ? 
                        'Давайте быстро познакомимся с платформой' : 
                        "Let's quickly get acquainted with the platform",
                    'navigation': {
                        'prev': this.currentLanguage === 'ru' ? '← Назад' : '← Back',
                        'next': this.currentLanguage === 'ru' ? 'Далее →' : 'Next →',
                        'start': this.currentLanguage === 'ru' ? 'Начать обучение!' : 'Start learning!',
                        'skip': this.currentLanguage === 'ru' ? 'Пропустить гайд' : 'Skip guide',
                        'dont_show': this.currentLanguage === 'ru' ? 'Больше не показывать' : "Don't show again"
                    }
                }
            },
            'en': {
                'splash': {
                    'loading_steps': [
                        'Initializing learning system...',
                        'Loading study materials...',
                        'Preparing interactive elements...',
                        'Almost ready...',
                        'Welcome!'
                    ],
                    'quotes': [
                        "Every step in learning brings you closer to your dream of becoming an excellent dentist"
                    ]
                },
                'guide': {
                    'welcome_title': '🎓 Welcome to Dental Academy!',
                    'welcome_subtitle': "Let's quickly get acquainted with the platform",
                    'navigation': {
                        'prev': '← Back',
                        'next': 'Next →',
                        'start': 'Start learning!',
                        'skip': 'Skip guide',
                        'dont_show': "Don't show again"
                    }
                }
            }
        };
        this.translationsLoaded = true;
    }

    t(key, fallback = '') {
        if (!this.translationsLoaded) {
            return fallback || key;
        }
        
        const keys = key.split('.');
        let current = this.translations[this.currentLanguage];
        
        if (!current && this.currentLanguage !== 'en') {
            current = this.translations['en'];
        }
        
        if (!current) {
            return fallback || key;
        }
        
        for (const k of keys) {
            if (current && typeof current === 'object' && k in current) {
                current = current[k];
            } else {
                if (this.currentLanguage !== 'en' && this.translations['en']) {
                    current = this.translations['en'];
                    for (const k2 of keys) {
                        if (current && typeof current === 'object' && k2 in current) {
                            current = current[k2];
                        } else {
                            return fallback || key;
                        }
                    }
                    return current;
                }
                return fallback || key;
            }
        }
        
        return current || fallback || key;
    }

    showSplashScreen() {
        if (this.splashShown) return;
        
        console.log('🎬 Showing splash screen for new user');
        this.splashShown = true;
        
        const loadingSteps = this.t('splash.loading_steps', [
            'Loading...', 'Preparing...', 'Almost ready...', 'Welcome!'
        ]);
        
        const quotes = this.t('splash.quotes', [
            "Welcome to your learning journey!"
        ]);
        
        const splashHTML = `
            <div id="dental-academy-splash" class="splash-overlay" role="dialog" aria-modal="true" aria-labelledby="splash-title">
                <div class="splash-container">
                    <!-- Скрытый заголовок для screen readers -->
                    <h1 id="splash-title" class="sr-only">Dental Academy Loading</h1>
                    
                    <!-- Анимированный логотип с favicon -->
                    <div class="splash-logo-container">
                        <div class="logo-animation">
                            <div class="logo-rings" aria-hidden="true">
                                <div class="ring ring-1"></div>
                                <div class="ring ring-2"></div>
                                <div class="ring ring-3"></div>
                            </div>
                            <div class="logo-center">
                                <img src="/static/favicon.png" 
                                     alt="Dental Academy Logo" 
                                     class="favicon-logo"
                                     loading="eager">
                            </div>
                        </div>
                        
                        <div class="logo-text">
                            <h2 class="logo-title" aria-label="Dental Academy">
                                <span class="logo-dental">Dental</span>
                                <span class="logo-academy">Academy</span>
                            </h2>
                            <p class="logo-subtitle">Preparing for Excellence</p>
                        </div>
                    </div>
                    
                    <!-- Прогресс бар -->
                    <div class="splash-progress" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">
                        <div class="progress-container">
                            <div class="progress-bar">
                                <div class="progress-fill" id="splash-progress-fill"></div>
                            </div>
                            <div class="progress-text">
                                <span id="loading-text" aria-live="polite">${loadingSteps[0]}</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Мотивационная цитата -->
                    <div class="splash-quote">
                        <p id="motivational-quote" aria-live="polite">
                            ${quotes[0]}
                        </p>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', splashHTML);
        
        // Устанавливаем фокус на сплеш для screen readers
        const splash = document.getElementById('dental-academy-splash');
        splash.focus();
        
        this.addSplashStyles();
        this.animateLoading();
        
        setTimeout(() => {
            this.hideSplashScreen();
        }, this.splashDuration);
    }

    addSplashStyles() {
        if (document.getElementById('splash-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'splash-styles';
        styles.textContent = `
            /* Screen reader only класс */
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

            .splash-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: linear-gradient(135deg, 
                    #667eea 0%, 
                    #764ba2 25%, 
                    #3ECDC1 50%,
                    #667eea 75%,
                    #764ba2 100%);
                background-size: 400% 400%;
                animation: gradientShift 4s ease-in-out infinite;
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                opacity: 1;
                transition: opacity 0.5s ease-out;
                outline: none;
            }

            .splash-overlay.fade-out {
                opacity: 0;
                pointer-events: none;
            }

            .splash-container {
                text-align: center;
                color: white;
                max-width: 500px;
                padding: 2rem;
            }

            .splash-logo-container {
                margin-bottom: 3rem;
            }

            .logo-animation {
                position: relative;
                width: 150px;
                height: 150px;
                margin: 0 auto 2rem;
            }

            .logo-rings {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
            }

            .ring {
                position: absolute;
                border: 3px solid rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                animation: ringPulse 2s ease-in-out infinite;
            }

            .ring-1 {
                width: 80px;
                height: 80px;
                top: 35px;
                left: 35px;
                border-color: rgba(62, 205, 193, 0.8);
                animation-delay: 0s;
            }

            .ring-2 {
                width: 110px;
                height: 110px;
                top: 20px;
                left: 20px;
                border-color: rgba(108, 92, 231, 0.6);
                animation-delay: 0.5s;
            }

            .ring-3 {
                width: 150px;
                height: 150px;
                top: 0;
                left: 0;
                border-color: rgba(253, 203, 110, 0.4);
                animation-delay: 1s;
            }

            .logo-center {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 80px;
                height: 80px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                backdrop-filter: blur(10px);
                animation: centerPulse 3s ease-in-out infinite;
                padding: 10px;
                box-sizing: border-box;
            }

            .favicon-logo {
                width: 60px;
                height: 60px;
                object-fit: contain;
                animation: logoFloat 4s ease-in-out infinite;
                filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.3));
            }

            .logo-text {
                animation: fadeInUp 1s ease-out 0.5s both;
            }

            .logo-title {
                margin: 0 0 0.5rem 0;
                font-size: 2.5rem;
                font-weight: 700;
                line-height: 1.2;
            }

            .logo-dental {
                background: linear-gradient(45deg, #3ECDC1, #4FD1C7);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                display: block;
            }

            .logo-academy {
                background: linear-gradient(45deg, #6C5CE7, #8983F3);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                display: block;
            }

            .logo-subtitle {
                font-size: 1.1rem;
                opacity: 0.9;
                font-style: italic;
                margin: 0;
                letter-spacing: 0.1em;
            }

            .splash-progress {
                margin-bottom: 2rem;
                animation: fadeInUp 1s ease-out 1s both;
            }

            .progress-container {
                width: 100%;
                max-width: 400px;
                margin: 0 auto;
            }

            .progress-bar {
                width: 100%;
                height: 8px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                overflow: hidden;
                margin-bottom: 1rem;
                position: relative;
            }

            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #3ECDC1, #6C5CE7, #FDCB6E);
                border-radius: 4px;
                width: 0%;
                transition: width 0.3s ease;
                position: relative;
                overflow: hidden;
            }

            .progress-fill::after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
                animation: shimmer 1.5s infinite;
            }

            .progress-text {
                font-size: 0.9rem;
                opacity: 0.9;
                min-height: 1.2em;
            }

            .splash-quote {
                animation: fadeInUp 1s ease-out 1.5s both;
            }

            .splash-quote p {
                font-size: 1rem;
                font-style: italic;
                opacity: 0.8;
                margin: 0;
                padding: 0 1rem;
                line-height: 1.5;
            }

            /* Анимации */
            @keyframes gradientShift {
                0%, 100% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
            }

            @keyframes ringPulse {
                0%, 100% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.1); opacity: 0.7; }
            }

            @keyframes centerPulse {
                0%, 100% { transform: translate(-50%, -50%) scale(1); }
                50% { transform: translate(-50%, -50%) scale(1.1); }
            }

            @keyframes logoFloat {
                0%, 100% { transform: translateY(0) rotate(0deg); }
                25% { transform: translateY(-5px) rotate(2deg); }
                75% { transform: translateY(5px) rotate(-2deg); }
            }

            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            @keyframes shimmer {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(100%); }
            }

            /* Адаптивность */
            @media (max-width: 768px) {
                .splash-container {
                    padding: 1rem;
                }
                
                .logo-animation {
                    width: 120px;
                    height: 120px;
                }
                
                .logo-title {
                    font-size: 2rem;
                }
                
                .ring-1 { width: 60px; height: 60px; top: 30px; left: 30px; }
                .ring-2 { width: 90px; height: 90px; top: 15px; left: 15px; }
                .ring-3 { width: 120px; height: 120px; top: 0; left: 0; }
                
                .logo-center {
                    width: 60px;
                    height: 60px;
                }
                
                .favicon-logo {
                    width: 40px;
                    height: 40px;
                }
            }

            /* Для людей с ограниченными возможностями */
            @media (prefers-reduced-motion: reduce) {
                .splash-overlay,
                .ring,
                .logo-center,
                .favicon-logo,
                .progress-fill::after {
                    animation: none !important;
                }
                
                .logo-text,
                .splash-progress,
                .splash-quote {
                    animation: none !important;
                    opacity: 1 !important;
                    transform: none !important;
                }
            }

            /* Высокий контраст */
            @media (prefers-contrast: high) {
                .splash-overlay {
                    background: #000;
                }
                
                .logo-dental,
                .logo-academy {
                    background: #fff;
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }
                
                .progress-fill {
                    background: #fff;
                }
            }
        `;
        
        document.head.appendChild(styles);
    }

    animateLoading() {
        const progressFill = document.getElementById('splash-progress-fill');
        const loadingText = document.getElementById('loading-text');
        const motivationalQuote = document.getElementById('motivational-quote');
        const progressBar = document.querySelector('[role="progressbar"]');
        
        if (!progressFill) return;

        const loadingSteps = this.t('splash.loading_steps', [
            'Loading...', 'Preparing...', 'Almost ready...', 'Welcome!'
        ]);
        
        const quotes = this.t('splash.quotes', [
            "Welcome to your learning journey!"
        ]);

        const steps = [
            { progress: 20, textIndex: 0, delay: 300 },
            { progress: 45, textIndex: 1, delay: 600 },
            { progress: 70, textIndex: 2, delay: 900 },
            { progress: 90, textIndex: 3, delay: 1200 },
            { progress: 100, textIndex: 4, delay: 1500 }
        ];

        let currentStep = 0;
        
        const animateStep = () => {
            if (currentStep < steps.length) {
                const step = steps[currentStep];
                const textIndex = Math.min(step.textIndex, loadingSteps.length - 1);
                
                progressFill.style.width = step.progress + '%';
                
                // Обновляем aria-valuenow для доступности
                if (progressBar) {
                    progressBar.setAttribute('aria-valuenow', step.progress);
                }
                
                if (loadingText && loadingSteps[textIndex]) {
                    loadingText.textContent = loadingSteps[textIndex];
                }
                
                // Меняем цитату на половине загрузки
                if (currentStep === 2 && motivationalQuote && quotes.length > 1) {
                    const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
                    motivationalQuote.style.opacity = '0';
                    setTimeout(() => {
                        motivationalQuote.textContent = randomQuote;
                        motivationalQuote.style.opacity = '0.8';
                    }, 300);
                }
                
                currentStep++;
                setTimeout(animateStep, step.delay);
            }
        };
        
        setTimeout(animateStep, 200);
    }

    hideSplashScreen() {
        const splash = document.getElementById('dental-academy-splash');
        if (splash) {
            splash.classList.add('fade-out');
            
            setTimeout(() => {
                splash.remove();
                
                // Удаляем стили сплеша
                const splashStyles = document.getElementById('splash-styles');
                if (splashStyles) {
                    splashStyles.remove();
                }
                
                // Показываем гайд для новых пользователей
                if (this.userStatus.shouldShowGuide && !this.guideShown) {
                    setTimeout(() => {
                        this.showNewUserGuide();
                    }, 500);
                }
                
                // Отмечаем завершение сплеша
                this.markSplashCompleted();
                
            }, 500);
        }
    }

    async markSplashCompleted() {
        try {
            await fetch('/api/complete-onboarding', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    completed_splash: true
                })
            });
        } catch (error) {
            console.warn('Could not update splash completion status:', error);
            // Fallback на localStorage
            localStorage.setItem('dental_academy_visited', 'true');
        }
    }

    showNewUserGuide() {
        if (this.guideShown) return;
        
        console.log('📚 Showing new user guide');
        this.guideShown = true;
        
        const guideHTML = `
            <div id="new-user-guide" class="guide-overlay" role="dialog" aria-modal="true" aria-labelledby="guide-title">
                <div class="guide-container">
                    <div class="guide-header">
                        <h2 id="guide-title">${this.t('guide.welcome_title', '🎓 Welcome to Dental Academy!')}</h2>
                        <p>${this.t('guide.welcome_subtitle', "Let's quickly get acquainted with the platform")}</p>
                    </div>
                    
                    <div class="guide-content">
                        <div class="guide-steps" role="region" aria-live="polite" aria-label="Guide steps">
                            ${this.generateGuideSteps()}
                        </div>
                        
                        <div class="guide-navigation" role="toolbar" aria-label="Guide navigation">
                            <button id="guide-prev" class="guide-btn secondary" disabled 
                                    aria-label="${this.t('guide.navigation.prev', '← Back')}">
                                ${this.t('guide.navigation.prev', '← Back')}
                            </button>
                            <div class="guide-dots" role="tablist" aria-label="Guide progress">
                                <button class="dot active" data-step="1" role="tab" aria-selected="true" 
                                        aria-label="Step 1 of 3"></button>
                                <button class="dot" data-step="2" role="tab" aria-selected="false" 
                                        aria-label="Step 2 of 3"></button>
                                <button class="dot" data-step="3" role="tab" aria-selected="false" 
                                        aria-label="Step 3 of 3"></button>
                            </div>
                            <button id="guide-next" class="guide-btn primary"
                                    aria-label="${this.t('guide.navigation.next', 'Next →')}">
                                ${this.t('guide.navigation.next', 'Next →')}
                            </button>
                        </div>
                    </div>
                    
                    <div class="guide-footer">
                        <label class="guide-checkbox">
                            <input type="checkbox" id="dont-show-again">
                            <span>${this.t('guide.navigation.dont_show', "Don't show again")}</span>
                        </label>
                        <button id="guide-close" class="guide-btn tertiary">
                            ${this.t('guide.navigation.skip', 'Skip guide')}
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', guideHTML);
        
        // Устанавливаем фокус на гайд
        const guide = document.getElementById('new-user-guide');
        guide.focus();
        
        this.addGuideStyles();
        this.setupGuideInteractions();
    }

    generateGuideSteps() {
        const steps = [
            {
                number: 1,
                title: this.t('guide.step_1.title', 'Choose a section to study'),
                description: this.t('guide.step_1.description', 'In the left panel you will find all sections of the BIG exam. Start with the basics!'),
                visual: this.generateSidebarVisual()
            },
            {
                number: 2,
                title: this.t('guide.step_2.title', 'Study materials'),
                description: this.t('guide.step_2.description', 'Each section contains interactive lessons, tests and practical assignments'),
                visual: this.generateProgressVisual()
            },
            {
                number: 3,
                title: this.t('guide.step_3.title', 'Track progress'),
                description: this.t('guide.step_3.description', 'In the right panel you can always see your overall progress and statistics'),
                visual: this.generateStatsVisual()
            }
        ];

        return steps.map((step, index) => `
            <div class="guide-step ${index === 0 ? 'active' : ''}" 
                 data-step="${step.number}" 
                 role="tabpanel" 
                 aria-labelledby="step-${step.number}-title"
                 ${index !== 0 ? 'aria-hidden="true"' : ''}>
                <div class="step-icon" aria-hidden="true">
                    <span class="step-number">${step.number}</span>
                </div>
                <div class="step-content">
                    <h3 id="step-${step.number}-title">${step.title}</h3>
                    <p>${step.description}</p>
                    <div class="step-visual" aria-label="Visual example">
                        ${step.visual}
                    </div>
                </div>
            </div>
        `).join('');
    }

    generateSidebarVisual() {
        const items = this.t('guide.step_1.sidebar_items', ['📚 Exams', '🧪 Research', '📋 BI-Test']);
        
        return `
            <div class="visual-sidebar" role="list" aria-label="Navigation sections">
                ${items.map((item, index) => `
                    <div class="visual-item ${index === 1 ? 'highlighted' : ''}" 
                         role="listitem" 
                         ${index === 1 ? 'aria-label="Currently selected: ' + item + '"' : ''}>${item}</div>
                `).join('')}
            </div>
        `;
    }

    generateProgressVisual() {
        const lessons = this.t('guide.step_2.lesson_items', ['Lesson 1', 'Lesson 2', 'Lesson 3']);
        
        return `
            <div class="visual-progress" role="list" aria-label="Lesson progress">
                ${lessons.map((lesson, index) => {
                    let progressClass = '';
                    let ariaLabel = '';
                    if (index === 0) {
                        progressClass = 'completed';
                        ariaLabel = `${lesson} - Completed`;
                    } else if (index === 1) {
                        progressClass = 'in-progress';
                        ariaLabel = `${lesson} - In progress`;
                    } else {
                        ariaLabel = `${lesson} - Not started`;
                    }
                    
                    return `
                        <div class="progress-item" role="listitem" aria-label="${ariaLabel}">
                            <span>${lesson}</span>
                            <div class="mini-progress ${progressClass}" 
                                 role="progressbar" 
                                 aria-label="Progress for ${lesson}"></div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    }

    generateStatsVisual() {
        const stats = this.t('guide.step_3.stats_items', ['📖 Lessons: 24/32', '⏱️ Time: 45 min', '🔥 Days: 5']);
        
        return `
            <div class="visual-stats" role="region" aria-label="Learning statistics">
                <div class="stat-circle" role="img" aria-label="75% overall progress">
                    <span>75%</span>
                </div>
                <div class="stat-info" role="list">
                    ${stats.map(stat => `<div role="listitem">${stat}</div>`).join('')}
                </div>
            </div>
        `;
    }

    addGuideStyles() {
        if (document.getElementById('guide-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'guide-styles';
        styles.textContent = `
            .guide-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: rgba(0, 0, 0, 0.8);
                backdrop-filter: blur(5px);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
                opacity: 0;
                animation: fadeIn 0.3s ease-out forwards;
                outline: none;
            }

            .guide-container {
                background: var(--bg-primary, #ffffff);
                border-radius: 20px;
                padding: 2rem;
                max-width: 700px;
                width: 90%;
                max-height: 85vh;
                display: flex;
                flex-direction: column;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
                position: relative;
                transform: translateY(20px);
                animation: slideUp 0.3s ease-out 0.1s forwards;
            }

            .guide-header {
                text-align: center;
                margin-bottom: 2rem;
                padding-bottom: 1rem;
                border-bottom: 2px solid var(--border-primary, #e0e0e0);
                flex-shrink: 0;
            }

            .guide-header h2 {
                color: var(--text-primary, #333);
                margin: 0 0 0.5rem 0;
                font-size: 1.5rem;
            }

            .guide-header p {
                color: var(--text-secondary, #666);
                margin: 0;
                font-size: 1rem;
            }

            .guide-content {
                flex: 1;
                display: flex;
                flex-direction: column;
                min-height: 0;
            }

            .guide-steps {
                flex: 1;
                position: relative;
                display: flex;
                flex-direction: column;
                min-height: 350px;
                overflow: hidden;
            }

            .guide-step {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                display: none;
                opacity: 0;
                transform: translateX(20px);
                transition: all 0.3s ease;
                padding: 1rem 0;
                overflow-y: auto;
            }

            .guide-step.active {
                display: flex;
                opacity: 1;
                transform: translateX(0);
                position: relative;
            }

            .guide-step {
                display: flex;
                gap: 1.5rem;
                align-items: flex-start;
            }

            .step-icon {
                flex-shrink: 0;
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, #3ECDC1, #6C5CE7);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 1.25rem;
                box-shadow: 0 4px 15px rgba(62, 205, 193, 0.3);
            }

            .step-content {
                flex: 1;
                min-width: 0;
            }

            .step-content h3 {
                color: var(--text-primary, #333);
                margin: 0 0 0.5rem 0;
                font-size: 1.25rem;
            }

            .step-content p {
                color: var(--text-secondary, #666);
                margin: 0 0 1.5rem 0;
                line-height: 1.6;
            }

            .step-visual {
                background: var(--bg-secondary, #f8f9fa);
                border-radius: 12px;
                padding: 1rem;
                border: 2px solid var(--border-primary, #e0e0e0);
            }

            /* Визуальные элементы */
            .visual-sidebar {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }

            .visual-item {
                padding: 0.75rem;
                background: white;
                border-radius: 8px;
                border: 1px solid #ddd;
                font-size: 0.9rem;
                transition: all 0.3s ease;
            }

            .visual-item.highlighted {
                background: linear-gradient(135deg, #3ECDC1, #6C5CE7);
                color: white;
                border-color: #3ECDC1;
                transform: scale(1.02);
                box-shadow: 0 4px 15px rgba(62, 205, 193, 0.3);
            }

            .visual-progress {
                display: flex;
                flex-direction: column;
                gap: 0.75rem;
            }

            .progress-item {
                display: flex;
                align-items: center;
                justify-content: space-between;
                font-size: 0.9rem;
            }

            .mini-progress {
                width: 60px;
                height: 4px;
                background: #e0e0e0;
                border-radius: 2px;
                position: relative;
                overflow: hidden;
            }

            .mini-progress.completed::after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: #4CAF50;
                border-radius: 2px;
            }

            .mini-progress.in-progress::after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 60%;
                height: 100%;
                background: #FF9800;
                border-radius: 2px;
            }

            .visual-stats {
                display: flex;
                align-items: center;
                gap: 1rem;
            }

            .stat-circle {
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, #3ECDC1, #6C5CE7);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 0.9rem;
                flex-shrink: 0;
            }

            .stat-info {
                display: flex;
                flex-direction: column;
                gap: 0.25rem;
                font-size: 0.8rem;
                color: var(--text-secondary, #666);
            }

            /* Навигация */
            .guide-navigation {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin: 1.5rem 0 1rem 0;
                padding-top: 1rem;
                border-top: 1px solid var(--border-primary, #e0e0e0);
                flex-shrink: 0;
            }

            .guide-dots {
                display: flex;
                gap: 0.5rem;
                align-items: center;
            }

            .dot {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: #ccc;
                cursor: pointer;
                transition: all 0.3s ease;
                border: none;
                padding: 0;
            }

            .dot.active {
                background: #3ECDC1;
                transform: scale(1.2);
            }

            .dot:focus {
                outline: 2px solid #3ECDC1;
                outline-offset: 2px;
            }

            .guide-btn {
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                border: none;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 0.9rem;
                min-width: 120px;
            }

            .guide-btn.primary {
                background: linear-gradient(135deg, #3ECDC1, #6C5CE7);
                color: white;
            }

            .guide-btn.primary:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(62, 205, 193, 0.3);
            }

            .guide-btn.secondary {
                background: var(--bg-secondary, #f8f9fa);
                color: var(--text-secondary, #666);
                border: 1px solid var(--border-primary, #e0e0e0);
            }

            .guide-btn.secondary:hover:not(:disabled) {
                background: var(--bg-tertiary, #e9ecef);
            }

            .guide-btn.tertiary {
                background: none;
                color: var(--text-tertiary, #999);
                text-decoration: underline;
                min-width: auto;
            }

            .guide-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none !important;
            }

            .guide-btn:focus {
                outline: 2px solid #3ECDC1;
                outline-offset: 2px;
            }

            .guide-footer {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-top: 1rem;
                padding-top: 1rem;
                border-top: 1px solid var(--border-primary, #e0e0e0);
                flex-shrink: 0;
            }

            .guide-checkbox {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                cursor: pointer;
                font-size: 0.9rem;
                color: var(--text-secondary, #666);
            }

            .guide-checkbox input {
                margin: 0;
            }

            .guide-checkbox input:focus {
                outline: 2px solid #3ECDC1;
                outline-offset: 2px;
            }

            /* Анимации */
            @keyframes fadeIn {
                to { opacity: 1; }
            }

            @keyframes slideUp {
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            /* Адаптивность */
            @media (max-width: 768px) {
                .guide-container {
                    padding: 1.5rem;
                    width: 95%;
                    max-height: 90vh;
                }
                
                .guide-step {
                    flex-direction: column;
                    text-align: center;
                    gap: 1rem;
                }
                
                .step-icon {
                    width: 50px;
                    height: 50px;
                    margin: 0 auto;
                }
                
                .guide-navigation {
                    flex-direction: column;
                    gap: 1rem;
                }
                
                .guide-footer {
                    flex-direction: column;
                    gap: 1rem;
                    text-align: center;
                }
                
                .guide-btn {
                    min-width: 140px;
                }
            }

            @media (max-width: 480px) {
                .guide-steps {
                    min-height: 300px;
                }
                
                .guide-container {
                    padding: 1rem;
                }
            }

            /* Темная тема */
            [data-theme="dark"] .guide-container {
                background: var(--bg-primary, #1a1a1a);
            }

            [data-theme="dark"] .visual-item {
                background: var(--bg-secondary, #2a2a2a);
                border-color: var(--border-primary, #444);
                color: var(--text-primary, #fff);
            }

            [data-theme="dark"] .step-visual {
                background: var(--bg-secondary, #2a2a2a);
                border-color: var(--border-primary, #444);
            }

            /* Доступность */
            @media (prefers-reduced-motion: reduce) {
                .guide-overlay,
                .guide-container,
                .guide-step {
                    animation: none !important;
                    transition: none !important;
                }
            }

            /* Высокий контраст */
            @media (prefers-contrast: high) {
                .guide-container {
                    border: 2px solid #000;
                }
                
                .guide-btn.primary {
                    background: #000;
                    color: #fff;
                    border: 2px solid #000;
                }
                
                .visual-item.highlighted {
                    background: #000;
                    color: #fff;
                }
            }
        `;
        
        document.head.appendChild(styles);
    }

    setupGuideInteractions() {
        let currentStep = 1;
        const totalSteps = 3;
        
        const prevBtn = document.getElementById('guide-prev');
        const nextBtn = document.getElementById('guide-next');
        const closeBtn = document.getElementById('guide-close');
        const dontShowAgain = document.getElementById('dont-show-again');
        
        const updateStep = (step) => {
            // Обновляем активный шаг
            document.querySelectorAll('.guide-step').forEach(el => {
                el.classList.remove('active');
                el.setAttribute('aria-hidden', 'true');
            });
            const activeStep = document.querySelector(`[data-step="${step}"]`);
            if (activeStep) {
                activeStep.classList.add('active');
                activeStep.removeAttribute('aria-hidden');
            }
            
            // Обновляем точки навигации
            document.querySelectorAll('.dot').forEach(el => {
                el.classList.remove('active');
                el.setAttribute('aria-selected', 'false');
            });
            const activeDot = document.querySelector(`.dot[data-step="${step}"]`);
            if (activeDot) {
                activeDot.classList.add('active');
                activeDot.setAttribute('aria-selected', 'true');
            }
            
            // Обновляем кнопки
            prevBtn.disabled = step === 1;
            const nextText = step === totalSteps ? 
                this.t('guide.navigation.start', 'Start learning!') : 
                this.t('guide.navigation.next', 'Next →');
            nextBtn.textContent = nextText;
            nextBtn.setAttribute('aria-label', nextText);
            
            currentStep = step;
        };
        
        // Навигация по шагам
        prevBtn.addEventListener('click', () => {
            if (currentStep > 1) {
                updateStep(currentStep - 1);
            }
        });
        
        nextBtn.addEventListener('click', () => {
            if (currentStep < totalSteps) {
                updateStep(currentStep + 1);
            } else {
                this.closeGuide();
            }
        });
        
        // Навигация по точкам
        document.querySelectorAll('.dot').forEach(dot => {
            dot.addEventListener('click', () => {
                const step = parseInt(dot.dataset.step);
                updateStep(step);
            });
        });
        
        // Закрытие гайда
        closeBtn.addEventListener('click', () => {
            this.closeGuide();
        });
        
        // Обработка "не показывать снова"
        dontShowAgain.addEventListener('change', (e) => {
            // Состояние будет сохранено при закрытии гайда
        });
        
        // Поддержка клавиатурной навигации
        document.addEventListener('keydown', (e) => {
            if (document.getElementById('new-user-guide')) {
                if (e.key === 'Escape') {
                    this.closeGuide();
                } else if (e.key === 'ArrowLeft' && currentStep > 1) {
                    updateStep(currentStep - 1);
                } else if (e.key === 'ArrowRight' && currentStep < totalSteps) {
                    updateStep(currentStep + 1);
                } else if (e.key === 'Enter' && e.target === nextBtn) {
                    nextBtn.click();
                }
            }
        });
    }

    async closeGuide() {
        const guide = document.getElementById('new-user-guide');
        const dontShowAgain = document.getElementById('dont-show-again');
        
        if (guide) {
            guide.style.opacity = '0';
            guide.style.transform = 'scale(0.95)';
            
            setTimeout(() => {
                guide.remove();
                
                // Удаляем стили гайда
                const guideStyles = document.getElementById('guide-styles');
                if (guideStyles) {
                    guideStyles.remove();
                }
            }, 300);
        }
        
        // Отмечаем завершение гайда
        try {
            await fetch('/api/complete-onboarding', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    completed_guide: true,
                    skip_future_guides: dontShowAgain ? dontShowAgain.checked : false
                })
            });
        } catch (error) {
            console.warn('Could not update guide completion status:', error);
            // Fallback на localStorage
            localStorage.setItem('dental_academy_guide_completed', 'true');
            if (dontShowAgain && dontShowAgain.checked) {
                localStorage.setItem('dental_academy_skip_guides', 'true');
            }
        }
        
        console.log('📚 User guide closed and marked as completed');
    }

    // Публичные методы для принудительного показа (для тестирования)
    showSplashManually() {
        this.splashShown = false;
        this.showSplashScreen();
    }

    showGuideManually() {
        this.guideShown = false;
        this.showNewUserGuide();
    }

    // Сброс флагов для тестирования
    async resetUserFlags() {
        try {
            await fetch('/api/reset-onboarding', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            console.log('🔄 User flags reset via API - refresh page to see splash and guide again');
        } catch (error) {
            console.warn('Could not reset via API, using localStorage fallback');
            localStorage.removeItem('dental_academy_visited');
            localStorage.removeItem('dental_academy_guide_completed');
            localStorage.removeItem('dental_academy_skip_guides');
            console.log('🔄 User flags reset via localStorage - refresh page to see splash and guide again');
        }
        
        // Сбрасываем локальные флаги
        this.splashShown = false;
        this.guideShown = false;
        this.userStatus.isNewUser = true;
        this.userStatus.shouldShowSplash = true;
        this.userStatus.shouldShowGuide = true;
    }
    
    // Метод для обновления языка
    async updateLanguage(newLanguage) {
        this.currentLanguage = newLanguage;
        
        // Перезагружаем переводы для нового языка
        await this.loadTranslations();
        
        console.log(`🌐 Language updated to: ${newLanguage}`);
    }
}

// Инициализация системы
document.addEventListener('DOMContentLoaded', () => {
    // Создаем экземпляр только на странице learning-map
    if (window.location.pathname.includes('/learning-map')) {
        window.splashAndGuideSystem = new SplashAndGuideSystem();
        
        // Добавляем в консоль для тестирования
        window.showSplash = () => window.splashAndGuideSystem.showSplashManually();
        window.showGuide = () => window.splashAndGuideSystem.showGuideManually();
        window.resetGuide = () => window.splashAndGuideSystem.resetUserFlags();
        
        console.log('🎬 Advanced Multilingual Splash and Guide System loaded');
        console.log('🧪 Test commands: showSplash(), showGuide(), resetGuide()');
        console.log('🌐 Current language:', window.splashAndGuideSystem.currentLanguage);
    }
});

// Поддержка смены языка
window.addEventListener('languageChanged', (event) => {
    if (window.splashAndGuideSystem) {
        window.splashAndGuideSystem.updateLanguage(event.detail.language);
    }
});

// Поддержка обновления языка через глобальные события
document.addEventListener('languageUpdated', (event) => {
    if (window.splashAndGuideSystem) {
        window.splashAndGuideSystem.updateLanguage(event.detail.newLanguage);
    }
});