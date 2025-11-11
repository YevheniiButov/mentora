// English Reading Practice - Enhanced Reading Comprehension
// static/js/english_reading.js
// NEW VERSION with all features: vocabulary tooltips, text highlighting, explanations, spaced repetition

let startTime = Date.now();
let passageId = null;
let lessonData = null;
let questions = [];
let vocabulary = [];
let paragraphs = [];
let userAnswers = {};
let currentQuestionFilter = 'all';
let vocabularySidebarOpen = true;

// Get passage ID from page
document.addEventListener('DOMContentLoaded', function() {
    const passageTitleEl = document.getElementById('passageTitle');
    if (passageTitleEl && passageTitleEl.dataset.passageId) {
        passageId = parseInt(passageTitleEl.dataset.passageId);
    } else if (typeof window.passageId !== 'undefined') {
        passageId = window.passageId;
    } else {
        const urlParams = new URLSearchParams(window.location.search);
        passageId = urlParams.get('passage_id') || null;
    }
    
    if (passageId) {
        loadLesson();
    }
    
    // Initialize vocabulary sidebar toggle
    const vocabToggle = document.getElementById('vocabToggle');
    if (vocabToggle) {
        vocabToggle.addEventListener('click', toggleVocabularySidebar);
    }
    
    // Initialize question filters
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const filter = e.target.dataset.filter;
            setQuestionFilter(filter);
        });
    });
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

