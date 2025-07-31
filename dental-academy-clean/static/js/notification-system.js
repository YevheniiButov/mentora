/**
 * Browser Notification System for Learning Planner
 * Handles browser notifications for study sessions and reminders
 */

class BrowserNotificationSystem {
    constructor() {
        this.permission = 'default';
        this.isSupported = 'Notification' in window;
        this.init();
    }
    
    async init() {
        if (!this.isSupported) {
            console.log('Browser notifications not supported');
            return;
        }
        
        // Проверяем разрешение
        this.permission = Notification.permission;
        
        // Если разрешение не запрошено, запрашиваем
        if (this.permission === 'default') {
            await this.requestPermission();
        }
        
        // Инициализируем уведомления
        this.setupNotifications();
    }
    
    async requestPermission() {
        try {
            this.permission = await Notification.requestPermission();
            console.log('Notification permission:', this.permission);
            
            if (this.permission === 'granted') {
                this.showWelcomeNotification();
            }
            
            return this.permission;
        } catch (error) {
            console.error('Error requesting notification permission:', error);
            return 'denied';
        }
    }
    
    setupNotifications() {
        if (this.permission !== 'granted') {
            return;
        }
        
        // Настраиваем уведомления для разных событий
        this.setupSessionReminders();
        this.setupProgressNotifications();
        this.setupExamReminders();
    }
    
    setupSessionReminders() {
        // Уведомления о предстоящих занятиях
        const sessionElements = document.querySelectorAll('[data-session-time]');
        
        sessionElements.forEach(element => {
            const sessionTime = element.dataset.sessionTime;
            const sessionTitle = element.dataset.sessionTitle;
            
            if (sessionTime) {
                this.scheduleSessionReminder(sessionTime, sessionTitle);
            }
        });
    }
    
    setupProgressNotifications() {
        // Уведомления о прогрессе
        const progressThresholds = [25, 50, 75, 90];
        
        progressThresholds.forEach(threshold => {
            this.checkProgressThreshold(threshold);
        });
    }
    
    setupExamReminders() {
        // Уведомления о экзамене
        const examDateElement = document.getElementById('exam-date');
        if (examDateElement && examDateElement.value) {
            const examDate = new Date(examDateElement.value);
            this.scheduleExamReminders(examDate);
        }
    }
    
    scheduleSessionReminder(sessionTime, sessionTitle) {
        const sessionDateTime = new Date(sessionTime);
        const now = new Date();
        
        // Уведомление за час до занятия
        const oneHourBefore = new Date(sessionDateTime.getTime() - 60 * 60 * 1000);
        
        if (oneHourBefore > now) {
            setTimeout(() => {
                this.showSessionReminder(sessionTitle, '1 час');
            }, oneHourBefore.getTime() - now.getTime());
        }
        
        // Уведомление за 15 минут до занятия
        const fifteenMinutesBefore = new Date(sessionDateTime.getTime() - 15 * 60 * 1000);
        
        if (fifteenMinutesBefore > now) {
            setTimeout(() => {
                this.showSessionReminder(sessionTitle, '15 минут');
            }, fifteenMinutesBefore.getTime() - now.getTime());
        }
    }
    
    scheduleExamReminders(examDate) {
        const now = new Date();
        const daysToExam = Math.ceil((examDate - now) / (1000 * 60 * 60 * 24));
        
        // Уведомления за 7, 3, 1 день до экзамена
        const reminderDays = [7, 3, 1];
        
        reminderDays.forEach(days => {
            if (daysToExam >= days) {
                const reminderTime = new Date(examDate.getTime() - days * 24 * 60 * 60 * 1000);
                
                setTimeout(() => {
                    this.showExamReminder(days);
                }, reminderTime.getTime() - now.getTime());
            }
        });
    }
    
    checkProgressThreshold(threshold) {
        const progressElement = document.querySelector('.overall-progress');
        if (!progressElement) return;
        
        const currentProgress = parseFloat(progressElement.textContent);
        
        if (currentProgress >= threshold) {
            this.showProgressNotification(threshold);
        }
    }
    
    showSessionReminder(sessionTitle, timeLeft) {
        const notification = new Notification('🦷 Напоминание о занятии', {
            body: `Через ${timeLeft} начинается: ${sessionTitle}`,
            icon: '/static/images/logo.png',
            badge: '/static/images/logo.png',
            tag: 'session-reminder',
            requireInteraction: false,
            actions: [
                {
                    action: 'start',
                    title: 'Начать сейчас'
                },
                {
                    action: 'snooze',
                    title: 'Напомнить через 5 мин'
                }
            ]
        });
        
        notification.onclick = () => {
            window.focus();
            notification.close();
            // Переходим к занятию
            this.navigateToSession();
        };
        
        notification.onaction = (event) => {
            if (event.action === 'start') {
                this.navigateToSession();
            } else if (event.action === 'snooze') {
                setTimeout(() => {
                    this.showSessionReminder(sessionTitle, '5 минут');
                }, 5 * 60 * 1000);
            }
            notification.close();
        };
        
        // Автоматически закрываем через 10 секунд
        setTimeout(() => {
            notification.close();
        }, 10000);
    }
    
    showProgressNotification(threshold) {
        const notification = new Notification('🎉 Достижение!', {
            body: `Вы достигли ${threshold}% прогресса в обучении!`,
            icon: '/static/images/medal.svg',
            badge: '/static/images/logo.png',
            tag: 'progress-achievement',
            requireInteraction: false
        });
        
        notification.onclick = () => {
            window.focus();
            notification.close();
            // Переходим к дашборду
            window.location.href = '/dashboard';
        };
        
        setTimeout(() => {
            notification.close();
        }, 8000);
    }
    
