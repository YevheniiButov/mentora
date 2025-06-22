/**
 * Универсальная система навигации по категориям для Dental Academy
 * Автоматически работает с любыми категориями, созданными через админ-панель
 * Включает fallback механизмы и отладку
 */

class UniversalCategorySystem {
    constructor(options = {}) {
        // Конфигурация с разумными значениями по умолчанию
        this.config = {
            categorySelector: '.learning-path-button',  // Изменено для LearningPath
            listSelector: '.subject-list', 
            itemSelector: '.subcategory-item',
            expandedClass: 'expanded',
            forceVisibleClass: 'force-visible',
            debugMode: options.debug || false,
            animationDuration: 400,
            useFallback: true,
            autoInit: true,
            ...options
        };
        
        // Состояние системы
        this.isInitialized = false;
        this.categories = new Map();
        this.activeCategory = null;
        
        // Счетчики для мониторинга
        this.stats = {
            categoriesFound: 0,
            successfulToggles: 0,
            fallbackUsed: 0,
            errors: 0
        };
        
        this.log('🚀 Инициализация UniversalCategorySystem');
        
        if (this.config.autoInit) {
            this.init();
        }
    }
    
    log(message, ...args) {
        if (this.config.debugMode) {
            console.log(`[CategorySystem] ${message}`, ...args);
        }
    }
    
    warn(message, ...args) {
        console.warn(`[CategorySystem] ⚠️ ${message}`, ...args);
    }
    
    error(message, ...args) {
        console.error(`[CategorySystem] ❌ ${message}`, ...args);
        this.stats.errors++;
    }
    
    init() {
        // Ждем полной загрузки DOM
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            // DOM уже загружен, инициализируем с небольшой задержкой
            setTimeout(() => this.setup(), 50);
        }
        
