/**
 * ЕДИНАЯ АДМИН ПАНЕЛЬ - JAVASCRIPT
 * Современный интерфейс для управления Mentora
 */

class AdminUnified {
    constructor() {
        this.sidebar = document.getElementById('sidebar');
        this.sidebarToggle = document.getElementById('sidebar-toggle');
        this.mobileSidebarToggle = document.getElementById('mobile-sidebar-toggle');
        this.themeToggle = document.getElementById('theme-toggle');
        this.loadingOverlay = document.getElementById('loading-overlay');
        
        this.init();
    }

    init() {
        this.initSidebar();
        this.initTheme();
        this.initNotifications();
        this.initTooltips();
        this.initConfirmations();
        this.initAjaxForms();
        this.initDashboardUpdates();
    }

    // ============================================
    // SIDEBAR УПРАВЛЕНИЕ
    // ============================================

    initSidebar() {
        // Мобильное меню
        if (this.mobileSidebarToggle) {
            this.mobileSidebarToggle.addEventListener('click', () => {
                this.toggleSidebar();
            });
        }

        if (this.sidebarToggle) {
            this.sidebarToggle.addEventListener('click', () => {
                this.toggleSidebar();
            });
        }

        // Закрытие сайдбара при клике вне его на мобильных
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                if (!this.sidebar.contains(e.target) && 
                    !this.mobileSidebarToggle.contains(e.target)) {
                    this.hideSidebar();
                }
            }
        });

        // Обработка изменения размера экрана
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768) {
                this.hideSidebar();
            }
        });
    }

    toggleSidebar() {
        if (this.sidebar) {
            this.sidebar.classList.toggle('show');
        }
    }

    hideSidebar() {
        if (this.sidebar) {
            this.sidebar.classList.remove('show');
        }
    }

    // ============================================
    // ТЕМА
    // ============================================

    initTheme() {
        if (!this.themeToggle) return;

        // Загрузка сохраненной темы
        const savedTheme = localStorage.getItem('admin-theme') || 'light';
        this.setTheme(savedTheme);

        this.themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            this.setTheme(newTheme);
        });
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('admin-theme', theme);
        
        if (this.themeToggle) {
            const icon = this.themeToggle.querySelector('i');
            icon.className = theme === 'dark' ? 'bi bi-sun' : 'bi bi-moon';
        }
    }

    // ============================================
    // УВЕДОМЛЕНИЯ
    // ============================================

    initNotifications() {
        this.checkForNotifications();
        // Обновляем уведомления каждые 30 секунд
        setInterval(() => this.checkForNotifications(), 30000);
    }

    checkForNotifications() {
        // Здесь можно делать запрос к серверу для получения уведомлений
        // Пока что просто обновляем счетчик
        const notificationCount = document.getElementById('notification-count');
        if (notificationCount) {
            // Заглушка - в реальном приложении это будет AJAX запрос
            notificationCount.textContent = '0';
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show notification-toast`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Добавляем стили для toast уведомлений
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            max-width: 500px;
        `;

        document.body.appendChild(notification);

        // Автоматическое скрытие через 5 секунд
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    // ============================================
    // TOOLTIPS
    // ============================================

    initTooltips() {
        // Инициализация Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // ============================================
    // ПОДТВЕРЖДЕНИЯ
    // ============================================

    initConfirmations() {
        document.addEventListener('click', (e) => {
            const confirmBtn = e.target.closest('[data-confirm]');
            if (!confirmBtn) return;

            e.preventDefault();
            
            const message = confirmBtn.getAttribute('data-confirm');
            const confirmType = confirmBtn.getAttribute('data-confirm-type') || 'warning';
            
            this.showConfirmDialog(message, confirmType, () => {
                // Если это ссылка
                if (confirmBtn.tagName === 'A') {
                    window.location.href = confirmBtn.href;
                }
                // Если это форма
                else if (confirmBtn.type === 'submit') {
                    confirmBtn.closest('form').submit();
                }
                // Если это кнопка с data-action
                else if (confirmBtn.hasAttribute('data-action')) {
                    this.executeAction(confirmBtn.getAttribute('data-action'), confirmBtn);
                }
            });
        });
    }

    showConfirmDialog(message, type, onConfirm) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="bi bi-exclamation-triangle text-${type}"></i>
                            Подтверждение
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${message}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
                        <button type="button" class="btn btn-${type}" id="confirm-action">Подтвердить</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        modal.querySelector('#confirm-action').addEventListener('click', () => {
            bsModal.hide();
            onConfirm();
        });

        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }

    // ============================================
    // AJAX ФОРМЫ
    // ============================================

    initAjaxForms() {
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (!form.hasAttribute('data-ajax')) return;

            e.preventDefault();
            this.submitAjaxForm(form);
        });
    }

    async submitAjaxForm(form) {
        this.showLoading();
        
        try {
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: form.method || 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            const data = await response.json();
            
            if (data.success) {
                this.showNotification(data.message, 'success');
                
                // Если указан redirect
                if (data.redirect) {
                    setTimeout(() => {
                        window.location.href = data.redirect;
                    }, 1000);
                }
                
                // Если нужно обновить страницу
                if (form.hasAttribute('data-reload')) {
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                }
            } else {
                this.showNotification(data.message || 'Произошла ошибка', 'danger');
            }
        } catch (error) {
            console.error('Ошибка отправки формы:', error);
            this.showNotification('Произошла ошибка при отправке формы', 'danger');
        } finally {
            this.hideLoading();
        }
    }

    // ============================================
    // LOADING
    // ============================================

    showLoading() {
        if (this.loadingOverlay) {
            this.loadingOverlay.classList.remove('d-none');
        }
    }

    hideLoading() {
        if (this.loadingOverlay) {
            this.loadingOverlay.classList.add('d-none');
        }
    }

    // ============================================
    // DASHBOARD UPDATES
    // ============================================

    initDashboardUpdates() {
        // Обновление статистики дашборда каждые 60 секунд
        if (window.location.pathname.includes('/admin') && 
            window.location.pathname.includes('/dashboard')) {
            setInterval(() => this.updateDashboardStats(), 60000);
        }
    }

    async updateDashboardStats() {
        try {
            if (!window.adminConfig || !window.adminConfig.urls.dashboard_stats) return;
            
            const response = await fetch(window.adminConfig.urls.dashboard_stats);
            const data = await response.json();
            
            if (data.success) {
                this.updateDashboardElements(data.stats);
            }
        } catch (error) {
            console.error('Ошибка обновления статистики:', error);
        }
    }

    updateDashboardElements(stats) {
        // Обновление элементов дашборда с новой статистикой
        Object.keys(stats).forEach(key => {
            const element = document.querySelector(`[data-stat="${key}"]`);
            if (element) {
                element.textContent = stats[key];
            }
        });
    }

    // ============================================
    // UTILITIES
    // ============================================

    getCsrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : '';
    }

    executeAction(action, element) {
        // Здесь можно добавить различные действия
        console.log('Executing action:', action, element);
    }

    // ============================================
    // API HELPERS
    // ============================================

    async apiCall(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            }
        };

        const response = await fetch(url, { ...defaultOptions, ...options });
        return response.json();
    }

    async apiGet(url) {
        return this.apiCall(url, { method: 'GET' });
    }

    async apiPost(url, data) {
        return this.apiCall(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async apiPut(url, data) {
        return this.apiCall(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async apiDelete(url) {
        return this.apiCall(url, { method: 'DELETE' });
    }
}

// ============================================
// ИНИЦИАЛИЗАЦИЯ
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    window.adminUnified = new AdminUnified();
});

// ============================================
// ГЛОБАЛЬНЫЕ HELPER ФУНКЦИИ
// ============================================

window.showAdminNotification = (message, type = 'info') => {
    if (window.adminUnified) {
        window.adminUnified.showNotification(message, type);
    }
};

window.showAdminLoading = () => {
    if (window.adminUnified) {
        window.adminUnified.showLoading();
    }
};

window.hideAdminLoading = () => {
    if (window.adminUnified) {
        window.adminUnified.hideLoading();
    }
};

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('adminSidebar');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
    }
    
    // Theme Toggle
    const themeToggle = document.getElementById('themeToggle');
    const html = document.documentElement;
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('admin-theme', newTheme);
            
            // Update icon
            const icon = themeToggle.querySelector('i');
            icon.className = newTheme === 'dark' ? 'bi bi-sun' : 'bi bi-moon';
        });
        
        // Load saved theme
        const savedTheme = localStorage.getItem('admin-theme') || 'light';
        html.setAttribute('data-theme', savedTheme);
        const icon = themeToggle.querySelector('i');
        icon.className = savedTheme === 'dark' ? 'bi bi-sun' : 'bi bi-moon';
    }
    
    // Auto-hide alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
}); 