    showExamReminder(daysLeft) {
        const notification = new Notification('⚠️ Напоминание о экзамене', {
            body: `До BIG экзамена осталось ${daysLeft} ${this.pluralize(daysLeft, 'день', 'дня', 'дней')}`,
            icon: '/static/images/logo.png',
            badge: '/static/images/logo.png',
            tag: 'exam-reminder',
            requireInteraction: true,
            actions: [
                {
                    action: 'study',
                    title: 'Продолжить подготовку'
                },
                {
                    action: 'dismiss',
                    title: 'Закрыть'
                }
            ]
        });
        
        notification.onclick = () => {
            window.focus();
            notification.close();
        };
        
        notification.onaction = (event) => {
            if (event.action === 'study') {
                window.location.href = '/dashboard/create-learning-plan';
            }
            notification.close();
        };
    }
    
    showWelcomeNotification() {
        const notification = new Notification('🦷 Добро пожаловать в Mentora Academy!', {
            body: 'Уведомления включены. Вы будете получать напоминания о занятиях и прогрессе.',
            icon: '/static/images/logo.png',
            badge: '/static/images/logo.png',
            tag: 'welcome',
            requireInteraction: false
        });
        
        setTimeout(() => {
            notification.close();
        }, 5000);
    }
    
    showCustomNotification(title, body, options = {}) {
        if (this.permission !== 'granted') {
            return;
        }
        
        const defaultOptions = {
            icon: '/static/images/logo.png',
            badge: '/static/images/logo.png',
            requireInteraction: false
        };
        
        const notification = new Notification(title, { ...defaultOptions, ...options });
        
        notification.onclick = () => {
            window.focus();
            notification.close();
        };
        
        if (!options.requireInteraction) {
            setTimeout(() => {
                notification.close();
            }, options.duration || 5000);
        }
        
        return notification;
    }
    
    navigateToSession() {
        // Находим активную сессию и переходим к ней
        const activeSession = document.querySelector('.session-item.active');
        if (activeSession) {
            const sessionUrl = activeSession.dataset.sessionUrl;
            if (sessionUrl) {
                window.location.href = sessionUrl;
            }
        } else {
            // Переходим к планировщику
            window.location.href = '/dashboard/create-learning-plan';
        }
    }
    
    pluralize(number, one, two, five) {
        const n = Math.abs(number);
        const n10 = n % 10;
        const n100 = n % 100;
        
        if (n100 >= 11 && n100 <= 19) {
            return five;
        }
        
        if (n10 === 1) {
            return one;
        }
        
        if (n10 >= 2 && n10 <= 4) {
            return two;
        }
        
        return five;
    }
    
    // Методы для интеграции с планировщиком
    notifySessionCreated(sessionData) {
        this.showCustomNotification(
            '📚 Новое занятие запланировано',
            `${sessionData.title} на ${sessionData.date}`,
            {
                tag: 'session-created',
                actions: [
                    {
                        action: 'view',
                        title: 'Посмотреть'
                    }
                ]
            }
        );
    }
    
    notifyPlanUpdated(planData) {
        this.showCustomNotification(
            '📊 План обновлен',
            `Ваш план обучения был адаптирован. Новый прогресс: ${planData.progress}%`,
            {
                tag: 'plan-updated'
            }
        );
    }
    
    notifyAchievementUnlocked(achievement) {
        this.showCustomNotification(
            '🏆 Достижение разблокировано!',
            achievement.title,
            {
                icon: '/static/images/medal.svg',
                tag: 'achievement',
                requireInteraction: true
            }
        );
    }
    
    // Методы для тестирования
    testNotification() {
        this.showCustomNotification(
            '🧪 Тестовое уведомление',
            'Система уведомлений работает корректно!',
            {
                tag: 'test',
                requireInteraction: true
            }
        );
    }
    
    testSessionReminder() {
        this.showSessionReminder('Тестовое занятие по эндодонтии', '5 минут');
    }
    
    testProgressNotification() {
        this.showProgressNotification(50);
    }
    
    testExamReminder() {
        this.showExamReminder(7);
    }
}

// Глобальный экземпляр системы уведомлений
let notificationSystem;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    notificationSystem = new BrowserNotificationSystem();
    
    // Добавляем кнопку тестирования в режиме разработки
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        addTestButtons();
    }
});

function addTestButtons() {
    const testContainer = document.createElement('div');
    testContainer.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: rgba(0,0,0,0.8);
        padding: 10px;
        border-radius: 8px;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        gap: 5px;
    `;
    
    testContainer.innerHTML = `
        <button onclick="notificationSystem.testNotification()" style="padding: 5px 10px; font-size: 12px;">Тест уведомления</button>
        <button onclick="notificationSystem.testSessionReminder()" style="padding: 5px 10px; font-size: 12px;">Тест занятия</button>
        <button onclick="notificationSystem.testProgressNotification()" style="padding: 5px 10px; font-size: 12px;">Тест прогресса</button>
        <button onclick="notificationSystem.testExamReminder()" style="padding: 5px 10px; font-size: 12px;">Тест экзамена</button>
    `;
    
    document.body.appendChild(testContainer);
}

// Экспорт для использования в других модулях
window.NotificationSystem = BrowserNotificationSystem; 