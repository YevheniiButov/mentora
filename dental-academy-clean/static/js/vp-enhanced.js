/**
 * ENHANCED VIRTUAL PATIENT MODULE
 * Adds emotional state, trade-offs, hidden information, and dynamic gameplay
 */

class EnhancedVPFeatures {
  constructor(dialogueInstance) {
    this.dialogue = dialogueInstance;
    this.emotionalState = {
      trust: 35,
      anxiety: 78,
      pain: 85,
      cooperation: 50
    };
    this.timeElapsed = 0;
    this.timeAvailable = 25; // minutes
    this.hiddenInfoUnlocked = [];
    this.scoreHidden = true; // Hide scores until end
    this.choicesHistory = [];
  }
  
  /**
   * Initialize enhanced features
   */
  init() {
    console.log('🎨 Enhanced VP features initialized');
    
    // Load emotional state from scenario
    if (this.dialogue.scenario && this.dialogue.scenario.scenario_data.emotional_state) {
      this.emotionalState = { ...this.dialogue.scenario.scenario_data.emotional_state };
    }
    
    // Update UI
    this.updateEmotionalStateUI();
    
    // Hide scores
    if (this.scoreHidden) {
      document.body.classList.add('score-hidden');
    }
    
    // Initialize time tracking
    this.startTimeTracking();
  }
  
  /**
   * Update emotional state bars in UI
   */
  updateEmotionalStateUI() {
    this.updateEmotionBar('trust', this.emotionalState.trust, '#3b82f6');
    this.updateEmotionBar('anxiety', this.emotionalState.anxiety, '#f97316');
    this.updateEmotionBar('pain', this.emotionalState.pain, '#ef4444');
    this.updateEmotionBar('cooperation', this.emotionalState.cooperation, '#10b981');
  }
  
  updateEmotionBar(emotion, value, color) {
    const valueEl = document.getElementById(`${emotion}Value`);
    const fillEl = document.getElementById(`${emotion}Fill`);
    
    if (valueEl && fillEl) {
      // Animate value change
      const currentValue = parseInt(valueEl.textContent) || 0;
      this.animateNumber(valueEl, currentValue, value, 600);
      
      // Animate bar
      fillEl.style.width = `${value}%`;
      
      // Add pulse effect for high anxiety/pain
      if ((emotion === 'anxiety' || emotion === 'pain') && value >= 70) {
        fillEl.classList.add('high-value-pulse');
      } else {
        fillEl.classList.remove('high-value-pulse');
      }
    }
  }
  
  /**
   * Animate number change
   */
  animateNumber(element, start, end, duration) {
    const range = end - start;
    const startTime = performance.now();
    
    const animate = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      const current = Math.round(start + (range * easeOutQuart));
      
      element.textContent = current;
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    
    requestAnimationFrame(animate);
  }
  
  /**
   * Process choice and apply trade-offs
   */
  processChoice(option) {
    console.log('🎯 Processing enhanced choice:', option);
    
    // Apply trade-offs to emotional state
    if (option.trade_offs) {
      this.applyTradeOffs(option.trade_offs);
    }
    
    // Show body language reaction
    if (option.body_language_reaction) {
      this.showBodyLanguageReaction(option.body_language_reaction);
    }
    
    // Unlock hidden information
    if (option.hidden_info_unlock && option.hidden_info_unlock.length > 0) {
      this.unlockHiddenInfo(option.hidden_info_unlock);
    }
    
    // Update time
    if (option.trade_offs && option.trade_offs.time_cost) {
      const timeCost = parseInt(option.trade_offs.time_cost) || 0;
      this.timeElapsed += Math.abs(timeCost);
      this.updateTimeIndicator();
    }
    
    // Store choice for consequences
    this.choicesHistory.push({
      option: option,
      timestamp: Date.now(),
      emotionalState: { ...this.emotionalState }
    });
    
    // Update UI
    this.updateEmotionalStateUI();
  }
  
