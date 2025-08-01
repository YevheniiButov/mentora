/**
 * Learning Plan JavaScript
 * Handles interactive learning planner with calendar integration
 */

let calendar;
let studyPlan = {
    examDate: null,
    startDate: null,
    endDate: null,
    intensity: 'moderate',
    studyDays: [1, 2, 3, 4, 5], // Monday to Friday
    studyTime: 'afternoon',
    totalHours: 0
};

// Initialize page when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeCalendar();
    initializeForm();
    generateDomainProgress();
    generateStudyGoals();
    updateHeaderStats();
    bindEventHandlers();
    
    // Инициализируем систему уведомлений
    if (typeof NotificationSystem !== 'undefined') {
        window.notificationSystem = new NotificationSystem();
    }
    
    // Загружаем скрипт уведомлений если не загружен
    if (!window.notificationSystem) {
        loadNotificationScript();
    }
});

/**
 * Загружает скрипт уведомлений
 */
function loadNotificationScript() {
    const script = document.createElement('script');
    script.src = '/static/js/notification-system.js';
    script.onload = function() {
        window.notificationSystem = new NotificationSystem();
    };
    document.head.appendChild(script);
}

/**
 * Initialize FullCalendar
 */
function initializeCalendar() {
    const calendarEl = document.getElementById('calendar');
    
    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek'
        },
        height: 'auto',
        locale: 'ru',
        events: generateSampleEvents(),
        eventClick: function(info) {
            showEventDetails(info.event);
        },
        dateClick: function(info) {
            addStudySession(info.date);
        },
        eventDidMount: function(info) {
            // Add custom styling based on event type
            if (info.event.extendedProps.type === 'exam') {
                info.el.style.backgroundColor = '#ef4444';
                info.el.style.borderColor = '#ef4444';
            }
        }
    });
    
    calendar.render();
}

/**
 * Generate sample events for calendar
 */
