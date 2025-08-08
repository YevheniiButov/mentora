// BIG Info Pages JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 BIG Info JavaScript initialized');

    // Tab Navigation
    initializeTabs();
    
    // FAQ Accordion
    initializeFAQ();
    
    // Document Checklist
    initializeChecklist();
    
    // Smooth Scrolling
    initializeSmoothScrolling();
});

// Tab Navigation System
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const contentSections = document.querySelectorAll('.content-section');
    
    if (tabButtons.length === 0) return;
    
    console.log('📑 Initializing tab navigation...');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Remove active class from all buttons and sections
            tabButtons.forEach(btn => btn.classList.remove('active'));
            contentSections.forEach(section => section.classList.remove('active'));
            
            // Add active class to clicked button and target section
            this.classList.add('active');
            const targetSection = document.getElementById(targetTab);
            if (targetSection) {
                targetSection.classList.add('active');
            }
            
            console.log(`📑 Switched to tab: ${targetTab}`);
        });
    });
    
    // Activate first tab by default
    if (tabButtons.length > 0) {
        tabButtons[0].click();
    }
}

// FAQ Accordion System
function initializeFAQ() {
    const faqQuestions = document.querySelectorAll('.faq-question');
    
    if (faqQuestions.length === 0) return;
    
    console.log('❓ Initializing FAQ accordion...');
    
    faqQuestions.forEach(question => {
        question.addEventListener('click', function() {
            const answer = this.nextElementSibling;
            const icon = this.querySelector('i');
            
            // Toggle answer visibility
            if (answer.style.maxHeight) {
                answer.style.maxHeight = null;
                icon.style.transform = 'rotate(0deg)';
            } else {
                answer.style.maxHeight = answer.scrollHeight + 'px';
                icon.style.transform = 'rotate(180deg)';
            }
            
            console.log('❓ FAQ item toggled');
        });
    });
}

// Document Checklist System
function initializeChecklist() {
    const checkboxes = document.querySelectorAll('.document-checkbox');
    
    if (checkboxes.length === 0) return;
    
    console.log('📋 Initializing document checklist...');
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const checkedCount = document.querySelectorAll('.document-checkbox:checked').length;
            const totalCount = checkboxes.length;
            
            console.log(`📋 Progress: ${checkedCount}/${totalCount} documents`);
            
            // Update progress indicators if they exist
            updateProgressIndicators(checkedCount, totalCount);
        });
    });
}

// Update Progress Indicators
function updateProgressIndicators(checked, total) {
    const progressElements = document.querySelectorAll('.progress-indicator');
    
    progressElements.forEach(element => {
        const percentage = Math.round((checked / total) * 100);
        element.textContent = `${checked}/${total} (${percentage}%)`;
        
        // Update progress bar if exists
        const progressBar = element.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
        }
    });
}

// Smooth Scrolling
function initializeSmoothScrolling() {
    const smoothScrollLinks = document.querySelectorAll('a[href^="#"]');
    
    smoothScrollLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                console.log(`📜 Smooth scroll to: ${targetId}`);
            }
        });
    });
}

// Print Checklist Function
function printChecklist() {
    console.log('🖨️ Printing checklist...');
    
    const checkedItems = document.querySelectorAll('.document-checkbox:checked');
    const uncheckedItems = document.querySelectorAll('.document-checkbox:not(:checked)');
    
    let printContent = `
        <html>
        <head>
            <title>BIG Registratie Documenten Checklist</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { text-align: center; margin-bottom: 30px; }
                .section { margin-bottom: 20px; }
                .section h3 { color: #3b82f6; border-bottom: 2px solid #3b82f6; padding-bottom: 5px; }
                .item { margin: 5px 0; padding: 5px; }
                .checked { background: #d1fae5; }
                .unchecked { background: #fef3c7; }
                .checkbox { display: inline-block; width: 16px; height: 16px; border: 2px solid #000; margin-right: 10px; }
                .checked .checkbox { background: #10b981; border-color: #10b981; }
                .checked .checkbox::after { content: '✓'; color: white; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>BIG Registratie Documenten Checklist</h1>
                <p>Gegenereerd op: ${new Date().toLocaleDateString('nl-NL')}</p>
            </div>
    `;
    
    // Add checked items
    if (checkedItems.length > 0) {
        printContent += '<div class="section"><h3>✅ Voltooide documenten</h3>';
        checkedItems.forEach(item => {
            const itemName = item.closest('.document-item').querySelector('.document-name').textContent;
            printContent += `<div class="item checked"><span class="checkbox"></span>${itemName}</div>`;
        });
        printContent += '</div>';
    }
    
    // Add unchecked items
    if (uncheckedItems.length > 0) {
        printContent += '<div class="section"><h3>⏳ Nog te verzamelen</h3>';
        uncheckedItems.forEach(item => {
            const itemName = item.closest('.document-item').querySelector('.document-name').textContent;
            printContent += `<div class="item unchecked"><span class="checkbox"></span>${itemName}</div>`;
        });
        printContent += '</div>';
    }
    
    printContent += '</body></html>';
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.print();
}

