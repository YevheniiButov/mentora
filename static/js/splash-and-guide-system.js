/* ===== УЛУЧШЕННАЯ СИСТЕМА ЗАГРУЗКИ И ГАЙДОВ ===== */
/* static/js/splash-and-guide-system.js */

class SplashAndGuideSystem {
    constructor() {
        this.isFirstVisit = !localStorage.getItem('user_visited_learning_map');
        this.showSplashAlways = true; // Можно изменить на false для показа только новым пользователям
        this.splashDuration = 3500; // Длительность сплеш-экрана
        this.guideDuration = 10000; // Время показа гайда
        
        this.init();
    }

    init() {
        // Показываем сплеш-экран при загрузке страницы learning-map
        if (window.location.pathname.includes('/learning-map')) {
            this.showSplashScreen();
        }
    }

    showSplashScreen() {
        console.log('🎬 Showing splash screen');
        
        const splashHTML = `
            <div id="dental-academy-splash" class="splash-overlay">
                <div class="splash-container">
                    <!-- Анимированный логотип -->
                    <div class="splash-logo-container">
                        <div class="logo-animation">
                            <div class="logo-rings">
                                <div class="ring ring-1"></div>
                                <div class="ring ring-2"></div>
                                <div class="ring ring-3"></div>
                            </div>
                            <div class="logo-center">
                                <div class="tooth-icon">🦷</div>
                            </div>
                        </div>
                        
                        <div class="logo-text">
                            <h1 class="logo-title">
                                <span class="logo-dental">Dental</span>
                                <span class="logo-academy">Academy</span>
                            </h1>
                            <p class="logo-subtitle">Preparing for Excellence</p>
                        </div>
                    </div>
                    
                    <!-- Прогресс бар -->
                    <div class="splash-progress">
                        <div class="progress-container">
                            <div class="progress-bar">
                                <div class="progress-fill"></div>
                            </div>
                            <div class="progress-text">
                                <span id="loading-text">Загрузка вашего учебного пространства...</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Мотивационная цитата -->
                    <div class="splash-quote">
                        <p id="motivational-quote">
                            "Каждый шаг в обучении приближает вас к мечте стать отличным стоматологом"
                        </p>
                    </div>
                </div>
            </div>
        `;

        // Добавляем сплеш-экран в DOM
        document.body.insertAdjacentHTML('beforeend', splashHTML);
        
        // Добавляем стили
        this.addSplashStyles();
        
        // Запускаем анимацию загрузки
        this.animateLoading();
        
        // Убираем сплеш-экран через указанное время
        setTimeout(() => {
            this.hideSplashScreen();
        }, this.splashDuration);
    }

