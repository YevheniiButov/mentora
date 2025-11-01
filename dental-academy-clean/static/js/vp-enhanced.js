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
    
    // Load constraints
    if (this.dialogue.scenario && this.dialogue.scenario.scenario_data.scenario_constraints) {
      this.constraints = this.dialogue.scenario.scenario_data.scenario_constraints;
      this.timeAvailable = this.constraints.time_available || 25;
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
   * Get dynamic patient statement based on trust level
   */
  getDynamicStatement(node) {
    if (!node.patient_statement_dynamic) {
      return node.patient_statement || '';
    }
    
    const trust = this.emotionalState.trust;
    const thresholds = node.trust_threshold || { low: 40, medium: 60, high: 75 };
    
    if (trust >= thresholds.high && node.patient_statement_dynamic.trust_high) {
      return node.patient_statement_dynamic.trust_high;
    } else if (trust >= thresholds.medium && node.patient_statement_dynamic.trust_medium) {
      return node.patient_statement_dynamic.trust_medium;
    } else {
      return node.patient_statement_dynamic.trust_low || node.patient_statement || '';
    }
  }
  
  /**
   * Check resource availability
   */
  checkResourceAvailability(resourceName) {
    if (!this.constraints || !this.constraints.resources) return true;
    
    const resource = this.constraints.resources[resourceName];
    if (!resource) return true;
    
    return resource.available;
  }
  
  getResourceWaitTime(resourceName) {
    if (!this.constraints || !this.constraints.resources) return 0;
    
    const resource = this.constraints.resources[resourceName];
    if (!resource) return 0;
    
    return resource.wait_time_minutes || 0;
  }
  
  /**
   * Trigger random event
   */
  triggerRandomEvent(eventType, probability = 0.3) {
    if (Math.random() > probability) return false;
    
    console.log('🎲 Random event triggered:', eventType);
    
    // Event-specific handling
    switch(eventType) {
      case 'anxiety_spike_in_waiting_room':
        this.showRandomEventNotification(
          '⚠️ Onverwacht voorval!',
          'Patiënte hyperventileert in wachtkamer - directe actie vereist!'
        );
        return true;
      
      case 'worse_than_expected':
        this.showRandomEventNotification(
          '🔍 Diagnostische verrassing!',
          'Röntgen toont periapikaal abces - ernstiger dan verwacht!'
        );
        this.emotionalState.anxiety += 15;
        this.updateEmotionalStateUI();
        return true;
      
      case 'insurance_call':
        this.showRandomEventNotification(
          '📞 Verzekeraar belt',
          'Assistente onderbreekt: verzekeraar wil bevestiging van behandeling'
        );
        this.timeElapsed += 5; // Lost time
        this.updateTimeIndicator();
        return true;
        
      default:
        return false;
    }
  }
  
  showRandomEventNotification(title, message) {
    const dialogueThread = document.getElementById('dialogueThread');
    if (!dialogueThread) return;
    
    const notification = document.createElement('div');
    notification.className = 'random-event-notification';
    notification.innerHTML = `
      <div class="event-header">
        <strong>${title}</strong>
      </div>
      <div class="event-body">${message}</div>
    `;
    
    dialogueThread.appendChild(notification);
    notification.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    // Add CSS if not exists
    if (!document.getElementById('random-event-styles')) {
      const style = document.createElement('style');
      style.id = 'random-event-styles';
      style.textContent = `
        .random-event-notification {
          padding: 16px;
          background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
          border-left: 4px solid #f59e0b;
          border-radius: 12px;
          margin: 16px 0;
          animation: eventPulse 0.6s ease-out;
          box-shadow: 0 4px 16px rgba(245, 158, 11, 0.25);
        }
        .event-header {
          font-size: 15px;
          font-weight: 700;
          color: #78350f;
          margin-bottom: 8px;
        }
        .event-body {
          font-size: 14px;
          color: #92400e;
          line-height: 1.5;
        }
        @keyframes eventPulse {
          0% { transform: scale(0.95); opacity: 0; }
          50% { transform: scale(1.02); }
          100% { transform: scale(1); opacity: 1; }
        }
      `;
      document.head.appendChild(style);
    }
  }
  
  /**
   * Check budget constraints
   */
  checkBudgetAffordability(treatmentCost) {
    if (!this.constraints || !this.constraints.patient_budget) return true;
    
    const budget = this.constraints.patient_budget.max_affordable || Infinity;
    return treatmentCost <= budget;
  }
  
  getBudgetInfo() {
    if (!this.constraints || !this.constraints.patient_budget) return null;
    
    return this.constraints.patient_budget;
  }
  
  /**
   * Track delayed consequences
   */
  addDelayedConsequence(consequence, triggersInNodes) {
    if (!this.delayedConsequences) {
      this.delayedConsequences = [];
    }
    
    this.delayedConsequences.push({
      consequence: consequence,
      triggersIn: triggersInNodes,
      triggered: false
    });
  }
  
  checkAndTriggerConsequences(currentNodeId) {
    if (!this.delayedConsequences) return;
    
    this.delayedConsequences.forEach(dc => {
      if (!dc.triggered && dc.triggersIn.includes(currentNodeId)) {
        dc.triggered = true;
        this.showConsequenceNotification(dc.consequence);
      }
    });
  }
  
  showConsequenceNotification(consequence) {
    const dialogueThread = document.getElementById('dialogueThread');
    if (!dialogueThread) return;
    
    const notification = document.createElement('div');
    notification.className = 'consequence-notification';
    notification.innerHTML = `
      <span class="icon">⏳</span>
      <div>
        <strong>Gevolg van eerdere keuze:</strong> ${consequence}
      </div>
    `;
    
    dialogueThread.appendChild(notification);
    notification.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
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

