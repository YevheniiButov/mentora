/**
 * Dropdown Test Script
 * Простой тест для проверки работы выпадающих меню
 */

(function() {
    'use strict';
    
    console.log('Dropdown test script loaded');
    
    // Ждем загрузки DOM
    document.addEventListener('DOMContentLoaded', function() {
        console.log('DOM loaded, testing dropdowns...');
        
        // Находим все выпадающие меню
        const dropdowns = document.querySelectorAll('.dropdown');
        console.log('Found dropdowns:', dropdowns.length);
        
        dropdowns.forEach((dropdown, index) => {
            const toggle = dropdown.querySelector('.dropdown-toggle');
            const menu = dropdown.querySelector('.dropdown-menu');
            
            console.log(`Dropdown ${index}:`, {
                toggle: !!toggle,
                menu: !!menu,
                toggleText: toggle ? toggle.textContent.trim() : 'N/A',
                menuItems: menu ? menu.querySelectorAll('a, button, .dropdown-item').length : 0
            });
            
            if (toggle && menu) {
                // Добавляем простой обработчик для тестирования
                toggle.addEventListener('click', function(e) {
                    e.preventDefault();
                    console.log(`Dropdown ${index} toggle clicked`);
                    
                    // Простое переключение
                    if (menu.style.display === 'block') {
                        menu.style.display = 'none';
                        console.log(`Dropdown ${index} closed`);
                    } else {
                        menu.style.display = 'block';
                        console.log(`Dropdown ${index} opened`);
                    }
                });
                
                // Обработчики для элементов меню
                const menuItems = menu.querySelectorAll('a, button, .dropdown-item');
                menuItems.forEach((item, itemIndex) => {
                    item.addEventListener('click', function(e) {
                        e.preventDefault();
                        console.log(`Dropdown ${index}, item ${itemIndex} clicked:`, item.textContent.trim());
                        
                        // Если это ссылка, переходим
                        if (item.href && item.href !== '#') {
                            console.log('Navigating to:', item.href);
                            window.location.href = item.href;
                        }
                        
                        // Закрываем меню
                        menu.style.display = 'none';
                    });
                });
            }
        });
        
        // Закрытие при клике вне меню
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.dropdown')) {
                dropdowns.forEach(dropdown => {
                    const menu = dropdown.querySelector('.dropdown-menu');
                    if (menu) {
                        menu.style.display = 'none';
                    }
                });
            }
        });
    });
    
})();