// Load lesson with full format
async function loadLesson() {
    if (!passageId) {
        console.error('Passage ID not found');
        return;
    }
    
    try {
        // Request full format
        const response = await fetch(`/api/english/passage/${passageId}?format=full`, {
            headers: {
                'X-Use-Full-Format': 'true'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load lesson');
        }
        
        const data = await response.json();
        
        // Check if we got full format or old format
        if (data.lesson) {
            // New format
            lessonData = data.lesson;
            questions = lessonData.questions || [];
            vocabulary = lessonData.vocabulary || [];
            paragraphs = lessonData.paragraphs || [];
            
            renderLesson();
        } else if (data.passage) {
            // Old format - fallback
            console.warn('Using old format, some features may not be available');
            questions = data.questions || [];
            renderOldFormat(data.passage, questions);
        }
        
    } catch (error) {
        console.error('Error loading lesson:', error);
        const container = document.getElementById('questionsContainer');
        if (container) {
            container.innerHTML = '<p class="text-danger">Error loading lesson. Please refresh the page.</p>';
        }
    }
}

// Render lesson with all new features
function renderLesson() {
    if (!lessonData) return;
    
    // Update title
    const titleEl = document.getElementById('lessonTitle');
    if (titleEl) titleEl.textContent = lessonData.title;
    
    const passageTitleEl = document.getElementById('passageTitle');
    if (passageTitleEl) passageTitleEl.textContent = lessonData.title;
    
    // Update image
    if (lessonData.imageUrl) {
        const imgEl = document.getElementById('passageImage');
        if (imgEl) {
            imgEl.src = lessonData.imageUrl;
            imgEl.style.display = 'block';
        }
    }
    
    // Update estimated time
    const estimatedTimeEl = document.getElementById('estimatedTime');
    if (estimatedTimeEl && lessonData.estimatedTime) {
        estimatedTimeEl.textContent = `~${lessonData.estimatedTime} min`;
    }
    
    // Render paragraphs with highlighting support
    renderParagraphs();
    
    // Render vocabulary sidebar
    renderVocabulary();
    
    // Render questions
    renderQuestions();
    
    // Update progress
    updateProgress();
}

// Render paragraphs with support for highlighting
function renderParagraphs() {
    const container = document.getElementById('paragraphsContainer');
    if (!container) return;
    
    if (paragraphs.length > 0) {
        // Render structured paragraphs
        container.innerHTML = paragraphs.map(para => `
            <div class="paragraph" data-paragraph-id="${para.id}">
                <div class="paragraph-label">${para.label}</div>
                <div class="paragraph-content" data-paragraph-content="${para.id}">${highlightVocabulary(para.content)}</div>
            </div>
        `).join('');
    } else if (lessonData.text) {
        // Fallback to full text
        container.innerHTML = `<div class="paragraph-content">${highlightVocabulary(lessonData.text)}</div>`;
    }
}

// Highlight vocabulary words in text and make them clickable
function highlightVocabulary(text) {
    if (!vocabulary || vocabulary.length === 0) return text;
    
    let highlightedText = text;
    
    // Sort by word length (longest first) to avoid partial matches
    const sortedVocab = [...vocabulary].sort((a, b) => b.word.length - a.word.length);
    
    sortedVocab.forEach(vocab => {
        const word = vocab.word;
        const regex = new RegExp(`\\b${word}\\b`, 'gi');
        highlightedText = highlightedText.replace(regex, (match) => {
            return `<span class="vocab-word" data-vocab-id="${vocab.id}" title="${vocab.definition}">${match}</span>`;
        });
    });
    
    return highlightedText;
}

// Render vocabulary sidebar
function renderVocabulary() {
    const container = document.getElementById('vocabList');
    const mobileContainer = document.getElementById('vocabMobileList');
    
    const vocabHTML = vocabulary.length === 0 
        ? '<p class="text-muted">No vocabulary available</p>'
        : vocabulary.map(vocab => `
            <div class="vocab-item" data-vocab-id="${vocab.id}">
                <div class="vocab-word-header">
                    <strong class="vocab-word-text">${vocab.word}</strong>
                    <span class="vocab-pos">${vocab.partOfSpeech || ''}</span>
                </div>
                <div class="vocab-definition">${vocab.definition || ''}</div>
                ${vocab.contextSentence ? `<div class="vocab-context">${vocab.contextSentence}</div>` : ''}
                ${vocab.explanationInContext ? `<div class="vocab-explanation">${vocab.explanationInContext}</div>` : ''}
            </div>
        `).join('');
    
    if (container) {
        container.innerHTML = vocabHTML;
    }
    
    if (mobileContainer) {
        mobileContainer.innerHTML = vocabHTML;
    }
    
    // Add click handlers for vocabulary words in text
    document.querySelectorAll('.vocab-word').forEach(el => {
        el.addEventListener('click', (e) => {
            const vocabId = e.target.dataset.vocabId;
            showVocabularyTooltip(e.target, vocabId);
        });
    });
    
    // Setup mobile vocabulary button
    const mobileBtn = document.getElementById('vocabMobileBtn');
    const mobileOverlay = document.getElementById('vocabMobileOverlay');
    const mobileClose = document.getElementById('vocabMobileClose');
    
    if (mobileBtn && mobileOverlay) {
        mobileBtn.addEventListener('click', () => {
            mobileOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    }
    
    if (mobileClose && mobileOverlay) {
        mobileClose.addEventListener('click', () => {
            mobileOverlay.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
    
    // Close on overlay click
    if (mobileOverlay) {
        mobileOverlay.addEventListener('click', (e) => {
            if (e.target === mobileOverlay) {
                mobileOverlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    }
}

// Show vocabulary tooltip
function showVocabularyTooltip(element, vocabId) {
    const vocab = vocabulary.find(v => v.id === vocabId);
    if (!vocab) return;
    
    // Remove existing tooltip
    const existingTooltip = document.querySelector('.vocab-tooltip');
    if (existingTooltip) existingTooltip.remove();
    
    // Create tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'vocab-tooltip';
    tooltip.innerHTML = `
        <div class="tooltip-header">
            <strong>${vocab.word}</strong>
            <span class="tooltip-pos">${vocab.partOfSpeech || ''}</span>
        </div>
        <div class="tooltip-definition">${vocab.definition || ''}</div>
        ${vocab.contextSentence ? `<div class="tooltip-context">${vocab.contextSentence}</div>` : ''}
        ${vocab.explanationInContext ? `<div class="tooltip-explanation">${vocab.explanationInContext}</div>` : ''}
    `;
    
    document.body.appendChild(tooltip);
    
    // Position tooltip
    const rect = element.getBoundingClientRect();
    tooltip.style.top = `${rect.bottom + 10}px`;
    tooltip.style.left = `${rect.left}px`;
    
    // Remove tooltip on click outside
    setTimeout(() => {
        document.addEventListener('click', function removeTooltip(e) {
            if (!tooltip.contains(e.target) && e.target !== element) {
                tooltip.remove();
                document.removeEventListener('click', removeTooltip);
            }
        });
    }, 100);
}

// Render questions with filtering
function renderQuestions() {
        const container = document.getElementById('questionsContainer');
        if (!container) return;
        
    // Filter questions by type (vocabulary filter removed - vocabulary is in sidebar)
    let filteredQuestions = questions;
    if (currentQuestionFilter !== 'all') {
        const filterMap = {
            'main-idea': 'main_idea',
            'inference': 'inference',
            'synthesis': 'synthesis'
        };
        filteredQuestions = questions.filter(q => q.type === filterMap[currentQuestionFilter]);
    }
    
    container.innerHTML = filteredQuestions.map((q, idx) => {
        const questionNum = idx + 1;
        const difficultyClass = getDifficultyClass(q.difficulty);
        
        return `
            <div class="question-item ${difficultyClass}" data-question-id="${q.id}" data-question-type="${q.type}">
                <div class="question-header">
                    <span class="question-number">Q${questionNum}</span>
                    <span class="question-type-badge">${getQuestionTypeLabel(q.type)}</span>
                    <span class="question-difficulty">${q.difficulty || 'medium'}</span>
                </div>
                <div class="question-text">${q.question || q.question_text || ''}</div>
                ${q.hint ? `<div class="question-hint" style="display: none;"><strong>Hint:</strong> ${q.hint}</div>` : ''}
                <div class="question-options">
                    ${(q.options || []).map(opt => `
                        <label class="option-label">
                            <input type="radio" name="q${q.id}" value="${opt.id}" data-option-id="${opt.id}">
                            <span class="option-text">${opt.text}</span>
                        </label>
                    `).join('')}
                </div>
                <button class="btn-hint" data-question-id="${q.id}" style="display: none;">Show Hint</button>
            </div>
        `;
    }).join('');
    
    // Add hint buttons
    document.querySelectorAll('.btn-hint').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const questionId = e.target.dataset.questionId;
            const hintEl = document.querySelector(`[data-question-id="${questionId}"] .question-hint`);
            if (hintEl) {
                hintEl.style.display = hintEl.style.display === 'none' ? 'block' : 'none';
            }
        });
    });
    
    // Show submit button if questions exist
    const submitBtn = document.getElementById('submitBtn');
    if (submitBtn) {
        submitBtn.style.display = filteredQuestions.length > 0 ? 'block' : 'none';
    }
}

// Get difficulty class
function getDifficultyClass(difficulty) {
    const map = {
        'easy': 'difficulty-easy',
        'medium': 'difficulty-medium',
        'hard': 'difficulty-hard',
        'very_hard': 'difficulty-very-hard'
    };
    return map[difficulty] || 'difficulty-medium';
}

// Get question type label
function getQuestionTypeLabel(type) {
    const map = {
        'vocabulary': 'Vocabulary',
        'main_idea': 'Main Idea',
        'inference': 'Inference',
        'synthesis': 'Synthesis'
    };
    return map[type] || type;
}

// Set question filter
function setQuestionFilter(filter) {
    currentQuestionFilter = filter;
    
    // Update active button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.filter === filter);
    });
    
    // Re-render questions
    renderQuestions();
}

// Toggle vocabulary sidebar
function toggleVocabularySidebar() {
    vocabularySidebarOpen = !vocabularySidebarOpen;
    const sidebar = document.getElementById('vocabularySidebar');
    const toggle = document.getElementById('vocabToggle');
    
    if (sidebar) {
        sidebar.classList.toggle('collapsed', !vocabularySidebarOpen);
    }
    
    if (toggle) {
        const icon = toggle.querySelector('i');
        if (icon) {
            icon.className = vocabularySidebarOpen ? 'bi bi-chevron-right' : 'bi bi-chevron-left';
        }
    }
}

// Update progress
function updateProgress() {
    const total = questions.length;
    const answered = Object.keys(userAnswers).length;
    const percentage = total > 0 ? Math.round((answered / total) * 100) : 0;
    
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    if (progressFill) {
        progressFill.style.width = `${percentage}%`;
    }
    
    if (progressText) {
        progressText.textContent = `${answered} / ${total} questions`;
    }
}

// Track answer selection
document.addEventListener('change', (e) => {
    if (e.target.type === 'radio' && e.target.name.startsWith('q')) {
        const questionId = e.target.name.replace('q', '');
        const answerId = e.target.value;
        userAnswers[questionId] = answerId;
        updateProgress();
    }
});

// Submit answers
document.addEventListener('DOMContentLoaded', function() {
    const submitBtn = document.getElementById('submitBtn');
    if (submitBtn) {
        submitBtn.addEventListener('click', async () => {
            if (!passageId) {
                alert('Passage ID not found. Please refresh the page.');
                return;
            }
            
            const timeSpent = Math.floor((Date.now() - startTime) / 1000);
            
            try {
                const passageIdNum = parseInt(passageId);
                if (isNaN(passageIdNum)) {
                    throw new Error('Invalid passage ID');
                }
                
                const requestData = {
                    passage_id: passageIdNum,
                    answers: userAnswers,
                    time_spent: timeSpent
                };
                
                const response = await fetch('/api/english/submit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify(requestData)
                });
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
                    throw new Error(errorData.error || `Failed to submit answers: ${response.status}`);
                }
                
                const results = await response.json();
                showResults(results);
            } catch (error) {
                console.error('Error submitting answers:', error);
                alert(`Error submitting answers: ${error.message}. Please try again.`);
            }
        });
    }
});

function getCsrfToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.getAttribute('content') : '';
}

// Show results with highlighting
function showResults(results) {
    const modal = document.getElementById('resultsModal');
    const content = document.getElementById('resultsContent');
    
    if (!modal || !content) return;
    
    // Highlight correct/incorrect answers in text
    highlightAnswersInText(results.results || []);
    
    content.innerHTML = `
        <div class="score-display">
            <h3>${results.score || 0} / ${results.total || 0}</h3>
            <p>${results.percentage || 0}%</p>
            ${results.estimated_band ? `<p>Estimated Band: ${results.estimated_band}</p>` : ''}
            ${results.xp_earned ? `<p class="xp-earned">+${results.xp_earned} XP</p>` : ''}
        </div>
        <div class="results-details">
            ${(results.results || []).map((r, i) => {
                const question = questions.find(q => q.id === r.question_id || q.id === (i + 1));
                return `
                <div class="result-item ${r.correct ? 'correct' : 'incorrect'}">
                        <div class="result-header">
                            <p><strong>Q${r.question_number || (i + 1)}:</strong> ${r.correct ? '✓ Correct' : '✗ Incorrect'}</p>
                        </div>
                    ${!r.correct ? `
                            <div class="result-details">
                        <p>Your answer: ${r.user_answer || 'No answer'}</p>
                        <p>Correct answer: ${r.correct_answer || 'N/A'}</p>
                                ${r.explanation ? `<div class="explanation-box"><strong>Explanation:</strong> ${r.explanation}</div>` : ''}
                            </div>
                    ` : ''}
                        ${question && question.learningPoint ? `<div class="learning-point"><strong>Learning Point:</strong> ${question.learningPoint}</div>` : ''}
                </div>
                `;
            }).join('')}
        </div>
    `;
    
    modal.style.display = 'flex';
}

// Highlight answers in text based on results
function highlightAnswersInText(results) {
    results.forEach(result => {
        const question = questions.find(q => q.id === result.question_id);
        if (!question || !question.paragraph) return;
        
        // Find paragraph and highlight relevant text
        const paraEl = document.querySelector(`[data-paragraph-id="${question.paragraph}"]`);
        if (paraEl) {
            paraEl.classList.add(result.correct ? 'paragraph-correct' : 'paragraph-incorrect');
        }
    });
}

// Fallback for old format
function renderOldFormat(passage, questionsData) {
    const titleEl = document.getElementById('lessonTitle');
    if (titleEl) titleEl.textContent = passage.title;
    
    const passageTitleEl = document.getElementById('passageTitle');
    if (passageTitleEl) passageTitleEl.textContent = passage.title;
    
    const passageTextEl = document.getElementById('passageText');
    if (passageTextEl) {
        const container = document.getElementById('paragraphsContainer');
        if (container) {
            container.innerHTML = `<div class="paragraph-content">${passage.text}</div>`;
        }
    }
    
    questions = questionsData;
    renderQuestions();
    updateProgress();
}
