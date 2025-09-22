/**
 * Phone animation functionality for main page
 */

// Phone animation functionality
(function() {
    'use strict';
    let currentScreen = 0;
    const totalScreens = 4;
    let autoInterval = null;
    
    // Particle animation function
    function setupParticles() {
        let particlesContainer = document.getElementById('particles');
        if (!particlesContainer) {
            particlesContainer = document.createElement('div');
            particlesContainer.id = 'particles';
            particlesContainer.className = 'particles-container';
            // Добавляем в hero-section
            const heroSection = document.querySelector('.hero-section');
            if (heroSection) {
                heroSection.appendChild(particlesContainer);
            }
        }
        if (particlesContainer) {
            startParticleSystem(particlesContainer);
        }
    }
    
    function createParticle(particlesContainer) {
        if (!particlesContainer) return;
        const particle = document.createElement('div');
        particle.className = 'particle';
        // Размер
        const size = Math.random() * 5 + 3;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        // Позиция
        particle.style.left = Math.random() * 100 + '%';
        // Длительность
        const duration = Math.random() * 7 + 8;
        particle.style.animationDuration = `${duration}s`;
        // Задержка
        particle.style.animationDelay = Math.random() * 3 + 's';
        // Прозрачность
        particle.style.opacity = Math.random() * 0.8 + 0.2;
        particlesContainer.appendChild(particle);
        setTimeout(() => {
            if (particle.parentNode) {
                particle.parentNode.removeChild(particle);
            }
        }, (duration + 3) * 1000);
    }
    
    function startParticleSystem(particlesContainer) {
        const createParticles = () => {
            createParticle(particlesContainer);
            setTimeout(createParticles, Math.random() * 1000 + 500);
        };
        createParticle(particlesContainer);
        setTimeout(createParticles, 1000);
    }
    // End particle animation

    function initPhoneAnimation() {
        // Ждем загрузки DOM
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', setupAnimation);
        } else {
            setupAnimation();
        }
    }
    
    function setupAnimation() {
        setupParticles();
        
        const screenSlides = document.querySelector('.screen-slides');
        const indicators = document.querySelectorAll('.indicator');
        const deviceMockup = document.querySelector('.device-mockup');
        
        if (!screenSlides) {
            console.warn('Screen slides not found');
            return;
        }
        
        if (!indicators || indicators.length === 0) {
            console.warn('Indicators not found');
            return;
        }
        
        // Screen update function
        function updateScreen() {
            const translateX = -currentScreen * 25; // 25% per screen
            screenSlides.style.transform = `translateX(${translateX}%)`;
            
            // Update indicators
            indicators.forEach((indicator, index) => {
                indicator.classList.toggle('active', index === currentScreen);
            });
        }
        
        // Go to next screen
        function nextScreen() {
            currentScreen = (currentScreen + 1) % totalScreens;
            updateScreen();
        }
        
        // Go to specific screen
        function goToScreen(index) {
            currentScreen = index;
            updateScreen();
            restartAutoAdvance();
        }
        
        // Auto-advance
        function startAutoAdvance() {
            stopAutoAdvance();
            autoInterval = setInterval(nextScreen, 4000);
        }
        
        function stopAutoAdvance() {
            if (autoInterval) {
                clearInterval(autoInterval);
                autoInterval = null;
            }
        }
        
        function restartAutoAdvance() {
            stopAutoAdvance();
            startAutoAdvance();
        }
        
        // Event handlers
        indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', (e) => {
                e.preventDefault();
                goToScreen(index);
            });
        });
        
        // Pause on hover
        if (deviceMockup) {
            deviceMockup.addEventListener('mouseenter', () => {
                stopAutoAdvance();
            });
            
            deviceMockup.addEventListener('mouseleave', () => {
                startAutoAdvance();
            });
        }
        
        // Swipe events for mobile devices
        let startX = 0;
        screenSlides.addEventListener('touchstart', (e) => {
            // Check if touch is on phone animation element
            if (!e.target.closest('.device-mockup, .screen-slides, .screen-content')) {
                return;
            }
            startX = e.touches[0].clientX;
        }, { passive: true });
        
        screenSlides.addEventListener('touchend', (e) => {
            // Check if touch is on phone animation element
            if (!e.target.closest('.device-mockup, .screen-slides, .screen-content')) {
                return;
            }
            
            if (!startX) return;
            const endX = e.changedTouches[0].clientX;
            const diffX = startX - endX;
            
            if (Math.abs(diffX) > 50) { // Minimum swipe distance
                if (diffX > 0) {
                    nextScreen(); // Swipe left
                } else {
                    currentScreen = (currentScreen - 1 + totalScreens) % totalScreens;
                    updateScreen();
                }
                restartAutoAdvance();
            }
            startX = 0;
        }, { passive: true });
        
        // Initialize
        updateScreen();
        startAutoAdvance();
        
        // Global access for debugging
        window.phoneAnimation = {
            next: nextScreen,
            goTo: goToScreen,
            stop: stopAutoAdvance,
            start: startAutoAdvance
        };
    }
    
    // Start
    initPhoneAnimation();
})();

// Notification System - show pre-registration notification
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        // Check if user is authenticated
        const isAuthenticated = document.querySelector('meta[name="user-authenticated"]')?.content === 'true';
        
        if (window.mentorNotifications && !isAuthenticated) {
            window.mentorNotifications.showPreRegistration();
        }
    }, 1000); // Show after 1 second
});
