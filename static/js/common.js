// static/js/common.js
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация круговых прогресс-баров
    initCircularProgress();
    
    // Обработчик для мобильного меню
    initMobileMenu();
  });
  
  function initCircularProgress() {
    const circles = document.querySelectorAll('.progress-circle');
    
    circles.forEach(circle => {
      const progressValue = parseInt(circle.getAttribute('data-progress') || 0);
      const radius = 45; // По умолчанию для среднего размера
      const circumference = 2 * Math.PI * radius;
      
      // Создаем SVG-элементы программно
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('viewBox', '0 0 100 100');
      
      const bgCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      bgCircle.setAttribute('class', 'progress-circle-bg');
      bgCircle.setAttribute('cx', '50');
      bgCircle.setAttribute('cy', '50');
      bgCircle.setAttribute('r', radius);
      
      const valueCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      valueCircle.setAttribute('class', 'progress-circle-value');
      valueCircle.setAttribute('cx', '50');
      valueCircle.setAttribute('cy', '50');
      valueCircle.setAttribute('r', radius);
      valueCircle.setAttribute('stroke-dasharray', circumference);
      valueCircle.setAttribute('stroke-dashoffset', circumference - (circumference * progressValue / 100));
      
      svg.appendChild(bgCircle);
      svg.appendChild(valueCircle);
      
      // Создаем текст для отображения процента
      const textElement = document.createElement('div');
      textElement.className = 'progress-circle-text';
      textElement.textContent = `${progressValue}%`;
      
      // Очищаем и добавляем новые элементы
      circle.innerHTML = '';
      circle.appendChild(svg);
      circle.appendChild(textElement);
    });
  }
  
  function initMobileMenu() {
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    if (!menuToggle) return;
    
    menuToggle.addEventListener('click', function() {
      const sidebar = document.querySelector('.sidebar');
      if (sidebar) {
        sidebar.classList.toggle('mobile-visible');
      }
    });
  }