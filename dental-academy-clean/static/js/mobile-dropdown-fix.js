/**
 * Mobile Dropdown Fix
 * Исправление проблем с выпадающими меню на мобильных устройствах
 */

class MobileDropdownFix {
    constructor() {
        this.isMobile = window.innerWidth <= 768;
        this.isTablet = window.innerWidth > 768 && window.innerWidth <= 1024;
        this.init();
    }

    init() {
        if (this.isMobile || this.isTablet) {
            this.setupMobileDropdowns();
            this.setupTouchHandlers();
            this.setupBootstrapDropdownFix();
        }
    }

    /**
     * Настройка выпадающих меню для мобильных устройств
     */
    setupMobileDropdowns() {
        // Находим все выпадающие меню
        const dropdowns = document.querySelectorAll('.dropdown');
        
        dropdowns.forEach(dropdown => {
            const toggle = dropdown.querySelector('.dropdown-toggle');
            const menu = dropdown.querySelector('.dropdown-menu');
            
            if (!toggle || !menu) return;

            // Удаляем стандартные Bootstrap обработчики
            toggle.removeAttribute('data-bs-toggle');
            toggle.removeAttribute('data-bs-auto-close');
            
            // Добавляем собственные обработчики
            this.addCustomDropdownHandlers(toggle, menu, dropdown);
        });
    }