function generateSampleEvents() {
    const events = [];
    
    // Use diagnostic results if available
    const domains = diagnosticResults ? diagnosticResults.domains : [
        { name: 'Endodontics', score: 85 },
        { name: 'Periodontics', score: 72 },
        { name: 'Orthodontics', score: 68 },
        { name: 'Oral Surgery', score: 82 },
        { name: 'Prosthodontics', score: 75 },
        { name: 'Preventive Care', score: 88 }
    ];
    
    const colors = ['#3ECDC1', '#6C5CE7', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6'];
    const today = new Date();
    
    // Generate study sessions for next 30 days
    for (let i = 1; i <= 30; i++) {
        const date = new Date(today);
        date.setDate(today.getDate() + i);
        
        // Skip weekends for sample data
        if (date.getDay() === 0 || date.getDay() === 6) continue;
        
        const domainIndex = Math.floor(Math.random() * domains.length);
        const domain = domains[domainIndex];
        const duration = Math.floor(Math.random() * 3) + 1; // 1-3 hours
        
        events.push({
            title: `${domain.name} (${duration}ч)`,
            start: date.toISOString().split('T')[0],
            backgroundColor: colors[domainIndex],
            borderColor: colors[domainIndex],
            extendedProps: {
                domain: domain.name,
                duration: duration,
                type: 'study',
                score: domain.score
            }
        });
    }
    
    // Add exam date if available
    if (studyPlan.examDate) {
        events.push({
            title: 'BIG Экзамен',
            start: studyPlan.examDate,
            backgroundColor: '#ef4444',
            borderColor: '#ef4444',
            extendedProps: {
                type: 'exam'
            }
        });
    }
    
    return events;
}

/**
 * Initialize form with default values
 */
function initializeForm() {
    const today = new Date();
    const examDate = new Date(today);
    examDate.setDate(today.getDate() + 90);
    
    const endDate = new Date(examDate);
    endDate.setDate(examDate.getDate() - 7);
    
    document.getElementById('exam-date').value = examDate.toISOString().split('T')[0];
    document.getElementById('start-date').value = today.toISOString().split('T')[0];
    document.getElementById('end-date').value = endDate.toISOString().split('T')[0];
    
    // Update study plan
    studyPlan.examDate = examDate.toISOString().split('T')[0];
    studyPlan.startDate = today.toISOString().split('T')[0];
    studyPlan.endDate = endDate.toISOString().split('T')[0];
}

/**
 * Generate domain progress panel
 */
function generateDomainProgress() {
    const container = document.getElementById('domain-progress');
    if (!container) return;
    
    const domains = diagnosticResults ? diagnosticResults.domains : [
        { name: 'Endodontics', score: 85, target: 90, hours: 12 },
        { name: 'Periodontics', score: 72, target: 85, hours: 18 },
        { name: 'Orthodontics', score: 68, target: 80, hours: 24 },
        { name: 'Oral Surgery', score: 82, target: 88, hours: 15 },
        { name: 'Prosthodontics', score: 75, target: 85, hours: 20 },
        { name: 'Preventive Care', score: 88, target: 92, hours: 8 }
    ];
    
    domains.forEach((domain, index) => {
        const progressItem = document.createElement('div');
        progressItem.className = 'progress-item';
        
        const progressPercentage = Math.round((domain.score / domain.target) * 100);
        
        progressItem.innerHTML = `
            <div class="progress-info">
                <div class="progress-name">${domain.name}</div>
                <div class="progress-detail">${domain.score}% из ${domain.target}% - ${domain.hours}ч</div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 0%"></div>
            </div>
            <div class="progress-percentage">${progressPercentage}%</div>
        `;
        
        container.appendChild(progressItem);
        
        // Animate progress bar
        setTimeout(() => {
            const progressFill = progressItem.querySelector('.progress-fill');
            if (progressFill) {
                progressFill.style.width = `${progressPercentage}%`;
            }
        }, 100 + index * 100);
    });
}

/**
 * Generate study goals
 */
function generateStudyGoals() {
    const container = document.getElementById('goals-container');
    if (!container) return;
    
    const goals = [
        {
            title: 'Улучшить знания в ортодонтии',
            description: 'Повысить уровень с 68% до 80% за 4 недели',
            deadline: '4 недели',
            progress: 25
        },
        {
            title: 'Освоить пародонтологию',
            description: 'Изучить продвинутые хирургические процедуры',
            deadline: '3 недели',
            progress: 60
        },
        {
            title: 'Подготовка к финальному тесту',
            description: 'Пройти все практические модули',
            deadline: '12 недель',
            progress: 78
        }
    ];
    
    goals.forEach((goal, index) => {
        const goalCard = document.createElement('div');
        goalCard.className = 'goal-card';
        goalCard.style.animationDelay = `${index * 0.1}s`;
        
        goalCard.innerHTML = `
            <div class="goal-header">
                <div class="goal-title">${goal.title}</div>
                <div class="goal-deadline">
                    <i class="fas fa-clock"></i> ${goal.deadline}
                </div>
            </div>
            <div class="goal-description">${goal.description}</div>
            <div class="goal-progress">
                <div class="progress-bar" style="flex: 1;">
                    <div class="progress-fill" style="width: ${goal.progress}%"></div>
                </div>
                <span style="margin-left: 12px; font-weight: 600; color: var(--primary-color);">
                    ${goal.progress}%
                </span>
            </div>
        `;
        
        container.appendChild(goalCard);
    });
}

/**
 * Update header statistics
 */
function updateHeaderStats() {
    const today = new Date();
    const examDate = studyPlan.examDate ? new Date(studyPlan.examDate) : new Date(today.getTime() + 90 * 24 * 60 * 60 * 1000);
    
    const daysToExam = Math.ceil((examDate - today) / (1000 * 60 * 60 * 24));
    
    const domains = diagnosticResults ? diagnosticResults.domains : [
        { hours: 12 }, { hours: 18 }, { hours: 24 }, { hours: 15 }, { hours: 20 }, { hours: 8 }
    ];
    const totalHours = domains.reduce((sum, domain) => sum + (domain.hours || 0), 0);
    
    const overallScore = diagnosticResults ? diagnosticResults.overallScore : 78;
    
    // Animate stats
    animateValue('days-to-exam', 0, daysToExam, 1000);
    animateValue('study-hours', 0, totalHours, 1200);
    animateValue('completion-rate', 0, overallScore, 1400, '%');
}

/**
 * Animate value changes
 */
function animateValue(elementId, start, end, duration, suffix = '') {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const startTime = performance.now();
    
    function updateValue(currentTime) {
        const elapsedTime = currentTime - startTime;
        const progress = Math.min(elapsedTime / duration, 1);
        const currentValue = Math.floor(start + (end - start) * progress);
        
        element.textContent = currentValue + suffix;
        
        if (progress < 1) {
            requestAnimationFrame(updateValue);
        }
    }
    
    requestAnimationFrame(updateValue);
}

/**
 * Bind event handlers
 */
function bindEventHandlers() {
    // Intensity selector
    document.querySelectorAll('.intensity-option').forEach(option => {
        option.addEventListener('click', function() {
            document.querySelectorAll('.intensity-option').forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
            studyPlan.intensity = this.dataset.intensity;
        });
    });

    // Form submission
    const form = document.getElementById('plan-config-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            generateStudyPlan();
        });
    }

    // Date change handlers
    const examDateInput = document.getElementById('exam-date');
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    
    if (examDateInput) examDateInput.addEventListener('change', updatePlanDates);
    if (startDateInput) startDateInput.addEventListener('change', updatePlanDates);
    if (endDateInput) endDateInput.addEventListener('change', updatePlanDates);
}

