class VirtualPatientDialogue {
  constructor(scenarioId, attemptId) {
    this.scenarioId = scenarioId;
    this.attemptId = attemptId;
    this.scenario = null;
    this.attempt = null;
    this.currentNodeId = null;
    this.score = 0;
    this.fillInScore = 0;
    this.startTime = Date.now();
    this.state = 'loading'; // loading, playing, complete
    this.dialogueHistory = [];
    this.notes = '';
    
    // DOM elements
    this.container = document.getElementById('vpContainer');
    this.loadingEl = document.getElementById('vpLoading');
    this.interfaceEl = document.getElementById('vpInterface');
    this.dialogueThread = document.getElementById('dialogueThread');
    this.interactionArea = document.getElementById('interactionArea');
    this.interactionContent = document.getElementById('interactionContent');
    this.interactionLoading = document.getElementById('interactionLoading');
    this.completionModal = document.getElementById('completionModal');
    this.modalBackdrop = document.getElementById('modalBackdrop');
    this.notesArea = document.getElementById('notesArea');
    this.progressRing = document.getElementById('progressRing');
  }
  
  async init(scenarioId, attemptId) {
    try {
      // 1. Загрузить сценарий
      const scenarioResponse = await fetch(`/api/vp/daily-scenario`);
      if (!scenarioResponse.ok) throw new Error('Failed to load scenario');
      const scenarioData = await scenarioResponse.json();
      
      if (!scenarioData.success) {
        this.showError(scenarioData.message || 'No scenario available');
        return;
      }
      
      this.scenario = scenarioData.scenario;
      
      // 1.1. Установить/создать attempt
      if (attemptId) {
        this.attemptId = attemptId;
      } else {
        try {
          const attemptResp = await fetch('/api/vp/start-attempt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scenario_id: this.scenario.id })
          });
          const attemptJson = await attemptResp.json();
          if (attemptJson && attemptJson.success) {
            this.attemptId = attemptJson.attempt_id;
          } else {
            console.warn('Attempt not created:', attemptJson);
          }
        } catch (e) {
          console.warn('Failed to start attempt automatically', e);
        }
      }
      
      // 2. Показать интерфейс
      this.showInterface();
      
      // 3. Инициализировать компоненты
      this.initPatientInfo();
      this.initDetailToggles();
      this.initProgressTracking();
      this.initTimerUpdate();
      this.initMobileModalControls();
      
      // 4. Показать initial_state (начальное сообщение пациента)
      const initialState = this.scenario.scenario_data.initial_state;
      const hasInitialState = initialState && initialState.patient_statement;
      
      if (hasInitialState) {
        this.addMessageToThread('from-patient', initialState.patient_statement);
        
        // Показать заметки врача если есть
        if (initialState.notes_dentist) {
          console.log('Initial notes:', initialState.notes_dentist);
        }
      }
      
      // 5. Показать первый узел с вариантами ответа
      const nodes = this.scenario.scenario_data.dialogue_nodes;
      if (nodes && nodes.length > 0) {
        this.currentNodeId = nodes[0].id;
        // Не показываем patient_statement первого узла, если уже показали initial_state
        await this.displayNode(this.currentNodeId, !hasInitialState);
      } else {
        this.showError('Сценарий не содержит узлов диалога');
        return;
      }
      
      this.state = 'playing';
    } catch (error) {
      console.error('Initialization error:', error);
      this.showError('Ошибка при загрузке сценария. Пожалуйста, попробуйте позже.');
    }
  }
  
  initMobileModalControls() {
    const toggleBtn = document.getElementById('menuToggleBtn');
    const patientModal = document.getElementById('patientModal');
    const patientModalBackdrop = document.getElementById('patientModalBackdrop');
    const patientModalClose = document.getElementById('patientModalClose');
    
    // Make button visible only when present (mobile)
    if (toggleBtn) {
      toggleBtn.style.display = 'inline-flex';
      toggleBtn.addEventListener('click', () => {
        if (patientModal) patientModal.style.display = 'flex';
      });
    }
    
    if (patientModalBackdrop) {
      patientModalBackdrop.addEventListener('click', () => {
        patientModal.style.display = 'none';
      });
    }
    
    if (patientModalClose) {
      patientModalClose.addEventListener('click', () => {
        patientModal.style.display = 'none';
      });
    }
  }

  showInterface() {
    this.loadingEl.style.display = 'none';
    this.interfaceEl.style.display = 'flex';
  }
  
  initPatientInfo() {
    const data = this.scenario.scenario_data || {};
    const patientInfo = data.patient_info || {};
    
    // Безопасные значения по умолчанию
    const patientName = patientInfo.name || 'Patient';
    const patientAge = patientInfo.age || 'Onbekend';
    const patientGender = patientInfo.gender || 'unknown';
    
    // Инициалы
    const initials = patientName && patientName.trim() 
      ? (patientName.split(' ').map(n => n[0] || '').filter(Boolean).join('').toUpperCase() || 'P')
      : 'P';
    const initialsEl = document.getElementById('patientInitials');
    const initialsMobileEl = document.getElementById('patientInitialsMobile');
    if (initialsEl) initialsEl.textContent = initials;
    if (initialsMobileEl) initialsMobileEl.textContent = initials;
    
    // Основная информация
    const nameEl = document.getElementById('patientName');
    const nameMobileEl = document.getElementById('patientNameMobile');
    const ageEl = document.getElementById('patientAge');
    const ageMobileEl = document.getElementById('patientAgeMobile');
    const genderEl = document.getElementById('patientGender');
    
    if (nameEl) nameEl.textContent = patientName;
    if (nameMobileEl) nameMobileEl.textContent = patientName;
    if (ageEl) ageEl.textContent = patientAge;
    if (ageMobileEl) ageMobileEl.textContent = `${patientAge} jaar`;
    if (genderEl) genderEl.textContent = this.translateGender(patientGender);
    
    // История болезни
    const historyEl = document.getElementById('patientHistory');
    const historyMobileEl = document.getElementById('patientHistoryMobile');
    const historyText = patientInfo.medical_history || 'Geen informatie';
    if (historyEl) historyEl.textContent = historyText;
    if (historyMobileEl) historyMobileEl.textContent = historyText;
    
    // Аллергии
    const allergiesContainer = document.getElementById('allergiesContainer');
    const allergiesMobile = document.getElementById('allergiesMobile');
    if (patientInfo.allergies && Array.isArray(patientInfo.allergies) && patientInfo.allergies.length > 0) {
      const allergiesHtml = patientInfo.allergies.map(a => 
        `<span class="allergy-tag">${a}</span>`
      ).join('');
      if (allergiesContainer) allergiesContainer.innerHTML = allergiesHtml;
      
      const allergiesMobileHtml = patientInfo.allergies.map(a => 
        `<span class="allergy-tag">${a}</span>`
      ).join('');
      if (allergiesMobile) allergiesMobile.innerHTML = allergiesMobileHtml;
    } else {
      if (allergiesContainer) allergiesContainer.innerHTML = '';
      if (allergiesMobile) allergiesMobile.innerHTML = '';
    }
    
    // Симптомы
    const symptomsContainer = document.getElementById('symptomsContainer');
    if (patientInfo.symptoms && Array.isArray(patientInfo.symptoms) && patientInfo.symptoms.length > 0) {
      const symptomsHtml = patientInfo.symptoms.map(s => 
        `<div class="symptom-item">
           <span class="symptom-icon">⚠</span>
           <span>${s}</span>
         </div>`
      ).join('');
      if (symptomsContainer) symptomsContainer.innerHTML = symptomsHtml;
    } else {
      if (symptomsContainer) symptomsContainer.innerHTML = '';
    }
    
    // Vital signs если есть
    const vitalSignsSection = document.getElementById('vitalSignsSection');
    const vitalsContainer = document.getElementById('vitalsContainer');
    if (patientInfo.vital_signs && typeof patientInfo.vital_signs === 'object') {
      if (vitalSignsSection) vitalSignsSection.style.display = 'block';
      const vitalsHtml = Object.entries(patientInfo.vital_signs).map(([key, value]) => 
        `<div class="vital-item">
           <span class="vital-label">${this.translateVitalSign(key)}</span>
           <span class="vital-value">${value}</span>
         </div>`
      ).join('');
      if (vitalsContainer) vitalsContainer.innerHTML = vitalsHtml;
    } else {
      if (vitalSignsSection) vitalSignsSection.style.display = 'none';
      if (vitalsContainer) vitalsContainer.innerHTML = '';
    }
  }
  
  initDetailToggles() {
    const toggles = document.querySelectorAll('.detail-toggle');
    toggles.forEach(toggle => {
      toggle.addEventListener('click', (e) => {
        const section = toggle.dataset.section;
        const content = document.getElementById(`detail-${section}`);
        const isOpen = content.style.display !== 'none';
        
        content.style.display = isOpen ? 'none' : 'block';
        toggle.classList.toggle('active', !isOpen);
      });
    });
    
    // Mobile card toggle
    const mobileToggle = document.getElementById('mobileCardToggle');
    const mobileExpanded = document.getElementById('mobileCardExpanded');
    mobileToggle.addEventListener('click', () => {
      const isOpen = mobileExpanded.style.display !== 'none';
      mobileExpanded.style.display = isOpen ? 'none' : 'block';
      mobileToggle.classList.toggle('active', !isOpen);
    });
  }
  
  initProgressTracking() {
    const data = this.scenario.scenario_data || {};
    const dialogueNodes = data.dialogue_nodes || [];
    const totalNodes = dialogueNodes.length;
    const totalStepsEl = document.getElementById('totalSteps');
    if (totalStepsEl) {
      totalStepsEl.textContent = totalNodes;
    }
  }
  
  initTimerUpdate() {
    const timeSpentEl = document.getElementById('timeSpent');
    if (!timeSpentEl) return;
    
    setInterval(() => {
      const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
      const minutes = Math.floor(elapsed / 60);
      const seconds = elapsed % 60;
      const formatted = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
      timeSpentEl.textContent = formatted;
    }, 1000);
  }
  
  async displayNode(nodeId, showPatientStatement = true) {
    this.interactionLoading.style.display = 'flex';
    this.interactionContent.style.display = 'none';
    
    try {
      // Найти узел в сценарии
      console.log('Looking for node:', nodeId);
      console.log('Available nodes:', this.scenario.scenario_data.dialogue_nodes);
      const node = this.scenario.scenario_data.dialogue_nodes.find(n => n.id === nodeId);
      if (!node) {
        console.error('Node not found:', nodeId);
        console.error('Available node IDs:', this.scenario.scenario_data.dialogue_nodes.map(n => n.id));
        throw new Error(`Node not found: ${nodeId}`);
      }
      console.log('Found node:', node);
      
      // Добавить сообщение пациента в диалог только если нужно
      // (для первого узла не показываем, если уже показали initial_state)
      if (showPatientStatement && node.patient_statement) {
        this.addMessageToThread('from-patient', node.patient_statement);
      }
      
      // Обновить прогресс
      this.updateProgress(nodeId);
      
      // Показать interaction элемент
      setTimeout(() => {
        this.renderInteraction(node);
        this.interactionLoading.style.display = 'none';
        this.interactionContent.style.display = 'block';
      }, 300);
    } catch (error) {
      console.error('Error displaying node:', error);
      this.showError('Ошибка при отображении узла');
    }
  }
  
  addMessageToThread(sender, message) {
    const messageEl = document.createElement('div');
    messageEl.className = `dialogue-message ${sender}`;
    messageEl.innerHTML = `
      <div class="message-content">${this.escapeHtml(message)}</div>
      <div class="message-timestamp">${new Date().toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' })}</div>
    `;
    messageEl.classList.add('animate-slideInUp');
    this.dialogueThread.appendChild(messageEl);
    
    // Scroll to bottom
    this.dialogueThread.scrollTop = this.dialogueThread.scrollHeight;
  }
  
  renderInteraction(node) {
    this.interactionContent.innerHTML = '';
    
    // Если есть fill-in
    if (node.fill_in) {
      this.renderFillIn(node);
    }
    // Если есть options
    else if (node.options && node.options.length > 0) {
      this.renderOptions(node);
    }
    // Если это конец (outcome node)
    else if (node.is_outcome) {
      this.handleOutcome(node);
    }
  }
  
  renderOptions(node) {
    const container = document.createElement('div');
    container.className = 'options-container';
    
    node.options.forEach((option, index) => {
      const button = document.createElement('button');
      button.className = 'option-button';
      button.textContent = option.text;
      // Устанавливаем ID опции, если его нет
      if (!option.id) {
        option.id = `option_${index}`;
      }
      button.addEventListener('click', () => this.selectOption(option, node));
      container.appendChild(button);
    });
    
    this.interactionContent.appendChild(container);
  }
  
  renderFillIn(node) {
    const container = document.createElement('div');
    container.className = 'fill-in-container';
    
    const fillInConfig = node.fill_in;
    
    // Проверяем, что fillInConfig существует и корректный
    if (!fillInConfig) {
      console.error('Fill-in config is missing for node:', node.id);
      return;
    }
    
    // Текст с пропуском
    const textEl = document.createElement('p');
    textEl.className = 'fill-in-text';
    
    let text = '';
    
    // Если есть text в конфиге (старый формат с ____)
    if (fillInConfig.text && typeof fillInConfig.text === 'string') {
      text = fillInConfig.text.replace('____', `<span class="blank">[?]</span>`);
    }
    // Если есть word в конфиге (новый формат - заменяем слово в patient_statement)
    else if (fillInConfig.word && typeof fillInConfig.word === 'string') {
      // Используем patient_statement из узла, если есть
      const sourceText = node.patient_statement || node.title || '';
      
      // Заменяем слово на пропуск (case-insensitive)
      const wordRegex = new RegExp(`\\b${fillInConfig.word}\\b`, 'gi');
      text = sourceText.replace(wordRegex, `<span class="blank">[?]</span>`);
      
      // Если замена не произошла, просто показываем текст с пропуском в конце
      if (text === sourceText) {
        text = sourceText + ' <span class="blank">[?]</span>';
      }
    }
    // Fallback: используем patient_statement с пропуском
    else {
      const sourceText = node.patient_statement || node.title || 'Vul het ontbrekende woord in:';
      text = sourceText + ' <span class="blank">[?]</span>';
    }
    
    textEl.innerHTML = text;
    container.appendChild(textEl);
    
    // Input group
    const inputGroup = document.createElement('div');
    inputGroup.className = 'fill-in-input-group';
    
    const label = document.createElement('label');
    label.className = 'fill-in-label';
    label.textContent = 'Voer het juiste woord in:';
    inputGroup.appendChild(label);
    
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'fill-in-input';
    input.placeholder = 'Typ hier...';
    input.setAttribute('data-node-id', node.id);
    inputGroup.appendChild(input);
    
    // Actions
    const actions = document.createElement('div');
    actions.className = 'fill-in-actions';
    
    const hintBtn = document.createElement('button');
    hintBtn.className = 'btn-hint';
    hintBtn.textContent = '? Hint';
    hintBtn.addEventListener('click', () => this.showFillInHint(fillInConfig, input));
    actions.appendChild(hintBtn);
    
    const submitBtn = document.createElement('button');
    submitBtn.className = 'btn-submit';
    submitBtn.textContent = 'Controleer antwoord';
    submitBtn.addEventListener('click', () => this.validateFillIn(input, node, fillInConfig));
    actions.appendChild(submitBtn);
    
    inputGroup.appendChild(actions);
    container.appendChild(inputGroup);
    
    // Focus on input
    setTimeout(() => input.focus(), 100);
    
    this.interactionContent.appendChild(container);
  }
  
  async selectOption(option, node) {
    // Disable all buttons
    const buttons = this.interactionContent.querySelectorAll('.option-button');
    buttons.forEach(btn => btn.disabled = true);
    
    try {
      // Убедиться, что attempt существует
      if (!this.attemptId && this.scenario?.id) {
        try {
          const attemptResp = await fetch('/api/vp/start-attempt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scenario_id: this.scenario.id })
          });
          const attemptJson = await attemptResp.json();
          if (attemptJson && attemptJson.success) {
            this.attemptId = attemptJson.attempt_id;
          }
        } catch (e) {
          console.warn('Attempt fallback creation failed', e);
        }
      }
      
      // Получить точку перед сохранением
      let optionScore = option.score || 0;
      this.score += optionScore;
      
      // Логирование для диагностики
      console.log('Sending choice data:', {
        attempt_id: this.attemptId,
        option_id: option.id,
        score: optionScore,
        next_node: option.next_node,
        dialogue_history: this.dialogueHistory
      });
      
      // Сохранить выбор на backend
      const response = await fetch('/api/vp/save-choice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          attempt_id: this.attemptId,
          option_id: option.id,
          score: optionScore,
          next_node: option.next_node,
          dialogue_history: this.dialogueHistory
        })
      });
      
      const result = await response.json();
      if (!result.success) throw new Error('Failed to save choice');
      
      // Обновить UI
      this.updateScore(result.current_score, result.fill_in_score);
      
      // Показать выбранный вариант визуально
      const selectedBtn = Array.from(buttons).find(btn => btn.textContent === option.text);
      if (selectedBtn) {
        selectedBtn.classList.add('correct');
      }
      
      // Добавить ответ врача в диалог
      this.addMessageToThread('from-doctor', option.text);
      
      // Переход к следующему узлу
      setTimeout(() => {
        if (option.next_node && option.next_node !== 'end') {
          this.currentNodeId = option.next_node;
          // Всегда показываем patient_statement для следующих узлов (после первого)
          this.displayNode(this.currentNodeId, true);
        } else {
          // Сценарий завершен
          this.completeScenario();
        }
      }, 1000);
    } catch (error) {
      console.error('Error selecting option:', error);
      buttons.forEach(btn => btn.disabled = false);
    }
  }
  
  showFillInHint(fillInConfig, input) {
    if (!fillInConfig) {
      console.error('Fill-in config is missing for hint');
      return;
    }
    
    const hint = (fillInConfig.hint && typeof fillInConfig.hint === 'string') 
      ? fillInConfig.hint 
      : 'Geen hint beschikbaar';
    
    const message = document.createElement('div');
    message.className = 'hint-message';
    message.textContent = hint;
    input.parentElement.insertBefore(message, input.nextSibling);
    setTimeout(() => message.remove(), 5000);
  }
  
  async validateFillIn(input, node, fillInConfig) {
    const userAnswer = input.value.trim();
    
    if (!userAnswer) {
      input.classList.add('error');
      input.classList.remove('success');
      setTimeout(() => input.classList.remove('error'), 500);
      return;
    }
    
    try {
      // Валидировать на backend
      const response = await fetch('/api/vp/validate-fill-in', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          attempt_id: this.attemptId,
          node_id: node.id,
          user_answer: userAnswer
        })
      });
      
      const result = await response.json();
      
      if (result.valid) {
        // Правильно!
        input.classList.add('success');
        input.classList.remove('error');
        input.disabled = true;
        
        this.fillInScore += result.score;
        this.updateScore(this.score, this.fillInScore);
        
        // Feedback
        this.showFeedback('success', result.message);
        
        // Добавить ответ в диалог
        this.addMessageToThread('from-doctor', userAnswer);
        
        // Переход к следующему узлу
        setTimeout(() => {
          this.currentNodeId = node.next_node || 'end';
          if (this.currentNodeId === 'end') {
            this.completeScenario();
          } else {
            // Всегда показываем patient_statement для следующих узлов
            this.displayNode(this.currentNodeId, true);
          }
        }, 1500);
      } else {
        // Неправильно
        input.classList.add('error');
        input.classList.remove('success');
        
        // Feedback с подсказкой
        this.showFeedback('error', result.message);
        
        // Shake animation
        setTimeout(() => {
          input.value = '';
          input.classList.remove('error');
          input.focus();
        }, 500);
      }
    } catch (error) {
      console.error('Error validating fill-in:', error);
    }
  }
  
  showFeedback(type, message) {
    const feedback = document.createElement('div');
    feedback.className = `feedback-message ${type}`;
    feedback.textContent = message;
    this.interactionContent.appendChild(feedback);
    setTimeout(() => feedback.remove(), 4000);
  }
  
  updateScore(dialogueScore, fillInScore) {
    this.score = dialogueScore;
    this.fillInScore = fillInScore;
    const total = this.score + this.fillInScore;
    
    document.getElementById('headerScore').textContent = total;
    document.getElementById('sidebarScore').textContent = total;
    document.getElementById('dialogueScore').textContent = this.score;
    document.getElementById('fillInScoreWidget').textContent = this.fillInScore;
  }
  
  updateProgress(nodeId) {
    const totalNodes = this.scenario.scenario_data.dialogue_nodes.length;
    const currentIndex = this.scenario.scenario_data.dialogue_nodes.findIndex(n => n.id === nodeId);
    const progress = ((currentIndex + 1) / totalNodes) * 100;
    
    document.getElementById('currentStep').textContent = currentIndex + 1;
    document.getElementById('progressFill').style.width = progress + '%';
    document.getElementById('progressPercent').textContent = Math.round(progress) + '%';
    
    // Update SVG ring
    const circumference = 282.7;
    const offset = circumference - (progress / 100) * circumference;
    this.progressRing.style.strokeDashoffset = offset;
  }
  
  async completeScenario() {
    try {
      const response = await fetch('/api/vp/complete-attempt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          attempt_id: this.attemptId
        })
      });
      
      const result = await response.json();
      if (!result.success) throw new Error('Failed to complete');
      
      const attempt = result.attempt;
      this.showResultsModal(attempt);
    } catch (error) {
      console.error('Error completing scenario:', error);
    }
  }
  
  showResultsModal(attempt) {
    const level = attempt.level;
    const badges = {
      'excellent': { icon: '✓', emoji: '⭐' },
      'good': { icon: '✓', emoji: '👍' },
      'needs_improvement': { icon: '!', emoji: '📚' },
      'poor': { icon: '✗', emoji: '🔄' }
    };
    
    const badge = badges[level] || badges['needs_improvement'];
    
    document.getElementById('badgeIcon').textContent = badge.icon;
    document.getElementById('badgeLabel').textContent = this.translateLevel(level);
    document.getElementById('badgeIcon').className = `badge-icon ${level}`;
    
    document.getElementById('finalTotalScore').textContent = attempt.total_score;
    document.getElementById('finalPercentage').textContent = attempt.percentage + '%';
    document.getElementById('finalDialogueScore').textContent = attempt.score;
    document.getElementById('finalFillInScore').textContent = attempt.fill_in_score;
    document.getElementById('feedbackMessage').textContent = attempt.feedback;
    
    this.completionModal.style.display = 'flex';
    
    // Buttons
    document.getElementById('continueBtn').addEventListener('click', () => {
      // Redirect to the modern learning map demo template
      window.location.href = '/demo/learning-map-modern';
    });
    
    document.getElementById('modalCloseBtn').addEventListener('click', () => {
      this.completionModal.style.display = 'none';
    });
    
    document.getElementById('modalBackdrop').addEventListener('click', () => {
      this.completionModal.style.display = 'none';
    });
  }
  
  handleOutcome(node) {
    // Если это outcome node - завершить
    this.completeScenario();
  }
  
  translateGender(gender) {
    const map = {
      'male': 'Man',
      'female': 'Vrouw',
      'other': 'Anders'
    };
    return map[gender] || gender;
  }
  
  translateVitalSign(sign) {
    const map = {
      'blood_pressure': 'Bloeddruk',
      'heart_rate': 'Hartslag',
      'temperature': 'Temperatuur',
      'oxygen_saturation': 'Zuurstofverzadiging'
    };
    return map[sign] || sign;
  }
  
  translateLevel(level) {
    const map = {
      'excellent': 'Uitstekend',
      'good': 'Goed',
      'needs_improvement': 'Kan beter',
      'poor': 'Moet herhalen'
    };
    return map[level] || level;
  }
  
  showError(message) {
    const error = document.createElement('div');
    error.style.cssText = `
      padding: 20px;
      background-color: #EF4444;
      color: white;
      border-radius: 8px;
      text-align: center;
      margin: 40px 20px;
    `;
    error.textContent = message;
    this.container.appendChild(error);
  }
  
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Initialize
const vpDialogue = new VirtualPatientDialogue();

