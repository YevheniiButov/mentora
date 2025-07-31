// Общая функция для AJAX-запросов с CSRF-защитой
function sendApiRequest(url, method, data) {
    return fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`API вернул статус ${response.status}`);
        }
        return response.json();
    });
}

// Готовые функции для работы с API
const API = {
    // Сохранение прогресса урока
    saveProgress: function(lessonId, timeSpent, completed = false) {
        return sendApiRequest(`/${currentLang}/api/save-progress`, 'POST', {
            lesson_id: lessonId,
            time_spent: timeSpent,
            completed: completed
        });
    },
    
    // Другие функции API...
};