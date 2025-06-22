class ThemeController {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'light';
        this.systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        this.init();
    }

    init() {
        // Устанавливаем начальную тему
        this.setTheme(this.theme);

        // Слушаем изменения системной темы
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            if (this.theme === 'system') {
                this.setTheme(e.matches ? 'dark' : 'light');
            }
        });

        // Добавляем переключатель темы в DOM
        this.addThemeToggle();
    }

    setTheme(theme) {
        // Сохраняем выбор пользователя
        this.theme = theme;
        localStorage.setItem('theme', theme);

        // Применяем тему
        if (theme === 'system') {
            document.documentElement.setAttribute('data-theme', this.systemTheme);
        } else {
            document.documentElement.setAttribute('data-theme', theme);
        }

        // Обновляем иконку переключателя
        this.updateToggleIcon();

        // Уведомляем о изменении темы
        this.notifyThemeChange();
    }

    toggleTheme() {
        const newTheme = this.theme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    addThemeToggle() {
        // Создаем переключатель темы
        const toggle = document.createElement('button');
        toggle.className = 'theme-toggle';
        toggle.setAttribute('aria-label', 'Toggle theme');
        toggle.innerHTML = this.getToggleIcon();

        // Добавляем обработчик
        toggle.addEventListener('click', () => this.toggleTheme());

        // Добавляем в DOM
        const header = document.querySelector('.header');
        if (header) {
            header.appendChild(toggle);
        }
    }

    getToggleIcon() {
        return this.theme === 'light' 
            ? '<i class="bi bi-moon-fill"></i>'
            : '<i class="bi bi-sun-fill"></i>';
    }

    updateToggleIcon() {
        const toggle = document.querySelector('.theme-toggle');
        if (toggle) {
            toggle.innerHTML = this.getToggleIcon();
        }
    }

    notifyThemeChange() {
        // Создаем и отправляем событие
        const event = new CustomEvent('themechange', {
            detail: { theme: this.theme }
        });
        window.dispatchEvent(event);
    }
}

// Инициализация контроллера
document.addEventListener('DOMContentLoaded', () => {
    window.themeController = new ThemeController();
});

// Дополнительные стили для анимаций
const additionalStyles = `
@keyframes slideOutUp {
    from {
        transform: translateY(0);
        opacity: 1;
    }
    to {
        transform: translateY(-100%);
        opacity: 0;
    }
}

.notification-content {
    display: flex;
    align-items: center;
    gap: 12px;
}

.notification-content i {
    font-size: 18px;
}
`;

// Добавляем стили
const style = document.createElement('style');
style.textContent = additionalStyles;
document.head.appendChild(style);

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeController;
} 