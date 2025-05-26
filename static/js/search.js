// search.js

// Функция для поиска в иерархии обучения
async function searchLearningContent(query) {
    if (!query || query.length < 2) {
        hideSearchResults();
        return;
    }
    
    try {
        const response = await fetch(`/${currentLang}/api/search?q=${encodeURIComponent(query)}`);
        if (!response.ok) {
            throw new Error(`Search API returned status ${response.status}`);
        }
        
        const results = await response.json();
        displaySearchResults(results);
        
    } catch (error) {
        console.error('Error during search:', error);
        showSearchError('An error occurred during search. Please try again.');
    }
}

// Отображение результатов поиска
function displaySearchResults(results) {
    const resultsContainer = document.getElementById('search-results');
    resultsContainer.innerHTML = '';
    
    if (results.length === 0) {
        resultsContainer.innerHTML = `
            <div class="empty-search-results">
                <p>No results found for your query</p>
            </div>
        `;
        return;
    }
    
    const categorizedResults = {
        categories: results.filter(r => r.type === 'category'),
        subcategories: results.filter(r => r.type === 'subcategory'),
        topics: results.filter(r => r.type === 'topic'),
        lessons: results.filter(r => r.type === 'lesson')
    };
    
    // Создаем разделы результатов для каждого типа
    for (const [type, items] of Object.entries(categorizedResults)) {
        if (items.length === 0) continue;
        
        const section = document.createElement('div');
        section.className = 'search-result-section';
        section.innerHTML = `<h3>${type.charAt(0).toUpperCase() + type.slice(1)}</h3>`;
        
        const list = document.createElement('ul');
        items.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `
                <a href="javascript:void(0)" onclick="navigateToSearchResult('${type}', ${item.id})">
                    <i class="bi bi-${item.icon || 'arrow-right'}"></i>
                    <span>${item.name}</span>
                </a>
            `;
            list.appendChild(li);
        });
        
        section.appendChild(list);
        resultsContainer.appendChild(section);
    }
    
    // Показываем контейнер результатов
    resultsContainer.style.display = 'block';
}

// Навигация к результату поиска
function navigateToSearchResult(type, id) {
    // Скрываем результаты поиска
    hideSearchResults();
    
    // Навигация в зависимости от типа
    switch (type) {
        case 'category':
            // Раскрываем категорию
            const categoryElement = document.getElementById(`category-${id}`);
            if (categoryElement) {
                toggleCategory(`category-${id}`, true); // force open
            }
            break;
            
        case 'subcategory':
            // Находим родительскую категорию и раскрываем подкатегорию
            const subcategoryElement = document.getElementById(`subcat-${id}`);
            if (subcategoryElement) {
                // Находим родительскую категорию
                const parentCategory = subcategoryElement.closest('.main-category');
                if (parentCategory) {
                    toggleCategory(parentCategory.id, true); // force open
                }
                toggleSubcategory(`subcat-${id}`, true); // force open
            }
            break;
            
        case 'topic':
            // Загружаем тему напрямую
            loadTopic(id, '');
            break;
            
        case 'lesson':
            // Переходим к уроку
            startLesson(id);
            break;
    }
}