  /**
   * Apply trade-offs from choice
   */
  applyTradeOffs(tradeOffs) {
    for (const [key, value] of Object.entries(tradeOffs)) {
      if (key === 'empathy' || key === 'trust') {
        const change = parseInt(value) || 0;
        this.emotionalState.trust = Math.max(0, Math.min(100, this.emotionalState.trust + change));
      }
      
      if (key === 'anxiety') {
        const change = parseInt(value) || 0;
        this.emotionalState.anxiety = Math.max(0, Math.min(100, this.emotionalState.anxiety + change));
      }
      
      if (key === 'pain' || key === 'pain_relief_speed') {
        // Pain relief affects pain level
        if (value === '+immediate' || value === '+fast') {
          this.emotionalState.pain = Math.max(0, this.emotionalState.pain - 30);
        } else if (value === '+good') {
          this.emotionalState.pain = Math.max(0, this.emotionalState.pain - 20);
        } else if (value === '+moderate') {
          this.emotionalState.pain = Math.max(0, this.emotionalState.pain - 10);
        }
      }
      
      if (key === 'patient_satisfaction') {
        const change = parseInt(value) || 0;
        this.emotionalState.cooperation = Math.max(0, Math.min(100, this.emotionalState.cooperation + change));
      }
    }
  }
  
