/**
 * Синхронизация прогресса между разными вкладками
 * Слушаем пользовательские события и обновляем данные
 */

// Событие: пользователь завершил урок/сессию
document.addEventListener('progressUpdated', (e) => {
    console.log('📊 Progress updated event received:', e.detail);
    
    // Get Alpine component instance if available
    const alpineComponent = Alpine.$data(document.querySelector('[x-data]'));
    
    // Обновить вкладку Progress если она активна
    if (alpineComponent && alpineComponent.activeTab === 'progress') {
        refreshProgressTabData(alpineComponent);
    }
    
    // Обновить вкладку Individual если она активна
    if (alpineComponent && alpineComponent.activeTab === 'individual') {
        refreshIndividualPlanData(alpineComponent);
    }
});

function refreshProgressTabData(component) {
    fetch('/api/individual-plan/progress')
        .then(r => r.json())
        .then(data => {
            console.log('📈 Progress data refreshed:', data);
            
            // Update component data if available
            if (component && typeof component.loadProgressData === 'function') {
                component.loadProgressData();
            } else {
                // Fallback: manual update
                updateProgressElements(data);
            }
        })
        .catch(err => console.error('❌ Progress fetch error:', err));
}

function refreshIndividualPlanData(component) {
    // Fetch individual plan data
    fetch('/api/individual-plan/data')
        .then(r => r.json())
        .then(data => {
            console.log('📋 Individual plan refreshed:', data);
            
            // Update component data if available
            if (component && typeof component.loadIndividualPlanData === 'function') {
                component.loadIndividualPlanData();
            }
        })
        .catch(err => console.error('❌ Individual plan fetch error:', err));
}

function updateProgressElements(data) {
    // Manual DOM updates for progress elements
    const elements = {
        '.total-questions': data.total_questions_answered || 0,
        '.daily-streak': data.daily_streak || 0,
        '.overall-progress': `${Math.round(data.overall_progress || 0)}%`,
        '.questions-today': data.questions_today || 0,
        '.time-today': `${Math.round((data.time_today || 0) / 60)}h`
    };
    
    Object.entries(elements).forEach(([selector, value]) => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
            if (el.textContent !== undefined) {
                el.textContent = value;
            }
        });
    });
}

// Триггер события из других страниц
window.triggerProgressUpdate = function(stats) {
    console.log('🚀 Triggering progress update event:', stats);
    
    const event = new CustomEvent('progressUpdated', {
        detail: stats
    });
    
    document.dispatchEvent(event);
};

// Слушаем события завершения уроков
document.addEventListener('DOMContentLoaded', function() {
    // Listen for lesson completion events from lesson pages
    document.addEventListener('lessonCompleted', (e) => {
        console.log('✅ Lesson completed event:', e.detail);
        window.triggerProgressUpdate(e.detail);
    });
    
    // Listen for session completion events
    document.addEventListener('sessionCompleted', (e) => {
        console.log('✅ Session completed event:', e.detail);
        window.triggerProgressUpdate(e.detail);
    });
});