/**
 * Update plan dates
 */
function updatePlanDates() {
    const examDate = document.getElementById('exam-date')?.value;
    const startDate = document.getElementById('start-date')?.value;
    const endDate = document.getElementById('end-date')?.value;
    
    if (examDate && startDate && endDate) {
        const exam = new Date(examDate);
        const start = new Date(startDate);
        
        const daysToExam = Math.ceil((exam - start) / (1000 * 60 * 60 * 24));
        const element = document.getElementById('days-to-exam');
        if (element) {
            element.textContent = daysToExam;
        }
        
        // Update study plan
        studyPlan.examDate = examDate;
        studyPlan.startDate = startDate;
        studyPlan.endDate = endDate;
    }
}

/**
 * Generate study plan
 */
function generateStudyPlan() {
    const submitButton = document.querySelector('#plan-config-form button[type="submit"]');
    if (!submitButton) return;
    
    const originalText = submitButton.innerHTML;
    
    // Show loading state
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Plan maken...';
    submitButton.disabled = true;
    
    // Collect form data
    const formData = {
        exam_date: document.getElementById('exam-date')?.value,
        start_date: document.getElementById('start-date')?.value,
        end_date: document.getElementById('end-date')?.value,
        intensity: studyPlan.intensity,
        study_time: document.getElementById('study-time')?.value,
        diagnostic_session_id: learningPlanData?.sessionId
    };
    
    // Send request to server
    fetch('/dashboard/create-learning-plan', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update calendar with new plan
            if (calendar) {
                calendar.removeAllEvents();
                calendar.addEventSource(generateOptimizedEvents(data.plan));
            }
            
            // Show success message
            showNotification('План обучения успешно создан!', 'success');
            
            // Update goals if provided
            if (data.goals) {
                updateStudyGoals(data.goals);
            }
        } else {
            showNotification('Fout bij het maken van plan: ' + (data.message || 'Неизвестная ошибка'), 'error');
        }
    })
    .catch(error => {
        console.error('Error creating learning plan:', error);
        showNotification('Fout bij het maken van studieplan', 'error');
    })
    .finally(() => {
        // Reset button
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
    });
}

/**
 * Generate optimized events based on plan
 */
