class CardsNavigator {
    constructor(cardsContainer, cards) {
        this.cardsContainer = cardsContainer;
        this.cards = cards;
        this.currentIndex = 0;
        this.totalCards = cards.length;
        this.startTime = Date.now(); // Отслеживаем время начала изучения
        
        this.init();
    }
    
    init() {
        this.createNavigationUI();
        this.showCard(0);
        this.updateProgress();
        this.addKeyboardNavigation();
    }
    
    createNavigationUI() {
        // Создаем контейнер для навигации
        const navigationContainer = document.createElement('div');
        navigationContainer.className = 'cards-navigation mt-4';
        
        // Индикатор прогресса
        const progressContainer = document.createElement('div');
        progressContainer.className = 'progress-container mb-3';
        progressContainer.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="progress-text">Карточка <span id="current-card-number">1</span> из <span id="total-cards">${this.totalCards}</span></span>
                <span class="progress-percentage" id="progress-percentage">0%</span>
            </div>
            <div class="progress">
                <div class="progress-bar" id="progress-bar" role="progressbar" style="width: 0%"></div>
            </div>
            <small class="text-muted mt-2 d-block">
                <i class="bi bi-keyboard"></i> Используйте стрелки ← → для навигации, Home/End для перехода к началу/концу
            </small>
        `;
        
        // Кнопки навигации
        const navigationButtons = document.createElement('div');
        navigationButtons.className = 'navigation-buttons d-flex justify-content-between align-items-center';
        navigationButtons.innerHTML = `
            <button class="btn btn-outline-primary" id="prev-card" disabled>
                <i class="bi bi-chevron-left"></i> Предыдущая
            </button>
            <button class="btn btn-outline-primary" id="next-card">
                Следующая <i class="bi bi-chevron-right"></i>
            </button>
        `;
        
        navigationContainer.appendChild(progressContainer);
        navigationContainer.appendChild(navigationButtons);
        
        // Вставляем навигацию после контейнера с карточками
        this.cardsContainer.parentNode.insertBefore(navigationContainer, this.cardsContainer.nextSibling);
        
        // Добавляем обработчики событий
        document.getElementById('prev-card').addEventListener('click', () => this.previousCard());
        // Обработчик для next-card будет устанавливаться динамически в updateNavigationButtons
        
        // Сохраняем ссылки на элементы
        this.navigationContainer = navigationContainer;
        this.prevButton = document.getElementById('prev-card');
        this.nextButton = document.getElementById('next-card');
        this.currentCardNumber = document.getElementById('current-card-number');
        this.totalCardsElement = document.getElementById('total-cards');
        this.progressPercentage = document.getElementById('progress-percentage');
        this.progressBar = document.getElementById('progress-bar');
    }
    
    showCard(index) {
        // Скрываем все карточки
        this.cards.forEach((card, i) => {
            if (i === index) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
        
        this.currentIndex = index;
        this.updateNavigationButtons();
        this.updateProgress();
    }
    
    previousCard() {
        if (this.currentIndex > 0) {
            this.showCard(this.currentIndex - 1);
        }
    }
    
    nextCard() {
        if (this.currentIndex < this.totalCards - 1) {
            this.showCard(this.currentIndex + 1);
        }
    }
    
    updateNavigationButtons() {
        this.prevButton.disabled = this.currentIndex === 0;
        // Кнопка "Следующая/Завершить" всегда активна
        this.nextButton.disabled = false;
        
        // Обновляем текст кнопки "Следующая" на "Завершить" для последней карточки
        if (this.currentIndex === this.totalCards - 1) {
            this.nextButton.innerHTML = 'Завершить <i class="bi bi-check-circle"></i>';
            this.nextButton.className = 'btn btn-success';
            this.nextButton.onclick = () => this.completeLesson();
        } else {
            this.nextButton.innerHTML = 'Следующая <i class="bi bi-chevron-right"></i>';
            this.nextButton.className = 'btn btn-outline-primary';
            this.nextButton.onclick = () => this.nextCard();
        }
    }
    
    completeLesson() {
        // Получаем CSRF токен из мета-тега
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
        
        // Получаем ID урока из URL
        const lessonId = window.location.pathname.split('/').pop();
        
        fetch(`/content/api/lesson/${lessonId}/complete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Показываем экран завершения
                this.showCompletionScreen();
            } else {
                this.showNotification('Ошибка: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.showNotification('Произошла ошибка при завершении урока', 'error');
        });
    }
    
    showNotification(message, type) {
        // Определяем класс для типа уведомления
        let alertClass = 'alert-info';
        if (type === 'success') alertClass = 'alert-success';
        else if (type === 'error') alertClass = 'alert-danger';
        else if (type === 'warning') alertClass = 'alert-warning';
        
        // Создаем уведомление
        const notification = document.createElement('div');
        notification.className = `${alertClass} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Автоматически удаляем через 5 секунд
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
    
    updateProgress() {
        const percentage = Math.round(((this.currentIndex + 1) / this.totalCards) * 100);
        
        this.currentCardNumber.textContent = this.currentIndex + 1;
        this.totalCardsElement.textContent = this.totalCards;
        this.progressPercentage.textContent = percentage + '%';
        this.progressBar.style.width = percentage + '%';
    }
    
    addKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // Проверяем, что фокус не находится в поле ввода
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                return;
            }
            
            switch(e.key) {
                case 'ArrowLeft':
                    e.preventDefault();
                    if (this.currentIndex > 0) {
                        this.previousCard();
                    }
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    if (this.currentIndex < this.totalCards - 1) {
                        this.nextCard();
                    }
                    break;
                case 'Home':
                    e.preventDefault();
                    this.showCard(0);
                    break;
                case 'End':
                    e.preventDefault();
                    this.showCard(this.totalCards - 1);
                    break;
            }
        });
    }
    
    showCompletionScreen() {
        // Создаем экран завершения
        const completionScreen = document.createElement('div');
        completionScreen.className = 'completion-screen';
        completionScreen.innerHTML = `
            <div class="completion-content">
                <div class="completion-icon">
                    <i class="bi bi-check-circle-fill"></i>
                </div>
                <h2>Урок завершен!</h2>
                <p>Поздравляем! Вы успешно изучили все карточки в этом уроке.</p>
                
                <div class="completion-stats">
                    <div class="stat-item">
                        <i class="bi bi-card-text"></i>
                        <span>Изучено карточек: ${this.totalCards}</span>
                    </div>
                    <div class="stat-item">
                        <i class="bi bi-clock"></i>
                        <span>Время изучения: <span id="time-spent">${this.calculateTimeSpent()}</span></span>
                    </div>
                </div>
                
                <div class="completion-actions">
                    <button class="btn btn-outline-primary" id="next-lesson-btn">
                        <i class="bi bi-arrow-right"></i> Следующий урок
                    </button>
                    <button class="btn btn-primary" id="repeat-lesson-btn">
                        <i class="bi bi-arrow-clockwise"></i> Повторить урок
                    </button>
                    <button class="btn btn-secondary" id="go-topics-btn">
                        <i class="bi bi-list"></i> К списку тем
                    </button>
                    <button class="btn btn-outline-secondary" id="close-completion-btn">
                        <i class="bi bi-x"></i> Закрыть
                    </button>
                </div>
            </div>
        `;
        
        // Скрываем основной контент
        const mainContent = document.querySelector('.container');
        if (mainContent) {
            mainContent.style.display = 'none';
        }
        
        // Добавляем экран завершения
        document.body.appendChild(completionScreen);
        
        // Добавляем обработчики событий для кнопок
        document.getElementById('next-lesson-btn').addEventListener('click', () => this.goToNextLesson());
        document.getElementById('repeat-lesson-btn').addEventListener('click', () => this.repeatLesson());
        document.getElementById('go-topics-btn').addEventListener('click', () => this.goToTopics());
        document.getElementById('close-completion-btn').addEventListener('click', () => this.closeCompletionScreen());
        
        // Добавляем возможность закрыть экран по клику вне контента
        completionScreen.addEventListener('click', (e) => {
            if (e.target === completionScreen) {
                this.closeCompletionScreen();
            }
        });
        
        // Добавляем возможность закрыть по Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeCompletionScreen();
            }
        });
    }
    
    closeCompletionScreen() {
        const completionScreen = document.querySelector('.completion-screen');
        if (completionScreen) {
            completionScreen.remove();
        }
        
        // Показываем основной контент обратно
        const mainContent = document.querySelector('.container');
        if (mainContent) {
            mainContent.style.display = 'block';
        }
    }
    
    calculateTimeSpent() {
        const timeSpent = Math.floor((Date.now() - this.startTime) / 1000 / 60); // в минутах
        return `${Math.max(1, timeSpent)} мин`;
    }
    
    goToNextLesson() {
        // Получаем ID урока из URL
        const lessonId = window.location.pathname.split('/').pop();
        
        // Показываем состояние загрузки
        const nextButton = document.querySelector('.completion-actions .btn-outline-primary');
        if (nextButton) {
            nextButton.innerHTML = '<i class="bi bi-hourglass-split"></i> Загрузка...';
            nextButton.disabled = true;
        }
        
        // Запрашиваем следующий урок
        fetch(`/content/api/lesson/${lessonId}/next`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.next_lesson) {
                    // Переходим к следующему уроку
                    window.location.href = data.next_lesson.url;
                } else {
                    // Если нет следующего урока, показываем уведомление
                    this.showNotification(data.message || 'Это был последний урок в теме', 'info');
                    
                    // Возвращаем кнопку в исходное состояние
                    if (nextButton) {
                        nextButton.innerHTML = '<i class="bi bi-arrow-right"></i> Следующий урок';
                        nextButton.disabled = false;
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                this.showNotification('Ошибка при получении следующего урока', 'error');
                
                // Возвращаем кнопку в исходное состояние
                if (nextButton) {
                    nextButton.innerHTML = '<i class="bi bi-arrow-right"></i> Следующий урок';
                    nextButton.disabled = false;
                }
            });
    }
    
    repeatLesson() {
        // Перезагружаем страницу для повторного изучения
        location.reload();
    }
    
    goToTopics() {
        // Возвращаемся к списку тем
        const currentUrl = window.location.pathname;
        const urlParts = currentUrl.split('/');
        
        // Убираем ID урока и возвращаемся к теме
        if (urlParts.length >= 6) {
            const topicUrl = urlParts.slice(0, -1).join('/');
            window.location.href = topicUrl;
        } else {
            // Если не можем определить URL темы, возвращаемся к категориям
            window.location.href = '/content';
        }
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    const cardsContainer = document.querySelector('.cards-container');
    if (cardsContainer) {
        const cards = Array.from(cardsContainer.children);
        if (cards.length > 1) {
            new CardsNavigator(cardsContainer, cards);
        }
    }
}); 