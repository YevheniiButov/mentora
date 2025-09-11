/**
 * Mobile Dropdown Fix - Simplified Version
 * Простое и надежное исправление выпадающих меню
 */

(function() {
    'use strict';
    
    let isInitialized = false;
    
    function initMobileDropdowns() {
        if (isInitialized) return;
        isInitialized = true;
        
        console.log('Initializing mobile dropdown fix...');
        
        // Ждем полной загрузки DOM
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initMobileDropdowns);
            return;
        }
        
        // Находим все выпадающие меню
        const dropdowns = document.querySelectorAll('.dropdown');
        console.log('Found dropdowns:', dropdowns.length);
        
        dropdowns.forEach((dropdown, index) => {
            const toggle = dropdown.querySelector('.dropdown-toggle');
            const menu = dropdown.querySelector('.dropdown-menu');
            
            if (!toggle || !menu) {
                console.log(`Dropdown ${index}: missing toggle or menu`);
                return;
            }
            
            console.log(`Setting up dropdown ${index}`);
            setupDropdown(dropdown, toggle, menu);
        });
    }
    
    function setupDropdown(dropdown, toggle, menu) {
        let isOpen = false;
        
        // Удаляем все существующие обработчики
        const newToggle = toggle.cloneNode(true);
        toggle.parentNode.replaceChild(newToggle, toggle);
        const newMenu = menu.cloneNode(true);
        menu.parentNode.replaceChild(newMenu, menu);
        
        // Обновляем ссылки
        const finalToggle = newToggle;
        const finalMenu = newMenu;
        
        // Функция открытия
        function openDropdown() {
            console.log('Opening dropdown');
            isOpen = true;
            finalMenu.style.display = 'block';
            finalMenu.classList.add('show');
            finalToggle.classList.add('show');
            finalToggle.setAttribute('aria-expanded', 'true');
            
            // Позиционирование
            positionDropdown(finalMenu, finalToggle);
        }
        
        // Функция закрытия
        function closeDropdown() {
            console.log('Closing dropdown');
            isOpen = false;
            finalMenu.style.display = 'none';
            finalMenu.classList.remove('show');
            finalToggle.classList.remove('show');
            finalToggle.setAttribute('aria-expanded', 'false');
        }
        
        // Обработчик клика на toggle
        finalToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Toggle clicked, isOpen:', isOpen);
            
            if (isOpen) {
                closeDropdown();
            } else {
                // Закрываем все другие меню
                closeAllDropdowns();
                openDropdown();
            }
        });
        
        // Обработчики для элементов меню
        const menuItems = finalMenu.querySelectorAll('.dropdown-item, a, button');
        menuItems.forEach(item => {
            item.addEventListener('click', function(e) {
                console.log('Menu item clicked:', item.textContent);
                e.stopPropagation();
                
                // Если это ссылка, переходим
                if (item.href && item.href !== '#') {
                    window.location.href = item.href;
                    return;
                }
                
                // Если есть onclick, выполняем
                if (item.onclick) {
                    item.onclick();
                    return;
                }
                
                // Если это кнопка с data-action
                const action = item.getAttribute('data-action');
                if (action) {
                    handleMenuAction(action, item);
                    return;
                }
                
                // Закрываем меню
                closeDropdown();
            });
        });
        
        // Закрытие при клике вне меню
        document.addEventListener('click', function(e) {
            if (!dropdown.contains(e.target)) {
                closeDropdown();
            }
        });
        
        // Закрытие при скролле
        window.addEventListener('scroll', closeDropdown);
        
        // Закрытие при изменении ориентации
        window.addEventListener('orientationchange', function() {
            setTimeout(closeDropdown, 100);
        });
    }
    
    function positionDropdown(menu, toggle) {
        const toggleRect = toggle.getBoundingClientRect();
        const menuRect = menu.getBoundingClientRect();
        const viewportHeight = window.innerHeight;
        const viewportWidth = window.innerWidth;
        
        // Сбрасываем стили
        menu.style.position = 'fixed';
        menu.style.top = 'auto';
        menu.style.left = 'auto';
        menu.style.right = 'auto';
        menu.style.bottom = 'auto';
        menu.style.transform = 'none';
        menu.style.zIndex = '1050';
        
        // Определяем позицию
        const spaceBelow = viewportHeight - toggleRect.bottom;
        const spaceAbove = toggleRect.top;
        
        // Позиционируем по вертикали
        if (spaceBelow >= 200 || spaceBelow >= spaceAbove) {
            // Размещаем снизу
            menu.style.top = `${toggleRect.bottom + 5}px`;
        } else {
            // Размещаем сверху
            menu.style.bottom = `${viewportHeight - toggleRect.top + 5}px`;
        }
        
        // Позиционируем по горизонтали
        const spaceRight = viewportWidth - toggleRect.left;
        if (spaceRight >= 200) {
            menu.style.left = `${toggleRect.left}px`;
        } else {
            menu.style.right = `${viewportWidth - toggleRect.right}px`;
        }
        
        // Ограничиваем размеры
        menu.style.maxWidth = `${Math.min(300, viewportWidth - 20)}px`;
        menu.style.maxHeight = `${Math.min(400, viewportHeight * 0.6)}px`;
        menu.style.overflowY = 'auto';
    }
    
    function closeAllDropdowns() {
        const allMenus = document.querySelectorAll('.dropdown-menu.show');
        allMenus.forEach(menu => {
            menu.style.display = 'none';
            menu.classList.remove('show');
        });
        
        const allToggles = document.querySelectorAll('.dropdown-toggle.show');
        allToggles.forEach(toggle => {
            toggle.classList.remove('show');
            toggle.setAttribute('aria-expanded', 'false');
        });
    }
    
    function handleMenuAction(action, element) {
        console.log('Handling menu action:', action);
        
        switch(action) {
            case 'logout':
                if (confirm('Are you sure you want to logout?')) {
                    window.location.href = '/auth/logout';
                }
                break;
            case 'profile':
                window.location.href = '/profile';
                break;
            case 'settings':
                window.location.href = '/settings';
                break;
            case 'language':
                const lang = element.getAttribute('data-lang');
                if (lang) {
                    window.location.href = `/?lang=${lang}`;
                }
                break;
            default:
                console.log('Unknown action:', action);
        }
    }
    
    // Инициализация
    initMobileDropdowns();
    
    // Переинициализация при изменении размера окна
    window.addEventListener('resize', function() {
        setTimeout(initMobileDropdowns, 100);
    });
    
    // Экспорт для отладки
    window.MobileDropdownFix = {
        init: initMobileDropdowns,
        closeAll: closeAllDropdowns
    };
    
})();