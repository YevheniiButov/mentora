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
                'pre_registration_content_short': '🎉 Pre-registration for Mentora is now open! Secure your spot in our exclusive early access program.',
                'register_now': 'Register Now',
                'remind_later': 'Remind Later'
            },
            'nl': {
                'pre_registration_title': 'Voorregistratie is nu open!',
                'pre_registration_subtitle': 'Wees een van de eersten die zich bij Mentora aansluit',
                'pre_registration_content_short': '🎉 Voorregistratie voor Mentora is nu open! Zeker je plek in ons exclusieve vroegtijdige toegangsprogramma.',
                'register_now': 'Registreer Nu',
                'remind_later': 'Later Herinneren'
            },
            'ru': {
                'pre_registration_title': 'Предварительная регистрация открыта!',
                'pre_registration_subtitle': 'Станьте одним из первых участников Mentora',
                'pre_registration_content_short': '🎉 Предварительная регистрация в Mentora открыта! Закрепите свое место в программе раннего доступа.',
                'register_now': 'Зарегистрироваться',
                'remind_later': 'Напомнить позже'
            },
            'uk': {
                'pre_registration_title': 'Попередня реєстрація відкрита!',
                'pre_registration_subtitle': 'Станьте одним з перших учасників Mentora',
                'pre_registration_content_short': '🎉 Попередня реєстрація в Mentora відкрита! Закріпіть своє місце в програмі раннього доступу.',
                'register_now': 'Зареєструватися',
                'remind_later': 'Нагадати пізніше'
            },
            'fa': {
                'pre_registration_title': 'ثبت نام اولیه اکنون باز است!',
                'pre_registration_subtitle': 'یکی از اولین کسانی باشید که به Mentora می پیوندد',
                'pre_registration_content_short': '🎉 ثبت نام اولیه برای Mentora اکنون باز است! جای خود را در برنامه دسترسی زودهنگام انحصاری ما تضمین کنید.',
                'register_now': 'الان ثبت نام کنید',
                'remind_later': 'بعداً یادآوری کن'
            },
            'pt': {
                'pre_registration_title': 'Pré-registro está aberto!',
                'pre_registration_subtitle': 'Seja um dos primeiros a se juntar ao Mentora',
                'pre_registration_content_short': '🎉 O pré-registro para o Mentora está aberto! Garanta seu lugar em nosso programa exclusivo de acesso antecipado.',
                'register_now': 'Registrar Agora',
                'remind_later': 'Lembrar Mais Tarde'
            },
            'es': {
                'pre_registration_title': '¡La preinscripción está abierta!',
                'pre_registration_subtitle': 'Sé uno de los primeros en unirse a Mentora',
                'pre_registration_content_short': '🎉 ¡La preinscripción para Mentora está abierta! Asegura tu lugar en nuestro programa exclusivo de acceso temprano.',
                'register_now': 'Registrarse Ahora',
                'remind_later': 'Recordar Más Tarde'
            },
            'tr': {
                'pre_registration_title': 'Ön kayıt şimdi açık!',
                'pre_registration_subtitle': 'Mentora\'ya katılan ilk kişilerden biri olun',
                'pre_registration_content_short': '🎉 Mentora için ön kayıt şimdi açık! Özel erken erişim programımızda yerinizi güvence altına alın.',
                'register_now': 'Şimdi Kayıt Ol',
                'remind_later': 'Daha Sonra Hatırlat'
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
    
    
    // ========================================
    // АВТОМАТИЧЕСКИЙ ПОКАЗ
    // ========================================
    
    checkAutoShow() {
        // Проверяем, показывать ли уведомление автоматически
        const lastShown = localStorage.getItem('mentora_notification_last_shown');
        const notificationDismissed = localStorage.getItem('mentora_notification_dismissed');
        const currentPage = window.location.pathname;
        const today = new Date().toDateString();
        
        console.log('🔍 checkAutoShow:', {
            currentPage,
            lastShown,
            notificationDismissed,
            today,
            shouldShow: !notificationDismissed && lastShown !== today
        });
        
        // Показываем только на главной странице
        if (currentPage === '/' || currentPage === '/index' || currentPage === '') {
            // Если уведомление не было отклонено и не показывалось сегодня
            if (!notificationDismissed && lastShown !== today) {
                console.log('✅ Показываем уведомление через', this.autoShowDelay + 'ms');
                setTimeout(() => {
                    this.showPreRegistration();
                    localStorage.setItem('mentora_notification_last_shown', today);
                }, this.autoShowDelay);
            } else {
                console.log('❌ Уведомление не показываем:', {
                    reason: notificationDismissed ? 'отклонено' : 'уже показано сегодня'
                });
            }
        } else {
            console.log('❌ Не главная страница:', currentPage);
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
        console.log('mentorNotifications.forceShow() - принудительно показать уведомление');
        console.log('mentorNotifications.getAnalytics() - получить аналитику');
        console.log('mentorNotifications.resetAnalytics() - сбросить аналитику');
        console.log('mentorNotifications.currentLang - текущий язык:', this.currentLang);
        console.log('mentorNotifications.debug() - отладочная информация');
    }
    
    // Принудительно показать уведомление (для тестирования)
    forceShow() {
        console.log('🔧 Принудительный показ уведомления...');
        this.showPreRegistration();
    }
    
    // Отладочная информация
    debug() {
        const lastShown = localStorage.getItem('mentora_notification_last_shown');
        const notificationDismissed = localStorage.getItem('mentora_notification_dismissed');
        const currentPage = window.location.pathname;
        const today = new Date().toDateString();
        
        console.log('🔍 Отладочная информация:');
        console.log('- Текущая страница:', currentPage);
        console.log('- Последний показ:', lastShown);
        console.log('- Отклонено:', notificationDismissed);
        console.log('- Сегодня:', today);
        console.log('- Показывать?', !notificationDismissed && lastShown !== today);
        console.log('- Язык:', this.currentLang);
        console.log('- Задержка:', this.autoShowDelay + 'ms');
    }
}

// Инициализация системы уведомлений
document.addEventListener('DOMContentLoaded', function() {
    try {
        // Создаем глобальный экземпляр
        window.mentorNotifications = new NotificationSystem();
        
        // Всегда показываем в консоли что система загружена
        console.log('🎯 Mentora Notifications loaded! Type mentorNotifications.test() for help');
        console.log('🔧 Available functions:', Object.getOwnPropertyNames(window.mentorNotifications));
        
    } catch (error) {
        console.error('❌ Error loading Mentora Notifications:', error);
    }
});

// Экспорт для использования в других файлах
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NotificationSystem;
}
