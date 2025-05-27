/**
 * Mobile App JavaScript - Dental Academy
 * Optimized for mobile experience
 */

class MobileApp {
    constructor() {
        this.currentTheme = 'light';
        this.isMenuOpen = false;
        this.touchStartY = 0;
        this.touchStartX = 0;
        this.isScrolling = false;
        
        this.init();
    }
    
    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeApp());
        } else {
            this.initializeApp();
        }
    }
    
    initializeApp() {
        console.log('🚀 Mobile App initializing...');
        
        // Core initialization
        this.setupThemeSystem();
        this.setupNavigation();
        this.setupGestures();
        this.setupPWA();
        this.setupAccessibility();
        this.setupPerformanceOptimizations();
        this.setupFlashMessages();
        
        // Initialize components
        this.initializeComponents();
        
        console.log('✅ Mobile App initialized');
    }
    
    // ===== THEME SYSTEM =====
    setupThemeSystem() {
        const savedTheme = localStorage.getItem('theme');
        this.currentTheme = savedTheme || 'light';
        this.applyTheme(this.currentTheme);
        
        // Theme toggle handlers
        const themeToggle = document.getElementById('mobile-theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
        
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
        
        // Show feedback
        this.showToast(
            newTheme === 'dark' ? 'Темная тема включена' : 'Светлая тема включена',
            'success'
        );
    }
    
    applyTheme(theme) {
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        document.body.classList.remove('theme-light', 'theme-dark');
        document.body.classList.add(`theme-${theme}`);
        
        // Update theme icon
        const themeIcon = document.querySelector('.theme-icon');
        const themeText = document.querySelector('.theme-text');
        
        if (themeIcon && themeText) {
            if (theme === 'dark') {
                themeIcon.className = 'bi bi-sun theme-icon';
                themeText.textContent = 'Светлая тема';
            } else {
                themeIcon.className = 'bi bi-moon theme-icon';
                themeText.textContent = 'Темная тема';
            }
        }
        
        // Update meta theme-color for browser
        const metaTheme = document.querySelector('meta[name="theme-color"]');
        if (metaTheme) {
            metaTheme.content = theme === 'dark' ? '#111827' : '#3ECDC1';
        }
    }
    
    // ===== NAVIGATION =====
    setupNavigation() {
        // Back button
        const backBtn = document.getElementById('mobile-back-btn');
        if (backBtn) {
            backBtn.addEventListener('click', () => this.handleBackNavigation());
        }
        
        // Menu button
        const menuBtn = document.getElementById('mobile-menu-btn');
        if (menuBtn) {
            menuBtn.addEventListener('click', () => this.toggleMenu());
        }
        
        // Menu close button
        const menuClose = document.getElementById('mobile-menu-close');
        if (menuClose) {
            menuClose.addEventListener('click', () => this.closeMenu());
        }
        
        // Menu overlay
        const menuOverlay = document.getElementById('mobile-menu-modal');
        if (menuOverlay) {
            menuOverlay.addEventListener('click', (e) => {
                if (e.target === menuOverlay) {
                    this.closeMenu();
                }
            });
        }
        
        // Language selector
        const langSelect = document.getElementById('mobile-language-select');
        if (langSelect) {
            langSelect.addEventListener('change', (e) => this.changeLanguage(e.target.value));
        }
        
        // Bottom navigation active state
        this.updateNavigationState();
        
        // Handle navigation with history API
        window.addEventListener('popstate', () => this.handleHistoryChange());
    }
    
    handleBackNavigation() {
        if (window.history.length > 1) {
            window.history.back();
        } else {
            // Fallback to home page
            window.location.href = '/';
        }
    }
    
    toggleMenu() {
        const menuModal = document.getElementById('mobile-menu-modal');
        if (menuModal) {
            if (this.isMenuOpen) {
                this.closeMenu();
            } else {
                this.openMenu();
            }
        }
    }
    
    openMenu() {
        const menuModal = document.getElementById('mobile-menu-modal');
        if (menuModal) {
            menuModal.style.display = 'flex';
            requestAnimationFrame(() => {
                menuModal.querySelector('.mobile-modal').classList.add('show');
            });
            this.isMenuOpen = true;
            
            // Prevent body scroll
            document.body.style.overflow = 'hidden';
            
            // Focus management
            const firstFocusable = menuModal.querySelector('button, a, input, select');
            if (firstFocusable) {
                firstFocusable.focus();
            }
        }
    }
    
    closeMenu() {
        const menuModal = document.getElementById('mobile-menu-modal');
        if (menuModal) {
            const modal = menuModal.querySelector('.mobile-modal');
            modal.classList.remove('show');
            
            setTimeout(() => {
                menuModal.style.display = 'none';
                document.body.style.overflow = '';
            }, 200);
            
            this.isMenuOpen = false;
        }
    }
    
    changeLanguage(lang) {
        // Update URL with new language
        const currentPath = window.location.pathname;
        const pathParts = currentPath.split('/');
        
        // Check if current path has language code
        const supportedLangs = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa'];
        if (pathParts.length > 1 && supportedLangs.includes(pathParts[1])) {
            pathParts[1] = lang;
        } else {
            pathParts.splice(1, 0, lang);
        }
        
        const newPath = pathParts.join('/');
        window.location.href = newPath;
    }
    
    updateNavigationState() {
        // Update active state based on current page
        const navItems = document.querySelectorAll('.mobile-nav-item');
        const currentPath = window.location.pathname;
        
        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.href && currentPath.includes(new URL(item.href).pathname)) {
                item.classList.add('active');
            }
        });
    }
    
    handleHistoryChange() {
        this.updateNavigationState();
        this.closeMenu();
    }
    
    // ===== GESTURES =====
    setupGestures() {
        // Swipe gestures
        document.addEventListener('touchstart', (e) => this.handleTouchStart(e), { passive: true });
        document.addEventListener('touchmove', (e) => this.handleTouchMove(e), { passive: true });
        document.addEventListener('touchend', (e) => this.handleTouchEnd(e), { passive: true });
        
        // Pull to refresh (if needed)
        this.setupPullToRefresh();
        
        // Prevent double-tap zoom on buttons
        this.preventDoubleZoom();
    }
    
    handleTouchStart(e) {
        const touch = e.touches[0];
        this.touchStartY = touch.clientY;
        this.touchStartX = touch.clientX;
        this.isScrolling = false;
    }
    
    handleTouchMove(e) {
        if (!this.touchStartY || !this.touchStartX) return;
        
        const touch = e.touches[0];
        const diffY = this.touchStartY - touch.clientY;
        const diffX = this.touchStartX - touch.clientX;
        
        // Determine if scrolling
        if (Math.abs(diffY) > Math.abs(diffX)) {
            this.isScrolling = true;
        }
    }
    
    handleTouchEnd(e) {
        if (!this.touchStartY || !this.touchStartX) return;
        
        const touch = e.changedTouches[0];
        const diffY = this.touchStartY - touch.clientY;
        const diffX = this.touchStartX - touch.clientX;
        
        // Swipe right to go back (if at edge)
        if (Math.abs(diffX) > Math.abs(diffY) && diffX < -50 && this.touchStartX < 50) {
            this.handleBackNavigation();
        }
        
        // Reset
        this.touchStartY = 0;
        this.touchStartX = 0;
        this.isScrolling = false;
    }
    
    setupPullToRefresh() {
        let startY = 0;
        let isPulling = false;
        const pullThreshold = 100;
        
        const content = document.getElementById('mobile-main-content');
        if (!content) return;
        
        content.addEventListener('touchstart', (e) => {
            if (content.scrollTop === 0) {
                startY = e.touches[0].clientY;
                isPulling = false;
            }
        }, { passive: true });
        
        content.addEventListener('touchmove', (e) => {
            if (content.scrollTop === 0 && startY) {
                const currentY = e.touches[0].clientY;
                const pullDistance = currentY - startY;
                
                if (pullDistance > 0) {
                    isPulling = true;
                    // Visual feedback could be added here
                }
            }
        }, { passive: true });
        
        content.addEventListener('touchend', () => {
            if (isPulling && (startY - event.changedTouches[0].clientY) < -pullThreshold) {
                // Trigger refresh
                this.refreshPage();
            }
            startY = 0;
            isPulling = false;
        }, { passive: true });
    }
    
    preventDoubleZoom() {
        // Prevent double-tap zoom on interactive elements
        const interactiveElements = document.querySelectorAll('button, .mobile-btn, .mobile-card, .mobile-nav-item');
        
        interactiveElements.forEach(element => {
            let lastTap = 0;
            element.addEventListener('touchend', (e) => {
                const currentTime = new Date().getTime();
                const tapLength = currentTime - lastTap;
                
                if (tapLength < 500 && tapLength > 0) {
                    e.preventDefault();
                }
                lastTap = currentTime;
            });
        });
    }
    
    // ===== PWA FEATURES =====
    setupPWA() {
        // Service Worker registration
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('SW registered:', registration);
                })
                .catch(error => {
                    console.log('SW registration failed:', error);
                });
        }
        
        // Install prompt
        let deferredPrompt;
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            this.showInstallPrompt();
        });
        
        // App installed
        window.addEventListener('appinstalled', () => {
            console.log('PWA installed');
            this.showToast('Приложение установлено!', 'success');
        });
    }
    
    showInstallPrompt() {
        // Could show a custom install prompt
        const installBanner = document.createElement('div');
        installBanner.className = 'mobile-install-prompt';
        installBanner.innerHTML = `
            <div class="mobile-install-content">
                <span>Установить приложение?</span>
                <button class="mobile-btn mobile-btn-small mobile-btn-primary" id="install-btn">
                    Установить
                </button>
                <button class="mobile-btn mobile-btn-small mobile-btn-secondary" id="dismiss-install">
                    Не сейчас
                </button>
            </div>
        `;
        
        document.body.appendChild(installBanner);
        
        // Handle install
        document.getElementById('install-btn').addEventListener('click', async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const result = await deferredPrompt.userChoice;
                console.log('Install result:', result);
                deferredPrompt = null;
            }
            installBanner.remove();
        });
        
        // Handle dismiss
        document.getElementById('dismiss-install').addEventListener('click', () => {
            installBanner.remove();
        });
    }
    
    // ===== ACCESSIBILITY =====
    setupAccessibility() {
        // Focus management for modals
        this.setupFocusTraps();
        
        // Announce page changes for screen readers
        this.setupScreenReaderAnnouncements();
        
        // Keyboard navigation
        this.setupKeyboardNavigation();
        
        // High contrast detection
        this.setupHighContrastMode();
    }
    
    setupFocusTraps() {
        const modals = document.querySelectorAll('.mobile-modal');
        
        modals.forEach(modal => {
            modal.addEventListener('keydown', (e) => {
                if (e.key === 'Tab') {
                    this.trapFocus(e, modal);
                }
                if (e.key === 'Escape') {
                    this.closeMenu();
                }
            });
        });
    }
    
    trapFocus(e, container) {
        const focusableElements = container.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        const firstFocusable = focusableElements[0];
        const lastFocusable = focusableElements[focusableElements.length - 1];
        
        if (e.shiftKey) {
            if (document.activeElement === firstFocusable) {
                lastFocusable.focus();
                e.preventDefault();
            }
        } else {
            if (document.activeElement === lastFocusable) {
                firstFocusable.focus();
                e.preventDefault();
            }
        }
    }
    
    setupScreenReaderAnnouncements() {
        // Create live region for announcements
        const liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'mobile-sr-only';
        liveRegion.id = 'mobile-live-region';
        document.body.appendChild(liveRegion);
    }
    
    announceToScreenReader(message, priority = 'polite') {
        const liveRegion = document.getElementById('mobile-live-region');
        if (liveRegion) {
            liveRegion.setAttribute('aria-live', priority);
            liveRegion.textContent = message;
            
            // Clear after announcement
            setTimeout(() => {
                liveRegion.textContent = '';
            }, 1000);
        }
    }
    
    setupKeyboardNavigation() {
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Escape to close menu
            if (e.key === 'Escape' && this.isMenuOpen) {
                this.closeMenu();
            }
            
            // Alt + M to open menu
            if (e.altKey && e.key === 'm') {
                e.preventDefault();
                this.toggleMenu();
            }
        });
    }
    
    setupHighContrastMode() {
        // Detect high contrast mode
        if (window.matchMedia('(prefers-contrast: high)').matches) {
            document.body.classList.add('high-contrast');
        }
        
        window.matchMedia('(prefers-contrast: high)').addEventListener('change', (e) => {
            if (e.matches) {
                document.body.classList.add('high-contrast');
            } else {
                document.body.classList.remove('high-contrast');
            }
        });
    }
    
    // ===== PERFORMANCE =====
    setupPerformanceOptimizations() {
        // Lazy loading for images
        this.setupLazyLoading();
        
        // Intersection Observer for animations
        this.setupIntersectionObserver();
        
        // Debounce scroll events
        this.setupScrollOptimization();
        
        // Preload critical resources
        this.preloadCriticalResources();
    }
    
    setupLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    }
    
    setupIntersectionObserver() {
        const animatedElements = document.querySelectorAll('.mobile-animate-on-scroll');
        
        const animationObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('mobile-animated');
                    animationObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        animatedElements.forEach(el => animationObserver.observe(el));
    }
    
    setupScrollOptimization() {
        let ticking = false;
        
        const updateScrollPosition = () => {
            // Update scroll-based UI elements
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            // Could hide/show header based on scroll direction
            // this.updateHeaderVisibility(scrollTop);
            
            ticking = false;
        };
        
        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(updateScrollPosition);
                ticking = true;
            }
        }, { passive: true });
    }
    
    preloadCriticalResources() {
        // Preload critical CSS and JS
        const criticalResources = [
            '/static/css/mobile-app.css',
            '/static/js/mobile-app.js'
        ];
        
        criticalResources.forEach(resource => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.href = resource;
            link.as = resource.endsWith('.css') ? 'style' : 'script';
            document.head.appendChild(link);
        });
    }
    
    // ===== FLASH MESSAGES =====
    setupFlashMessages() {
        // Handle server-side flash messages
        this.processServerFlashMessages();
        
        // Setup dynamic flash messages
        this.createFlashMessageContainer();
    }
    
    processServerFlashMessages() {
        const serverMessages = document.querySelectorAll('.alert');
        serverMessages.forEach(message => {
            const type = this.getMessageType(message.className);
            const text = message.querySelector('.flash-text')?.textContent || message.textContent;
            
            if (text) {
                this.showToast(text, type);
                message.remove();
            }
        });
    }
    
    getMessageType(className) {
        if (className.includes('alert-success')) return 'success';
        if (className.includes('alert-danger') || className.includes('alert-error')) return 'error';
        if (className.includes('alert-warning')) return 'warning';
        return 'info';
    }
    
    createFlashMessageContainer() {
        if (!document.getElementById('mobile-toast-container')) {
            const container = document.createElement('div');
            container.id = 'mobile-toast-container';
            document.body.appendChild(container);
        }
    }
    
    showToast(message, type = 'info', duration = 4000) {
        const container = document.getElementById('mobile-toast-container');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = `mobile-toast mobile-toast-${type}`;
        
        const icons = {
            success: 'bi-check-circle-fill',
            error: 'bi-exclamation-triangle-fill',
            warning: 'bi-exclamation-circle-fill',
            info: 'bi-info-circle-fill'
        };
        
        toast.innerHTML = `
            <div class="mobile-toast-content">
                <div class="mobile-toast-icon">
                    <i class="${icons[type]}"></i>
                </div>
                <div class="mobile-toast-text">${message}</div>
            </div>
        `;
        
        container.appendChild(toast);
        
        // Show toast
        requestAnimationFrame(() => {
            toast.classList.add('show');
        });
        
        // Auto hide
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, duration);
        
        // Announce to screen readers
        this.announceToScreenReader(message);
    }
    
    // ===== COMPONENT INITIALIZATION =====
    initializeComponents() {
        // Initialize progress bars
        this.initializeProgressBars();
        
        // Initialize cards
        this.initializeCards();
        
        // Initialize forms
        this.initializeForms();
    }
    
    initializeProgressBars() {
        const progressBars = document.querySelectorAll('.mobile-progress-fill');
        
        const progressObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const progressBar = entry.target;
                    const targetWidth = progressBar.style.width;
                    
                    progressBar.style.width = '0%';
                    setTimeout(() => {
                        progressBar.style.width = targetWidth;
                    }, 100);
                    
                    progressObserver.unobserve(progressBar);
                }
            });
        });
        
        progressBars.forEach(bar => progressObserver.observe(bar));
    }
    
    initializeCards() {
        const cards = document.querySelectorAll('.mobile-card');
        
        cards.forEach(card => {
            // Add touch feedback
            card.addEventListener('touchstart', () => {
                card.style.transform = 'scale(0.98)';
            }, { passive: true });
            
            card.addEventListener('touchend', () => {
                card.style.transform = '';
            }, { passive: true });
            
            card.addEventListener('touchcancel', () => {
                card.style.transform = '';
            }, { passive: true });
        });
    }
    
    initializeForms() {
        // Auto-resize textareas
        const textareas = document.querySelectorAll('textarea');
        textareas.forEach(textarea => {
            textarea.addEventListener('input', () => {
                textarea.style.height = 'auto';
                textarea.style.height = textarea.scrollHeight + 'px';
            });
        });
        
        // Form validation feedback
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!form.checkValidity()) {
                    e.preventDefault();
                    this.showFormValidationErrors(form);
                }
            });
        });
    }
    
    showFormValidationErrors(form) {
        const invalidFields = form.querySelectorAll(':invalid');
        if (invalidFields.length > 0) {
            const firstInvalid = invalidFields[0];
            firstInvalid.focus();
            
            const errorMessage = firstInvalid.validationMessage || 'Пожалуйста, заполните это поле';
            this.showToast(errorMessage, 'error');
        }
    }
    
    // ===== UTILITY METHODS =====
    refreshPage() {
        this.showToast('Обновление...', 'info', 1000);
        setTimeout(() => {
            window.location.reload();
        }, 500);
    }
    
    // Global method for showing notifications
    static showNotification(message, type = 'info', duration = 4000) {
        if (window.mobileApp) {
            window.mobileApp.showToast(message, type, duration);
        }
    }
}

// Initialize mobile app
document.addEventListener('DOMContentLoaded', () => {
    window.mobileApp = new MobileApp();
});

// Global utilities
window.showMobileToast = (message, type, duration) => {
    if (window.mobileApp) {
        window.mobileApp.showToast(message, type, duration);
    }
};

window.closeMobileMenu = () => {
    if (window.mobileApp) {
        window.mobileApp.closeMenu();
    }
};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MobileApp;
}