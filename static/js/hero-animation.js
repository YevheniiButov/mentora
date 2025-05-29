// ===== АНИМИРОВАННЫЙ ТЕЛЕФОН И ЧАСТИЦЫ =====
// Добавьте этот код в ваш файл static/js/main.js или создайте новый файл hero-animation.js

class HeroPhoneAnimation {
    constructor() {
        this.currentScreen = 0;
        this.totalScreens = 4;
        this.screenSlides = null;
        this.indicators = null;
        this.autoAdvanceInterval = null;
        this.particlesContainer = null;
        
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupPhone());
        } else {
            this.setupPhone();
        }
    }

    setupPhone() {
        this.screenSlides = document.getElementById('screenSlides');
        this.indicators = document.querySelectorAll('.indicator');
        this.particlesContainer = document.getElementById('particles');

        if (!this.screenSlides || !this.indicators.length) {
            console.log('Hero phone elements not found, skipping animation setup');
            return;
        }

        this.setupScreenSwitching();
        this.setupParticles();
        this.setupIntersectionObserver();
        
        console.log('🚀 Hero phone animation initialized');
    }

    setupScreenSwitching() {
        // Click indicators to jump to specific screen
        this.indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => {
                this.goToScreen(index);
            });
        });

        // Auto-advance screens every 4 seconds
        this.startAutoAdvance();

        // Pause auto-advance on hover
        const deviceMockup = document.querySelector('.device-mockup');
        if (deviceMockup) {
            deviceMockup.addEventListener('mouseenter', () => {
                this.pauseAutoAdvance();
            });

            deviceMockup.addEventListener('mouseleave', () => {
                this.startAutoAdvance();
            });
        }

        // Touch/swipe support for mobile
        this.setupTouchNavigation();
    }

    setupTouchNavigation() {
        let startX = 0;
        let startY = 0;
        let deltaX = 0;

        this.screenSlides.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        }, { passive: true });

        this.screenSlides.addEventListener('touchmove', (e) => {
            deltaX = e.touches[0].clientX - startX;
        }, { passive: true });

        this.screenSlides.addEventListener('touchend', () => {
            if (Math.abs(deltaX) > 50) {
                if (deltaX > 0 && this.currentScreen > 0) {
                    this.goToScreen(this.currentScreen - 1);
                } else if (deltaX < 0 && this.currentScreen < this.totalScreens - 1) {
                    this.goToScreen(this.currentScreen + 1);
                }
            }
            deltaX = 0;
        }, { passive: true });
    }

    goToScreen(screenIndex) {
        if (screenIndex < 0 || screenIndex >= this.totalScreens) return;
        
        this.currentScreen = screenIndex;
        this.updateScreen();
        
        // Restart auto-advance
        this.startAutoAdvance();
    }

    updateScreen() {
        const offset = -this.currentScreen * 25; // 25% per screen (100% / 4 screens)
        this.screenSlides.style.transform = `translateX(${offset}%)`;
        
        this.indicators.forEach((indicator, index) => {
            indicator.classList.toggle('active', index === this.currentScreen);
        });

        // Trigger animations for the current screen
        this.animateCurrentScreen();
    }

    animateCurrentScreen() {
        const currentScreenElement = this.screenSlides.children[this.currentScreen];
        if (!currentScreenElement) return;

        // Reset and trigger animations for progress bars
        const progressBars = currentScreenElement.querySelectorAll('.progress-fill');
        progressBars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0%';
            
            setTimeout(() => {
                bar.style.width = width;
            }, 300);
        });

        // Animate feature cards
        const featureCards = currentScreenElement.querySelectorAll('.feature-card');
        featureCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 200 + (index * 100));
        });
    }

    nextScreen() {
        this.currentScreen = (this.currentScreen + 1) % this.totalScreens;
        this.updateScreen();
    }

    startAutoAdvance() {
        this.pauseAutoAdvance(); // Clear existing interval
        
        this.autoAdvanceInterval = setInterval(() => {
            this.nextScreen();
        }, 4000);
    }

    pauseAutoAdvance() {
        if (this.autoAdvanceInterval) {
            clearInterval(this.autoAdvanceInterval);
            this.autoAdvanceInterval = null;
        }
    }

    setupParticles() {
        // Найти или создать контейнер для частиц
        this.particlesContainer = document.getElementById('particles');
        
        if (!this.particlesContainer) {
            // Создаем контейнер если его нет
            this.particlesContainer = document.createElement('div');
            this.particlesContainer.id = 'particles';
            this.particlesContainer.className = 'particles-container';
            
            // Добавляем в hero-section
            const heroSection = document.querySelector('.hero-section');
            if (heroSection) {
                heroSection.appendChild(this.particlesContainer);
                console.log('✨ Created particles container');
            }
        }

        if (this.particlesContainer) {
            this.startParticleSystem();
            console.log('🎪 Particles system started');
        }
    }

    createParticle() {
        if (!this.particlesContainer) return;

        const particle = document.createElement('div');
        particle.className = 'particle';
        
        // Random size between 3-8px (увеличено для видимости)
        const size = Math.random() * 5 + 3;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        
        // Random horizontal position
        particle.style.left = Math.random() * 100 + '%';
        
        // Random animation duration between 8-15 seconds (замедлено для видимости)
        const duration = Math.random() * 7 + 8;
        particle.style.animationDuration = `${duration}s`;
        
        // Random delay
        particle.style.animationDelay = Math.random() * 3 + 's';
        
        // Добавляем случайную прозрачность
        particle.style.opacity = Math.random() * 0.8 + 0.2;
        
        this.particlesContainer.appendChild(particle);
        
        // Remove particle after animation completes
        setTimeout(() => {
            if (particle.parentNode) {
                particle.parentNode.removeChild(particle);
            }
        }, (duration + 3) * 1000);
    }

    startParticleSystem() {
        const createParticles = () => {
            // Создаем частицы независимо от видимости для тестирования
            this.createParticle();
            
            // Create new particle every 500-1500ms (увеличена частота)
            setTimeout(createParticles, Math.random() * 1000 + 500);
        };

        // Немедленно создаем первую частицу
        this.createParticle();
        
        // Запускаем систему
        setTimeout(createParticles, 1000);
        
        console.log('🎆 Particle creation started');
    }

    isElementInViewport(el) {
        if (!el) return false;
        
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }

    setupIntersectionObserver() {
        // Pause animations when not in view to save performance
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.startAutoAdvance();
                } else {
                    this.pauseAutoAdvance();
                }
            });
        }, { threshold: 0.1 });

        const heroSection = document.querySelector('.hero-section');
        if (heroSection) {
            observer.observe(heroSection);
        }
    }

    // Public methods for external control
    play() {
        this.startAutoAdvance();
    }

    pause() {
        this.pauseAutoAdvance();
    }

    destroy() {
        this.pauseAutoAdvance();
        
        // Remove event listeners
        this.indicators.forEach(indicator => {
            indicator.replaceWith(indicator.cloneNode(true));
        });
        
        // Clear particles
        if (this.particlesContainer) {
            this.particlesContainer.innerHTML = '';
        }
    }
}

