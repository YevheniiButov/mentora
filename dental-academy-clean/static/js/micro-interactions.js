/**
 * Micro-Interactions Module
 * Handles animations, effects, and interactive feedback
 */

class MicroInteractions {
  constructor() {
    this.animationsEnabled = true;
    this.particlesEnabled = true;
    this.initialize();
  }

  initialize() {
    this.setupEventListeners();
    this.createParticleContainer();
  }

  setupEventListeners() {
    // Option selection animations
    document.addEventListener('click', (e) => {
      if (e.target.closest('.option')) {
        this.animateOptionSelect(e.target.closest('.option'));
      }
    });

    // Button click animations
    document.addEventListener('click', (e) => {
      if (e.target.closest('.nav-btn')) {
        this.animateButtonClick(e.target.closest('.nav-btn'));
      }
    });

    // Progress updates
    document.addEventListener('progressUpdate', (e) => {
      this.animateProgressUpdate(e.detail.percentage);
    });

    // Timer urgency
    document.addEventListener('timerUpdate', (e) => {
      this.updateTimerUrgency(e.detail.remaining, e.detail.total);
    });
  }

  createParticleContainer() {
    const container = document.createElement('div');
    container.id = 'particle-container';
    container.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 1000;
    `;
    document.body.appendChild(container);
  }

  animateOptionSelect(optionElement) {
    if (!this.animationsEnabled) return;

    // Add selection animation
    optionElement.style.transform = 'scale(0.98)';
    optionElement.style.transition = 'transform 0.15s ease';

    setTimeout(() => {
      optionElement.style.transform = '';
    }, 150);

    // Create ripple effect
    this.createRippleEffect(optionElement);
  }

  animateButtonClick(buttonElement) {
    if (!this.animationsEnabled) return;

    // Add click animation
    buttonElement.style.transform = 'scale(0.95)';
    buttonElement.style.transition = 'transform 0.1s ease';

    setTimeout(() => {
      buttonElement.style.transform = '';
    }, 100);
  }

  createRippleEffect(element) {
    const rect = element.getBoundingClientRect();
    const ripple = document.createElement('div');
    
    ripple.style.cssText = `
      position: absolute;
      left: ${rect.left + rect.width / 2}px;
      top: ${rect.top + rect.height / 2}px;
      width: 0;
      height: 0;
      background: rgba(255, 255, 255, 0.3);
      border-radius: 50%;
      transform: translate(-50%, -50%);
      animation: rippleExpand 0.6s ease-out;
      pointer-events: none;
      z-index: 1000;
    `;

    document.body.appendChild(ripple);

    setTimeout(() => {
      if (ripple.parentNode) {
        ripple.parentNode.removeChild(ripple);
      }
    }, 600);
  }

  celebrateCorrectAnswer(optionElement) {
    if (!this.animationsEnabled) return;

    // Add celebration class
    optionElement.classList.add('celebrate');

    // Create confetti effect
    if (this.particlesEnabled) {
      this.createConfetti(optionElement);
    }

    // Play success animation
    this.animateSuccess(optionElement);

    setTimeout(() => {
      optionElement.classList.remove('celebrate');
    }, 1000);
  }

  createConfetti(element) {
    const rect = element.getBoundingClientRect();
    const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57'];
    
    for (let i = 0; i < 20; i++) {
      const confetti = document.createElement('div');
      const color = colors[Math.floor(Math.random() * colors.length)];
      
      confetti.style.cssText = `
        position: fixed;
        left: ${rect.left + rect.width / 2}px;
        top: ${rect.top + rect.height / 2}px;
        width: 8px;
        height: 8px;
        background: ${color};
        border-radius: 2px;
        pointer-events: none;
        z-index: 1000;
        animation: confettiFall 1s ease-out forwards;
      `;

      document.body.appendChild(confetti);

      setTimeout(() => {
        if (confetti.parentNode) {
          confetti.parentNode.removeChild(confetti);
        }
      }, 1000);
    }
  }

  animateSuccess(element) {
    // Add success glow
    element.style.boxShadow = '0 0 20px rgba(76, 175, 80, 0.5)';
    element.style.transition = 'box-shadow 0.3s ease';

    setTimeout(() => {
      element.style.boxShadow = '';
    }, 300);
  }

  showIncorrectFeedback(optionElement) {
    if (!this.animationsEnabled) return;

    // Add shake animation
    optionElement.style.animation = 'shake 0.6s ease-in-out';
    
    setTimeout(() => {
      optionElement.style.animation = '';
    }, 600);

    // Add error glow
    optionElement.style.boxShadow = '0 0 20px rgba(244, 67, 54, 0.5)';
    element.style.transition = 'box-shadow 0.3s ease';

    setTimeout(() => {
      optionElement.style.boxShadow = '';
    }, 300);
  }

  animateProgressUpdate(percentage) {
    const progressBar = document.querySelector('.progress-fill');
    if (!progressBar) return;

    // Smooth progress animation
    progressBar.style.transition = 'width 0.5s ease';
    progressBar.style.width = `${percentage}%`;

    // Add progress pulse
    progressBar.style.animation = 'progressPulse 0.5s ease-out';
    
    setTimeout(() => {
      progressBar.style.animation = '';
    }, 500);
  }

  updateTimerUrgency(remaining, total) {
    const timer = document.querySelector('.timer-badge');
    if (!timer) return;

    const percentage = remaining / total;

    // Update timer appearance based on urgency
    timer.className = 'timer-badge';
    
    if (percentage <= 0.25) {
      timer.classList.add('danger');
      timer.style.animation = 'timerPulse 0.5s infinite';
    } else if (percentage <= 0.5) {
      timer.classList.add('warning');
      timer.style.animation = 'timerPulse 1s infinite';
    } else {
      timer.style.animation = '';
    }
  }

  showConfidenceLevel(confidence) {
    const indicator = document.querySelector('.confidence-indicator');
    if (!indicator) return;

    const fill = indicator.querySelector('.confidence-fill');
    if (!fill) return;

    // Update width with animation
    fill.style.transition = 'width 0.5s ease';
    fill.style.width = `${confidence * 100}%`;

    // Update color class
    indicator.className = 'confidence-indicator';
    if (confidence > 0.8) {
      indicator.classList.add('high');
    } else if (confidence > 0.5) {
      indicator.classList.add('medium');
    } else {
      indicator.classList.add('low');
    }
  }

  pulseTimer(urgency) {
    const timer = document.getElementById('timer');
    if (!timer) return;

    const pulseSpeed = Math.max(0.5, 2 - urgency);
    timer.style.animation = `pulse ${pulseSpeed}s infinite`;
  }

  createLoadingAnimation(element) {
    const spinner = document.createElement('div');
    spinner.className = 'loading-spinner';
    spinner.innerHTML = `
      <div class="spinner-ring"></div>
      <div class="spinner-ring"></div>
      <div class="spinner-ring"></div>
    `;

    element.appendChild(spinner);
    return spinner;
  }

  removeLoadingAnimation(spinner) {
    if (spinner && spinner.parentNode) {
      spinner.parentNode.removeChild(spinner);
    }
  }

  animateModalShow(modal) {
    modal.style.opacity = '0';
    modal.style.transform = 'scale(0.9) translateY(20px)';
    modal.style.transition = 'all 0.3s ease';

    requestAnimationFrame(() => {
      modal.style.opacity = '1';
      modal.style.transform = 'scale(1) translateY(0)';
    });
  }

  animateModalHide(modal, callback) {
    modal.style.opacity = '0';
    modal.style.transform = 'scale(0.9) translateY(20px)';

    setTimeout(() => {
      if (callback) callback();
    }, 300);
  }

  createFloatingNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `floating-notification ${type}`;
    notification.textContent = message;

    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: var(--glass-bg);
      backdrop-filter: var(--glass-blur);
      border: 1px solid var(--glass-border);
      border-radius: 12px;
      padding: 16px 20px;
      color: white;
      font-weight: 500;
      z-index: 1000;
      transform: translateX(100%);
      transition: transform 0.3s ease;
      box-shadow: var(--glass-shadow);
    `;

    document.body.appendChild(notification);

    // Animate in
    requestAnimationFrame(() => {
      notification.style.transform = 'translateX(0)';
    });

    // Auto remove
    setTimeout(() => {
      notification.style.transform = 'translateX(100%)';
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    }, 3000);

    return notification;
  }

