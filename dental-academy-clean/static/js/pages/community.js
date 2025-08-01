/**
 * 🚀 Modern Community Page JavaScript
 * Clean, Modular & Performance-Optimized
 * =====================================
 */

// 🎯 Configuration & Constants
const CONFIG = {
    ANIMATION_DURATION: 2000,
    REFRESH_INTERVAL: 30000,
    TOAST_DURATION: 4000,
    DEBOUNCE_DELAY: 250,
    LOCALE: 'nl-NL'
  };
  
  // 🛠️ Utility Functions
  const Utils = {
    /**
     * Format number with Dutch locale
     */
    formatNumber: (num) => new Intl.NumberFormat(CONFIG.LOCALE).format(num),
  
    /**
     * Debounce function calls
     */
    debounce: (func, delay) => {
      let timeoutId;
      return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(null, args), delay);
      };
    },
  
    /**
     * Animate value from start to end
     */
    animateValue: (element, start, end, duration, formatter = (val) => val) => {
      const range = end - start;
      const startTime = performance.now();
      
      const animate = (currentTime) => {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function (ease-out)
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = start + (range * easeOut);
        
        element.textContent = formatter(Math.floor(current));
        
        if (progress < 1) {
          requestAnimationFrame(animate);
        } else {
          element.textContent = formatter(end);
        }
      };
      
      requestAnimationFrame(animate);
    },
  
    /**
     * Create element with classes and attributes
     */
    createElement: (tag, classes = [], attributes = {}) => {
      const element = document.createElement(tag);
      element.classList.add(...classes);
      Object.entries(attributes).forEach(([key, value]) => {
        element.setAttribute(key, value);
      });
      return element;
    }
  };
  
  // 🔔 Toast Notification System
  class ToastManager {
    constructor() {
      this.container = this.createContainer();
      this.toasts = new Set();
    }
  
    createContainer() {
      const existing = document.querySelector('.toast-container');
      if (existing) return existing;
  
      const container = Utils.createElement('div', ['toast-container']);
      document.body.appendChild(container);
      return container;
    }
  
    show(message, type = 'info') {
      const toast = this.createToast(message, type);
      this.container.appendChild(toast);
      this.toasts.add(toast);
  
      // Trigger animation
      requestAnimationFrame(() => {
        toast.classList.add('show');
      });
  
      // Auto remove
      setTimeout(() => {
        this.hide(toast);
      }, CONFIG.TOAST_DURATION);
  
      return toast;
    }
  
    createToast(message, type) {
      const toast = Utils.createElement('div', ['toast', `toast-${type}`]);
      
      const icons = {
        success: 'check-circle',
        error: 'alert-circle',
        warning: 'alert-triangle',
        info: 'info'
      };
  
      toast.innerHTML = `
        <div class="toast-content">
          <i class="icon-${icons[type] || icons.info}"></i>
          <span>${message}</span>
        </div>
      `;
  
      return toast;
    }
  
    hide(toast) {
      if (!this.toasts.has(toast)) return;
  
      toast.classList.remove('show');
      this.toasts.delete(toast);
  
      setTimeout(() => {
        if (toast.parentNode) {
          this.container.removeChild(toast);
        }
      }, 300);
    }
  
    clear() {
      this.toasts.forEach(toast => this.hide(toast));
    }
  }
  
  // 📊 Animated Statistics Counter
  class StatsCounter {
    constructor(element) {
      this.element = element;
      this.finalValue = this.parseValue();
      this.hasAnimated = false;
      
      this.setupIntersectionObserver();
    }
  
    parseValue() {
      const text = this.element.textContent;
      const match = text.match(/[\d,]+/);
      return match ? parseInt(match[0].replace(/,/g, ''), 10) : 0;
    }
  
    setupIntersectionObserver() {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting && !this.hasAnimated) {
            this.animate();
            this.hasAnimated = true;
          }
        });
      }, { threshold: 0.5 });
  
      observer.observe(this.element);
    }
  
    animate() {
      Utils.animateValue(
        this.element,
        0,
        this.finalValue,
        CONFIG.ANIMATION_DURATION,
        Utils.formatNumber
      );
    }
  }
  
  // 🎯 Category Card Component
  class CategoryCard {
    constructor(element) {
      this.element = element;
      this.categoryId = element.dataset.categoryId;
      this.isAnimating = false;
      
      this.init();
    }
  
    init() {
      this.addEventListeners();
      this.setupHoverEffects();
    }
  
    addEventListeners() {
      this.element.addEventListener('click', this.handleClick.bind(this));
      this.element.addEventListener('mouseenter', this.handleMouseEnter.bind(this));
      this.element.addEventListener('mouseleave', this.handleMouseLeave.bind(this));
    }
  
    setupHoverEffects() {
      this.element.style.transition = 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)';
    }
  
    handleClick(e) {
      e.preventDefault();
      
      if (this.isAnimating) return;
      this.isAnimating = true;
  
      // Click animation
      this.element.style.transform = 'translateY(-2px) scale(0.98)';
      
      setTimeout(() => {
        this.element.style.transform = 'translateY(-2px) scale(1)';
        this.isAnimating = false;
      }, 150);
  
      // Get category info
      const categoryName = this.element.querySelector('.category-name')?.textContent || 'Category';
      
      // Show feedback
      App.toast.show(`Opening ${categoryName}...`, 'info');
  
      // Navigate (placeholder)
      setTimeout(() => {
        console.log(`Navigate to category: ${this.categoryId}`);
        // window.location.href = `/community/category/${this.categoryId}`;
      }, 500);
    }
  
    handleMouseEnter() {
      if (!this.isAnimating) {
        this.element.style.transform = 'translateY(-2px)';
      }
    }
  
    handleMouseLeave() {
      if (!this.isAnimating) {
        this.element.style.transform = 'translateY(0)';
      }
    }
  }
  
  // 📰 Activity Feed Manager
  class ActivityFeed {
    constructor(container) {
      this.container = container;
      this.items = [...container.querySelectorAll('.activity-item')];
      this.lastUpdate = Date.now();
      
      this.init();
    }
  
    init() {
      this.animateInitialItems();
      this.setupPeriodicRefresh();
    }
  
    animateInitialItems() {
      this.items.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
          item.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
          item.style.opacity = '1';
          item.style.transform = 'translateY(0)';
        }, index * 100);
      });
    }
  
    setupPeriodicRefresh() {
      setInterval(() => {
        this.checkForUpdates();
      }, CONFIG.REFRESH_INTERVAL);
    }
  
    async checkForUpdates() {
      try {
        console.log('🔄 Checking for new activity...');
        
        // In a real app, this would be an API call
        // const response = await fetch('/api/community/activity/recent');
        // const newActivities = await response.json();
        
        // Simulate new activity (for demo)
        if (Math.random() > 0.7) {
          this.simulateNewActivity();
        }
      } catch (error) {
        console.error('❌ Error checking for updates:', error);
      }
    }
  
    simulateNewActivity() {
      const mockActivity = {
        user: 'Dr. Smith',
        action: 'replied to',
        topic: 'Root canal complications',
        time: 'just now',
        avatar: '👨‍⚕️'
      };
  
      App.toast.show('New activity in the forum!', 'info');
      console.log('📢 New activity:', mockActivity);
    }
  
    addActivity(activityData) {
      const activityElement = this.createActivityElement(activityData);
      this.container.insertBefore(activityElement, this.container.firstChild);
      
      // Animate in
      requestAnimationFrame(() => {
        activityElement.style.opacity = '1';
        activityElement.style.transform = 'translateY(0)';
      });
  
      // Remove oldest if too many
      if (this.container.children.length > 10) {
        const oldest = this.container.lastElementChild;
        oldest.style.opacity = '0';
        oldest.style.transform = 'translateY(-20px)';
        setTimeout(() => oldest.remove(), 300);
      }
    }
  
    createActivityElement(data) {
      const item = Utils.createElement('div', ['activity-item']);
      item.style.opacity = '0';
      item.style.transform = 'translateY(20px)';
      item.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
  
      item.innerHTML = `
        <div class="activity-avatar">
          <span>${data.avatar}</span>
        </div>
        <div class="activity-content">
          <div class="activity-text">
            <strong>${data.user}</strong>
            <span>${data.action}</span>
            <em>"${data.topic}"</em>
          </div>
          <div class="activity-meta">
            <span class="activity-time">${data.time}</span>
          </div>
        </div>
      `;
  
      return item;
    }
  }
  
  // ⚡ Quick Actions Manager
  class QuickActions {
    constructor() {
      this.buttons = document.querySelectorAll('.action-btn');
      this.init();
    }
  
    init() {
      this.buttons.forEach(button => {
        button.addEventListener('click', this.handleAction.bind(this, button));
      });
    }
  
    handleAction(button, e) {
      e.preventDefault();
  
      const action = button.textContent.trim();
      const buttonRect = button.getBoundingClientRect();
  
      // Visual feedback
      this.animateButton(button);
  
      // Show contextual message
      const messages = {
        'Nieuw Topic': 'Topic creation form will open here!',
        'Stel een Vraag': 'Question form coming soon!',
        'Deel een Case': 'Case sharing feature in development!'
      };
  
      const message = messages[action] || `${action} feature coming soon!`;
      App.toast.show(message, 'info');
  
      // Create ripple effect
      this.createRipple(button, e);
    }
  
    animateButton(button) {
      button.style.transform = 'scale(0.95)';
      setTimeout(() => {
        button.style.transform = 'scale(1)';
      }, 150);
    }
  
    createRipple(button, event) {
      const ripple = Utils.createElement('span', ['ripple']);
      const rect = button.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      const x = event.clientX - rect.left - size / 2;
      const y = event.clientY - rect.top - size / 2;
  
      ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 0.6s ease-out;
        pointer-events: none;
      `;
  
      // Add ripple styles if not exists
      if (!document.querySelector('#ripple-styles')) {
        const style = Utils.createElement('style', [], { id: 'ripple-styles' });
        style.textContent = `
          @keyframes ripple {
            to {
              transform: scale(2);
              opacity: 0;
            }
          }
          .action-btn {
            position: relative;
            overflow: hidden;
          }
        `;
        document.head.appendChild(style);
      }
  
      button.appendChild(ripple);
  
      setTimeout(() => {
        ripple.remove();
      }, 600);
    }
  }
  
  // 🎛️ Main Application Controller
  class CommunityApp {
    constructor() {
      this.components = new Map();
      this.toast = new ToastManager();
      
      this.init();
    }
  
    init() {
      // Wait for DOM to be ready
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => this.initializeComponents());
      } else {
        this.initializeComponents();
      }
    }
  
    initializeComponents() {
      console.log('🚀 Initializing Community App...');
  
      try {
        // Initialize stats counters
        this.initStatsCounters();
        
        // Initialize category cards
        this.initCategoryCards();
        
        // Initialize activity feed
        this.initActivityFeed();
        
        // Initialize quick actions
        this.initQuickActions();
  
        // Show welcome message
        setTimeout(() => {
          this.toast.show('Welcome to the Community! 👋', 'success');
        }, 1000);
  
        console.log('✅ Community App initialized successfully');
      } catch (error) {
        console.error('❌ Error initializing Community App:', error);
        this.toast.show('There was an error loading the page. Please refresh.', 'error');
      }
    }
  
    initStatsCounters() {
      const statElements = document.querySelectorAll('.stat-number, .stat-value');
      statElements.forEach(element => {
        this.components.set(`counter-${element.id || Math.random()}`, new StatsCounter(element));
      });
    }
  
    initCategoryCards() {
      const categoryCards = document.querySelectorAll('.category-card');
      categoryCards.forEach(card => {
        const id = card.dataset.categoryId;
        this.components.set(`card-${id}`, new CategoryCard(card));
      });
    }
  
    initActivityFeed() {
      const activityFeed = document.querySelector('.activity-feed');
      if (activityFeed) {
        this.components.set('activity-feed', new ActivityFeed(activityFeed));
      }
    }
  
    initQuickActions() {
      this.components.set('quick-actions', new QuickActions());
    }
  
    // Public API methods
    showToast(message, type = 'info') {
      return this.toast.show(message, type);
    }
  
    getComponent(id) {
      return this.components.get(id);
    }
  
    // Cleanup method for SPA navigation
    destroy() {
      this.components.clear();
      this.toast.clear();
    }
  }
  
  // 🌟 Initialize Application
  const App = new CommunityApp();
  
  // 🔧 Development helpers (remove in production)
  if (process.env.NODE_ENV === 'development') {
    window.CommunityApp = App;
    window.Utils = Utils;
    
    console.log('🛠️ Development mode: Community App available as window.CommunityApp');
  }
  
  // 📦 Export for module systems
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CommunityApp, ToastManager, Utils };
  }