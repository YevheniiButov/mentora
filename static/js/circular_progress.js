
    document.addEventListener('DOMContentLoaded', function() {
      // Устанавливаем значения прогресса для круговых индикаторов
      const progressCircles = document.querySelectorAll('.circular-progress[data-progress]');
      progressCircles.forEach(circle => {
        const progress = circle.getAttribute('data-progress') || 0;
        circle.style.setProperty('--progress', progress);
      });
      
      // Устанавливаем значения активности
      const activityCircles = document.querySelectorAll('.circular-progress[data-activity]');
      activityCircles.forEach(circle => {
        const activity = circle.getAttribute('data-activity') || 0;
        circle.style.setProperty('--activity', activity);
      });
    });
 