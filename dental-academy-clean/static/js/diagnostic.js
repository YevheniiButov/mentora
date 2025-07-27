/**
 * Diagnostic Results JavaScript
 * Handles interactive elements and data visualization for diagnostic results
 */

// Initialize page when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (typeof diagnosticData !== 'undefined') {
        setTimeout(() => {
            updateOverallScore();
            generateDomainCards();
            generateRecommendations();
            animateProgressRings();
        }, 500);
    }
});

/**
 * Update overall score with animation
 */
function updateOverallScore() {
    const scoreElement = document.getElementById('overall-score');
    const badgeElement = document.getElementById('readiness-badge');
    const progressCircle = document.getElementById('progress-circle');
    
    if (!scoreElement || !diagnosticData) return;
    
    // Animate score
    let currentScore = 0;
    const targetScore = diagnosticData.overallScore || 0;
    const increment = targetScore / 50;
    
    const scoreAnimation = setInterval(() => {
        currentScore += increment;
        if (currentScore >= targetScore) {
            currentScore = targetScore;
            clearInterval(scoreAnimation);
        }
        scoreElement.textContent = Math.round(currentScore) + '%';
    }, 20);

    // Update progress circle
    if (progressCircle) {
        const circumference = 2 * Math.PI * 80;
        progressCircle.style.strokeDasharray = circumference;
        const offset = circumference - (targetScore / 100) * circumference;
        progressCircle.style.strokeDashoffset = offset;
    }

    // Update readiness badge
    if (badgeElement) {
        const readinessConfig = {
            ready: {
                icon: 'fas fa-check-circle',
                text: 'Готов к экзамену',
                class: 'readiness-ready'
            },
            almost_ready: {
                icon: 'fas fa-clock',
                text: 'Почти готов',
                class: 'readiness-almost'
            },
            in_progress: {
                icon: 'fas fa-play-circle',
                text: 'В процессе подготовки',
                class: 'readiness-progress'
            }
        };

        const readinessLevel = diagnosticData.readinessLevel || 'in_progress';
        const config = readinessConfig[readinessLevel];
        
        if (config) {
            badgeElement.innerHTML = `<i class="${config.icon}"></i>${config.text}`;
            badgeElement.className = `readiness-level ${config.class}`;
      }
    }
  }

  /**
 * Generate domain analysis cards
 */
function generateDomainCards() {
    const grid = document.getElementById('domain-grid');
    if (!grid || !diagnosticData || !diagnosticData.domains) return;
    
    diagnosticData.domains.forEach((domain, index) => {
        const card = document.createElement('div');
        card.className = 'domain-card';
        card.style.animationDelay = `${index * 0.1}s`;
        
        card.innerHTML = `
            <div class="domain-header">
                <div class="domain-name">${domain.name}</div>
                <div class="domain-score">${domain.score}%</div>
            </div>
            <div class="domain-progress">
                <div class="domain-progress-fill" style="width: 0%"></div>
            </div>
            <div class="domain-chart">
                <canvas id="chart-${domain.code}"></canvas>
            </div>
            <div class="domain-insights">
                ${domain.strengths ? domain.strengths.map(strength => 
                    `<div class="insight-item">
                        <div class="insight-icon insight-strong"><i class="fas fa-check"></i></div>
                        <span>Сильная сторона: ${strength}</span>
                    </div>`
                ).join('') : ''}
                ${domain.weaknesses ? domain.weaknesses.map(weakness => 
                    `<div class="insight-item">
                        <div class="insight-icon insight-weak"><i class="fas fa-times"></i></div>
                        <span>Требует внимания: ${weakness}</span>
                    </div>`
                ).join('') : ''}
            </div>
        `;
        
        grid.appendChild(card);
        
        // Animate progress bar
        setTimeout(() => {
            const progressFill = card.querySelector('.domain-progress-fill');
            if (progressFill) {
                progressFill.style.width = `${domain.progress || domain.score}%`;
            }
        }, 100 + index * 200);
        
        // Create chart with optimized timing
        setTimeout(() => {
            if (domain.chartData) {
                createDomainChart(domain.code, domain.chartData);
            }
        }, 50 + index * 50); // Уменьшаем задержку
    });
  }

  /**
 * Create domain chart with Chart.js
 */
function createDomainChart(domainCode, data) {
    // Проверяем, загружен ли Chart.js
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js не загружен, пропускаем создание графика');
        return;
    }
    
    const canvas = document.getElementById(`chart-${domainCode}`);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map((_, i) => `Q${i + 1}`),
            datasets: [{
                label: 'Progress',
                data: data,
                borderColor: '#3ECDC1',
                backgroundColor: 'rgba(62, 205, 193, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#3ECDC1',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 10
                        }
                    }
                },
                y: {
                    min: 0,
                    max: 100,
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    },
                    ticks: {
                        font: {
                            size: 10
                        }
                    }
                }
            },
            elements: {
                point: {
                    hoverRadius: 8
                }
            }
      }
    });
  }

  /**
 * Generate recommendations
 */
