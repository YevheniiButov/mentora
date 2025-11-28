class ThemeController {
    constructor() {
        // Синхронизация с картой обучения - используем те же ключи
        const THEME_STORAGE_KEY = 'mentora_theme';
        const THEME_AUTO_KEY = 'mentora_theme_auto';
        
        // Инициализация состояния
        this.systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        
        // Проверяем сохраненную тему из карты обучения или старую систему
        const savedTheme = localStorage.getItem(THEME_STORAGE_KEY) || localStorage.getItem('theme');
        const autoTheme = localStorage.getItem(THEME_AUTO_KEY) === 'true';
        
        if (autoTheme || savedTheme === 'system') {
            this.theme = 'system';
            this.isDark = this.systemTheme === 'dark';
        } else {
            this.theme = savedTheme || 'light';
            this.isDark = this.calculateIsDark();
        }
        
        // Синхронизируем со старой системой
        if (savedTheme) {
            localStorage.setItem('theme', savedTheme);
            localStorage.setItem('isDark', this.isDark);
        }
        
        // Инициализация
        this.init();
    }

    calculateIsDark() {
        const THEME_STORAGE_KEY = 'mentora_theme';
        const savedTheme = localStorage.getItem(THEME_STORAGE_KEY) || localStorage.getItem('theme');
        
        if (this.theme === 'system') {
            return this.systemTheme === 'dark';
        } else if (this.theme === 'toggle') {
            return localStorage.getItem('isDark') === 'true';
        }
        // Проверяем сохраненную тему
        if (savedTheme === 'dark' || savedTheme === 'light') {
            return savedTheme === 'dark';
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
        
        // Слушаем изменения темы из других страниц (например, карты обучения)
        window.addEventListener('themechange', (e) => {
            const THEME_STORAGE_KEY = 'mentora_theme';
            const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
            
            // Обновляем тему если она изменилась из другого источника
            if (e.detail && e.detail.appliedTheme) {
                const newTheme = e.detail.appliedTheme;
                if (newTheme !== (this.isDark ? 'dark' : 'light')) {
                    this.isDark = newTheme === 'dark';
                    this.theme = newTheme;
                    this.applyTheme();
                }
            }
        });
        
        // Слушаем изменения localStorage (синхронизация между вкладками)
        window.addEventListener('storage', (e) => {
            const THEME_STORAGE_KEY = 'mentora_theme';
            if (e.key === THEME_STORAGE_KEY || e.key === 'theme') {
                const newTheme = e.newValue;
                if (newTheme && (newTheme === 'dark' || newTheme === 'light')) {
                    this.theme = newTheme;
                    this.isDark = newTheme === 'dark';
                    this.applyTheme();
                }
            }
        });
    }

    applyTheme() {
        // Применяем тему к документу
        const appliedTheme = this.isDark ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', appliedTheme);
        
        // Обновляем meta theme-color для мобильных браузеров
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        metaThemeColor.content = appliedTheme === 'dark' ? '#1a1a2e' : '#3ECDC1';
        
        // Принудительно обновляем color-scheme
        document.documentElement.style.colorScheme = appliedTheme;
        
        // Отправляем событие
        this.notifyThemeChange();
    }

    toggleTheme() {
        const THEME_STORAGE_KEY = 'mentora_theme';
        const THEME_AUTO_KEY = 'mentora_theme_auto';
        
        // Определяем текущую тему
        const currentIsDark = this.isDark || document.documentElement.getAttribute('data-theme') === 'dark';
        
        // Переключаем на противоположную тему
        this.isDark = !currentIsDark;
        const newTheme = this.isDark ? 'dark' : 'light';
        
        // Сохраняем в обе системы для совместимости
        localStorage.setItem(THEME_STORAGE_KEY, newTheme);
        localStorage.setItem(THEME_AUTO_KEY, 'false');
        localStorage.setItem('theme', newTheme);
        localStorage.setItem('isDark', this.isDark);
        
        // Устанавливаем тему
        this.theme = newTheme;
        
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