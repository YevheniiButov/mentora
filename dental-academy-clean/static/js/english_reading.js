// English Reading Practice - IELTS Academic Reading
// static/js/english_reading.js

let startTime = Date.now();
let passageId = null;
let questions = [];

// Get passage ID from page
document.addEventListener('DOMContentLoaded', function() {
    const passageTitleEl = document.getElementById('passageTitle');
    if (passageTitleEl && passageTitleEl.dataset.passageId) {
        passageId = parseInt(passageTitleEl.dataset.passageId);
    } else if (typeof window.passageId !== 'undefined') {
        passageId = window.passageId;
    } else {
        // Try to get from URL
        const urlParams = new URLSearchParams(window.location.search);
        passageId = urlParams.get('passage_id') || null;
    }
    
    // Load questions when passage ID is available
    if (passageId) {
        loadQuestions();
    }
});

// Timer
setInterval(() => {
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    const timerEl = document.getElementById('timer');
    if (timerEl) {
        timerEl.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
}, 1000);

// Load questions
async function loadQuestions() {
    if (!passageId) {
        console.error('Passage ID not found');
        return;
    }
    
    try {
        const response = await fetch(`/api/english/passage/${passageId}`);
        if (!response.ok) {
            throw new Error('Failed to load questions');
        }
        
        const data = await response.json();
        questions = data.questions || [];
        
        // Update passage image if available
        if (data.passage && data.passage.image_url) {
            const passageImageEl = document.getElementById('passageImage');
            if (passageImageEl) {
                passageImageEl.src = data.passage.image_url;
                passageImageEl.style.display = 'block';
            } else {
                // Create image element if it doesn't exist
                const passageSection = document.querySelector('.passage-section');
                const passageTitle = document.getElementById('passageTitle');
                if (passageSection && passageTitle) {
                    const img = document.createElement('img');
                    img.src = data.passage.image_url;
                    img.alt = data.passage.title;
                    img.className = 'passage-image';
                    img.id = 'passageImage';
                    passageTitle.insertAdjacentElement('afterend', img);
                }
            }
        }
        
        const container = document.getElementById('questionsContainer');
        if (!container) return;
        
        container.innerHTML = '';
        
        questions.forEach(q => {
            const questionDiv = document.createElement('div');
            questionDiv.className = 'question-item';
            
            if (q.question_type === 'multiple_choice') {
                const options = q.options || {};
                questionDiv.innerHTML = `
                    <p><strong>Q${q.question_number || q.id}.</strong> ${q.question_text}</p>
                    ${Object.entries(options).map(([key, value]) => `
                        <label>
                            <input type="radio" name="q${q.id}" value="${key}">
                            <span>${key}. ${value}</span>
                        </label>
                    `).join('')}
                `;
            } else if (q.question_type === 'fill_blank') {
                questionDiv.innerHTML = `
                    <p><strong>Q${q.question_number || q.id}.</strong> ${q.question_text}</p>
                    <input type="text" class="fill-blank-input" data-question-id="${q.id}" placeholder="Enter your answer">
                `;
            } else if (q.question_type === 'true_false_ng') {
                questionDiv.innerHTML = `
                    <p><strong>Q${q.question_number || q.id}.</strong> ${q.question_text}</p>
                    <label><input type="radio" name="q${q.id}" value="TRUE"> TRUE</label>
                    <label><input type="radio" name="q${q.id}" value="FALSE"> FALSE</label>
                    <label><input type="radio" name="q${q.id}" value="NOT GIVEN"> NOT GIVEN</label>
                `;
            } else if (q.question_type === 'matching') {
                // For matching questions, display options
                const options = q.options || {};
                questionDiv.innerHTML = `
                    <p><strong>Q${q.question_number || q.id}.</strong> ${q.question_text}</p>
                    ${Object.entries(options).map(([key, value]) => `
                        <label>
                            <input type="radio" name="q${q.id}" value="${key}">
                            <span>${key}. ${value}</span>
                        </label>
                    `).join('')}
                `;
            }
            
            container.appendChild(questionDiv);
        });
    } catch (error) {
        console.error('Error loading questions:', error);
        const container = document.getElementById('questionsContainer');
        if (container) {
            container.innerHTML = '<p class="text-danger">Error loading questions. Please refresh the page.</p>';
        }
    }
}

// Submit answers
document.addEventListener('DOMContentLoaded', function() {
    const submitBtn = document.getElementById('submitBtn');
    if (submitBtn) {
        submitBtn.addEventListener('click', async () => {
            if (!passageId) {
                alert('Passage ID not found. Please refresh the page.');
                return;
            }
            
            const answers = {};
            
            questions.forEach(q => {
                if (q.question_type === 'fill_blank') {
                    const input = document.querySelector(`input[data-question-id="${q.id}"]`);
                    if (input) {
                        answers[q.id] = input.value.trim();
                    }
                } else {
                    const selected = document.querySelector(`input[name="q${q.id}"]:checked`);
                    if (selected) {
                        answers[q.id] = selected.value;
                    } else {
                        answers[q.id] = '';
                    }
                }
            });
            
            const timeSpent = Math.floor((Date.now() - startTime) / 1000);
            
            try {
                const response = await fetch('/api/english/submit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({
                        passage_id: passageId,
                        answers: answers,
                        time_spent: timeSpent
                    })
                });
                
                if (!response.ok) {
                    throw new Error('Failed to submit answers');
                }
                
                const results = await response.json();
                showResults(results);
            } catch (error) {
                console.error('Error submitting answers:', error);
                alert('Error submitting answers. Please try again.');
            }
        });
    }
    
    // Load questions when page loads
    loadQuestions();
});

function getCsrfToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.getAttribute('content') : '';
}

function showResults(results) {
    const modal = document.getElementById('resultsModal');
    const content = document.getElementById('resultsContent');
    
    if (!modal || !content) return;
    
    content.innerHTML = `
        <div class="score-display">
            <h3>${results.score || 0} / ${results.total || 0}</h3>
            <p>${results.percentage || 0}%</p>
            ${results.estimated_band ? `<p>Estimated Band: ${results.estimated_band}</p>` : ''}
            ${results.xp_earned ? `<p class="xp-earned">+${results.xp_earned} XP</p>` : ''}
        </div>
        <div class="results-details">
            ${(results.results || []).map((r, i) => `
                <div class="result-item ${r.correct ? 'correct' : 'incorrect'}">
                    <p><strong>Q${i+1}:</strong> ${r.correct ? '✓ Correct' : '✗ Incorrect'}</p>
                    ${!r.correct ? `
                        <p>Your answer: ${r.user_answer || 'No answer'}</p>
                        <p>Correct answer: ${r.correct_answer || 'N/A'}</p>
                        ${r.explanation ? `<p class="explanation">${r.explanation}</p>` : ''}
                    ` : ''}
                </div>
            `).join('')}
        </div>
    `;
    
    modal.style.display = 'flex';
}