  animateElementEnter(element, delay = 0) {
    element.style.opacity = '0';
    element.style.transform = 'translateY(20px)';
    element.style.transition = 'all 0.5s ease';

    setTimeout(() => {
      element.style.opacity = '1';
      element.style.transform = 'translateY(0)';
    }, delay);
  }

  animateElementExit(element, callback) {
    element.style.opacity = '0';
    element.style.transform = 'translateY(-20px)';

    setTimeout(() => {
      if (callback) callback();
    }, 500);
  }

  createTypingEffect(element, text, speed = 50) {
    element.textContent = '';
    let index = 0;

    const typeChar = () => {
      if (index < text.length) {
        element.textContent += text.charAt(index);
        index++;
        setTimeout(typeChar, speed);
      }
    };

    typeChar();
  }

  // Utility methods
  disableAnimations() {
    this.animationsEnabled = false;
  }

  enableAnimations() {
    this.animationsEnabled = true;
  }

  disableParticles() {
    this.particlesEnabled = false;
  }

  enableParticles() {
    this.particlesEnabled = true;
  }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
  @keyframes rippleExpand {
    0% {
      width: 0;
      height: 0;
      opacity: 1;
    }
    100% {
      width: 200px;
      height: 200px;
      opacity: 0;
    }
  }

  @keyframes confettiFall {
    0% {
      transform: translate(-50%, -50%) rotate(0deg);
      opacity: 1;
    }
    100% {
      transform: translate(-50%, 100vh) rotate(720deg);
      opacity: 0;
    }
  }

  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
  }

  @keyframes progressPulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.02); }
    100% { transform: scale(1); }
  }

  @keyframes timerPulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
  }

  .loading-spinner {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
  }

  .spinner-ring {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--premium-primary);
    animation: spinnerBounce 1.4s ease-in-out infinite both;
  }

  .spinner-ring:nth-child(1) { animation-delay: -0.32s; }
  .spinner-ring:nth-child(2) { animation-delay: -0.16s; }

  @keyframes spinnerBounce {
    0%, 80%, 100% {
      transform: scale(0);
    }
    40% {
      transform: scale(1);
    }
  }

  .floating-notification.success {
    border-color: var(--premium-success);
  }

  .floating-notification.error {
    border-color: var(--premium-danger);
  }

  .floating-notification.warning {
    border-color: var(--premium-warning);
  }
`;

document.head.appendChild(style);

// Initialize micro-interactions
document.addEventListener('DOMContentLoaded', function() {
  window.microInteractions = new MicroInteractions();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = MicroInteractions;
} 