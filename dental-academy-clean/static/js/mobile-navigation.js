/**
 * Мобильная навигация для карты обучения
 * Управляет drawer-меню и мобильными компонентами
 */

class MobileNavigation {
    constructor() {
        this.isInitialized = false;
        this.isDrawerOpen = false;
        this.init();
    }

    init() {
        if (this.isInitialized) return;
        
        this.setupElements();
        this.setupEventListeners();
        this.setupTouchGestures();
        this.isInitialized = true;

    }

    setupElements() {
        this.navToggle = document.getElementById('mobileNavToggle');
        this.drawer = document.getElementById('mobileDrawer');
        this.overlay = document.getElementById('mobileDrawerOverlay');
        this.body = document.body;
        
        if (!this.navToggle || !this.drawer || !this.overlay) {
            console.warn('⚠️ Не найдены элементы мобильной навигации');
            return;
        }
    }

    setupEventListeners() {
        // Переключение drawer
        this.navToggle?.addEventListener('click', () => this.toggleDrawer());
        
        // Закрытие по клику на overlay
        this.overlay?.addEventListener('click', () => this.closeDrawer());
        
        // Закрытие по Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isDrawerOpen) {
                this.closeDrawer();
            }
        });

        // Обработка кликов по предметам в drawer
        this.drawer?.addEventListener('click', (e) => {
            const subjectItem = e.target.closest('.subject-item');
            if (subjectItem) {
                const subjectId = subjectItem.dataset.subject;
                if (subjectId) {
                    this.navigateToSubject(subjectId);
                    this.closeDrawer();
                }
            }
        });

        // Обработка кликов по путям обучения
        this.drawer?.addEventListener('click', (e) => {
            const pathButton = e.target.closest('.learning-path-button');
            if (pathButton) {
                this.togglePathExpansion(pathButton);
            }
        });
    }

    setupTouchGestures() {
        let startX = 0;
        let startY = 0;
        let isDragging = false;

        // Swipe для открытия drawer
        document.addEventListener('touchstart', (e) => {
            if (e.touches.length === 1) {
                startX = e.touches[0].clientX;
                startY = e.touches[0].clientY;
                isDragging = false;
            }
        });

        document.addEventListener('touchmove', (e) => {
            if (e.touches.length === 1 && !this.isDrawerOpen) {
                const currentX = e.touches[0].clientX;
                const currentY = e.touches[0].clientY;
                const deltaX = currentX - startX;
                const deltaY = currentY - startY;

                // Проверяем, что это горизонтальный swipe
                if (Math.abs(deltaX) > Math.abs(deltaY) && deltaX > 50) {
                    isDragging = true;
                }
            }
        });

        document.addEventListener('touchend', (e) => {
            if (isDragging && !this.isDrawerOpen) {
                this.openDrawer();
            }
            isDragging = false;
        });

        // Swipe для закрытия drawer
        this.drawer?.addEventListener('touchstart', (e) => {
            if (e.touches.length === 1) {
                startX = e.touches[0].clientX;
                startY = e.touches[0].clientY;
                isDragging = false;
            }
        });

        this.drawer?.addEventListener('touchmove', (e) => {
            if (e.touches.length === 1 && this.isDrawerOpen) {
                const currentX = e.touches[0].clientX;
                const currentY = e.touches[0].clientY;
                const deltaX = currentX - startX;
                const deltaY = currentY - startY;

                // Проверяем, что это горизонтальный swipe влево
                if (Math.abs(deltaX) > Math.abs(deltaY) && deltaX < -50) {
                    isDragging = true;
                }
            }
        });

        this.drawer?.addEventListener('touchend', (e) => {
            if (isDragging && this.isDrawerOpen) {
                this.closeDrawer();
            }
            isDragging = false;
        });
    }

    toggleDrawer() {
        if (this.isDrawerOpen) {
            this.closeDrawer();
        } else {
            this.openDrawer();
        }
    }

    openDrawer() {
        if (!this.drawer || !this.overlay || !this.navToggle) return;

        this.drawer.classList.add('active');
        this.overlay.classList.add('active');
        this.navToggle.classList.add('active');
        this.body.style.overflow = 'hidden';
        this.isDrawerOpen = true;

        // Анимация появления
        this.drawer.style.transform = 'translateX(0)';

    }

    closeDrawer() {
        if (!this.drawer || !this.overlay || !this.navToggle) return;

        this.drawer.classList.remove('active');
        this.overlay.classList.remove('active');
        this.navToggle.classList.remove('active');
        this.body.style.overflow = '';
        this.isDrawerOpen = false;

        // Анимация скрытия
        this.drawer.style.transform = 'translateX(-100%)';

    }

    togglePathExpansion(button) {
        const pathId = button.dataset.path;
        const subjectList = document.getElementById(`mobile-path-filter-list-${pathId}`);
        
        if (!subjectList) return;

        const isExpanded = subjectList.classList.contains('expanded');
        
        // Закрываем все другие списки
        document.querySelectorAll('.subject-list').forEach(list => {
            list.classList.remove('expanded');
        });

        // Открываем/закрываем текущий список
        if (!isExpanded) {
            subjectList.classList.add('expanded');
        }

        // Анимация chevron
        const chevron = button.querySelector('.chevron-icon');
        if (chevron) {
            chevron.style.transform = isExpanded ? 'rotate(0deg)' : 'rotate(90deg)';
        }
    }

    navigateToSubject(subjectId) {
        const currentLang = document.documentElement.lang || 'nl';
        const url = `/${currentLang}/learning-map/subject/${subjectId}`;

        window.location.href = url;
    }

    // Обновление прогресса
    updateProgress(stats) {
        const progressCircle = document.querySelector('.mobile-progress-circle .circle-progress');
        if (progressCircle && stats.total_progress !== undefined) {
            const circumference = 2 * Math.PI * 36; // r=36
            const progress = (stats.total_progress / 100) * circumference;
            progressCircle.style.strokeDasharray = `${progress} ${circumference}`;
        }

        // Обновляем текстовые значения
        const progressText = document.querySelector('.mobile-progress-text');
        if (progressText && stats.total_progress !== undefined) {
            progressText.textContent = `${stats.total_progress}%`;
        }
    }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    // Проверяем, что мы на мобильном устройстве
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        window.mobileNavigation = new MobileNavigation();
    }
});

// Обработка изменения размера окна
window.addEventListener('resize', () => {
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile && !window.mobileNavigation) {
        window.mobileNavigation = new MobileNavigation();
    } else if (!isMobile && window.mobileNavigation) {
        // Закрываем drawer при переходе на десктоп
        window.mobileNavigation.closeDrawer();
        window.mobileNavigation = null;
    }
});

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MobileNavigation;
} 