        // Наблюдаем за изменениями DOM для динамически добавляемых категорий
        this.setupMutationObserver();
    }
    
    setup() {
        this.log('📱 Настройка универсальной системы категорий');
        
        try {
            // Сканируем все категории на странице
            this.scanCategories();
            
            // Настраиваем event delegation для автоматической работы с новыми элементами
            this.setupEventDelegation();
            
            // Включаем отладочный режим если нужно
            if (this.config.debugMode) {
                this.enableDebugMode();
            }
            
            // Добавляем стили для fallback
            this.injectFallbackStyles();
            
            // Проверяем работоспособность CSS
            this.testCSSAnimations();
            
            this.isInitialized = true;
            this.log('✅ Система категорий готова к работе');
            this.logStats();
            
            // Экспортируем в window для отладки
            window.categorySystem = this;
            
        } catch (error) {
            this.error('Ошибка при инициализации:', error);
        }
    }
    
    scanCategories() {
        const categoryButtons = document.querySelectorAll(this.config.categorySelector);
        this.stats.categoriesFound = categoryButtons.length;
        
        this.log(`🔍 Найдено категорий: ${categoryButtons.length}`);
        
        if (categoryButtons.length === 0) {
            this.warn('Категории не найдены! Проверьте селектор:', this.config.categorySelector);
            this.warn('Ищем элементы с классом .learning-path-button (LearningPath) или .content-category (ContentCategory)');
            return;
        }
        
        // Регистрируем каждую категорию
        categoryButtons.forEach((button, index) => {
            this.registerCategory(button, index);
        });
    }
    
    registerCategory(button, index) {
        // Поддерживаем и LearningPath и ContentCategory
        const categoryId = button.getAttribute('data-path') || button.getAttribute('data-category');
        
        if (!categoryId) {
            this.error(`Кнопка ${index} не имеет атрибута data-path или data-category:`, button);
            return;
        }
        
        // Ищем соответствующий список (поддерживаем оба формата ID)
        let listId = `path-${categoryId}-subjects`;  // Для LearningPath
        let list = document.getElementById(listId);
        
        if (!list) {
            listId = `category-${categoryId}-subcategories`;  // Для ContentCategory
            list = document.getElementById(listId);
        }
        
        if (!list) {
            this.error(`Список не найден для категории ${categoryId}: #${listId}`);
            return;
        }
        
        // Настраиваем категорию
        const categoryData = {
            id: categoryId,
            button,
            list,
            items: list.querySelectorAll(this.config.itemSelector),
            isExpanded: false
        };
        
        // Сохраняем в коллекцию
        this.categories.set(categoryId, categoryData);
        
        // Настраиваем ARIA атрибуты
        button.setAttribute('aria-expanded', 'false');
        button.setAttribute('aria-controls', listId);
        button.setAttribute('role', 'button');
        button.setAttribute('tabindex', '0');
        
        // Добавляем type="button" если это не задано
        if (button.tagName === 'BUTTON' && !button.hasAttribute('type')) {
            button.setAttribute('type', 'button');
        }
        
        this.log(`✅ Категория зарегистрирована: ID=${categoryId}, элементов=${categoryData.items.length}`);
    }
    
    setupEventDelegation() {
        // Универсальный обработчик через делегирование
        document.addEventListener('click', (e) => {
            const categoryButton = e.target.closest(this.config.categorySelector);
            if (categoryButton) {
                e.preventDefault();
                e.stopPropagation();
                
                const categoryId = categoryButton.getAttribute('data-path') || categoryButton.getAttribute('data-category');
                if (categoryId) {
                    this.toggleCategory(categoryId);
                }
            }
        });
        
        // Поддержка клавиатуры
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                const categoryButton = e.target.closest(this.config.categorySelector);
                if (categoryButton) {
                    e.preventDefault();
                    const categoryId = categoryButton.getAttribute('data-path') || categoryButton.getAttribute('data-category');
                    if (categoryId) {
                        this.toggleCategory(categoryId);
                    }
                }
            }
        });
        
        this.log('📡 Event delegation настроен');
    }
    
    setupMutationObserver() {
        // Наблюдаем за добавлением новых категорий
        const observer = new MutationObserver((mutations) => {
            let newCategoriesFound = false;
            
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // Проверяем добавленные элементы на наличие категорий
                        const newCategories = node.querySelectorAll ? 
                            node.querySelectorAll(this.config.categorySelector) : [];
                        
                        if (newCategories.length > 0) {
                            newCategoriesFound = true;
                        }
                        
                        // Проверяем сам элемент
                        if (node.matches && node.matches(this.config.categorySelector)) {
                            newCategoriesFound = true;
                        }
                    }
                });
            });
            
            if (newCategoriesFound) {
                this.log('🔄 Обнаружены новые категории, пересканирование...');
                setTimeout(() => this.scanCategories(), 100);
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        this.log('👁️ MutationObserver активен');
    }
    
    toggleCategory(categoryId) {
        this.log(`🔄 Переключение категории: ${categoryId}`);
        
        const category = this.categories.get(categoryId);
        
        if (!category) {
            this.error(`Категория не найдена: ${categoryId}`);
            return false;
        }
        
        try {
            const wasExpanded = category.isExpanded;
            
            // Закрываем все остальные категории
            this.closeAllCategories(categoryId);
            
            // Переключаем текущую категорию
            if (wasExpanded) {
                this.closeCategory(categoryId);
            } else {
                this.openCategory(categoryId);
            }
            
            this.stats.successfulToggles++;
            return true;
            
        } catch (error) {
            this.error(`Ошибка при переключении категории ${categoryId}:`, error);
            
            // Fallback: принудительное переключение
            if (this.config.useFallback) {
                this.forceCategoryToggle(categoryId);
            }
            
            return false;
        }
    }
    
    openCategory(categoryId) {
        const category = this.categories.get(categoryId);
        if (!category) return;
        
        this.log(`🔓 Открытие категории: ${categoryId}`);
        
        const { button, list, items } = category;
        
        // Метод 1: CSS классы
        list.classList.add(this.config.expandedClass);
        list.setAttribute('data-expanded', 'true');
        
        // Метод 2: ARIA
        button.setAttribute('aria-expanded', 'true');
        
        // Метод 3: Fallback через inline стили (если CSS не работает)
        if (this.config.useFallback) {
            setTimeout(() => {
                if (this.getComputedOpacity(list) < 0.5) {
                    this.log(`🔧 CSS не работает для ${categoryId}, используем fallback`);
                    this.applyFallbackStyles(list, items, true);
                    this.stats.fallbackUsed++;
                }
            }, 100);
        }
        
        // Обновляем состояние
        category.isExpanded = true;
        this.activeCategory = categoryId;
        
        // Плавная прокрутка к открытой категории
        setTimeout(() => {
            button.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'nearest',
                inline: 'nearest'
            });
        }, 200);
        
        this.log(`✅ Категория ${categoryId} открыта`);
    }
    
    closeCategory(categoryId) {
        const category = this.categories.get(categoryId);
        if (!category) return;
        
        this.log(`🔒 Закрытие категории: ${categoryId}`);
        
        const { button, list, items } = category;
        
        // Метод 1: Убираем CSS классы
        list.classList.remove(this.config.expandedClass, this.config.forceVisibleClass);
        list.removeAttribute('data-expanded');
        
        // Метод 2: ARIA
        button.setAttribute('aria-expanded', 'false');
        
        // Метод 3: Очищаем fallback стили
        this.clearFallbackStyles(list, items);
        
        // Обновляем состояние
        category.isExpanded = false;
        if (this.activeCategory === categoryId) {
            this.activeCategory = null;
        }
        
        this.log(`✅ Категория ${categoryId} закрыта`);
    }
    
    closeAllCategories(exceptCategoryId = null) {
        this.categories.forEach((category, categoryId) => {
            if (categoryId !== exceptCategoryId && category.isExpanded) {
                this.closeCategory(categoryId);
            }
        });
    }
    
    forceCategoryToggle(categoryId) {
        this.log(`⚡ Принудительное переключение категории: ${categoryId}`);
        
        const category = this.categories.get(categoryId);
        if (!category) return;
        
        const { list, items } = category;
        const isCurrentlyVisible = list.classList.contains(this.config.forceVisibleClass);
        
        if (isCurrentlyVisible) {
            // Закрываем
            list.classList.remove(this.config.forceVisibleClass);
            this.clearFallbackStyles(list, items);
            category.isExpanded = false;
        } else {
            // Открываем
            this.closeAllCategories(categoryId);
            list.classList.add(this.config.forceVisibleClass);
            this.applyFallbackStyles(list, items, true);
            category.isExpanded = true;
            this.activeCategory = categoryId;
        }
        
        this.stats.fallbackUsed++;
    }
    
    applyFallbackStyles(list, items, visible) {
        if (visible) {
            // Показываем список
            Object.assign(list.style, {
                display: 'block',
                maxHeight: 'none',
                opacity: '1',
                overflow: 'visible',
                visibility: 'visible',
                transform: 'translateY(0)',
                marginTop: '0.75rem',
                paddingTop: '0.5rem'
            });
            
            // Показываем элементы
            items.forEach((item, index) => {
                setTimeout(() => {
                    Object.assign(item.style, {
                        opacity: '1',
                        transform: 'translateX(0)',
                        visibility: 'visible'
                    });
                }, index * 50);
            });
        } else {
            // Скрываем
            list.style.cssText = '';
            items.forEach(item => {
                item.style.cssText = '';
            });
        }
    }
    
    clearFallbackStyles(list, items) {
        list.style.cssText = '';
        items.forEach(item => {
            item.style.cssText = '';
        });
    }
    
    getComputedOpacity(element) {
        return parseFloat(window.getComputedStyle(element).opacity) || 0;
    }
    
    testCSSAnimations() {
        // Создаем тестовый элемент для проверки CSS
        const testElement = document.createElement('div');
        testElement.className = this.config.listSelector.replace('.', '') + ' ' + this.config.expandedClass;
        testElement.style.position = 'absolute';
        testElement.style.left = '-9999px';
        
        document.body.appendChild(testElement);
        
        const opacity = this.getComputedOpacity(testElement);
        document.body.removeChild(testElement);
        
        if (opacity < 0.8) {
            this.warn('CSS анимации могут работать некорректно, включен fallback режим');
            this.config.useFallback = true;
        } else {
            this.log('✅ CSS анимации работают корректно');
        }
    }
    
    injectFallbackStyles() {
        // Добавляем критические стили если они отсутствуют
        const style = document.createElement('style');
        style.textContent = `
            ${this.config.listSelector}.${this.config.forceVisibleClass} {
                display: block !important;
                max-height: none !important;
                opacity: 1 !important;
                overflow: visible !important;
                visibility: visible !important;
            }
            ${this.config.listSelector}.${this.config.forceVisibleClass} ${this.config.itemSelector} {
                opacity: 1 !important;
                transform: none !important;
                visibility: visible !important;
            }
        `;
        document.head.appendChild(style);
        
        this.log('💉 Fallback стили добавлены');
    }
    
    enableDebugMode() {
        // Отладочный режим отключен в продакшене
        this.log('🐛 Отладочный режим отключен');
    }
    
    logStats() {
        // Статистика в продакшене недоступна
        if (this.config.debugMode) {
            console.log('Статистика:', this.stats);
        }
    }
    
    // Публичные методы для внешнего использования
    
    openCategoryById(categoryId) {
        this.closeAllCategories();
        this.openCategory(categoryId);
    }
    
    closeAllCategoriesPublic() {
        this.closeAllCategories();
    }
    
    refreshCategories() {
        this.log('🔄 Обновление списка категорий');
        this.categories.clear();
        this.scanCategories();
    }
    
    getStats() {
        return { ...this.stats };
    }
    
    debug() {
        // Отладочная информация в продакшене недоступна
        if (this.config.debugMode) {
            console.log('UniversalCategorySystem работает');
            return {
                categories: this.categories.size,
                active: this.activeCategory
            };
        }
        return null;
    }
}

// Автоматическая инициализация
document.addEventListener('DOMContentLoaded', () => {
    // Инициализируем с небольшой задержкой для уверенности
    setTimeout(() => {
        window.universalCategorySystem = new UniversalCategorySystem({
            debug: false // Отладка отключена для продакшена
        });
    }, 100);
});

// Поддержка модульной системы
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UniversalCategorySystem;
} 