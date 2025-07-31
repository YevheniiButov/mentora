/**
 * JavaScript для детального вида предмета
 * Обеспечивает интерактивность и анимации
 */

// Глобальные переменные
let currentView = 'grid';
let progressAnimations = [];
let toastContainer = null;

// Инициализация страницы
function initSubjectDetail() {
    console.log('🚀 Инициализация детального вида предмета...');
    
    // Создаем контейнер для toast уведомлений
    createToastContainer();
    
    // Инициализируем компоненты
    initModuleCards();
    initScrollAnimations();
    initKeyboardNavigation();
    initTooltips();
    
    // Показываем welcome анимацию
    animatePageLoad();
    
    console.log('✅ Детальный вид предмета инициализирован');
}

// Инициализация круговых индикаторов прогресса
function initProgressCircles() {
    const circles = document.querySelectorAll('.progress-circle');
    
    circles.forEach(circle => {
        const progress = parseInt(circle.dataset.progress) || 0;
        
        // Устанавливаем CSS переменную для анимации
        circle.style.setProperty('--progress', progress);
        
        // Анимируем появление
        setTimeout(() => {
            circle.style.background = `conic-gradient(
                var(--profession-primary) 0deg,
                var(--profession-primary) ${progress * 3.6}deg,
                #f1f5f9 ${progress * 3.6}deg
            )`;
        }, 500);
        
        // Анимируем число
        animateNumber(circle.querySelector('.progress-text'), 0, progress, 1500, '%');
    });
}

// Переключение вида модулей (сетка/список)
function initViewToggle() {
    const viewButtons = document.querySelectorAll('.view-btn');
    const container = document.getElementById('modules-container');
    
    viewButtons.forEach(button => {
        button.addEventListener('click', () => {
            const view = button.dataset.view;
            
            // Обновляем активное состояние кнопок
            viewButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Переключаем вид
            switchView(view, container);
        });
    });
}

// Переключение между видами
function switchView(view, container) {
    container.style.opacity = '0.5';
    container.style.transform = 'scale(0.95)';
    
    setTimeout(() => {
        container.className = view === 'grid' ? 'modules-grid' : 'modules-list';
        currentView = view;
        
        // Сохраняем предпочтение пользователя
        localStorage.setItem('modules-view-preference', view);
        
        container.style.opacity = '1';
        container.style.transform = 'scale(1)';
        
        // Показываем toast
        showToast(`Weergave gewijzigd naar ${view === 'grid' ? 'raster' : 'lijst'}`, 'info');
    }, 200);
}

// Инициализация карточек модулей
function initModuleCards() {
    const moduleCards = document.querySelectorAll('.module-card');
    
    moduleCards.forEach((card, index) => {
        // Анимация появления с задержкой
        setTimeout(() => {
            card.classList.add('animate-slide-up');
        }, index * 100);
        
        // Обработчик клика для быстрого перехода
        card.addEventListener('click', (e) => {
            // Игнорируем клики по кнопкам
            if (e.target.closest('.module-action')) return;
            
            const moduleId = card.dataset.moduleId;
            if (moduleId) {
                // Добавляем эффект loading
                card.style.transform = 'scale(0.98)';
                card.style.opacity = '0.8';
                
                setTimeout(() => {
                    window.location.href = `/lesson/module/${moduleId}`;
                }, 200);
            }
        });
        
        // Hover эффекты для прогресс-баров
        const progressBar = card.querySelector('.progress-fill');
        if (progressBar) {
            card.addEventListener('mouseenter', () => {
                progressBar.style.transform = 'scaleY(1.2)';
                progressBar.style.transformOrigin = 'bottom';
            });
            
            card.addEventListener('mouseleave', () => {
                progressBar.style.transform = 'scaleY(1)';
            });
        }
    });
}

// Инициализация достижений
function initAchievements() {
    const achievements = document.querySelectorAll('.achievement-item');
    
    achievements.forEach((achievement, index) => {
        if (achievement.classList.contains('earned')) {
            // Анимация для заработанных достижений
            setTimeout(() => {
                achievement.style.animation = 'pulse 0.6s ease-out';
            }, index * 200);
        }
        
        // Tooltip для достижений
        achievement.addEventListener('mouseenter', (e) => {
            showAchievementTooltip(e.target, achievement);
        });
        
        achievement.addEventListener('mouseleave', () => {
            hideAchievementTooltip();
        });
    });
}

// Анимация чисел
function animateNumber(element, start, end, duration, suffix = '') {
    const startTime = performance.now();
    const range = end - start;
    
    function animate(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function (ease-out)
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = start + (range * easeOut);
        
        element.textContent = Math.round(current) + suffix;
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    }
    
    requestAnimationFrame(animate);
}