function generateOptimizedEvents(plan = null) {
    const events = [];
    const domains = diagnosticResults ? diagnosticResults.domains : [
        { name: 'Endodontics', score: 85, hours: 12 },
        { name: 'Periodontics', score: 72, hours: 18 },
        { name: 'Orthodontics', score: 68, hours: 24 },
        { name: 'Oral Surgery', score: 82, hours: 15 },
        { name: 'Prosthodontics', score: 75, hours: 20 },
        { name: 'Preventive Care', score: 88, hours: 8 }
    ];
    
    const colors = ['#3ECDC1', '#6C5CE7', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6'];
    
    const startDate = new Date(studyPlan.startDate || new Date());
    const endDate = new Date(studyPlan.endDate || new Date(startDate.getTime() + 90 * 24 * 60 * 60 * 1000));
    
    // Generate optimized schedule based on domain priorities
    let currentDate = new Date(startDate);
    let domainIndex = 0;
    
    while (currentDate <= endDate) {
        // Skip weekends if not selected
        if (currentDate.getDay() === 0 || currentDate.getDay() === 6) {
            currentDate.setDate(currentDate.getDate() + 1);
            continue;
        }
        
        const domain = domains[domainIndex % domains.length];
        const hoursPerSession = studyPlan.intensity === 'light' ? 1.5 : 
                               studyPlan.intensity === 'moderate' ? 2.5 : 4;
        
        events.push({
            title: `${domain.name} (${hoursPerSession}ч)`,
            start: currentDate.toISOString().split('T')[0],
            backgroundColor: colors[domainIndex % colors.length],
            borderColor: colors[domainIndex % colors.length],
            extendedProps: {
                domain: domain.name,
                duration: hoursPerSession,
                type: 'study',
                priority: domain.score < 75 ? 'high' : 'normal'
            }
        });
        
        domainIndex++;
        currentDate.setDate(currentDate.getDate() + 1);
    }
    
    return events;
}

/**
 * Show event details
 */
function showEventDetails(event) {
    const details = `
        <div style="padding: 20px;">
            <h3>${event.title}</h3>
            <p><strong>Домен:</strong> ${event.extendedProps.domain}</p>
            <p><strong>Продолжительность:</strong> ${event.extendedProps.duration} часов</p>
            <p><strong>Дата:</strong> ${event.start.toLocaleDateString('ru-RU')}</p>
            ${event.extendedProps.score ? `<p><strong>Текущий уровень:</strong> ${event.extendedProps.score}%</p>` : ''}
        </div>
    `;
    
    showModal('Детали занятия', details);
}

/**
 * Add study session
 */
function addStudySession(date) {
    const dateStr = date.toISOString().split('T')[0];
    const domains = diagnosticResults ? diagnosticResults.domains : [
        'Endodontics', 'Periodontics', 'Orthodontics', 'Oral Surgery', 'Prosthodontics', 'Preventive Care'
    ];
    
    const domain = prompt('Выберите домен для изучения:\n' + domains.map((d, i) => `${i + 1}. ${d.name || d}`).join('\n'));
    
    if (domain) {
        const domainIndex = parseInt(domain) - 1;
        const selectedDomain = domains[domainIndex];
        
        if (selectedDomain) {
            calendar.addEvent({
                title: `${selectedDomain.name || selectedDomain} (2ч)`,
                start: dateStr,
                backgroundColor: '#3ECDC1',
                borderColor: '#3ECDC1',
                extendedProps: {
                    domain: selectedDomain.name || selectedDomain,
                    duration: 2,
                    type: 'study'
                }
            });
        }
    }
}

/**
 * Toggle calendar view
 */
function toggleCalendarView() {
    if (!calendar) return;
    
    const currentView = calendar.view.type;
    if (currentView === 'dayGridMonth') {
        calendar.changeView('timeGridWeek');
    } else {
        calendar.changeView('dayGridMonth');
    }
}

/**
 * Show modal
 */
function showModal(title, content) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
        background: rgba(0,0,0,0.5); display: flex; align-items: center; 
        justify-content: center; z-index: 1000;
    `;
    
    modal.innerHTML = `
        <div style="background: white; border-radius: 12px; max-width: 500px; width: 90%;">
            <div style="padding: 20px; border-bottom: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0;">${title}</h3>
                <button onclick="this.closest('.modal').remove()" style="background: none; border: none; font-size: 24px; cursor: pointer;">&times;</button>
            </div>
            ${content}
        </div>
    `;
    
    modal.className = 'modal';
    document.body.appendChild(modal);
    
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed; top: 20px; right: 20px; 
        background: ${type === 'success' ? '#22c55e' : type === 'error' ? '#ef4444' : '#3ECDC1'}; 
        color: white; padding: 16px 24px; border-radius: 8px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.2); z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;
    
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 12px;">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Update study goals
 */
function updateStudyGoals(goals) {
    const container = document.getElementById('goals-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    goals.forEach((goal, index) => {
        const goalCard = document.createElement('div');
        goalCard.className = 'goal-card';
        goalCard.style.animationDelay = `${index * 0.1}s`;
        
        goalCard.innerHTML = `
            <div class="goal-header">
                <div class="goal-title">${goal.title}</div>
                <div class="goal-deadline">
                    <i class="fas fa-clock"></i> ${goal.deadline}
                </div>
            </div>
            <div class="goal-description">${goal.description}</div>
            <div class="goal-progress">
                <div class="progress-bar" style="flex: 1;">
                    <div class="progress-fill" style="width: ${goal.progress}%"></div>
                </div>
                <span style="margin-left: 12px; font-weight: 600; color: var(--primary-color);">
                    ${goal.progress}%
                </span>
            </div>
        `;
        
        container.appendChild(goalCard);
    });
}

/**
 * Export plan to iCal format
 */
function exportToICal() {
    const planId = getCurrentPlanId();
    if (!planId) {
        showNotification('Maak eerst een studieplan', 'warning');
        return;
    }
    
    // Показываем индикатор загрузки
    const button = event.target;
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Экспорт...';
    button.disabled = true;
    
    // Скачиваем iCal файл
    const link = document.createElement('a');
    link.href = `/export-plan/${planId}/ical`;
    link.download = `learning_plan_${planId}.ics`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Восстанавливаем кнопку
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
        showNotification('Календарь успешно экспортирован!', 'success');
    }, 1000);
}

/**
 * Export plan to PDF format
 */
function exportToPDF() {
    const planId = getCurrentPlanId();
    if (!planId) {
        showNotification('Maak eerst een studieplan', 'warning');
        return;
    }
    
    // Показываем индикатор загрузки
    const button = event.target;
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Экспорт...';
    button.disabled = true;
    
    // Скачиваем PDF файл
    const link = document.createElement('a');
    link.href = `/export-plan/${planId}/pdf`;
    link.download = `learning_plan_${planId}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Восстанавливаем кнопку
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
        showNotification('PDF отчет успешно экспортирован!', 'success');
    }, 2000);
}

/**
 * Get current plan ID from page data
 */
function getCurrentPlanId() {
    // Пытаемся получить ID плана из различных источников
    if (learningPlanData && learningPlanData.planId) {
        return learningPlanData.planId;
    }
    
    // Ищем в URL
    const urlParams = new URLSearchParams(window.location.search);
    const planId = urlParams.get('plan_id');
    if (planId) {
        return planId;
    }
    
    // Ищем в localStorage
    const storedPlanId = localStorage.getItem('current_plan_id');
    if (storedPlanId) {
        return storedPlanId;
    }
    
    return null;
}

/**
 * Show export buttons after plan creation
 */
function showExportButtons() {
    const exportButtons = document.getElementById('export-buttons');
    if (exportButtons) {
        exportButtons.style.display = 'block';
        exportButtons.style.animation = 'slideDown 0.3s ease-out';
    }
}

// Add CSS for notification animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style); 