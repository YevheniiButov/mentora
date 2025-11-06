/**
 * Интерактивный интерфейс для виртуальных пациентов
 */
class VirtualPatientPlayer {
    constructor(scenarioId, scenarioData) {
        this.scenarioId = scenarioId;
        this.scenarioData = scenarioData;
        this.currentNode = 'start';
        this.score = 0;
        this.choices = [];
        this.attempt = null;
        
        this.init();
    }
    
    init() {
        this.startAttempt();
        this.renderCurrentNode();
        this.setupEventListeners();
    }
    
    async startAttempt() {
        try {
            const response = await fetch(`/virtual-patients/${this.scenarioId}/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            });
            
            if (response.ok) {
                const data = await response.json();
                this.attempt = data.attempt;

            }
        } catch (error) {
            console.error('Ошибка при запуске попытки:', error);
        }
    }
    
    renderCurrentNode() {
        const currentNodeData = this.findNode(this.currentNode);
        if (!currentNodeData) {
            console.error('Узел не найден:', this.currentNode);
            return;
        }
        
        this.updatePatientStatement(currentNodeData.patient_statement);
        this.updatePatientEmotion(currentNodeData.patient_emotion || 'neutral');
        this.renderOptions(currentNodeData.options);
        this.updateProgress();
        
        // Если это финальный узел, показываем результаты
        if (currentNodeData.is_final) {
            this.showResults();
        }
    }
    
    findNode(nodeId) {
        const nodes = this.scenarioData.default.dialogue_nodes;
        return nodes.find(node => node.id === nodeId);
    }
    
    updatePatientStatement(statement) {
        const statementElement = document.getElementById('patient-statement');
        if (statementElement) {
            // Анимация появления нового текста
            statementElement.style.opacity = '0';
            setTimeout(() => {
                statementElement.textContent = statement;
                statementElement.style.opacity = '1';
            }, 200);
        }
    }
    
    updatePatientEmotion(emotion) {
        const emotionElement = document.getElementById('patient-emotion');
        if (emotionElement) {
            // Удаляем предыдущие классы эмоций
            emotionElement.classList.remove('emotion-happy', 'emotion-concerned', 'emotion-distressed', 'emotion-anxious');
            
            // Добавляем новый класс эмоции
            emotionElement.classList.add(`emotion-${emotion}`);
            
            // Обновляем иконку и текст
            const emotionIcon = emotionElement.querySelector('.emotion-icon');
            const emotionText = emotionElement.querySelector('.emotion-text');
            
            if (emotionIcon && emotionText) {
                switch (emotion) {
                    case 'happy':
                        emotionIcon.className = 'fas fa-smile emotion-icon';
                        emotionText.textContent = 'Спокоен';
                        break;
                    case 'concerned':
                        emotionIcon.className = 'fas fa-frown emotion-icon';
                        emotionText.textContent = 'Обеспокоен';
                        break;
                    case 'distressed':
                        emotionIcon.className = 'fas fa-exclamation-triangle emotion-icon';
                        emotionText.textContent = 'Расстроен';
                        break;
                    case 'anxious':
                        emotionIcon.className = 'fas fa-heartbeat emotion-icon';
                        emotionText.textContent = 'Тревожен';
                        break;
                    default:
                        emotionIcon.className = 'fas fa-meh emotion-icon';
                        emotionText.textContent = 'Нейтрален';
                }
            }
        }
    }
    
    renderOptions(options) {
        const optionsContainer = document.getElementById('dialogue-options');
        if (!optionsContainer) return;
        
        optionsContainer.innerHTML = '';
        
        if (options && options.length > 0) {
            options.forEach((option, index) => {
                const optionElement = document.createElement('div');
                optionElement.className = 'dialogue-option mb-3';
                optionElement.innerHTML = `
                    <button class="btn btn-outline-primary w-100 text-start option-btn" 
                            data-option-id="${option.id}"
                            data-score="${option.score}"
                            data-next-node="${option.next_node}">
                        <div class="d-flex align-items-center">
                            <span class="option-number me-3">${index + 1}</span>
                            <span class="option-text">${option.text}</span>
                        </div>
                    </button>
                `;
                optionsContainer.appendChild(optionElement);
            });
        }
    }
    
    setupEventListeners() {
        // Обработка выбора опций
        document.addEventListener('click', (e) => {
            if (e.target.closest('.option-btn')) {
                const btn = e.target.closest('.option-btn');
                this.handleOptionClick(btn);
            }
        });
        
        // Горячие клавиши
        document.addEventListener('keydown', (e) => {
            if (e.key >= '1' && e.key <= '9') {
                const optionIndex = parseInt(e.key) - 1;
                const optionBtns = document.querySelectorAll('.option-btn');
                if (optionBtns[optionIndex]) {
                    this.handleOptionClick(optionBtns[optionIndex]);
                }
            }
        });
    }
    
    handleOptionClick(btn) {
        const optionId = btn.dataset.optionId;
        const score = parseInt(btn.dataset.score);
        const nextNode = btn.dataset.nextNode;
        
        // Добавляем очки
        this.score += score;
        
        // Сохраняем выбор
        this.choices.push({
            node: this.currentNode,
            option: optionId,
            score: score,
            timestamp: new Date().toISOString()
        });
        
        // Анимация выбора
        btn.classList.add('selected');
        setTimeout(() => {
            // Переходим к следующему узлу
            this.currentNode = nextNode;
            this.renderCurrentNode();
        }, 500);
        
        // Отправляем выбор на сервер
        this.saveChoice(optionId, score, nextNode);
    }
    
    async saveChoice(optionId, score, nextNode) {
        if (!this.attempt) return;
        
        try {
            await fetch(`/virtual-patients/${this.scenarioId}/choice`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    attempt_id: this.attempt.id,
                    option_id: optionId,
                    score: score,
                    next_node: nextNode
                })
            });
        } catch (error) {
            console.error('Ошибка при сохранении выбора:', error);
        }
    }
    
    updateProgress() {
        const progressElement = document.getElementById('scenario-progress');
        if (progressElement) {
            const totalNodes = this.scenarioData.default.dialogue_nodes.length;
            const currentPosition = this.scenarioData.default.dialogue_nodes.findIndex(node => node.id === this.currentNode) + 1;
            const progressPercent = (currentPosition / totalNodes) * 100;
            
            progressElement.style.width = `${progressPercent}%`;
            progressElement.setAttribute('aria-valuenow', progressPercent);
        }
        
        // Обновляем счет
        const scoreElement = document.getElementById('current-score');
        if (scoreElement) {
            scoreElement.textContent = this.score;
        }
    }
    
    async showResults() {
        try {
            const response = await fetch(`/virtual-patients/${this.scenarioId}/complete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    attempt_id: this.attempt.id,
                    final_score: this.score,
                    choices: this.choices
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                window.location.href = data.redirect_url;
            }
        } catch (error) {
            console.error('Ошибка при завершении сценария:', error);
        }
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    const scenarioData = window.scenarioData;
    const scenarioId = window.scenarioId;
    
    if (scenarioData && scenarioId) {
        window.virtualPatientPlayer = new VirtualPatientPlayer(scenarioId, scenarioData);
    }
});

// Дополнительные функции для интерфейса
function togglePatientInfo() {
    const infoPanel = document.getElementById('patient-info-panel');
    if (infoPanel) {
        infoPanel.classList.toggle('collapsed');
    }
}

function restartScenario() {
    if (confirm('Вы уверены, что хотите начать сценарий заново?')) {
        window.location.reload();
    }
}

// Функции для мобильной версии
function toggleMobilePatientInfo() {
    const modal = document.getElementById('mobile-patient-info');
    if (modal) {
        const bsModal = new bootstrap.Modal(modal);
        bsModal.toggle();
    }
}

// Автосохранение прогресса
setInterval(() => {
    if (window.virtualPatientPlayer && window.virtualPatientPlayer.attempt) {
        // Сохраняем текущий прогресс
        localStorage.setItem(`vp_progress_${window.virtualPatientPlayer.scenarioId}`, JSON.stringify({
            currentNode: window.virtualPatientPlayer.currentNode,
            score: window.virtualPatientPlayer.score,
            choices: window.virtualPatientPlayer.choices,
            timestamp: new Date().toISOString()
        }));
    }
}, 30000); // Каждые 30 секунд 