// Анимация загрузки страницы
function animatePageLoad() {
    const header = document.querySelector('.subject-detail-header');
    const sidebar = document.querySelector('.sidebar-sticky');
    
    // Анимация заголовка
    if (header) {
        header.style.opacity = '0';
        header.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            header.style.transition = 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
            header.style.opacity = '1';
            header.style.transform = 'translateY(0)';
        }, 100);
    }
    
    // Анимация боковой панели
    if (sidebar) {
        sidebar.style.opacity = '0';
        sidebar.style.transform = 'translateX(20px)';
        
        setTimeout(() => {
            sidebar.style.transition = 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
            sidebar.style.opacity = '1';
            sidebar.style.transform = 'translateX(0)';
        }, 300);
    }
}

// Инициализация анимаций при скролле
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-slide-up');
                
                // Анимируем прогресс-бары при появлении
                const progressBars = entry.target.querySelectorAll('.progress-fill');
                progressBars.forEach(bar => {
                    const width = bar.style.width;
                    bar.style.width = '0%';
                    setTimeout(() => {
                        bar.style.transition = 'width 1s ease-out';
                        bar.style.width = width;
                    }, 200);
                });
            }
        });
    }, observerOptions);
    
    // Наблюдаем за карточками
    document.querySelectorAll('.module-card, .progress-card, .achievements-card').forEach(card => {
        observer.observe(card);
    });
}

// Инициализация клавиатурной навигации
function initKeyboardNavigation() {
    document.addEventListener('keydown', (e) => {
        // Быстрые клавиши
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case '1':
                    e.preventDefault();
                    switchView('grid', document.getElementById('modules-container'));
                    break;
                case '2':
                    e.preventDefault();
                    switchView('list', document.getElementById('modules-container'));
                    break;
                case 'k':
                    e.preventDefault();
                    focusSearchInput();
                    break;
            }
        }
        
        // Навигация по модулям стрелками
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
            const moduleCards = Array.from(document.querySelectorAll('.module-card'));
            const focused = document.activeElement;
            const currentIndex = moduleCards.indexOf(focused);
            
            if (currentIndex !== -1) {
                e.preventDefault();
                const nextIndex = e.key === 'ArrowDown' 
                    ? Math.min(currentIndex + 1, moduleCards.length - 1)
                    : Math.max(currentIndex - 1, 0);
                
                moduleCards[nextIndex].focus();
            }
        }
    });
    
    // Делаем карточки модулей фокусируемыми
    document.querySelectorAll('.module-card').forEach(card => {
        card.setAttribute('tabindex', '0');
        
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                card.click();
            }
        });
    });
}

// Инициализация подсказок
function initTooltips() {
    // Создаем общий tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.style.cssText = `
        position: absolute;
        background: rgba(0, 0, 0, 0.9);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.375rem;
        font-size: 0.875rem;
        z-index: 1000;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.2s ease;
        max-width: 200px;
        word-wrap: break-word;
    `;
    document.body.appendChild(tooltip);
    
    // Добавляем tooltip к элементам с data-tooltip
    document.querySelectorAll('[data-tooltip]').forEach(element => {
        element.addEventListener('mouseenter', (e) => {
            const text = e.target.dataset.tooltip;
            if (text) {
                tooltip.textContent = text;
                tooltip.style.opacity = '1';
                
                // Позиционируем tooltip
                const rect = e.target.getBoundingClientRect();
                tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
                tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
            }
        });
        
        element.addEventListener('mouseleave', () => {
            tooltip.style.opacity = '0';
        });
    });
}

// Система уведомлений (Toast)
function createToastContainer() {
    if (toastContainer) return;
    
    toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container';
    toastContainer.style.cssText = `
        position: fixed;
        top: 2rem;
        right: 2rem;
        z-index: 1050;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        max-width: 400px;
    `;
    document.body.appendChild(toastContainer);
}

function showToast(message, type = 'info', duration = 4000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const colors = {
        info: '#3b82f6',
        success: '#22c55e',
        warning: '#f59e0b',
        error: '#ef4444'
    };
    
    const icons = {
        info: 'ℹ️',
        success: '✅',
        warning: '⚠️',
        error: '❌'
    };
    
    toast.style.cssText = `
        background: white;
        color: #1f2937;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        border-left: 4px solid ${colors[type]};
        transform: translateX(100%);
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-weight: 500;
        position: relative;
        cursor: pointer;
    `;
    
    toast.innerHTML = `
        <span style="font-size: 1.125rem;">${icons[type]}</span>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" style="
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            background: none;
            border: none;
            font-size: 1.125rem;
            cursor: pointer;
            color: #6b7280;
            line-height: 1;
            padding: 0;
            width: 1.5rem;
            height: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
        ">×</button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Анимация появления
    requestAnimationFrame(() => {
        toast.style.transform = 'translateX(0)';
    });
    
    // Автоматическое удаление
    setTimeout(() => {
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 300);
    }, duration);
    
    // Удаление по клику
    toast.addEventListener('click', () => {
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    });
}

