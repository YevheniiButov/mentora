// debug-phone.js - Отладочный скрипт для проверки анимации телефона
console.log('🔍 Debug Phone Script Loaded');

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 DOM Content Loaded - Debug Phone');
    
    // Проверяем наличие элементов телефона
    const phoneContainer = document.querySelector('.device-mockup');
    const screenSlides = document.getElementById('screenSlides');
    const indicators = document.querySelectorAll('.indicator');
    
    console.log('📱 Phone Container:', phoneContainer);
    console.log('🖥️ Screen Slides:', screenSlides);
    console.log('🔘 Indicators:', indicators.length);
    
    if (phoneContainer) {
        console.log('✅ Phone container found');
    } else {
        console.log('❌ Phone container NOT found');
    }
    
    if (screenSlides) {
        console.log('✅ Screen slides found');
    } else {
        console.log('❌ Screen slides NOT found');
    }
    
    if (indicators.length > 0) {
        console.log('✅ Indicators found:', indicators.length);
    } else {
        console.log('❌ Indicators NOT found');
    }
    
    // Проверяем загрузку наших скриптов
    console.log('🔍 HeroPhoneAnimation available:', typeof HeroPhoneAnimation !== 'undefined');
    console.log('🔍 AppInitializer available:', typeof AppInitializer !== 'undefined');
    
    // Проверяем глобальные переменные
    console.log('🔍 window.heroPhoneAnimation:', window.heroPhoneAnimation);
    console.log('🔍 window.controlHeroPhone:', window.controlHeroPhone);
    
    // Тестируем ручное переключение экранов
    if (screenSlides && indicators.length > 0) {
        console.log('🧪 Testing manual screen switching...');
        
        // Добавляем тестовые кнопки
        const testContainer = document.createElement('div');
        testContainer.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px;
            border-radius: 5px;
            z-index: 10000;
            font-family: monospace;
            font-size: 12px;
        `;
        
        testContainer.innerHTML = `
            <div>🔍 Phone Debug</div>
            <button onclick="testScreen(0)">Screen 1</button>
            <button onclick="testScreen(1)">Screen 2</button>
            <button onclick="testScreen(2)">Screen 3</button>
            <button onclick="testScreen(3)">Screen 4</button>
            <button onclick="testAutoAdvance()">Auto</button>
        `;
        
        document.body.appendChild(testContainer);
        
        // Глобальные функции для тестирования
        window.testScreen = function(screenIndex) {
            console.log('🧪 Testing screen:', screenIndex);
            if (screenSlides) {
                const offset = -screenIndex * 25;
                screenSlides.style.transform = `translateX(${offset}%)`;
                console.log('✅ Applied transform:', `translateX(${offset}%)`);
            }
            
            indicators.forEach((indicator, index) => {
                indicator.classList.toggle('active', index === screenIndex);
            });
        };
        
        window.testAutoAdvance = function() {
            console.log('🧪 Testing auto advance');
            if (window.heroPhoneAnimation) {
                window.heroPhoneAnimation.startAutoAdvance();
                console.log('✅ Auto advance started');
            } else {
                console.log('❌ heroPhoneAnimation not available');
            }
        };
        
        console.log('✅ Debug panel added');
    }
});

// Проверяем загрузку через window.onload
window.addEventListener('load', function() {
    console.log('🔍 Window Loaded - Debug Phone');
    console.log('🔍 Final check - HeroPhoneAnimation:', typeof HeroPhoneAnimation !== 'undefined');
    console.log('🔍 Final check - window.heroPhoneAnimation:', window.heroPhoneAnimation);
}); 