/**
 * 🎯 NOTIFICATION SYSTEM
 * Система всплывающих уведомлений для Mentora
 */

class NotificationSystem {
    constructor() {
        this.overlay = null;
        this.popup = null;
        this.currentNotification = null;
        this.autoShowDelay = 1000; // 1 секунда после загрузки страницы
        this.currentLang = this.detectLanguage();
        
        this.init();
    }
    
    detectLanguage() {
        // Определяем язык из meta тега или localStorage
        const metaLang = document.querySelector('meta[name="current-language"]');
        if (metaLang) {
            return metaLang.getAttribute('content');
        }
        
        // Fallback на localStorage или браузер
        return localStorage.getItem('mentora_language') || 
               (navigator.language || navigator.userLanguage).split('-')[0] || 
               'en';
    }
    
    init() {
        // Создаем HTML структуру если её нет
        this.createNotificationHTML();
        
        // Проверяем localStorage для автопоказа
        this.checkAutoShow();
        
        // Обработчик клика по overlay
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) {
                this.hide();
            }
        });
        
        // Обработчик ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.overlay.classList.contains('show')) {
                this.hide();
            }
        });
    }
    
    createNotificationHTML() {
        // Создаем overlay если его нет
        this.overlay = document.getElementById('notificationOverlay');
        if (!this.overlay) {
            this.overlay = document.createElement('div');
            this.overlay.id = 'notificationOverlay';
            this.overlay.className = 'notification-overlay';
            document.body.appendChild(this.overlay);
        }
        
        // Создаем popup если его нет
        this.popup = document.getElementById('notificationPopup');
        if (!this.popup) {
            this.popup = document.createElement('div');
            this.popup.id = 'notificationPopup';
            this.popup.className = 'notification-popup';
            this.overlay.appendChild(this.popup);
        }
    }
    
    show(config) {
        this.currentNotification = config;
        this.render(config);
        
        // Показываем с анимацией
        requestAnimationFrame(() => {
            this.overlay.classList.add('show');
            // ИСПРАВЛЕНО: не блокируем прокрутку, чтобы не мешать пользователю
            // document.body.style.overflow = 'hidden'; // Блокируем скролл
        });
        
        // Отслеживаем показ
        this.trackNotificationShow(config.type);
    }
    
    hide() {
        this.overlay.classList.remove('show');
        // ИСПРАВЛЕНО: не нужно разблокировать прокрутку, так как мы её не блокируем
        // document.body.style.overflow = ''; // Разблокируем скролл
        
        // Очищаем после анимации
        setTimeout(() => {
            this.popup.innerHTML = '';
            this.currentNotification = null;
        }, 300);
        
        // Отслеживаем закрытие
        if (this.currentNotification) {
            this.trackNotificationHide(this.currentNotification.type);
        }
    }
    
    render(config) {
        const sparkles = `
            <div class="sparkle"></div>
            <div class="sparkle"></div>
            <div class="sparkle"></div>
            <div class="sparkle"></div>
        `;
        
        this.popup.innerHTML = `
            <div class="notification-header ${config.type}">
                ${sparkles}
                <button class="close-btn" onclick="mentorNotifications.hide()">
                    <i class="bi bi-x"></i>
                </button>
                <div class="notification-icon">
                    <i class="${config.icon}"></i>
                </div>
                <h2 class="notification-title">${config.title}</h2>
                <p class="notification-subtitle">${config.subtitle}</p>
            </div>
            
            <div class="notification-body">
                <div class="notification-content">
                    ${config.content}
                </div>
                
                ${config.features ? `
                    <ul class="notification-features">
                        ${config.features.map(feature => `
                            <li><i class="bi bi-check-circle-fill"></i> ${feature}</li>
                        `).join('')}
                    </ul>
                ` : ''}
                
                <div class="notification-actions">
                    <a href="${config.primaryAction.url}" class="btn-primary-custom" onclick="mentorNotifications.trackClick('${config.type}', 'primary')">
                        <i class="${config.primaryAction.icon}"></i>
                        ${config.primaryAction.text}
                    </a>
                    ${config.secondaryAction ? `
                        <button class="btn-secondary-custom" onclick="mentorNotifications.handleSecondaryAction('${config.type}')">
                            <i class="${config.secondaryAction.icon}"></i>
                            ${config.secondaryAction.text}
                        </button>
                    ` : ''}
                </div>
            </div>
            
            ${config.footer ? `
                <div class="notification-footer">
                    ${config.footer}
                </div>
            ` : ''}
        `;
    }
    
    // ========================================
    // ПЕРЕВОДЫ
    // ========================================
    
    getTranslations() {
        const translations = {
            'en': {
                'pre_registration_title': 'Pre-registration is now open!',
                'pre_registration_subtitle': 'Be among the first to join Mentora',
                'pre_registration_content': '🎉 We are excited to announce that pre-registration for Mentora is now open! Secure your spot in our exclusive early access program.',
                'pre_registration_content_short': '🎉 Pre-registration for Mentora is now open! Secure your spot in our exclusive early access program.',
                'pre_registration_features': [
                    'Early access to all courses',
                    'Personal guidance from specialists',
                    'Priority technical support',
                    'Exclusive BIG exam preparation materials'
                ],
                'register_now': 'Register Now',
                'remind_later': 'Remind Later',
                'learn_more': 'Learn More',
                'understand': 'I Understand',
                'subscribe_notifications': 'Subscribe to Notifications',
                'limited_offer': '⏰ Limited time offer. Spots in the early access program are limited!',
                'join_hundreds': '🎯 Join hundreds of medical professionals already preparing with Mentora!',
                'launch_title': 'Mentora is now live!',
                'launch_subtitle': 'Platform for medical professionals training',
                'launch_content': 'Welcome to Mentora - your personal platform for preparing for the BI-toets exam in the Netherlands. Start learning today!',
                'launch_features': [
                    'Adaptive testing based on IRT',
                    'Virtual patients for practice',
                    'AI assistant for personal learning',
                    'Preparation specifically for work in the Netherlands'
                ],
                'start_learning': 'Start Learning'
            },
            'nl': {
                'pre_registration_title': 'Voorregistratie is nu open!',
                'pre_registration_subtitle': 'Wees een van de eersten die zich bij Mentora aansluit',
                'pre_registration_content': '🎉 We zijn verheugd aan te kondigen dat voorregistratie voor Mentora nu open is! Zeker je plek in ons exclusieve vroegtijdige toegangsprogramma.',
                'pre_registration_content_short': '🎉 Voorregistratie voor Mentora is nu open! Zeker je plek in ons exclusieve vroegtijdige toegangsprogramma.',
                'pre_registration_features': [
                    'Vroege toegang tot alle cursussen',
                    'Persoonlijke begeleiding van specialisten',
                    'Prioritaire technische ondersteuning',
                    'Exclusieve BIG-examen voorbereidingsmaterialen'
                ],
                'register_now': 'Registreer Nu',
                'remind_later': 'Later Herinneren',
                'learn_more': 'Meer Informatie',
                'understand': 'Ik Begrijp Het',
                'subscribe_notifications': 'Abonneren op Meldingen',
                'limited_offer': '⏰ Beperkte tijd aanbieding. Plaatsen in het vroegtijdige toegangsprogramma zijn beperkt!',
                'join_hundreds': '🎯 Sluit je aan bij honderden medische professionals die al voorbereiden met Mentora!',
                'launch_title': 'Mentora is nu live!',
                'launch_subtitle': 'Platform voor medische professionals training',
                'launch_content': 'Welkom bij Mentora - uw persoonlijke platform voor voorbereiding op het BI-toets examen in Nederland. Begin vandaag nog met leren!',
                'launch_features': [
                    'Adaptief testen gebaseerd op IRT',
                    'Virtuele patiënten voor praktijk',
                    'AI-assistent voor persoonlijk leren',
                    'Voorbereiding specifiek voor werk in Nederland'
                ],
                'start_learning': 'Begin met Leren'
            },
            'ru': {
                'pre_registration_title': 'Предварительная регистрация открыта!',
                'pre_registration_subtitle': 'Станьте одним из первых участников Mentora',
                'pre_registration_content': '🎉 Мы рады сообщить, что предварительная регистрация в Mentora теперь открыта! Закрепите свое место в нашей эксклюзивной программе раннего доступа.',
                'pre_registration_content_short': '🎉 Предварительная регистрация в Mentora открыта! Закрепите свое место в программе раннего доступа.',
                'pre_registration_features': [
                    'Ранний доступ ко всем курсам',
                    'Персональное сопровождение специалистов',
                    'Приоритетная техническая поддержка',
                    'Эксклюзивные материалы для подготовки к BIG экзамену'
                ],
                'register_now': 'Зарегистрироваться',
                'remind_later': 'Напомнить позже',
                'learn_more': 'Узнать больше',
                'understand': 'Понятно',
                'subscribe_notifications': 'Подписаться на уведомления',
                'limited_offer': '⏰ Ограниченное предложение. Количество мест в программе раннего доступа ограничено!',
                'join_hundreds': '🎯 Присоединяйтесь к сотням медицинских специалистов, которые уже готовятся с Mentora!',
                'launch_title': 'Mentora уже запущена!',
                'launch_subtitle': 'Платформа для подготовки медицинских специалистов',
                'launch_content': 'Добро пожаловать в Mentora - вашу персональную платформу для подготовки к BI-toets экзамену в Нидерландах. Начните обучение уже сегодня!',
                'launch_features': [
                    'Адаптивное тестирование на основе IRT',
                    'Виртуальные пациенты для практики',
                    'AI-помощник для персонального обучения',
                    'Подготовка специально для работы в Нидерландах'
                ],
                'start_learning': 'Начать обучение'
            }
        };
        
        return translations[this.currentLang] || translations['en'];
    }
    
    // ========================================
    // ПРЕДУСТАНОВЛЕННЫЕ УВЕДОМЛЕНИЯ
    // ========================================
    
    showPreRegistration() {
        const t = this.getTranslations();
        this.show({
            type: 'pre-registration',
            icon: 'bi bi-rocket-takeoff',
            title: t.pre_registration_title,
            subtitle: t.pre_registration_subtitle,
            content: t.pre_registration_content_short,
            primaryAction: {
                text: t.register_now,
                url: '/auth/register',
                icon: 'bi bi-person-plus'
            },
            secondaryAction: {
                text: t.remind_later,
                icon: 'bi bi-clock'
            }
        });
    }
    
    showEarlyAccess() {
        this.show({
            type: 'early-access',
            icon: 'bi bi-rocket-takeoff',
            title: 'Ранний доступ к Mentora!',
            subtitle: 'Получите эксклюзивный доступ к нашей платформе',
            content: `
                🎉 Мы рады сообщить о запуске программы раннего доступа к платформе Mentora! 
                Зарегистрируйтесь сейчас и получите все преимущества первопроходца.
            `,
            features: [
                'Бесплатный доступ ко всем курсам',
                'Персональное сопровождение специалиста',
                'Приоритетная техническая поддержка',
                'Эксклюзивные материалы для подготовки к BI-toets'
            ],
            primaryAction: {
                text: 'Зарегистрироваться бесплатно',
                url: '/auth/register',
                icon: 'bi bi-person-plus'
            },
            secondaryAction: {
                text: 'Напомнить позже',
                icon: 'bi bi-clock'
            },
            footer: '⏰ Предложение ограничено. Количество мест в программе раннего доступа ограничено!'
        });
    }
    
    showLaunchAnnouncement() {
        const t = this.getTranslations();
        this.show({
            type: 'mentora-launch',
            icon: 'bi bi-star-fill',
            title: t.launch_title || 'Mentora is now live!',
            subtitle: t.launch_subtitle || 'Platform for medical professionals training',
            content: t.launch_content || 'Welcome to Mentora - your personal platform for preparing for the BI-toets exam in the Netherlands. Start learning today!',
            features: t.launch_features || [
                'Adaptive testing based on IRT',
                'Virtual patients for practice',
                'AI assistant for personal learning',
                'Preparation specifically for work in the Netherlands'
            ],
            primaryAction: {
                text: t.start_learning || 'Start Learning',
                url: '/auth/register',
                icon: 'bi bi-play-circle'
            },
            secondaryAction: {
                text: t.learn_more || 'Learn More',
                icon: 'bi bi-info-circle'
            },
            footer: t.join_hundreds || '🎯 Join hundreds of medical professionals already preparing with Mentora!'
        });
    }
    
    showBigExamInfo() {
        this.show({
            type: 'big-exam',
            icon: 'bi bi-award',
            title: 'Подготовка к BI-toets',
            subtitle: 'Все что нужно знать о BIG экзамене',
            content: `
                BI-toets - это обязательный экзамен для медицинских специалистов из стран 
                вне ЕС, желающих работать в Нидерландах. Мы поможем вам подготовиться!
            `,
            features: [
                'Полная программа подготовки к экзамену',
                'Симуляция реальных условий тестирования',
                'Материалы на нидерландском языке',
                'Статистика и отслеживание прогресса'
            ],
            primaryAction: {
                text: 'Начать подготовку',
                url: '/learning',
                icon: 'bi bi-book'
            },
            secondaryAction: {
                text: 'Подробнее о BI-toets',
                icon: 'bi bi-question-circle'
            },
            footer: '📚 Более 1000+ вопросов и кейсов для полноценной подготовки'
        });
    }
    
    showMaintenanceWarning() {
        this.show({
            type: 'warning',
            icon: 'bi bi-exclamation-triangle',
            title: 'Плановое обслуживание',
            subtitle: 'Временные ограничения в работе системы',
            content: `
                Уважаемые пользователи! В ближайшее время планируется техническое 
                обслуживание системы. Возможны кратковременные перебои в работе.
            `,
            features: [
                'Обслуживание продлится не более 2 часов',
                'Ваш прогресс будет сохранен',
                'Улучшения производительности',
                'Исправление выявленных ошибок'
            ],
            primaryAction: {
                text: 'Понятно',
                url: '#',
                icon: 'bi bi-check'
            },
            secondaryAction: {
                text: 'Подписаться на уведомления',
                icon: 'bi bi-bell'
            },
            footer: 'Мы стараемся свести неудобства к минимуму. Спасибо за понимание!'
        });
    }
    
    // ========================================
    // АВТОМАТИЧЕСКИЙ ПОКАЗ
    // ========================================
    
    checkAutoShow() {
        // Проверяем, показывать ли уведомление автоматически
        const lastShown = localStorage.getItem('mentora_notification_last_shown');
        const notificationDismissed = localStorage.getItem('mentora_notification_dismissed');
        const currentPage = window.location.pathname;
        
        // Показываем только на главной странице
        if (currentPage === '/' || currentPage === '/index' || currentPage === '') {
            // Если уведомление не было отклонено и не показывалось сегодня
            const today = new Date().toDateString();
            
            if (!notificationDismissed && lastShown !== today) {
                setTimeout(() => {
                    this.showPreRegistration();
                    localStorage.setItem('mentora_notification_last_shown', today);
                }, this.autoShowDelay);
            }
        }
    }
    
    // ========================================
    // ОБРАБОТЧИКИ ДЕЙСТВИЙ
    // ========================================
    
    handleSecondaryAction(type) {
        if (type === 'pre-registration') {
            // Напомнить позже - устанавливаем отложенный показ
            const remindDate = new Date();
            remindDate.setDate(remindDate.getDate() + 1); // Через день
            localStorage.setItem('mentora_notification_remind_date', remindDate.toISOString());
        } else if (type === 'early-access') {
            // Напомнить позже - устанавливаем отложенный показ
            const remindDate = new Date();
            remindDate.setDate(remindDate.getDate() + 1); // Через день
            localStorage.setItem('mentora_notification_remind_date', remindDate.toISOString());
        } else if (type === 'mentora-launch') {
            // Узнать больше - переход на страницу с информацией
            window.location.href = '/about';
            return;
        }
        
        this.hide();
    }
    
    dismiss() {
        // Полностью отклонить уведомления
        localStorage.setItem('mentora_notification_dismissed', 'true');
        this.hide();
    }
    
    // ========================================
    // АНАЛИТИКА
    // ========================================
    
    trackNotificationShow(type) {
        // Отправляем событие в аналитику
        if (typeof gtag !== 'undefined') {
            gtag('event', 'notification_show', {
                'notification_type': type,
                'page_location': window.location.href
            });
        }
        
        // Локальная аналитика
        const shows = JSON.parse(localStorage.getItem('mentora_notification_shows') || '{}');
        shows[type] = (shows[type] || 0) + 1;
        localStorage.setItem('mentora_notification_shows', JSON.stringify(shows));
    }
    
    trackNotificationHide(type) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'notification_hide', {
                'notification_type': type
            });
        }
    }
    
    trackClick(type, action) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'notification_click', {
                'notification_type': type,
                'action_type': action
            });
        }
        
        // Локальная аналитика
        const clicks = JSON.parse(localStorage.getItem('mentora_notification_clicks') || '{}');
        const key = `${type}_${action}`;
        clicks[key] = (clicks[key] || 0) + 1;
        localStorage.setItem('mentora_notification_clicks', JSON.stringify(clicks));
    }
    
    // ========================================
    // АДМИНИСТРАТИВНЫЕ ФУНКЦИИ
    // ========================================
    
    getAnalytics() {
        return {
            shows: JSON.parse(localStorage.getItem('mentora_notification_shows') || '{}'),
            clicks: JSON.parse(localStorage.getItem('mentora_notification_clicks') || '{}'),
            lastShown: localStorage.getItem('mentora_notification_last_shown'),
            dismissed: localStorage.getItem('mentora_notification_dismissed'),
            remindDate: localStorage.getItem('mentora_notification_remind_date')
        };
    }
    
    resetAnalytics() {
        localStorage.removeItem('mentora_notification_shows');
        localStorage.removeItem('mentora_notification_clicks');
        localStorage.removeItem('mentora_notification_last_shown');
        localStorage.removeItem('mentora_notification_dismissed');
        localStorage.removeItem('mentora_notification_remind_date');
    }
    
    // Для тестирования в консоли
    test() {
        console.log('🎯 Testing Mentora Notifications:');
        console.log('mentorNotifications.showPreRegistration() - показать предварительную регистрацию');
        console.log('mentorNotifications.showEarlyAccess() - показать ранний доступ');
        console.log('mentorNotifications.showLaunchAnnouncement() - показать запуск');
        console.log('mentorNotifications.showBigExamInfo() - показать info о BI-toets');
        console.log('mentorNotifications.showMaintenanceWarning() - показать предупреждение');
        console.log('mentorNotifications.getAnalytics() - получить аналитику');
        console.log('mentorNotifications.resetAnalytics() - сбросить аналитику');
        console.log('mentorNotifications.currentLang - текущий язык:', this.currentLang);
    }
}

// Инициализация системы уведомлений
document.addEventListener('DOMContentLoaded', function() {
    // Создаем глобальный экземпляр
    window.mentorNotifications = new NotificationSystem();
    
    // Для отладки в консоли
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log('🎯 Mentora Notifications loaded! Type mentorNotifications.test() for help');
    }
});

// Экспорт для использования в других файлах
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NotificationSystem;
}