// Подсказки для достижений
function showAchievementTooltip(target, achievement) {
    const isEarned = achievement.classList.contains('earned');
    const name = achievement.querySelector('.achievement-name').textContent;
    
    const tooltips = {
        'Starter': isEarned ? 'Je bent begonnen met leren! 🚀' : 'Start je eerste module om dit te verdienen',
        'Student': isEarned ? 'Je hebt 25% voltooid! 📚' : 'Voltooi 25% van de modules',
        'Scholar': isEarned ? 'Halverwege! Goed bezig! 🎓' : 'Voltooi 50% van de modules',
        'Expert': isEarned ? 'Je bent bijna een expert! ⭐' : 'Voltooi 75% van de modules',
        'Master': isEarned ? 'Gefeliciteerd! Je bent een master! 🏆' : 'Voltooi alle modules'
    };
    
    const tooltip = document.querySelector('.custom-tooltip');
    if (tooltip && tooltips[name]) {
        tooltip.textContent = tooltips[name];
        tooltip.style.opacity = '1';
        
        const rect = target.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.bottom + 8 + 'px';
    }
}

function hideAchievementTooltip() {
    const tooltip = document.querySelector('.custom-tooltip');
    if (tooltip) {
        tooltip.style.opacity = '0';
    }
}

// API функции
async function updateModuleProgress(moduleId, progress) {
    try {
        const response = await fetch(`/api/modules/${moduleId}/progress`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ progress })
        });
        
        if (response.ok) {
            const data = await response.json();
            showToast('Voortgang opgeslagen!', 'success');
            return data;
        } else {
            throw new Error('Failed to update progress');
        }
    } catch (error) {
        console.error('Error updating progress:', error);
        showToast('Fout bij opslaan voortgang', 'error');
    }
}

async function loadStudySettings() {
    try {
        const response = await fetch('/api/study-settings');
        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        console.error('Error loading study settings:', error);
    }
    return null;
}

// Утилиты
function getCSRFToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.getAttribute('content') : '';
}

function focusSearchInput() {
    const searchInput = document.querySelector('#search-input, .search-input, [type="search"]');
    if (searchInput) {
        searchInput.focus();
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Экспорт прогресса
async function exportProgress() {
    try {
        showToast('Bezig met exporteren...', 'info');
        
        const response = await fetch('/api/export/progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'my_progress.pdf';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showToast('Voortgang geëxporteerd!', 'success');
        } else {
            throw new Error('Export failed');
        }
    } catch (error) {
        console.error('Export error:', error);
        showToast('Fout bij exporteren', 'error');
    }
}

// Восстановление предпочтений пользователя
function restoreUserPreferences() {
    // Восстанавливаем вид модулей
    const savedView = localStorage.getItem('modules-view-preference');
    if (savedView && savedView !== currentView) {
        const container = document.getElementById('modules-container');
        const viewButton = document.querySelector(`[data-view="${savedView}"]`);
        if (container && viewButton) {
            viewButton.click();
        }
    }
    
    // Восстанавливаем другие настройки
    loadStudySettings().then(settings => {
        if (settings) {
            console.log('👤 Настройки пользователя загружены:', settings);
        }
    });
}

// Очистка при выходе со страницы
window.addEventListener('beforeunload', () => {
    // Очищаем анимации
    progressAnimations.forEach(animation => {
        if (animation.cancel) animation.cancel();
    });
    
    // Сохраняем состояние
    const scrollPosition = window.pageYOffset;
    sessionStorage.setItem('subject-scroll-position', scrollPosition);
});

// Восстановление состояния при загрузке
window.addEventListener('load', () => {
    const scrollPosition = sessionStorage.getItem('subject-scroll-position');
    if (scrollPosition) {
        window.scrollTo(0, parseInt(scrollPosition));
        sessionStorage.removeItem('subject-scroll-position');
    }
    
    restoreUserPreferences();
});

// Обработка ошибок
window.addEventListener('error', (e) => {
    console.error('JavaScript error:', e.error);
    
    // Показываем пользователю friendly сообщение только для критических ошибок
    if (e.error && e.error.message && e.error.message.includes('fetch')) {
        showToast('Probleem met netwerkverbinding', 'warning');
    }
});

// Экспорт функций для глобального использования
window.SubjectDetail = {
    showToast,
    updateModuleProgress,
    exportProgress,
    switchView,
    initProgressCircles,
    animateNumber
};

console.log('📚 Subject Detail JavaScript loaded successfully');

// CSS стили для анимаций (инжектируем в head)
const animationStyles = `
<style>
@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}

.animate-slide-up {
    animation: slideUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.module-card {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.module-card:focus {
    outline: 2px solid var(--profession-primary);
    outline-offset: 2px;
}

.progress-fill {
    transition: width 1s ease-out, transform 0.2s ease;
}

.achievement-item {
    transition: all 0.3s ease;
}

.achievement-item:hover {
    transform: translateY(-2px);
}
</style>
`;

// Добавляем стили в head
document.head.insertAdjacentHTML('beforeend', animationStyles);