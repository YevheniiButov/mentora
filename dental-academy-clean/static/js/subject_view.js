/**
 * subject_view.js - Функциональность для страницы просмотра предметов
 * Become a Tandarts - Образовательная платформа
 */

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация компонентов страницы
    initializeComponents();
    
    // Обработчики событий
    setupEventListeners();
    
    // Загрузка начальных данных (если необходимо)
    loadInitialData();
  });
  
  /**
   * Инициализация компонентов страницы
   */
  function initializeComponents() {
    // Инициализация круговых индикаторов прогресса
    initCircularProgress();
    
    // Инициализация мобильного меню
    initMobileMenu();
    
    // Отображение хлебных крошек
    updateBreadcrumbs(getCurrentBreadcrumbs());
  }
  
  /**
   * Инициализация круговых индикаторов прогресса
   */
  function initCircularProgress() {
    const circles = document.querySelectorAll('.progress-circle');
    
    circles.forEach(circle => {
      try {
        const progressValue = parseInt(circle.getAttribute('data-progress') || 0);
        
        // Проверяем, не инициализирован ли уже
        if (circle.classList.contains('initialized')) return;
        
        // Обновляем атрибуты доступности
        circle.setAttribute('aria-valuenow', progressValue);
        
        // Создаем или находим контейнер для текста
        let textElement = circle.querySelector('.progress-circle-text');
        if (!textElement) {
          textElement = document.createElement('div');
          textElement.className = 'progress-circle-text';
          circle.appendChild(textElement);
        }
        
        // Обновляем текст
        textElement.textContent = `${progressValue}%`;
        
        // Анимация SVG (если нужна)
        let svg = circle.querySelector('svg');
        if (!svg && progressValue > 0) {
          const circleSize = circle.classList.contains('small') ? 40 : 
                           circle.classList.contains('large') ? 50 : 45;
          const circumference = 2 * Math.PI * circleSize;
          const dashOffset = circumference - (circumference * progressValue / 100);
          
          svg = document.createElement('div');
          svg.innerHTML = `
            <svg viewBox="0 0 100 100" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
              <circle class="progress-circle-bg" cx="50" cy="50" r="${circleSize}" />
              <circle 
                class="progress-circle-value" 
                cx="50" 
                cy="50" 
                r="${circleSize}"
                stroke-dasharray="${circumference}"
                stroke-dashoffset="${dashOffset}"
                style="transition: stroke-dashoffset 0.5s ease-in-out;"
              />
            </svg>
          `;
          circle.insertBefore(svg.firstElementChild, textElement);
        }
        
        // Помечаем как инициализированный
        circle.classList.add('initialized');
        
      } catch (error) {
        console.error('Error initializing circular progress:', error);
      }
    });
  }
  
  /**
   * Инициализация мобильного меню
   */
  function initMobileMenu() {
    const toggleButton = document.querySelector('.toggle-subjects');
    const leftColumn = document.querySelector('.left-column');
    
    if (toggleButton && leftColumn) {
      toggleButton.addEventListener('click', function(e) {
        e.preventDefault();
        leftColumn.classList.toggle('mobile-visible');
      });
    }
  }
  
  /**
   * Настройка обработчиков событий
   */
  function setupEventListeners() {
    // Обработка нажатия на модуль
    setupModuleClickHandlers();
    
    // Обработка нажатия на категорию
    setupCategoryClickHandlers();
    
    // Обработка нажатия на подкатегорию
    setupSubcategoryClickHandlers();
    
    // Обработка нажатия на тему
    setupTopicClickHandlers();
  }
  
  /**
   * Загрузка начальных данных
   */
  function loadInitialData() {
    // Если есть необходимость загрузить данные при инициализации
    const categoryContent = document.getElementById('category-content');
    
    if (categoryContent && window.hierarchyData) {
      // Используем предзагруженные данные из window.hierarchyData (если доступны)
      renderCategories(window.hierarchyData.categories);
    }
  }
  
  /**
   * Обработчики нажатия на модули
   */
  function setupModuleClickHandlers() {
    document.querySelectorAll('.module-button').forEach(button => {
      button.addEventListener('click', function() {
        const moduleId = this.getAttribute('data-module-id');
        if (moduleId) {
          startModule(moduleId);
        }
      });
    });
  }
  
  /**
   * Запуск модуля
   * @param {string} moduleId - ID модуля для запуска
   */
  function startModule(moduleId) {
    const currentLang = document.documentElement.lang || 'en';
    
    // Показать индикатор загрузки
    showLoadingIndicator();
    
    // Отправляем запрос к API
    fetch(`/${currentLang}/learning-map/api/start-module/${moduleId}`)
      .then(response => {
        // Проверяем, не является ли ответ перенаправлением
        if (response.redirected) {
          console.warn('API вернул перенаправление, возможно пользователь не авторизован');
          throw new Error('Перенаправление на страницу входа');
        }
        
        if (!response.ok) {
          return response.json().then(errData => {
            throw new Error(errData.message || `API вернул статус ${response.status}`);
          }).catch(() => {
            throw new Error(`API вернул статус ${response.status}`);
          });
        }
        return response.json();
      })
      .then(data => {
        if (data.success && data.redirect_url) {
          window.location.href = data.redirect_url;
        } else {
          throw new Error(data.message || 'URL перенаправления не предоставлен');
        }
      })
      .catch(error => {
        console.warn(`Ошибка API: ${error.message}. Пробуем прямую навигацию...`);
        // Пробуем прямой переход к модулю
        window.location.href = `/${currentLang}/modules/${moduleId}`;
      })
      .finally(() => {
        hideLoadingIndicator();
      });
  }
  
  /**
   * Обработчики нажатия на категории
   */
  function setupCategoryClickHandlers() {
    document.querySelectorAll('.category-card').forEach(card => {
      card.addEventListener('click', function() {
        const categoryId = this.getAttribute('data-category-id');
        const categoryName = this.getAttribute('data-category-name');
        
        if (categoryId && categoryName) {
          showCategory(categoryId, categoryName);
        }
      });
    });
  }

  /**
   * Обработчики нажатия на подкатегории
   */
  function setupSubcategoryClickHandlers() {
    // Обработчики добавляются динамически при рендеринге подкатегорий
    // в функции renderSubcategories
  }

  /**
   * Обработчики нажатия на темы
   */
  function setupTopicClickHandlers() {
    // Обработчики добавляются динамически при рендеринге тем
    // в функции renderTopics
  }
  
  /**
   * Отображение категории
   * @param {string} categoryId - ID категории
   * @param {string} categoryName - Название категории
   * @param {Event} event - Событие клика (необязательно)
   */
  function showCategory(categoryId, categoryName, event) {
    if (event) event.preventDefault();
    
    // Обновляем хлебные крошки
    updateBreadcrumbs([
      { name: 'Учебная карта', link: null },
      { name: categoryName, link: null }
    ]);
    
    // Показываем индикатор загрузки в контейнере для подкатегорий
    document.getElementById('category-content').style.display = 'none';
    document.getElementById('subcategories-section').style.display = 'block';
    document.getElementById('topics-section').style.display = 'none';
    document.getElementById('lessons-section').style.display = 'none';
    document.getElementById('virtual-patients-section').style.display = 'none';
    
    document.getElementById('subcategories-title').textContent = categoryName;
    document.getElementById('subcategories-container').innerHTML = 
      '<div class="text-center p-4"><div class="spinner"></div><p class="mt-3">Загрузка подкатегорий...</p></div>';
    
    // Проверяем, является ли это категорией Interacties & Contraindicaties
    const isInteractiesCategory = categoryName && (
      categoryName.toLowerCase().includes('interacties') || 
      categoryName.toLowerCase().includes('contraindicaties')
    );
    
    // Показываем интерактивный блок для категории Interacties & Contraindicaties
    const interactiesBlock = document.getElementById('interacties-checker-block');
    if (interactiesBlock) {
      if (isInteractiesCategory) {
        interactiesBlock.style.display = 'block';
        console.log('✅ Показан интерактивный блок для категории:', categoryName);
      } else {
        interactiesBlock.style.display = 'none';
      }
    }
    
    // Получаем текущий язык
    const currentLang = document.documentElement.lang || 'en';
    
    // Запрашиваем подкатегории через API
    fetch(`/${currentLang}/api/category/${categoryId}/subcategories`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`API вернул статус ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        renderSubcategories(data.subcategories, categoryName);
      })
      .catch(error => {
        console.error('Ошибка загрузки подкатегорий:', error);
        document.getElementById('subcategories-container').innerHTML = 
          `<div class="alert alert-danger">Ошибка загрузки подкатегорий: ${error.message}</div>`;
      });
  }
  
  /**
   * Отображение подкатегорий
   * @param {Array} subcategories - Массив подкатегорий
   * @param {string} categoryName - Название родительской категории
   */
  function renderSubcategories(subcategories, categoryName) {
    const container = document.getElementById('subcategories-container');
    container.innerHTML = '';
    
    if (!subcategories || subcategories.length === 0) {
      container.innerHTML = '<div class="alert alert-info">В этой категории нет подкатегорий</div>';
      return;
    }
    
    subcategories.forEach(subcategory => {
      const card = document.createElement('div');
      card.className = 'card subcategory-card card-hover mb-3';
      card.setAttribute('data-subcategory-id', subcategory.id);
      card.setAttribute('data-subcategory-name', subcategory.name);
      
      card.innerHTML = `
        <div class="card-body">
          <div class="d-flex align-items-center mb-2">
            <i class="bi bi-${subcategory.icon || 'bookmark'} me-2"></i>
            <h3 class="card-title mb-0">${subcategory.name}</h3>
          </div>
          ${subcategory.description ? `<p class="card-description">${subcategory.description}</p>` : ''}
          <div class="d-flex justify-content-between align-items-center mt-2">
            <span class="badge badge-secondary">${subcategory.topics_count || 0} тем</span>
            <i class="bi bi-arrow-right text-secondary"></i>
          </div>
        </div>
      `;
      
      card.addEventListener('click', function() {
        showSubcategory(subcategory.id, subcategory.name, categoryName);
      });
      
      container.appendChild(card);
    });
  }
  
  /**
   * Отображение подкатегории и её тем
   * @param {string} subcategoryId - ID подкатегории
   * @param {string} subcategoryName - Название подкатегории
   * @param {string} categoryName - Название родительской категории
   */
  function showSubcategory(subcategoryId, subcategoryName, categoryName) {
    // Обновляем хлебные крошки
    updateBreadcrumbs([
      { name: 'Учебная карта', link: goToLearningMap },
      { name: categoryName, link: function() { goBackToCategory(categoryName); } },
      { name: subcategoryName, link: null }
    ]);
    
    // Показываем индикатор загрузки в контейнере для тем
    document.getElementById('subcategories-section').style.display = 'none';
    document.getElementById('topics-section').style.display = 'block';
    document.getElementById('lessons-section').style.display = 'none';
    document.getElementById('virtual-patients-section').style.display = 'none';
    
    document.getElementById('topics-title').textContent = subcategoryName;
    document.getElementById('topics-container').innerHTML = 
      '<div class="text-center p-4"><div class="spinner"></div><p class="mt-3">Загрузка тем...</p></div>';
    
    // Получаем текущий язык
    const currentLang = document.documentElement.lang || 'en';
    
    // Запрашиваем темы через API
    fetch(`/${currentLang}/api/subcategory/${subcategoryId}/topics`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`API вернул статус ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        renderTopics(data.topics, subcategoryName, categoryName);
      })
      .catch(error => {
        console.error('Ошибка загрузки тем:', error);
        document.getElementById('topics-container').innerHTML = 
          `<div class="alert alert-danger">Ошибка загрузки тем: ${error.message}</div>`;
      });
  }
  
  /**
   * Отображение тем подкатегории
   * @param {Array} topics - Массив тем
   * @param {string} subcategoryName - Название подкатегории
   * @param {string} categoryName - Название родительской категории
   */
  function renderTopics(topics, subcategoryName, categoryName) {
    const container = document.getElementById('topics-container');
    container.innerHTML = '';
    
    if (!topics || topics.length === 0) {
      container.innerHTML = '<div class="alert alert-info">В этой подкатегории нет тем</div>';
      return;
    }
    
    topics.forEach(topic => {
      const card = document.createElement('div');
      card.className = 'card topic-card card-hover mb-3';
      card.setAttribute('data-topic-id', topic.id);
      card.setAttribute('data-topic-name', topic.name);
      
      card.innerHTML = `
        <div class="card-body">
          <h3 class="card-title">${topic.name}</h3>
          ${topic.description ? `<p class="card-description">${topic.description}</p>` : ''}
          <div class="d-flex justify-content-between align-items-center mt-3">
            <span class="badge badge-secondary">${topic.lessons_count || 0} уроков</span>
            <div class="d-flex align-items-center">
              <div class="progress-bar-container" style="width: 60px; margin-right: 8px;">
                <div class="progress-bar-fill" style="width: ${topic.progress || 0}%;"></div>
              </div>
              <span class="text-sm">${topic.progress || 0}%</span>
            </div>
          </div>
        </div>
      `;
      
      card.addEventListener('click', function() {
        loadTopic(topic.id, topic.name, subcategoryName, categoryName);
      });
      
      container.appendChild(card);
    });
  }
  
  /**
   * Загрузка уроков темы
   * @param {string} topicId - ID темы
   * @param {string} topicName - Название темы
   * @param {string} subcategoryName - Название подкатегории
   * @param {string} categoryName - Название категории
   */
  function loadTopic(topicId, topicName, subcategoryName, categoryName) {
    // Обновляем хлебные крошки
    updateBreadcrumbs([
      { name: 'Учебная карта', link: goToLearningMap },
      { name: categoryName, link: function() { goBackToCategory(categoryName); } },
      { name: subcategoryName, link: function() { goBackToSubcategory(subcategoryId, subcategoryName, categoryName); } },
      { name: topicName, link: null }
    ]);
    
    // Показываем индикатор загрузки в контейнере для уроков
    document.getElementById('topics-section').style.display = 'none';
    document.getElementById('lessons-section').style.display = 'block';
    document.getElementById('virtual-patients-section').style.display = 'none';
    
    document.getElementById('lessons-title').textContent = topicName;
    document.getElementById('lessons-container').innerHTML = 
      '<div class="text-center p-4"><div class="spinner"></div><p class="mt-3">Загрузка уроков...</p></div>';
    
    // Получаем текущий язык
    const currentLang = document.documentElement.lang || 'en';
    
    // Запрашиваем уроки через API
    fetch(`/${currentLang}/api/topic/${topicId}/lessons`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`API вернул статус ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        renderLessons(data.lessons);
      })
      .catch(error => {
        console.error('Ошибка загрузки уроков:', error);
        document.getElementById('lessons-container').innerHTML = 
          `<div class="alert alert-danger">Ошибка загрузки уроков: ${error.message}</div>`;
      });
  }
  
  /**
   * Отображение уроков
   * @param {Array} lessons - Массив уроков
   */
  function renderLessons(lessons) {
    const container = document.getElementById('lessons-container');
    container.innerHTML = '';
    
    if (!lessons || lessons.length === 0) {
      container.innerHTML = '<div class="alert alert-info">В этой теме нет уроков</div>';
      return;
    }
    
    lessons.forEach(lesson => {
      // Определяем класс и иконку для индикатора прогресса
      let statusClass = 'not-started';
      let statusIcon = 'bi-circle';
      
      if (lesson.completed) {
        statusClass = 'completed';
        statusIcon = 'bi-check-circle-fill';
      } else if (lesson.progress > 0) {
        statusClass = 'in-progress';
        statusIcon = 'bi-play-circle-fill';
      }
      
      const lessonCard = document.createElement('div');
      lessonCard.className = 'lesson-card';
      lessonCard.innerHTML = `
        <div class="lesson-info">
          <div class="lesson-title">${lesson.title}</div>
          <div class="lesson-meta">
            <span>${lesson.cards_count || 0} карточек</span>
          </div>
        </div>
        <div class="lesson-status">
          <span class="lesson-status-badge ${statusClass}">
            <i class="bi ${statusIcon} me-1"></i>
            ${lesson.completed ? 'Завершено' : 
              lesson.progress > 0 ? 'В процессе' : 'Не начато'}
          </span>
        </div>
      `;
      
      lessonCard.addEventListener('click', function() {
        startLesson(lesson.id);
      });
      
      container.appendChild(lessonCard);
    });
  }
  
  /**
   * Запуск урока
   * @param {string} lessonId - ID урока для запуска
   */
  function startLesson(lessonId) {
    const currentLang = document.documentElement.lang || 'en';
    window.location.href = `/${currentLang}/mobile/lesson/${lessonId}`;
  }
  
  /**
   * Отображение виртуальных пациентов
   * @param {Event} event - Событие клика
   */
  function showVirtualPatients(event) {
    if (event) event.preventDefault();
    
    // Обновляем хлебные крошки
    updateBreadcrumbs([
      { name: 'Учебная карта', link: goToLearningMap },
      { name: 'Виртуальные пациенты', link: null }
    ]);
    
    // Скрываем другие секции и показываем виртуальных пациентов
    document.getElementById('category-content').style.display = 'none';
    document.getElementById('subcategories-section').style.display = 'none';
    document.getElementById('topics-section').style.display = 'none';
    document.getElementById('lessons-section').style.display = 'none';
    document.getElementById('virtual-patients-section').style.display = 'block';
  }
  
  /**
   * Обновление хлебных крошек
   * @param {Array} crumbs - Массив объектов с данными для хлебных крошек
   */
  function updateBreadcrumbs(crumbs) {
    const breadcrumbs = document.getElementById('breadcrumbs');
    if (!breadcrumbs) return;
    
    breadcrumbs.innerHTML = '';
    
    crumbs.forEach((crumb, index) => {
      const crumbElement = document.createElement('span');
      crumbElement.className = 'crumb';
      
      if (crumb.link) {
        const link = document.createElement('a');
        link.href = '#';
        link.textContent = crumb.name;
        link.onclick = function(e) {
          e.preventDefault();
          crumb.link();
        };
        crumbElement.appendChild(link);
      } else {
        crumbElement.textContent = crumb.name;
        crumbElement.classList.add('active');
      }
      
      breadcrumbs.appendChild(crumbElement);
      
      // Добавляем разделитель, если это не последний элемент
      if (index < crumbs.length - 1) {
        const separator = document.createElement('span');
        separator.className = 'separator';
        separator.textContent = '/';
        breadcrumbs.appendChild(separator);
      }
    });
  }
  
  /**
   * Получение текущего состояния хлебных крошек
   * @returns {Array} Массив объектов для хлебных крошек
   */
  function getCurrentBreadcrumbs() {
    // По умолчанию возвращаем основные хлебные крошки
    return [{ name: 'Учебная карта', link: null }];
  }
  
  /**
   * Возврат к карте обучения
   */
  function goToLearningMap() {
    // Скрываем интерактивный блок при возврате на главную карту
    const interactiesBlock = document.getElementById('interacties-checker-block');
    if (interactiesBlock) {
      interactiesBlock.style.display = 'none';
    }
    
    const currentLang = document.documentElement.lang || 'en';
    window.location.href = `/${currentLang}/learning-map`;
  }
  
  /**
   * Возврат к категории
   * @param {string} categoryName - Название категории
   */
  function goBackToCategory(categoryName) {
    // Находим категорию по имени и отображаем её
    const categoryCard = document.querySelector(`.category-card[data-category-name="${categoryName}"]`);
    if (categoryCard) {
      const categoryId = categoryCard.getAttribute('data-category-id');
      showCategory(categoryId, categoryName);
    } else {
      // Если карточка не найдена, просто показываем список категорий
      document.getElementById('subcategories-section').style.display = 'none';
      document.getElementById('topics-section').style.display = 'none';
      document.getElementById('lessons-section').style.display = 'none';
      document.getElementById('virtual-patients-section').style.display = 'none';
      document.getElementById('category-content').style.display = 'block';
      
      // Скрываем интерактивный блок при возврате к списку категорий
      const interactiesBlock = document.getElementById('interacties-checker-block');
      if (interactiesBlock) {
        interactiesBlock.style.display = 'none';
      }
    }
  }
  
  /**
   * Возврат к подкатегории
   * @param {string} subcategoryId - ID подкатегории
   * @param {string} subcategoryName - Название подкатегории
   * @param {string} categoryName - Название категории
   */
  function goBackToSubcategory(subcategoryId, subcategoryName, categoryName) {
    showSubcategory(subcategoryId, subcategoryName, categoryName);
  }
  
  /**
   * Отображение индикатора загрузки
   */
  function showLoadingIndicator() {
    // Создаем или отображаем глобальный индикатор загрузки
    let loader = document.getElementById('global-loader');
    
    if (!loader) {
      loader = document.createElement('div');
      loader.id = 'global-loader';
      loader.className = 'global-loader';
      loader.innerHTML = '<div class="spinner"></div>';
      document.body.appendChild(loader);
    }
    
    loader.style.display = 'flex';
  }
  
  /**
   * Скрытие индикатора загрузки
   */
  function hideLoadingIndicator() {
    const indicator = document.querySelector('.loading-indicator');
    if (indicator) {
      indicator.style.display = 'none';
    }
  }
  
  /**
   * Обновление статистики прогресса
   * @param {Object} newData - Новые данные статистики
   */
  function updateProgressStats(newData) {
    if (newData.overall_progress !== undefined) {
      const progressCircle = document.querySelector('[data-progress]');
      if (progressCircle) {
        progressCircle.setAttribute('data-progress', newData.overall_progress);
        progressCircle.setAttribute('aria-valuenow', newData.overall_progress);
        progressCircle.classList.remove('initialized'); // Сбрасываем флаг
        initCircularProgress(); // Переинициализируем
      }
    }
  }

  // Безопасная инициализация при загрузке
  document.addEventListener('DOMContentLoaded', function() {
    initCircularProgress();
  });
  
  // Экспортируем функции для использования в других модулях
  window.updateProgressStats = updateProgressStats;
  window.initCircularProgress = initCircularProgress;