    /**
     * Добавление пользовательских обработчиков для выпадающих меню
     */
    addCustomDropdownHandlers(toggle, menu, dropdown) {
        let isOpen = false;
        let touchStartTime = 0;

        // Обработчик клика/тапа
        const handleToggle = (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            // Закрываем все другие меню
            this.closeAllDropdowns();
            
            // Переключаем текущее меню
            if (isOpen) {
                this.closeDropdown(toggle, menu);
                isOpen = false;
            } else {
                this.openDropdown(toggle, menu);
                isOpen = true;
            }
        };

        // Touch события для мобильных
        toggle.addEventListener('touchstart', (e) => {
            touchStartTime = Date.now();
            e.preventDefault();
        }, { passive: false });

        toggle.addEventListener('touchend', (e) => {
            e.preventDefault();
            const touchDuration = Date.now() - touchStartTime;
            
            // Если тап был коротким (меньше 500ms), считаем его кликом
            if (touchDuration < 500) {
                handleToggle(e);
            }
        }, { passive: false });

        // Клик для десктопа
        toggle.addEventListener('click', handleToggle);

        // Закрытие при клике вне меню
        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target)) {
                this.closeDropdown(toggle, menu);
                isOpen = false;
            }
        });

        // Закрытие при скролле
        window.addEventListener('scroll', () => {
            this.closeDropdown(toggle, menu);
            isOpen = false;
        });

        // Закрытие при изменении ориентации
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.closeDropdown(toggle, menu);
                isOpen = false;
            }, 100);
        });
    }

    /**
     * Открытие выпадающего меню
     */
    openDropdown(toggle, menu) {
        // Добавляем классы
        menu.classList.add('show');
        toggle.classList.add('show');
        toggle.setAttribute('aria-expanded', 'true');
        
        // Позиционирование для мобильных
        if (this.isMobile) {
            this.positionMobileDropdown(menu, toggle);
        }
        
        // Анимация появления
        menu.style.opacity = '0';
        menu.style.transform = 'translateY(-10px) scale(0.95)';
        menu.style.display = 'block';
        
        // Плавная анимация
        requestAnimationFrame(() => {
            menu.style.transition = 'all 0.3s ease';
            menu.style.opacity = '1';
            menu.style.transform = 'translateY(0) scale(1)';
        });
    }

    /**
     * Закрытие выпадающего меню
     */
    closeDropdown(toggle, menu) {
        // Анимация исчезновения
        menu.style.transition = 'all 0.2s ease';
        menu.style.opacity = '0';
        menu.style.transform = 'translateY(-10px) scale(0.95)';
        
        setTimeout(() => {
            menu.classList.remove('show');
            toggle.classList.remove('show');
            toggle.setAttribute('aria-expanded', 'false');
            menu.style.display = 'none';
            menu.style.transition = '';
            menu.style.opacity = '';
            menu.style.transform = '';
        }, 200);
    }

    /**
     * Закрытие всех выпадающих меню
     */
    closeAllDropdowns() {
        const allMenus = document.querySelectorAll('.dropdown-menu.show');
        const allToggles = document.querySelectorAll('.dropdown-toggle.show');
        
        allMenus.forEach(menu => {
            const toggle = menu.previousElementSibling;
            if (toggle) {
                this.closeDropdown(toggle, menu);
            }
        });
        
        allToggles.forEach(toggle => {
            toggle.classList.remove('show');
            toggle.setAttribute('aria-expanded', 'false');
        });
    }

    /**
     * Позиционирование выпадающего меню для мобильных
     */
    positionMobileDropdown(menu, toggle) {
        const toggleRect = toggle.getBoundingClientRect();
        const menuRect = menu.getBoundingClientRect();
        const viewportHeight = window.innerHeight;
        const viewportWidth = window.innerWidth;
        
        // Сбрасываем стили позиционирования
        menu.style.position = 'fixed';
        menu.style.top = 'auto';
        menu.style.left = 'auto';
        menu.style.right = 'auto';
        menu.style.bottom = 'auto';
        menu.style.transform = 'none';
        
        // Определяем позицию
        const spaceBelow = viewportHeight - toggleRect.bottom;
        const spaceAbove = toggleRect.top;
        const spaceRight = viewportWidth - toggleRect.left;
        const spaceLeft = toggleRect.right;
        
        // Позиционируем по вертикали
        if (spaceBelow >= menuRect.height || spaceBelow >= spaceAbove) {
            // Размещаем снизу
            menu.style.top = `${toggleRect.bottom + 5}px`;
        } else {
            // Размещаем сверху
            menu.style.bottom = `${viewportHeight - toggleRect.top + 5}px`;
        }
        
        // Позиционируем по горизонтали
        if (spaceRight >= menuRect.width) {
            // Размещаем слева
            menu.style.left = `${toggleRect.left}px`;
        } else if (spaceLeft >= menuRect.width) {
            // Размещаем справа
            menu.style.right = `${viewportWidth - toggleRect.right}px`;
        } else {
            // Центрируем
            menu.style.left = '50%';
            menu.style.transform = 'translateX(-50%)';
        }
        
        // Ограничиваем размеры
        menu.style.maxWidth = `${Math.min(menuRect.width, viewportWidth - 20)}px`;
        menu.style.maxHeight = `${Math.min(menuRect.height, viewportHeight * 0.6)}px`;
        menu.style.overflowY = 'auto';
    }

    /**
     * Настройка touch обработчиков
     */
    setupTouchHandlers() {
        // Предотвращаем двойной тап для зума
        document.addEventListener('touchstart', (e) => {
            if (e.touches.length > 1) {
                e.preventDefault();
            }
        }, { passive: false });

        // Улучшенная обработка touch событий для выпадающих меню
        const dropdownItems = document.querySelectorAll('.dropdown-item');
        dropdownItems.forEach(item => {
            item.addEventListener('touchstart', (e) => {
                e.stopPropagation();
            });
            
            item.addEventListener('touchend', (e) => {
                e.stopPropagation();
                // Небольшая задержка для лучшего UX
                setTimeout(() => {
                    if (item.href) {
                        window.location.href = item.href;
                    } else if (item.onclick) {
                        item.onclick();
                    }
                }, 100);
            });
        });
    }

    /**
     * Исправление Bootstrap dropdown для мобильных
     */
    setupBootstrapDropdownFix() {
        // Отключаем стандартные Bootstrap dropdown события
        document.addEventListener('DOMContentLoaded', () => {
            // Удаляем Bootstrap инициализацию для мобильных
            if (this.isMobile && window.bootstrap) {
                const dropdownElements = document.querySelectorAll('[data-bs-toggle="dropdown"]');
                dropdownElements.forEach(element => {
                    const dropdown = bootstrap.Dropdown.getInstance(element);
                    if (dropdown) {
                        dropdown.dispose();
                    }
                });
            }
        });
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    new MobileDropdownFix();
});

// Инициализация при изменении размера окна
window.addEventListener('resize', () => {
    // Переинициализируем при изменении размера
    setTimeout(() => {
        new MobileDropdownFix();
    }, 100);
});

// Экспорт для использования в других модулях
window.MobileDropdownFix = MobileDropdownFix;
