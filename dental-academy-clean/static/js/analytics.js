// static/js/analytics.js - Client-side analytics tracking

class AnalyticsTracker {
    constructor() {
        this.sessionId = this.getSessionId();
        this.startTime = Date.now();
        this.pageStartTime = Date.now();
        this.scrollDepth = 0;
        this.maxScrollDepth = 0;
        this.isPageVisible = true;
        
        this.init();
    }
    
    init() {
        // Track page load
        this.trackPageView();
        
        // Track scroll depth
        this.trackScrollDepth();
        
        // Track time on page
        this.trackTimeOnPage();
        
        // Track page visibility
        this.trackPageVisibility();
        
        // Track before page unload
        this.trackPageUnload();
        
        // Track clicks on important elements
        this.trackClicks();
    }
    
    getSessionId() {
        let sessionId = sessionStorage.getItem('analytics_session_id');
        if (!sessionId) {
            sessionId = this.generateSessionId();
            sessionStorage.setItem('analytics_session_id', sessionId);
        }
        return sessionId;
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    trackPageView() {
        const pageData = {
            url: window.location.href,
            title: document.title,
            referrer: document.referrer,
            timestamp: new Date().toISOString(),
            session_id: this.sessionId
        };
        
        this.sendEvent('page_view', pageData);
    }
    
    trackScrollDepth() {
        let ticking = false;
        
        const updateScrollDepth = () => {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const docHeight = document.documentElement.scrollHeight - window.innerHeight;
            const scrollPercent = Math.round((scrollTop / docHeight) * 100);
            
            if (scrollPercent > this.maxScrollDepth) {
                this.maxScrollDepth = scrollPercent;
                this.scrollDepth = scrollPercent;
            }
            
            ticking = false;
        };
        
        const requestTick = () => {
            if (!ticking) {
                requestAnimationFrame(updateScrollDepth);
                ticking = true;
            }
        };
        
        window.addEventListener('scroll', requestTick, { passive: true });
    }
    
    trackTimeOnPage() {
        // Update time on page every 60 seconds (reduced frequency to avoid server overload)
        // Only track if page has been visible for at least 10 seconds
        setInterval(() => {
            if (this.isPageVisible) {
                const timeOnPage = Math.round((Date.now() - this.pageStartTime) / 1000);
                // Only send event if user has been on page for at least 10 seconds
                if (timeOnPage >= 10) {
                    this.sendEvent('time_on_page', {
                        time_on_page: timeOnPage,
                        session_id: this.sessionId
                    });
                }
            }
        }, 60000); // Changed from 30000 to 60000 (60 seconds instead of 30)
    }
    
    trackPageVisibility() {
        document.addEventListener('visibilitychange', () => {
            this.isPageVisible = !document.hidden;
            
            if (this.isPageVisible) {
                this.pageStartTime = Date.now();
            } else {
                // Page became hidden, send final time on page
                const timeOnPage = Math.round((Date.now() - this.pageStartTime) / 1000);
                this.sendEvent('page_hidden', {
                    time_on_page: timeOnPage,
                    scroll_depth: this.maxScrollDepth,
                    session_id: this.sessionId
                });
            }
        });
    }
    
    trackPageUnload() {
        window.addEventListener('beforeunload', () => {
            const timeOnPage = Math.round((Date.now() - this.pageStartTime) / 1000);
            
            // Send final analytics data
            this.sendEvent('page_unload', {
                time_on_page: timeOnPage,
                scroll_depth: this.maxScrollDepth,
                session_id: this.sessionId
            }, true); // Use sendBeacon for reliability
        });
    }
    
    trackClicks() {
        document.addEventListener('click', (event) => {
            const target = event.target;
            const link = target.closest('a');
            
            if (link) {
                const linkData = {
                    url: link.href,
                    text: link.textContent.trim(),
                    target: link.target || '_self',
                    session_id: this.sessionId
                };
                
                this.sendEvent('link_click', linkData);
            }
            
            // Track button clicks
            if (target.tagName === 'BUTTON' || target.classList.contains('btn')) {
                const buttonData = {
                    text: target.textContent.trim(),
                    class: target.className,
                    id: target.id,
                    session_id: this.sessionId
                };
                
                this.sendEvent('button_click', buttonData);
            }
        });
    }
    
    trackCustomEvent(eventName, eventData = {}) {
        this.sendEvent(eventName, {
            ...eventData,
            session_id: this.sessionId,
            timestamp: new Date().toISOString()
        });
    }
    
    sendEvent(eventName, eventData, useBeacon = false) {
        const payload = {
            event_name: eventName,
            event_data: eventData,
            page_url: window.location.href,
            user_agent: navigator.userAgent,
            timestamp: new Date().toISOString()
        };
        
        // Check if we're in development mode or if analytics endpoint is available
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            // Skip analytics in development mode
            return;
        }
        
        if (useBeacon && navigator.sendBeacon) {
            // Use sendBeacon for reliable delivery on page unload
            // Note: sendBeacon doesn't support custom headers, so CSRF is handled server-side for beacons
            try {
                const blob = new Blob([JSON.stringify(payload)], { type: 'text/plain;charset=UTF-8' });
                navigator.sendBeacon('/analytics/track-event', blob);
            } catch (error) {
                // Silently fail for sendBeacon errors
            }
        } else {
            // Use fetch for normal events
            const csrfToken = document.querySelector('meta[name="csrf-token"]');
            const headers = {
                'Content-Type': 'application/json',
            };
            
            if (csrfToken) {
                headers['X-CSRFToken'] = csrfToken.getAttribute('content');
            }
            
            fetch('/analytics/track-event', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(payload)
            })
            .then(response => {
                if (!response.ok) {
                    // Only log errors if it's not a 400 (which might be expected for invalid requests)
                    if (response.status !== 400) {
                        console.warn(`Analytics tracking error: ${response.status} ${response.statusText}`);
                    }
                    return response.json().catch(() => ({}));
                }
                return response.json();
            })
            .catch(error => {
                // Only log network errors, not 400 responses
                if (error.name !== 'AbortError') {
                    // Silently ignore analytics errors to avoid console spam
                }
            });
        }
    }
    
    // Public methods for manual tracking
    trackLogin(userId) {
        this.trackCustomEvent('user_login', { user_id: userId });
    }
    
    trackRegistration(userId) {
        this.trackCustomEvent('user_registration', { user_id: userId });
    }
    
    trackFormSubmission(formName) {
        this.trackCustomEvent('form_submission', { form_name: formName });
    }
    
    trackDownload(filename) {
        this.trackCustomEvent('file_download', { filename: filename });
    }
    
    trackSearch(query) {
        this.trackCustomEvent('search', { query: query });
    }
}

// Initialize analytics when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.analytics = new AnalyticsTracker();
    
    // Track login events
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function() {
            window.analytics.trackCustomEvent('login_attempt');
        });
    }
    
    // Track registration events
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function() {
            window.analytics.trackCustomEvent('registration_attempt');
        });
    }
    
    // Track form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const formName = form.id || form.className || 'unknown_form';
            window.analytics.trackFormSubmission(formName);
        });
    });
    
    // Track downloads
    const downloadLinks = document.querySelectorAll('a[download]');
    downloadLinks.forEach(link => {
        link.addEventListener('click', function() {
            const filename = this.download || this.href.split('/').pop();
            window.analytics.trackDownload(filename);
        });
    });
    
    // Track search
    const searchInputs = document.querySelectorAll('input[type="search"], input[name*="search"]');
    searchInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (this.value.trim()) {
                window.analytics.trackSearch(this.value.trim());
            }
        });
    });
});

// Export for use in other scripts
window.AnalyticsTracker = AnalyticsTracker;