// ===== INITIALIZATION =====
let heroPhoneAnimation = null;

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHeroAnimation);
} else {
    initHeroAnimation();
}

function initHeroAnimation() {
    // Only initialize if hero section exists
    const heroSection = document.querySelector('.hero-section');
    const screenSlides = document.getElementById('screenSlides');
    
    if (heroSection && screenSlides) {
        heroPhoneAnimation = new HeroPhoneAnimation();
        
        // Make it globally accessible for debugging
        window.heroPhoneAnimation = heroPhoneAnimation;
    }
}

// ===== PERFORMANCE OPTIMIZATIONS =====

// Reduce particle frequency on mobile devices
function isMobileDevice() {
    return window.innerWidth <= 768 || /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

// Respect user's motion preferences
function respectsReducedMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

// ===== UTILITY FUNCTIONS =====

// Function to manually control the phone animation
window.controlHeroPhone = {
    goToScreen: (index) => {
        if (heroPhoneAnimation) {
            heroPhoneAnimation.goToScreen(index);
        }
    },
    
    play: () => {
        if (heroPhoneAnimation) {
            heroPhoneAnimation.play();
        }
    },
    
    pause: () => {
        if (heroPhoneAnimation) {
            heroPhoneAnimation.pause();
        }
    },
    
    next: () => {
        if (heroPhoneAnimation) {
            heroPhoneAnimation.nextScreen();
        }
    }
};

// ===== EVENT LISTENERS FOR ACCESSIBILITY =====

// Keyboard navigation for screen switching
document.addEventListener('keydown', (e) => {
    if (!heroPhoneAnimation) return;
    
    // Only if hero section is in focus
    const heroSection = document.querySelector('.hero-section');
    if (!heroSection || !heroPhoneAnimation.isElementInViewport(heroSection)) return;
    
    switch(e.key) {
        case 'ArrowLeft':
            e.preventDefault();
            heroPhoneAnimation.goToScreen(Math.max(0, heroPhoneAnimation.currentScreen - 1));
            break;
        case 'ArrowRight':
            e.preventDefault();
            heroPhoneAnimation.goToScreen(Math.min(heroPhoneAnimation.totalScreens - 1, heroPhoneAnimation.currentScreen + 1));
            break;
        case ' ':
        case 'Enter':
            if (e.target.classList.contains('indicator')) {
                e.preventDefault();
                const screenIndex = parseInt(e.target.dataset.screen);
                heroPhoneAnimation.goToScreen(screenIndex);
            }
            break;
    }
});

// ===== CLEANUP ON PAGE UNLOAD =====
window.addEventListener('beforeunload', () => {
    if (heroPhoneAnimation) {
        heroPhoneAnimation.destroy();
    }
});