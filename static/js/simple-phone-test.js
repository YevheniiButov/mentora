// simple-phone-test.js - Простой тест анимации телефона
console.log('📱 Simple Phone Test Loaded');

// Ждем загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    console.log('📱 DOM Loaded - Simple Phone Test');
    
    // Ищем элементы телефона
    const phoneContainer = document.querySelector('.device-mockup');
    const screenSlides = document.getElementById('screenSlides');
    const indicators = document.querySelectorAll('.indicator');
    
    console.log('📱 Found elements:', {
        phoneContainer: !!phoneContainer,
        screenSlides: !!screenSlides,
        indicatorsCount: indicators.length
    });
    
    // Если элементы найдены, тестируем анимацию
    if (phoneContainer && screenSlides && indicators.length > 0) {
        console.log('✅ All phone elements found, testing animation...');
        
        let currentScreen = 0;
        const totalScreens = 4;
        
        // Функция переключения экрана
        function switchScreen(screenIndex) {
            if (screenIndex < 0 || screenIndex >= totalScreens) return;
            
            currentScreen = screenIndex;
            const offset = -screenIndex * 25; // 25% на экран
            
            // Применяем трансформацию
            screenSlides.style.transform = `translateX(${offset}%)`;
            console.log(`📱 Switched to screen ${screenIndex + 1}, offset: ${offset}%`);
            
            // Обновляем индикаторы
            indicators.forEach((indicator, index) => {
                indicator.classList.toggle('active', index === screenIndex);
            });
        }
        
        // Автоматическое переключение
        let autoInterval = null;
        
        function startAutoSwitch() {
            if (autoInterval) clearInterval(autoInterval);
            
            autoInterval = setInterval(() => {
                const nextScreen = (currentScreen + 1) % totalScreens;
                switchScreen(nextScreen);
            }, 3000);
            
            console.log('📱 Auto switch started');
        }
        
        function stopAutoSwitch() {
            if (autoInterval) {
                clearInterval(autoInterval);
                autoInterval = null;
                console.log('📱 Auto switch stopped');
            }
        }
        
        // Обработчики для индикаторов
        indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => {
                switchScreen(index);
                stopAutoSwitch();
                // Перезапускаем через 5 секунд
                setTimeout(startAutoSwitch, 5000);
            });
        });
        
        // Touch/swipe поддержка
        let startX = 0;
        let currentX = 0;
        
        phoneContainer.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
        });
        
        phoneContainer.addEventListener('touchmove', (e) => {
            currentX = e.touches[0].clientX;
        });
        
        phoneContainer.addEventListener('touchend', () => {
            const diff = startX - currentX;
            const threshold = 50;
            
            if (Math.abs(diff) > threshold) {
                if (diff > 0 && currentScreen < totalScreens - 1) {
                    // Свайп влево - следующий экран
                    switchScreen(currentScreen + 1);
                } else if (diff < 0 && currentScreen > 0) {
                    // Свайп вправо - предыдущий экран
                    switchScreen(currentScreen - 1);
                }
                
                stopAutoSwitch();
                setTimeout(startAutoSwitch, 5000);
            }
        });
        
        // Mouse hover для остановки автопереключения
        phoneContainer.addEventListener('mouseenter', stopAutoSwitch);
        phoneContainer.addEventListener('mouseleave', startAutoSwitch);
        
        // Запускаем автоматическое переключение
        setTimeout(startAutoSwitch, 1000);
        
        // Добавляем глобальные функции для тестирования
        window.simplePhoneTest = {
            switchScreen,
            startAutoSwitch,
            stopAutoSwitch,
            currentScreen: () => currentScreen
        };
        
        console.log('✅ Simple phone animation initialized successfully!');
        console.log('🔧 Test functions available: window.simplePhoneTest');
        
    } else {
        console.log('❌ Phone elements not found:', {
            phoneContainer: !!phoneContainer,
            screenSlides: !!screenSlides,
            indicatorsCount: indicators.length
        });
        
        // Показываем все элементы с классом device-mockup
        const allDeviceElements = document.querySelectorAll('[class*="device"]');
        console.log('🔍 All device-related elements:', allDeviceElements);
        
        // Показываем все элементы с id screenSlides
        const allScreenElements = document.querySelectorAll('[id*="screen"]');
        console.log('🔍 All screen-related elements:', allScreenElements);
    }
});

// Проверяем загрузку через window.onload
window.addEventListener('load', function() {
    console.log('📱 Window Loaded - Simple Phone Test');
    
    // Финальная проверка
    const phoneContainer = document.querySelector('.device-mockup');
    if (phoneContainer) {
        console.log('✅ Phone container found on window load');
    } else {
        console.log('❌ Phone container still not found on window load');
    }
}); 