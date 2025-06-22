console.log('🔍 ОТЛАДКА СТРАНИЦЫ КАРТЫ ОБУЧЕНИЯ');
console.log('=' .repeat(50));

// 1. Проверяем, что DOM загружен
console.log('📄 Состояние DOM:', document.readyState);

// 2. Ищем все элементы с классом content-category
const categoryButtons = document.querySelectorAll('.content-category');
console.log('📊 Найдено кнопок .content-category:', categoryButtons.length);

if (categoryButtons.length === 0) {
    console.log('❌ Кнопки категорий не найдены!');
    
    // Ищем альтернативные селекторы
    console.log('🔍 Поиск альтернативных селекторов...');
    console.log('   .learning-path-button:', document.querySelectorAll('.learning-path-button').length);
    console.log('   button[data-category]:', document.querySelectorAll('button[data-category]').length);
    console.log('   [data-category]:', document.querySelectorAll('[data-category]').length);
    
    // Показываем все кнопки на странице
    const allButtons = document.querySelectorAll('button');
    console.log('🔘 Все кнопки на странице:', allButtons.length);
    allButtons.forEach((btn, index) => {
        console.log(`   Кнопка ${index + 1}:`, btn.className, btn.textContent.trim());
    });
} else {
    console.log('✅ Кнопки категорий найдены!');
    categoryButtons.forEach((btn, index) => {
        const categoryId = btn.getAttribute('data-category');
        const categoryName = btn.textContent.trim();
        console.log(`   📁 Кнопка ${index + 1}: ID=${categoryId}, текст="${categoryName}"`);
        
        // Проверяем соответствующий список
        const listId = `category-${categoryId}-subcategories`;
        const list = document.getElementById(listId);
        console.log(`      📋 Список #${listId}:`, list ? 'найден' : 'НЕ НАЙДЕН');
    });
}

// 3. Ищем секцию контента
const contentSection = document.querySelector('.section-header h2');
console.log('📂 Заголовок секции контента:', contentSection ? contentSection.textContent : 'НЕ НАЙДЕН');

// 4. Проверяем структуру левой колонки
const leftColumn = document.querySelector('.left-column');
console.log('📋 Левая колонка найдена:', !!leftColumn);

if (leftColumn) {
    const learningPaths = leftColumn.querySelectorAll('.learning-paths');
    console.log('   📁 Секций .learning-paths:', learningPaths.length);
    
    learningPaths.forEach((section, index) => {
        const items = section.querySelectorAll('.learning-path-item');
        console.log(`   📁 Секция ${index + 1}: ${items.length} элементов`);
    });
}

// 5. Проверяем наличие ошибок JavaScript
console.log('⚠️ Проверьте вкладку Console на наличие ошибок JavaScript');

console.log('🎯 ИНСТРУКЦИИ:');
console.log('1. Если кнопки не найдены - проблема в HTML');
console.log('2. Если кнопки найдены, но списки нет - проблема в структуре');
console.log('3. Если всё найдено - проблема в обработчиках событий'); 