  /**
   * Show body language reaction
   */
  showBodyLanguageReaction(reaction) {
    const dialogueThread = document.getElementById('dialogueThread');
    if (!dialogueThread) return;
    
    const notification = document.createElement('div');
    notification.className = 'body-language-notification';
    notification.innerHTML = `
      <span class="icon">👀</span>
      <div>
        <strong>Lichaamstaal:</strong> ${reaction}
      </div>
    `;
    
    dialogueThread.appendChild(notification);
    
    // Scroll to show
    notification.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
  
  /**
   * Unlock and show hidden information
   */
  unlockHiddenInfo(infoIds) {
    const hiddenInfo = this.dialogue.scenario.scenario_data.hidden_information || [];
    
    infoIds.forEach(id => {
      if (this.hiddenInfoUnlocked.includes(id)) return;
      
      const info = hiddenInfo.find(h => h.id === id);
      if (!info) return;
      
      this.hiddenInfoUnlocked.push(id);
      this.showHiddenInfoUnlock(info);
    });
  }
  
  showHiddenInfoUnlock(info) {
    const dialogueThread = document.getElementById('dialogueThread');
    if (!dialogueThread) return;
    
    const notification = document.createElement('div');
    notification.className = 'hidden-info-unlock';
    notification.innerHTML = `
      <span class="icon">🔓</span>
      <div>
        <strong>Nieuwe informatie onthuld!</strong>
        ${info.content}
      </div>
    `;
    
    dialogueThread.appendChild(notification);
    
    // Scroll and pulse
    notification.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    // Play sound effect (if available)
    this.playUnlockSound();
  }
  
  playUnlockSound() {
    // Optional: Add subtle sound effect
    try {
      const audio = new Audio('/static/sounds/unlock.mp3');
      audio.volume = 0.3;
      audio.play().catch(e => console.log('Sound play failed:', e));
    } catch (e) {
      // Ignore if sound not available
    }
  }
  
  /**
   * Time tracking
   */
  startTimeTracking() {
    this.timeIntervalId = setInterval(() => {
      this.updateTimeIndicator();
    }, 1000);
  }
  
  updateTimeIndicator() {
    const remaining = this.timeAvailable - this.timeElapsed;
    const percentage = (remaining / this.timeAvailable) * 100;
    
    // Update time display
    let indicator = document.getElementById('timeIndicator');
    if (!indicator) {
      indicator = document.createElement('div');
      indicator.id = 'timeIndicator';
      indicator.className = 'time-indicator';
      document.body.appendChild(indicator);
    }
    
    const minutes = Math.floor(remaining);
    const seconds = Math.round((remaining - minutes) * 60);
    
    indicator.innerHTML = `
      <span>⏱️</span>
      <span>${minutes}:${seconds.toString().padStart(2, '0')} resterend</span>
    `;
    
    // Add warning class
    indicator.classList.remove('warning', 'critical');
    if (remaining < 5) {
      indicator.classList.add('critical');
    } else if (remaining < 10) {
      indicator.classList.add('warning');
    }
    
    // Update pressure bar if exists
    const pressureFill = document.getElementById('timePressureFill');
    if (pressureFill) {
      pressureFill.style.width = `${percentage}%`;
    }
  }
  
  /**
   * Enhance choice options display
   */
  enhanceChoiceOptions(options) {
    options.forEach((option, index) => {
      const optionEl = document.querySelector(`[data-option-index="${index}"]`);
      if (!optionEl) return;
      
      // Add trade-offs display
      if (option.trade_offs) {
        const tradeOffsEl = this.createTradeOffsDisplay(option.trade_offs);
        optionEl.appendChild(tradeOffsEl);
      }
      
      // Add consequences preview (on hover)
      if (option.consequences) {
        const consequencesEl = this.createConsequencesDisplay(option.consequences);
        optionEl.appendChild(consequencesEl);
      }
    });
  }
  
  createTradeOffsDisplay(tradeOffs) {
    const container = document.createElement('div');
    container.className = 'choice-trade-offs';
    
    for (const [key, value] of Object.entries(tradeOffs)) {
      const tag = document.createElement('span');
      tag.className = 'trade-off-tag';
      
      // Determine if positive or negative
      const numValue = parseInt(value) || 0;
      if (numValue > 0 || value.includes('+')) {
        tag.classList.add('positive');
        tag.innerHTML = `<span class="icon">+</span>${this.formatTradeOff(key, value)}`;
      } else if (numValue < 0 || value.includes('-')) {
        tag.classList.add('negative');
        tag.innerHTML = `<span class="icon">−</span>${this.formatTradeOff(key, value)}`;
      } else {
        tag.classList.add('neutral');
        tag.textContent = this.formatTradeOff(key, value);
      }
      
      container.appendChild(tag);
    }
    
    return container;
  }
  
  formatTradeOff(key, value) {
    const labels = {
      'empathy': 'Empathie',
      'trust': 'Vertrouwen',
      'anxiety': 'Angst',
      'time_cost': 'Tijd',
      'diagnostic_quality': 'Diagnose kwaliteit',
      'pain_relief_speed': 'Pijnverlichting',
      'patient_satisfaction': 'Tevredenheid',
      'efficiency': 'Efficiëntie'
    };
    
    return `${labels[key] || key}: ${value}`;
  }
  
  createConsequencesDisplay(consequences) {
    const container = document.createElement('div');
    container.className = 'choice-consequences';
    
    if (consequences.immediate) {
      const item = document.createElement('div');
      item.className = 'consequence-item';
      item.innerHTML = `<span class="icon">⚡</span><span>${consequences.immediate}</span>`;
      container.appendChild(item);
    }
    
    if (consequences.delayed) {
      const item = document.createElement('div');
      item.className = 'consequence-item';
      item.innerHTML = `<span class="icon">⏳</span><span>${consequences.delayed}</span>`;
      container.appendChild(item);
    }
    
    return container;
  }
  
  /**
   * Reveal final scores
   */
  revealFinalScores() {
    document.body.classList.remove('score-hidden');
    
    // Show detailed breakdown
    this.showFinalReport();
  }
  
  showFinalReport() {
    // TODO: Create beautiful final report with all metrics
    console.log('📊 Final Report:', {
      emotionalState: this.emotionalState,
      timeUsed: this.timeElapsed,
      hiddenInfoUnlocked: this.hiddenInfoUnlocked.length,
      choices: this.choicesHistory.length
    });
  }
  
  /**
   * Cleanup
   */
  destroy() {
    if (this.timeIntervalId) {
      clearInterval(this.timeIntervalId);
    }
  }
}

// Export for use in main dialogue
window.EnhancedVPFeatures = EnhancedVPFeatures;