    addSplashStyles() {
        if (document.getElementById('splash-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'splash-styles';
        styles.textContent = `
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
                width: 60px;
                height: 60px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                backdrop-filter: blur(10px);
                animation: centerPulse 3s ease-in-out infinite;
            }

            .tooth-icon {
                font-size: 2rem;
                animation: toothRotate 4s linear infinite;
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
                height: 6px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 3px;
                overflow: hidden;
                margin-bottom: 1rem;
                position: relative;
            }

            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #3ECDC1, #6C5CE7, #FDCB6E);
                border-radius: 3px;
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

            @keyframes toothRotate {
                0% { transform: rotate(0deg); }
                25% { transform: rotate(10deg); }
                75% { transform: rotate(-10deg); }
                100% { transform: rotate(0deg); }
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
                
                .tooth-icon { font-size: 1.5rem; }
            }

            /* Для людей с ограниченными возможностями */
            @media (prefers-reduced-motion: reduce) {
                .splash-overlay,
                .ring,
                .logo-center,
                .tooth-icon,
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
        `;
        
        document.head.appendChild(styles);
    }

    animateLoading() {
        const progressFill = document.querySelector('.progress-fill');
        const loadingText = document.getElementById('loading-text');
        const motivationalQuote = document.getElementById('motivational-quote');
        
        if (!progressFill) return;

        const loadingSteps = [
            { progress: 20, text: 'Инициализация системы обучения...', delay: 300 },
            { progress: 45, text: 'Загрузка учебных материалов...', delay: 600 },
            { progress: 70, text: 'Подготовка интерактивных элементов...', delay: 900 },
            { progress: 90, text: 'Почти готово...', delay: 1200 },
            { progress: 100, text: 'Добро пожаловать!', delay: 1500 }
        ];

        const quotes = [
            "Каждый шаг в обучении приближает вас к мечте стать отличным стоматологом",
            "Знания - это инвестиция, которая всегда приносит лучшие проценты",
            "Успех в стоматологии начинается с качественной подготовки",
            "Ваше будущее создается тем, что вы изучаете сегодня"
        ];

        let currentStep = 0;
        
        const animateStep = () => {
            if (currentStep < loadingSteps.length) {
                const step = loadingSteps[currentStep];
                
                progressFill.style.width = step.progress + '%';
                if (loadingText) {
                    loadingText.textContent = step.text;
                }
                
                // Меняем цитату на половине загрузки
                if (currentStep === 2 && motivationalQuote) {
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
        
        // Начинаем анимацию через небольшую задержку
        setTimeout(animateStep, 200);
    }

    hideSplashScreen() {
        const splash = document.getElementById('dental-academy-splash');
        if (splash) {
            splash.classList.add('fade-out');
            
            setTimeout(() => {
                splash.remove();
                
                // Показываем гайд для новых пользователей
                if (this.isFirstVisit) {
                    setTimeout(() => {
                        this.showNewUserGuide();
                    }, 500);
                }
                
                // Отмечаем, что пользователь посетил карту обучения
                localStorage.setItem('user_visited_learning_map', 'true');
                
            }, 500);
        }
    }

    showNewUserGuide() {
        console.log('📚 Showing new user guide');
        
        const guideHTML = `
            <div id="new-user-guide" class="guide-overlay">
                <div class="guide-container">
                    <div class="guide-header">
                        <h2>🎓 Добро пожаловать в Dental Academy!</h2>
                        <p>Давайте быстро познакомимся с платформой</p>
                    </div>
                    
                    <div class="guide-content">
                        <div class="guide-steps">
                            <div class="guide-step active" data-step="1">
                                <div class="step-icon">
                                    <span class="step-number">1</span>
                                </div>
                                <div class="step-content">
                                    <h3>Выберите раздел для изучения</h3>
                                    <p>В левой панели вы найдете все разделы BIG экзамена. Начните с основ!</p>
                                    <div class="step-visual">
                                        <div class="visual-sidebar">
                                            <div class="visual-item">📚 Exams</div>
                                            <div class="visual-item highlighted">🧪 Investi</div>
                                            <div class="visual-item">📋 BI-Toets</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="guide-step" data-step="2">
                                <div class="step-icon">
                                    <span class="step-number">2</span>
                                </div>
                                <div class="step-content">
                                    <h3>Изучайте материалы</h3>
                                    <p>Каждый раздел содержит интерактивные уроки, тесты и практические задания</p>
                                    <div class="step-visual">
                                        <div class="visual-progress">
                                            <div class="progress-item">
                                                <span>Урок 1</span>
                                                <div class="mini-progress completed"></div>
                                            </div>
                                            <div class="progress-item">
                                                <span>Урок 2</span>
                                                <div class="mini-progress in-progress"></div>
                                            </div>
                                            <div class="progress-item">
                                                <span>Урок 3</span>
                                                <div class="mini-progress"></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="guide-step" data-step="3">
                                <div class="step-icon">
                                    <span class="step-number">3</span>
                                </div>
                                <div class="step-content">
                                    <h3>Отслеживайте прогресс</h3>
                                    <p>В правой панели вы всегда можете видеть свой общий прогресс и статистику</p>
                                    <div class="step-visual">
                                        <div class="visual-stats">
                                            <div class="stat-circle">
                                                <span>75%</span>
                                            </div>
                                            <div class="stat-info">
                                                <div>📖 Уроков: 24/32</div>
                                                <div>⏱️ Время: 45 мин</div>
                                                <div>🔥 Дней: 5</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="guide-navigation">
                            <button id="guide-prev" class="guide-btn secondary" disabled>
                                ← Назад
                            </button>
                            <div class="guide-dots">
                                <span class="dot active" data-step="1"></span>
                                <span class="dot" data-step="2"></span>
                                <span class="dot" data-step="3"></span>
                            </div>
                            <button id="guide-next" class="guide-btn primary">
                                Далее →
                            </button>
                        </div>
                    </div>
                    
                    <div class="guide-footer">
                        <label class="guide-checkbox">
                            <input type="checkbox" id="dont-show-again">
                            <span>Больше не показывать</span>
                        </label>
                        <button id="guide-close" class="guide-btn tertiary">
                            Пропустить гайд
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', guideHTML);
        this.addGuideStyles();
        this.setupGuideInteractions();
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
            }

            .guide-container {
                background: var(--bg-primary, #ffffff);
                border-radius: 20px;
                padding: 2rem;
                max-width: 600px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
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

            .guide-steps {
                min-height: 300px;
                position: relative;
            }

            .guide-step {
                display: none;
                opacity: 0;
                transform: translateX(20px);
                transition: all 0.3s ease;
            }

            .guide-step.active {
                display: block;
                opacity: 1;
                transform: translateX(0);
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
            }

            .visual-item.highlighted {
                background: linear-gradient(135deg, #3ECDC1, #6C5CE7);
                color: white;
                border-color: #3ECDC1;
                transform: scale(1.02);
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
                margin: 2rem 0 1rem 0;
                padding-top: 1rem;
                border-top: 1px solid var(--border-primary, #e0e0e0);
            }

            .guide-dots {
                display: flex;
                gap: 0.5rem;
            }

            .dot {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: #ccc;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .dot.active {
                background: #3ECDC1;
                transform: scale(1.2);
            }

            .guide-btn {
                padding: 0.5rem 1rem;
                border-radius: 8px;
                border: none;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 0.9rem;
            }

            .guide-btn.primary {
                background: linear-gradient(135deg, #3ECDC1, #6C5CE7);
                color: white;
            }

            .guide-btn.primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(62, 205, 193, 0.3);
            }

            .guide-btn.secondary {
                background: var(--bg-secondary, #f8f9fa);
                color: var(--text-secondary, #666);
                border: 1px solid var(--border-primary, #e0e0e0);
            }

            .guide-btn.tertiary {
                background: none;
                color: var(--text-tertiary, #999);
                text-decoration: underline;
            }

            .guide-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none !important;
            }

            .guide-footer {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-top: 1rem;
                padding-top: 1rem;
                border-top: 1px solid var(--border-primary, #e0e0e0);
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
            }

            /* Темная тема */
            [data-theme="dark"] .guide-container {
                background: var(--bg-primary, #1a1a1a);
            }

            [data-theme="dark"] .visual-item {
                background: var(--bg-secondary, #2a2a2a);
                border-color: var(--border-primary, #444);
            }

            [data-theme="dark"] .step-visual {
                background: var(--bg-secondary, #2a2a2a);
                border-color: var(--border-primary, #444);
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
            });
            document.querySelector(`[data-step="${step}"]`).classList.add('active');
            
            // Обновляем точки навигации
            document.querySelectorAll('.dot').forEach(el => {
                el.classList.remove('active');
            });
            document.querySelector(`.dot[data-step="${step}"]`).classList.add('active');
            
            // Обновляем кнопки
            prevBtn.disabled = step === 1;
            nextBtn.textContent = step === totalSteps ? 'Начать обучение!' : 'Далее →';
            
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
            if (e.target.checked) {
                localStorage.setItem('hide_user_guide', 'true');
            } else {
                localStorage.removeItem('hide_user_guide');
            }
        });
        
        // Закрытие по Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeGuide();
            }
        });
    }

    closeGuide() {
        const guide = document.getElementById('new-user-guide');
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
        
        console.log('📚 User guide closed');
    }

    // Публичные методы для принудительного показа
    showSplashManually() {
        this.showSplashScreen();
    }

    showGuideManually() {
        this.showNewUserGuide();
    }

    // Сброс флагов для тестирования
    resetUserFlags() {
        localStorage.removeItem('user_visited_learning_map');
        localStorage.removeItem('hide_user_guide');
        sessionStorage.removeItem('splashShown');
        console.log('🔄 User flags reset - refresh page to see splash and guide again');
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
        
        console.log('🎬 Splash and Guide System loaded');
        console.log('🧪 Test commands: showSplash(), showGuide(), resetGuide()');
    }
});