// Save Progress Function
function saveProgress() {
    console.log('💾 Saving progress...');
    
    const checkboxes = document.querySelectorAll('.document-checkbox');
    const progress = {};
    
    checkboxes.forEach(checkbox => {
        const itemName = checkbox.closest('.document-item').querySelector('.document-name').textContent;
        progress[itemName] = checkbox.checked;
    });
    
    // Save to localStorage
    localStorage.setItem('bigChecklistProgress', JSON.stringify(progress));
    
    // Show success message
    showNotification('Voortgang opgeslagen!', 'success');
}

// Load Progress Function
function loadProgress() {
    const savedProgress = localStorage.getItem('bigChecklistProgress');
    
    if (savedProgress) {
        const progress = JSON.parse(savedProgress);
        const checkboxes = document.querySelectorAll('.document-checkbox');
        
        checkboxes.forEach(checkbox => {
            const itemName = checkbox.closest('.document-item').querySelector('.document-name').textContent;
            if (progress[itemName]) {
                checkbox.checked = true;
            }
        });
        
        console.log('📋 Progress loaded from localStorage');
    }
}

// Show Notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 6px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        animation: slideIn 0.3s ease;
        background: ${type === 'success' ? '#10b981' : '#3b82f6'};
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Toggle FAQ Function (for onclick handlers)
function toggleFAQ(index) {
    const faqItems = document.querySelectorAll('.faq-item');
    const targetItem = faqItems[index];
    
    if (targetItem) {
        const question = targetItem.querySelector('.faq-question');
        question.click();
    }
}

// Auto-load progress when page loads
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(loadProgress, 500);
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .faq-answer {
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.3s ease;
    }
    
    .faq-question i {
        transition: transform 0.3s ease;
    }
    
    .document-item {
        transition: background-color 0.2s ease;
    }
    
    .checkmark {
        transition: all 0.2s ease;
    }
`;
document.head.appendChild(style);

// Daily Plan Interaction Functions
function startContent(contentType, contentId) {
    // Track start time
    const startTime = Date.now();
    localStorage.setItem(`content_start_${contentId}`, startTime);
    
    // Navigate to appropriate content
    switch(contentType) {
        case 'lesson':
            window.location.href = `/learning/lesson/${contentId}`;
            break;
        case 'question':
            window.location.href = `/practice/question/${contentId}`;
            break;
        default:
            console.error('Unknown content type:', contentType);
    }
}

function startReview(contentId, contentType) {
    // Mark as review session
    localStorage.setItem(`review_session_${contentId}`, 'true');
    startContent(contentType, contentId);
}

// Progress tracking
function markContentCompleted(contentId, contentType, wasCorrect = null) {
    const startTime = localStorage.getItem(`content_start_${contentId}`);
    const endTime = Date.now();
    const timeSpent = startTime ? Math.round((endTime - startTime) / 1000 / 60) : 0; // minutes
    
    // Send progress to backend
    fetch('/api/progress/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            content_id: contentId,
            content_type: contentType,
            time_spent: timeSpent,
            completed: true,
            correct: wasCorrect,
            is_review: localStorage.getItem(`review_session_${contentId}`) === 'true'
        })
    }).then(response => {
        if (response.ok) {
            // Update UI
            updateDailyProgress();
            // Clean up localStorage
            localStorage.removeItem(`content_start_${contentId}`);
            localStorage.removeItem(`review_session_${contentId}`);
        }
    }).catch(error => {
        console.error('Error updating progress:', error);
    });
}

function updateDailyProgress() {
    // Refresh daily plan progress
    fetch('/api/daily-plan/progress')
        .then(response => response.json())
        .then(data => {
            // Update progress indicators
            const progressElement = document.querySelector('.progress-value');
            if (progressElement) {
                progressElement.textContent = data.completion_percentage + '%';
            }
            
            // Update completed tasks styling
            data.completed_items.forEach(itemId => {
                const element = document.querySelector(`[data-content-id="${itemId}"]`);
                if (element) {
                    element.classList.add('completed');
                    const button = element.querySelector('.item-action');
                    if (button) {
                        button.textContent = 'Выполнено';
                        button.disabled = true;
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error updating daily progress:', error);
        });
}

// Initialize daily plan functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize daily plan if it exists
    const dailyPlanSection = document.querySelector('.daily-plan-section');
    if (dailyPlanSection) {
        console.log('📅 Daily Plan section found, initializing...');
        updateDailyProgress();
    }
}); 