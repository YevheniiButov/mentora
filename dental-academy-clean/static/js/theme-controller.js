class ThemeController {
    constructor() {
        // Инициализация состояния
        this.systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        this.theme = localStorage.getItem('theme') || 'light';
        this.isDark = this.calculateIsDark();
        
        // Инициализация
        this.init();
        
        // Отладочная информация
    }

    calculateIsDark() {
        if (this.theme === 'system') {
            return this.systemTheme === 'dark';
        } else if (this.theme === 'toggle') {
            return localStorage.getItem('isDark') === 'true';
        }
        return this.theme === 'dark';
    }

    init() {
        // Применяем начальную тему
        this.applyTheme();
        
        // Слушаем системные изменения темы
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            this.systemTheme = e.matches ? 'dark' : 'light';
            if (this.theme === 'system') {
                this.isDark = this.calculateIsDark();
                this.applyTheme();
            }
        });
    }

    applyTheme() {
        // Применяем тему к документу
        document.documentElement.setAttribute('data-theme', this.isDark ? 'dark' : 'light');
        
        // Отправляем событие
        this.notifyThemeChange();
    }

    toggleTheme() {
        if (this.theme !== 'toggle') {
            // Если не в режиме toggle, переключаемся на него
            this.theme = 'toggle';
            this.isDark = true; // Начинаем с темной темы
        } else {
            // В режиме toggle просто инвертируем текущее состояние
            this.isDark = !this.isDark;
        }
        
        // Сохраняем состояние
        localStorage.setItem('theme', this.theme);
        localStorage.setItem('isDark', this.isDark);
        
        // Применяем изменения
        this.applyTheme();
    }

    notifyThemeChange() {
        const event = new CustomEvent('themechange', {
            detail: {
                theme: this.theme,
                isDark: this.isDark,
                appliedTheme: this.isDark ? 'dark' : 'light'
            }
        });
        window.dispatchEvent(event);
    }
}

// Инициализация контроллера при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.themeController = new ThemeController();
}); 