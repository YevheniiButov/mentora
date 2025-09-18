// mobile.js - Mobile-specific JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Mobile-specific initialization
    console.log('Mobile JS loaded');
    
    // Handle mobile navigation
    const mobileNavToggle = document.querySelector('.navbar-toggler');
    const mobileNav = document.querySelector('#mobileNavbar');
    
    if (mobileNavToggle && mobileNav) {
        mobileNavToggle.addEventListener('click', function() {
            mobileNav.classList.toggle('show');
        });
    }
    
    // Handle touch events for better mobile experience
    const touchElements = document.querySelectorAll('.touchable');
    touchElements.forEach(element => {
        element.addEventListener('touchstart', function() {
            this.classList.add('touch-active');
        });
        
        element.addEventListener('touchend', function() {
            this.classList.remove('touch-active');
        });
    });
    
    // Prevent zoom on double tap
    let lastTouchEnd = 0;
    document.addEventListener('touchend', function(event) {
        const now = (new Date()).getTime();
        if (now - lastTouchEnd <= 300) {
            event.preventDefault();
        }
        lastTouchEnd = now;
    }, false);
    
    // Handle mobile-specific form interactions
    const mobileForms = document.querySelectorAll('form');
    mobileForms.forEach(form => {
        form.addEventListener('submit', function() {
            // Show loading state on mobile
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            }
        });
    });
    
    // Handle mobile-specific alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        // Auto-dismiss alerts on mobile after 5 seconds
        setTimeout(() => {
            if (alert && alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    });
    
    // Handle mobile-specific modals
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            // Focus on first input in modal
            const firstInput = this.querySelector('input, textarea, select');
            if (firstInput) {
                firstInput.focus();
            }
        });
    });
    
    // Handle mobile-specific scrolling
    let isScrolling = false;
    window.addEventListener('scroll', function() {
        if (!isScrolling) {
            window.requestAnimationFrame(function() {
                // Handle scroll-based animations or effects
                isScrolling = false;
            });
            isScrolling = true;
        }
    });
    
    // Handle mobile-specific orientation changes
    window.addEventListener('orientationchange', function() {
        // Reload page on orientation change to fix layout issues
        setTimeout(function() {
            window.location.reload();
        }, 100);
    });
    
    // Handle mobile-specific back button
    if (window.history && window.history.pushState) {
        window.addEventListener('popstate', function() {
            // Handle back button navigation
            if (window.history.length > 1) {
                window.history.back();
            } else {
                // Redirect to home if no history
                window.location.href = '/';
            }
        });
    }
    
    // Handle mobile-specific performance optimizations
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        // Lazy load images on mobile
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const image = entry.target;
                        image.src = image.dataset.src;
                        image.classList.remove('lazy');
                        imageObserver.unobserve(image);
                    }
                });
            });
            
            imageObserver.observe(img);
        }
    });
    
    // Handle mobile-specific error handling
    window.addEventListener('error', function(event) {
        console.error('Mobile JS Error:', event.error);
        // Show user-friendly error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger';
        errorDiv.innerHTML = '<i class="fas fa-exclamation-triangle"></i> An error occurred. Please try again.';
        document.body.insertBefore(errorDiv, document.body.firstChild);
        
        // Auto-remove error message
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    });
    
    // Handle mobile-specific network status
    window.addEventListener('online', function() {
        console.log('Mobile: Network online');
        // Show online indicator
        const onlineDiv = document.createElement('div');
        onlineDiv.className = 'alert alert-success';
        onlineDiv.innerHTML = '<i class="fas fa-wifi"></i> Connection restored';
        document.body.insertBefore(onlineDiv, document.body.firstChild);
        
        setTimeout(() => {
            if (onlineDiv.parentNode) {
                onlineDiv.remove();
            }
        }, 3000);
    });
    
    window.addEventListener('offline', function() {
        console.log('Mobile: Network offline');
        // Show offline indicator
        const offlineDiv = document.createElement('div');
        offlineDiv.className = 'alert alert-warning';
        offlineDiv.innerHTML = '<i class="fas fa-wifi-slash"></i> No internet connection';
        document.body.insertBefore(offlineDiv, document.body.firstChild);
    });
    
    console.log('Mobile JS initialization complete');
});

