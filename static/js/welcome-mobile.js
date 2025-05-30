/**
 * Welcome Mobile JavaScript - Dental Academy
 * Premium interactive welcome screen
 */

class WelcomeMobileApp {
    constructor() {
        this.deferredPrompt = null;
        this.isMenuOpen = false;
        this.isLanguageMenuOpen = false;
        this.currentTheme = 'light';
        
        console.log('🚀 Welcome Mobile App initializing...');
        this.init();
    }
    
    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeApp());
        } else {
            this.initializeApp();
        }
    }
    
    initializeApp() {
        // Core functionality
        this.setupMenu();
        this.setupThemeToggle();
        this.setupLanguageSelector();
        this.setupPWAInstall();
        
        // Visual enhancements
        this.setupAnimations();
        this.setupParticles();
        this.setupCounters();
        
        // User interactions
        this.setupTouchFeedback();
        this.setupKeyboardShortcuts();
        
        console.log('✅ Welcome Mobile App initialized');
    }
    
    // ===== MENU SYSTEM =====
    setupMenu() {
        const menuToggle = document.getElementById('menuToggle');
        const dropdownMenu = document.getElementById('dropdownMenu');
        const menuOverlay = document.getElementById('menuOverlay');
        
        if (!menuToggle || !dropdownMenu || !menuOverlay) return;
        
        // Toggle menu
        menuToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleMenu();
        });
        
        // Close menu when clicking overlay
        menuOverlay.addEventListener('click', () => {
            this.closeMenu();
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!dropdownMenu.contains(e.target) && !menuToggle.contains(e.target)) {
                this.closeMenu();
            }
        });
        
        // Prevent menu close when clicking inside menu
        dropdownMenu.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }
    
    toggleMenu() {
        const menuToggle = document.getElementById('menuToggle');
        const dropdownMenu = document.getElementById('dropdownMenu');
        const menuOverlay = document.getElementById('menuOverlay');
        
        this.isMenuOpen = !this.isMenuOpen;
        
        menuToggle.classList.toggle('active', this.isMenuOpen);
        dropdownMenu.classList.toggle('active', this.isMenuOpen);
        menuOverlay.classList.toggle('active', this.isMenuOpen);
        
        // Haptic feedback
        if (navigator.vibrate) {
            navigator.vibrate(50);
        }
        
        // Prevent body scroll when menu is open
        document.body.style.overflow = this.isMenuOpen ? 'hidden' : '';
    }
    
    closeMenu() {
        if (!this.isMenuOpen) return;
        
        this.isMenuOpen = false;
        this.isLanguageMenuOpen = false;
        
        document.getElementById('menuToggle').classList.remove('active');
        document.getElementById('dropdownMenu').classList.remove('active');
        document.getElementById('menuOverlay').classList.remove('active');
        document.getElementById('languageSubmenu').classList.remove('active');
        
        document.body.style.overflow = '';
    }
    
    // ===== THEME SYSTEM =====
    setupThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        const themeIcon = document.querySelector('.theme-icon');
        
        if (!themeToggle || !themeIcon) return;
        
        // Load saved theme
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.applyTheme(this.currentTheme);
        
        // Theme toggle click
        themeToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleTheme();
        });
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                this.applyTheme(e.matches ? 'dark' : 'light');
            }
        });
    }
    
    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
        localStorage.setItem('theme', newTheme);
        
        // Haptic feedback
        if (navigator.vibrate) {
            navigator.vibrate([50, 50, 50]);
        }
        
        // Show notification
        this.showNotification(
            window.WelcomeConfig?.translations?.themeChanged || 'Theme changed',
            'success'
        );
    }
    
    applyTheme(theme) {
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        document.body.setAttribute('data-theme', theme);
        
        // Update toggle switch
        const themeToggle = document.getElementById('themeToggle');
        const themeIcon = document.querySelector('.theme-icon');
        
        if (themeToggle && themeIcon) {
            themeToggle.classList.toggle('active', theme === 'dark');
            themeIcon.className = `bi bi-${theme === 'dark' ? 'sun' : 'moon'} theme-icon`;
        }
        
        // Update meta theme-color
        const metaTheme = document.querySelector('meta[name="theme-color"]');
        if (metaTheme) {
            metaTheme.content = theme === 'dark' ? '#0f172a' : '#667eea';
        }
    }
    
    // ===== LANGUAGE SYSTEM =====
    setupLanguageSelector() {
        const languageItem = document.getElementById('languageItem');
        const languageSubmenu = document.getElementById('languageSubmenu');
        const languageOptions = document.querySelectorAll('.language-option');
        
        if (!languageItem || !languageSubmenu) return;
        
        // Toggle language submenu
        languageItem.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleLanguageMenu();
        });
        
        // Language option selection
        languageOptions.forEach(option => {
            option.addEventListener('click', (e) => {
                e.stopPropagation();
                const selectedLang = option.dataset.lang;
                if (selectedLang && !option.classList.contains('active')) {
                    this.changeLanguage(selectedLang);
                }
            });
        });
    }
    
    toggleLanguageMenu() {
        const languageSubmenu = document.getElementById('languageSubmenu');
        this.isLanguageMenuOpen = !this.isLanguageMenuOpen;
        languageSubmenu.classList.toggle('active', this.isLanguageMenuOpen);
        
        // Haptic feedback
        if (navigator.vibrate) {
            navigator.vibrate(30);
        }
    }
    
    changeLanguage(langCode) {
        console.log(`🌍 Changing language to: ${langCode}`);
        
        // Show loading state
        this.showNotification('Changing language...', 'info', 1000);
        
        // Update URL with new language
        const currentPath = window.location.pathname;
        const pathParts = currentPath.split('/');
        const supportedLangs = window.WelcomeConfig?.supportedLanguages || 
                              ['en', 'nl', 'ru', 'uk', 'es', 'pt', 'tr', 'fa'];
        
        // Replace or add language code in URL
        if (pathParts.length > 1 && supportedLangs.includes(pathParts[1])) {
            pathParts[1] = langCode;
        } else {
            pathParts.splice(1, 0, langCode);
        }
        
        const newPath = pathParts.join('/');
        const search = window.location.search;
        
        // Navigate to new URL
        setTimeout(() => {
            window.location.href = newPath + search;
        }, 300);
    }
    
    // ===== PWA INSTALL =====
    setupPWAInstall() {
        const installItem = document.getElementById('installItem');
        
        // Listen for install prompt
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;
            
            // Show install option in menu
            if (installItem) {
                installItem.style.display = 'flex';
                installItem.addEventListener('click', () => this.promptInstall());
            }
        });
        
        // Handle app installed
        window.addEventListener('appinstalled', () => {
            console.log('📱 App installed successfully');
            this.deferredPrompt = null;
            
            if (installItem) {
                installItem.style.display = 'none';
            }
            
            this.showNotification(
                window.WelcomeConfig?.translations?.installSuccess || 'App installed!',
                'success'
            );
        });
    }
    
    promptInstall() {
        if (!this.deferredPrompt) return;
        
        this.deferredPrompt.prompt();
        
        this.deferredPrompt.userChoice.then((result) => {
            console.log('📱 Install prompt result:', result.outcome);
            this.deferredPrompt = null;
            
            if (result.outcome === 'accepted') {
                this.closeMenu();
            }
        });
    }
    
    // ===== ANIMATIONS =====
    setupAnimations() {
        // Intersection Observer for scroll animations
        const observerOptions = {
            threshold: 0.2,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.classList.add('animate-in');
                    }, index * 100);
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);
        
        // Observe animated elements
        document.querySelectorAll('[data-animate]').forEach(el => {
            observer.observe(el);
        });
        
        // Trigger animations immediately for elements in viewport
        setTimeout(() => {
            document.querySelectorAll('[data-animate]').forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.top < window.innerHeight && rect.bottom > 0) {
                    el.classList.add('animate-in');
                }
            });
        }, 300);
    }
    
    // ===== PARTICLE SYSTEM =====
    setupParticles() {
        const particlesContainer = document.getElementById('particlesContainer');
        if (!particlesContainer) return;
        
        // Create particles
        const particleCount = window.innerWidth < 768 ? 15 : 25;
        
        for (let i = 0; i < particleCount; i++) {
            setTimeout(() => {
                this.createParticle(particlesContainer);
            }, i * 200);
        }
        
        // Continuously create particles
        setInterval(() => {
            if (document.visibilityState === 'visible') {
                this.createParticle(particlesContainer);
            }
        }, 3000);
    }
    
    createParticle(container) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        // Random position and properties
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDuration = (20 + Math.random() * 10) + 's';
        particle.style.animationDelay = Math.random() * 5 + 's';
        
        // Random size
        const size = 2 + Math.random() * 2;
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';
        
        // Random opacity
        particle.style.opacity = 0.3 + Math.random() * 0.4;
        
        container.appendChild(particle);
        
        // Remove particle after animation
        setTimeout(() => {
            if (particle.parentNode) {
                particle.parentNode.removeChild(particle);
            }
        }, 30000);
    }
    
    // ===== COUNTERS =====
    setupCounters() {
        const counters = document.querySelectorAll('[data-count]');
        
        const animateCounter = (element) => {
            const target = parseInt(element.dataset.count);
            const duration = 2000;
            const start = Date.now();
            
            const updateCounter = () => {
                const now = Date.now();
                const progress = Math.min((now - start) / duration, 1);
                
                // Easing function (ease out cubic)
                const easeOutCubic = 1 - Math.pow(1 - progress, 3);
                const current = Math.floor(easeOutCubic * target);
                
                element.textContent = current.toLocaleString();
                
                if (progress < 1) {
                    requestAnimationFrame(updateCounter);
                }
            };
            
            updateCounter();
        };
        
        // Animate counters when they come into view
        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        animateCounter(entry.target);
                    }, 500);
                    counterObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        counters.forEach(counter => {
            counterObserver.observe(counter);
        });
    }
    
    // ===== TOUCH FEEDBACK =====
    setupTouchFeedback() {
        const interactiveElements = document.querySelectorAll(
            '.glass-card, .menu-item, .btn-primary, .btn-secondary, .language-option'
        );
        
        interactiveElements.forEach(element => {
            element.addEventListener('touchstart', (e) => {
                element.style.transform = 'scale(0.98)';
                this.createRipple(e, element);
                
                // Haptic feedback
                if (navigator.vibrate) {
                    navigator.vibrate(25);
                }
            });
            
            element.addEventListener('touchend', () => {
                setTimeout(() => {
                    element.style.transform = '';
                }, 150);
            });
            
            element.addEventListener('touchcancel', () => {
                element.style.transform = '';
            });
        });
    }
    
    createRipple(event, element) {
        const circle = document.createElement('div');
        const diameter = Math.max(element.clientWidth, element.clientHeight);
        const radius = diameter / 2;
        
        const touch = event.touches[0] || event;
        const rect = element.getBoundingClientRect();
        
        circle.style.width = circle.style.height = diameter + 'px';
        circle.style.left = (touch.clientX - rect.left - radius) + 'px';
        circle.style.top = (touch.clientY - rect.top - radius) + 'px';
        circle.style.position = 'absolute';
        circle.style.borderRadius = '50%';
        circle.style.background = 'rgba(255, 255, 255, 0.3)';
        circle.style.transform = 'scale(0)';
        circle.style.animation = 'ripple-animation 0.6s linear';
        circle.style.pointerEvents = 'none';
        circle.style.zIndex = '1000';
        
        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(circle);
        
        setTimeout(() => {
            if (circle.parentNode) {
                circle.parentNode.removeChild(circle);
            }
        }, 600);
    }
    
    // ===== KEYBOARD SHORTCUTS =====
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Escape to close menu
            if (e.key === 'Escape') {
                this.closeMenu();
            }
            
            // Ctrl/Cmd + Shift + T for theme toggle
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 't') {
                e.preventDefault();
                this.toggleTheme();
            }
            
            // Ctrl/Cmd + Shift + M for menu toggle
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'm') {
                e.preventDefault();
                this.toggleMenu();
            }
        });
    }
    
    // ===== NOTIFICATIONS =====
    showNotification(message, type = 'info', duration = 3000) {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.welcome-notification');
        existingNotifications.forEach(notification => notification.remove());
        
        // Create notification
        const notification = document.createElement('div');
        notification.className = `welcome-notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">
                    ${this.getNotificationIcon(type)}
                </div>
                <span class="notification-text">${message}</span>
            </div>
        `;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            left: 16px;
            right: 16px;
            max-width: 400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 16px;
            padding: 16px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
            z-index: 10000;
            transform: translateY(-100px);
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        requestAnimationFrame(() => {
            notification.style.transform = 'translateY(0)';
            notification.style.opacity = '1';
        });
        
        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                notification.style.transform = 'translateY(-100px)';
                notification.style.opacity = '0';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }, duration);
        }
    }
    
    getNotificationIcon(type) {
        const icons = {
            success: '<i class="bi bi-check-circle-fill" style="color: #22c55e;"></i>',
            error: '<i class="bi bi-x-circle-fill" style="color: #ef4444;"></i>',
            warning: '<i class="bi bi-exclamation-triangle-fill" style="color: #f59e0b;"></i>',
            info: '<i class="bi bi-info-circle-fill" style="color: #3b82f6;"></i>'
        };
        return icons[type] || icons.info;
    }
}

// Add ripple animation styles
const rippleStyles = document.createElement('style');
rippleStyles.textContent = `
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .notification-icon {
        font-size: 1.2rem;
    }
    
    .notification-text {
        flex: 1;
        color: #374151;
        font-weight: 500;
    }
`;
document.head.appendChild(rippleStyles);

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    window.welcomeApp = new WelcomeMobileApp();
});

// Global exposure for debugging
window.WelcomeMobileApp = WelcomeMobileApp;