function generateRecommendations() {
    const container = document.getElementById('recommendations-content');
    if (!container || !diagnosticData || !diagnosticData.recommendations) return;
    
    diagnosticData.recommendations.forEach((rec, index) => {
        const card = document.createElement('div');
        card.className = 'recommendation-card';
        card.style.animationDelay = `${index * 0.2}s`;
        
        const priorityClass = `priority-${rec.priority}`;
        const priorityIcon = rec.priority === 'high' ? 'fas fa-exclamation-circle' : 
                           rec.priority === 'medium' ? 'fas fa-info-circle' : 'fas fa-lightbulb';
        
        const priorityText = rec.priority === 'high' ? 'Высокий приоритет' : 
                           rec.priority === 'medium' ? 'Средний приоритет' : 'Низкий приоритет';
        
        card.innerHTML = `
            <div class="recommendation-priority ${priorityClass}">
                <i class="${priorityIcon}"></i>
                ${priorityText}
            </div>
            <h3 style="font-size: 18px; font-weight: 600; margin-bottom: 12px; color: var(--text-primary);">
                ${rec.title}
            </h3>
            <p style="color: var(--text-secondary); line-height: 1.6; margin-bottom: 16px;">
                ${rec.description}
            </p>
            <div style="display: flex; align-items: center; gap: 20px; font-size: 14px;">
                <span style="color: var(--text-secondary);">
                    <i class="fas fa-clock" style="margin-right: 8px;"></i>
                    Время: ${rec.timeEstimate || '2-3 недели'}
                </span>
                <span style="color: var(--text-secondary);">
                    <i class="fas fa-book" style="margin-right: 8px;"></i>
                    Модули: ${rec.modules ? rec.modules.join(', ') : 'Рекомендуемые модули'}
                </span>
            </div>
        `;
        
        container.appendChild(card);
    });
}

/**
 * Animate progress rings and cards
 */
function animateProgressRings() {
    const cards = document.querySelectorAll('.domain-card, .recommendation-card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('slide-up');
        }, index * 100);
    });
}

/**
 * Create learning plan
 */
function createLearningPlan() {
    const button = event.target;
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Создаем план...';
    button.disabled = true;
    
    // Send request to create learning plan
    fetch('/dashboard/create-learning-plan', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: JSON.stringify({
            diagnostic_session_id: diagnosticData.sessionId
        })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
            window.location.href = data.redirect_url || '/dashboard/learning-plan';
        } else {
            alert('Ошибка при создании плана обучения: ' + (data.message || 'Неизвестная ошибка'));
            button.innerHTML = originalText;
            button.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error creating learning plan:', error);
        alert('Ошибка при создании плана обучения');
        button.innerHTML = originalText;
        button.disabled = false;
    });
}

/**
 * Download diagnostic report
 */
function downloadReport() {
    if (!diagnosticData || !diagnosticData.sessionId) {
        alert('Данные для отчета недоступны');
        return;
    }
    
    // Create report data
    const reportData = {
        session_id: diagnosticData.sessionId,
        overall_score: diagnosticData.overallScore,
        domains: diagnosticData.domains,
        recommendations: diagnosticData.recommendations,
        generated_at: new Date().toISOString()
    };
    
    // Convert to JSON and download
    const dataStr = JSON.stringify(reportData, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `diagnostic-report-${diagnosticData.sessionId}.json`;
    link.click();
}

/**
 * Share results
 */
function shareResults() {
    if (navigator.share) {
        // Use native sharing if available
        navigator.share({
            title: 'Мои результаты BIG диагностики',
            text: `Мой общий уровень подготовки: ${diagnosticData.overallScore}%`,
            url: window.location.href
        });
      } else {
        // Fallback to copying URL
        navigator.clipboard.writeText(window.location.href).then(() => {
            alert('Ссылка на результаты скопирована в буфер обмена');
        }).catch(() => {
            alert('Не удалось скопировать ссылку');
        });
    }
  }

  /**
 * Export diagnostic data for external use
 */
function exportDiagnosticData() {
    return {
        overallScore: diagnosticData.overallScore,
        readinessLevel: diagnosticData.readinessLevel,
        domains: diagnosticData.domains,
        recommendations: diagnosticData.recommendations,
        sessionId: diagnosticData.sessionId
  };
} 