// 🛡️ ПРОСТАЯ ЗАЩИТА КОНТЕНТА DENTAL ACADEMY
// Тихая блокировка без popup'ов и запросов разрешений

class SimpleProtection {
    constructor() {
        this.isInitialized = false;
    }

    init() {
        if (this.isInitialized) return;
        
        console.log('🛡️ Инициализация простой защиты...');
        
        this.disableRightClick();
        this.disableKeyboardShortcuts();
        this.disableTextSelection();
        this.protectImages();
        this.disablePrint();
        this.addSimpleWatermark();
        
        this.isInitialized = true;
        console.log('✅ Простая защита активирована');
    }

    // 🖱️ Тихое отключение правого клика
    disableRightClick() {
        document.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            return false;
        });
    }

    // ⌨️ Тихая блокировка основных горячих клавиш
    disableKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            const key = e.key;
            const ctrlKey = e.ctrlKey || e.metaKey; // Учитываем Mac Command

            // Блокируем основные клавиши тихо (БЕЗ alert'ов)
            if (
                key === 'PrintScreen' ||                    // Print Screen
                (ctrlKey && key.toLowerCase() === 's') ||    // Ctrl+S (Save)
                (ctrlKey && key.toLowerCase() === 'p') ||    // Ctrl+P (Print)
                (ctrlKey && key.toLowerCase() === 'c') ||    // Ctrl+C (Copy)
                (ctrlKey && key.toLowerCase() === 'a') ||    // Ctrl+A (Select All)
                (ctrlKey && key.toLowerCase() === 'u') ||    // Ctrl+U (View Source)
                key === 'F12'                               // F12 (DevTools)
            ) {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        });
    }

    // 📝 Отключение выделения текста
    disableTextSelection() {
        // CSS стили через JavaScript
        const style = document.createElement('style');
        style.textContent = `
            .protected-content {
                -webkit-user-select: none !important;
                -moz-user-select: none !important;
                -ms-user-select: none !important;
                user-select: none !important;
                -webkit-touch-callout: none !important;
                -webkit-tap-highlight-color: transparent !important;
            }
            
            .protected-content * {
                -webkit-user-select: none !important;
                -moz-user-select: none !important;
                -ms-user-select: none !important;
                user-select: none !important;
            }
            
            /* Исключения для полей ввода */
            input, textarea, [contenteditable="true"] {
                -webkit-user-select: text !important;
                -moz-user-select: text !important;
                -ms-user-select: text !important;
                user-select: text !important;
            }
        `;
        document.head.appendChild(style);

        // JavaScript события (тихо блокируем)
        document.addEventListener('selectstart', (e) => {
            if (!this.isEditableElement(e.target)) {
                e.preventDefault();
                return false;
            }
        });

        document.addEventListener('dragstart', (e) => {
            if (!this.isEditableElement(e.target)) {
                e.preventDefault();
                return false;
            }
        });
    }

    // 🖼️ Простая защита изображений
    protectImages() {
        // Ждем загрузки DOM
        const protectExistingImages = () => {
            const images = document.querySelectorAll('img');
            images.forEach(img => {
                img.draggable = false;
                img.style.webkitUserDrag = 'none';
                img.style.userDrag = 'none';
                img.addEventListener('dragstart', (e) => e.preventDefault());
                img.addEventListener('contextmenu', (e) => e.preventDefault());
            });
        };

        // Защищаем существующие изображения
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', protectExistingImages);
        } else {
            protectExistingImages();
        }

        // Защищаем динамически добавляемые изображения
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        if (node.tagName === 'IMG') {
                            node.draggable = false;
                            node.style.webkitUserDrag = 'none';
                            node.addEventListener('dragstart', (e) => e.preventDefault());
                            node.addEventListener('contextmenu', (e) => e.preventDefault());
                        }
                        // Проверяем вложенные изображения
                        const images = node.querySelectorAll ? node.querySelectorAll('img') : [];
                        images.forEach(img => {
                            img.draggable = false;
                            img.style.webkitUserDrag = 'none';
                            img.addEventListener('dragstart', (e) => e.preventDefault());
                            img.addEventListener('contextmenu', (e) => e.preventDefault());
                        });
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // 🖨️ Простое отключение печати
    disablePrint() {
        // Перехватываем window.print (тихо)
        const originalPrint = window.print;
        window.print = function() {
            // Просто ничего не делаем - тихая блокировка
            return false;
        };

        // Блокируем событие beforeprint (тихо)
        window.addEventListener('beforeprint', (e) => {
            e.preventDefault();
            return false;
        });
    }

    // 💧 Простой водяной знак
    addSimpleWatermark() {
        // Создаем простой, незаметный водяной знак
        const watermark = document.createElement('div');
        watermark.className = 'simple-watermark';
        watermark.textContent = 'Dental Academy';
        
        watermark.style.cssText = `
            position: fixed;
            bottom: 10px;
            right: 10px;
            font-size: 10px;
            color: rgba(255, 255, 255, 0.1);
            pointer-events: none;
            z-index: 1;
            user-select: none;
            font-family: Arial, sans-serif;
        `;
        
        document.body.appendChild(watermark);
    }

    // ✏️ Проверка редактируемого элемента
    isEditableElement(element) {
        return element.tagName === 'INPUT' || 
               element.tagName === 'TEXTAREA' || 
               element.contentEditable === 'true' ||
               element.getAttribute('contenteditable') === 'true';
    }

    // 🔄 Обновление защиты для нового контента
    refreshProtection() {
        this.protectImages();
    }
}

// 🚀 Автоматическая инициализация
let simpleProtection;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        simpleProtection = new SimpleProtection();
        simpleProtection.init();
    });
} else {
    simpleProtection = new SimpleProtection();
    simpleProtection.init();
}

// Экспорт для внешнего использования
if (typeof window !== 'undefined') {
    window.SimpleProtection = SimpleProtection;
    window.simpleProtection = simpleProtection;
}

// Дополнительная защита от обхода
(function() {
    'use strict';
    
    // Простое переопределение некоторых методов (тихо)
    const originalAddEventListener = EventTarget.prototype.addEventListener;
    
    // Не блокируем полностью, просто логируем
    EventTarget.prototype.addEventListener = function(type, listener, options) {
        return originalAddEventListener.call(this, type, listener, options);
    };
})(); 