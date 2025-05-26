// Инициализация интерактивного режима обучения
function initInteractiveLearning() {
    // Элементы интерфейса
    const contentItems = document.querySelectorAll('.content-item');
    const progressBar = document.getElementById('progress-bar');
    const currentItemElement = document.getElementById('current-item');
    const progressPercentElement = document.getElementById('progress-percent');
    
    // Текущий индекс
    let currentIndex = 0;
    
    // Общее количество элементов
    const totalItems = contentItems.length;
    
    // Функция для обновления прогресс-бара
    function updateProgress(index) {
        const percent = Math.round(((index + 1) / totalItems) * 100);
        progressBar.style.width = percent + '%';
        currentItemElement.textContent = index + 1;
        progressPercentElement.textContent = percent + '%';
    }
    
    // Функция для отображения элемента по индексу
    window.showItem = function(index) {
        // Скрываем все элементы
        contentItems.forEach(item => {
            item.classList.remove('active');
        });
        
        // Отображаем нужный элемент
        contentItems[index].classList.add('active');
        
        // Обновляем прогресс
        updateProgress(index);
        
        // Сохраняем текущий индекс
        currentIndex = index;
        
        // Настройка кнопок для тестов
        const currentItem = contentItems[index];
        if (currentItem.dataset.type === 'test') {
            const testContent = currentItem.querySelector('.test-content');
            const checkButton = currentItem.querySelector('.check-btn');
            const nextButton = currentItem.querySelector('.next-btn');
            
            if (testContent && testContent.dataset.answered === 'false') {
                checkButton.style.display = 'inline-block';
                nextButton.style.display = 'none';
            } else {
                checkButton.style.display = 'none';
                nextButton.style.display = 'inline-block';
            }
        }
        
        // Сохраняем прогресс на сервере
        const lessonId = currentItem.dataset.lessonId;
        if (lessonId) {
            saveProgress(lessonId);
        }
    };
    
    // Функция для сохранения прогресса
    function saveProgress(lessonId) {
        const moduleId = document.querySelector('[data-module-id]').dataset.moduleId;
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
        
        fetch(`/api/progress/${lessonId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                'time_spent': 5.0,
                'completed': true
            })
        })
        .then(response => response.json())
        .then(data => console.log('Progress saved:', data))
        .catch(error => console.error('Error saving progress:', error));
    }
    
    // Обработчики кнопок
    initNavButtons();
    initTestOptions();
    
    // Показываем первый элемент и устанавливаем прогресс
    updateProgress(0);
}

// Инициализация кнопок навигации
function initNavButtons() {
    // Обработчики для кнопок "Предыдущий"
    document.querySelectorAll('.prev-btn').forEach(button => {
        button.addEventListener('click', function() {
            const currentIndex = getCurrentIndex();
            if (currentIndex > 0) {
                showItem(currentIndex - 1);
            }
        });
    });
    
    // Обработчики для кнопок "Следующий"
    document.querySelectorAll('.next-btn').forEach(button => {
        button.addEventListener('click', function() {
            const currentIndex = getCurrentIndex();
            const totalItems = document.querySelectorAll('.content-item').length;
            if (currentIndex < totalItems - 1) {
                showItem(currentIndex + 1);
            }
        });
    });
    
    // Обработчики для кнопок "Проверить"
    document.querySelectorAll('.check-btn').forEach(button => {
        button.addEventListener('click', function() {
            const contentItem = this.closest('.content-item');
            const testContent = contentItem.querySelector('.test-content');
            const options = contentItem.querySelectorAll('.test-option');
            const explanation = contentItem.querySelector('.explanation');
            const selectedOption = contentItem.querySelector('.test-option.selected');
            
            // Проверяем, выбран ли вариант ответа
            if (!selectedOption) {
                alert('Please select an answer option');
                return;
            }
            
            // Отмечаем, что тест отвечен
            testContent.dataset.answered = 'true';
            
            // Показываем правильные/неправильные ответы
            options.forEach(option => {
                if (option.dataset.correct === 'true') {
                    option.classList.add('correct');
                    option.innerHTML += ' <i class="bi bi-check-circle-fill text-success float-end"></i>';
                } else if (option.classList.contains('selected')) {
                    option.classList.add('incorrect');
                    option.innerHTML += ' <i class="bi bi-x-circle-fill text-danger float-end"></i>';
                }
                
                // Делаем опции некликабельными
                option.style.pointerEvents = 'none';
            });
            
            // Показываем объяснение
            if (explanation) {
                explanation.classList.add('visible');
            }
            
            // Скрываем кнопку проверки и показываем кнопку "Далее"
            this.style.display = 'none';
            contentItem.querySelector('.next-btn').style.display = 'inline-block';
        });
    });
}

// Инициализация тестовых вопросов
function initTestOptions() {
    // Обработчики для вариантов ответов тестов
    document.querySelectorAll('.test-option').forEach(option => {
        option.addEventListener('click', function() {
            // Проверяем, не был ли уже дан ответ
            const testContent = this.closest('.test-content');
            if (testContent && testContent.dataset.answered === 'true') {
                return;
            }
            
            // Снимаем выделение со всех вариантов
            const allOptions = this.closest('.options').querySelectorAll('.test-option');
            allOptions.forEach(opt => opt.classList.remove('selected'));
            
            // Выделяем выбранный вариант
            this.classList.add('selected');
        });
    });
}

// Получение текущего индекса
function getCurrentIndex() {
    const activeItem = document.querySelector('.content-item.active');
    return activeItem ? parseInt(activeItem.dataset.index) : 0;
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initInteractiveLearning();
});