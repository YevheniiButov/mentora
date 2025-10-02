/**
 * Membership Card Download Functionality
 * Handles PNG and PDF export of membership cards
 */

// Configuration
const CARD_CONFIG = {
    width: 350,
    height: 220,
    scale: 2, // For high DPI exports
    backgroundColor: '#ffffff'
};

// Get member ID for filename
function getMemberId() {
    const memberIdElement = document.querySelector('.member-id');
    if (memberIdElement) {
        const idText = memberIdElement.textContent;
        const match = idText.match(/MNT-([A-Z0-9]+)/);
        return match ? match[1] : 'unknown';
    }
    return 'unknown';
}

// Show loading overlay
function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'flex';
    }
}

// Hide loading overlay
function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// Download file helper
function downloadFile(dataUrl, filename) {
    const link = document.createElement('a');
    link.download = filename;
    link.href = dataUrl;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Generate PNG from card
async function downloadPNG() {
    try {
        showLoading();
        
        const cardElement = document.getElementById('card-content');
        if (!cardElement) {
            throw new Error('Card element not found');
        }

        // Configure html2canvas options
        const canvas = await html2canvas(cardElement, {
            width: CARD_CONFIG.width,
            height: CARD_CONFIG.height,
            scale: CARD_CONFIG.scale,
            backgroundColor: CARD_CONFIG.backgroundColor,
            useCORS: true,
            allowTaint: true,
            logging: false,
            onclone: function(clonedDoc) {
                // Ensure styles are applied in cloned document
                const clonedCard = clonedDoc.getElementById('card-content');
                if (clonedCard) {
                    clonedCard.style.transform = 'none';
                    clonedCard.style.boxShadow = 'none';
                }
            }
        });

        // Convert to PNG
        const dataUrl = canvas.toDataURL('image/png', 1.0);
        const memberId = getMemberId();
        const filename = `mentora_card_${memberId}.png`;
        
        downloadFile(dataUrl, filename);
        
    } catch (error) {
        console.error('Error generating PNG:', error);
        alert('Ошибка при генерации PNG файла. Попробуйте еще раз.');
    } finally {
        hideLoading();
    }
}

// Generate PDF from card
async function downloadPDF() {
    try {
        showLoading();
        
        const cardElement = document.getElementById('card-content');
        if (!cardElement) {
            throw new Error('Card element not found');
        }

        // First generate canvas
        const canvas = await html2canvas(cardElement, {
            width: CARD_CONFIG.width,
            height: CARD_CONFIG.height,
            scale: CARD_CONFIG.scale,
            backgroundColor: CARD_CONFIG.backgroundColor,
            useCORS: true,
            allowTaint: true,
            logging: false,
            onclone: function(clonedDoc) {
                const clonedCard = clonedDoc.getElementById('card-content');
                if (clonedCard) {
                    clonedCard.style.transform = 'none';
                    clonedCard.style.boxShadow = 'none';
                }
            }
        });

        // Create PDF
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF({
            orientation: 'landscape',
            unit: 'mm',
            format: [105, 66] // Credit card size in mm
        });

        // Calculate dimensions for PDF
        const imgWidth = 105; // mm
        const imgHeight = 66; // mm
        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();
        
        // Center the image
        const x = (pageWidth - imgWidth) / 2;
        const y = (pageHeight - imgHeight) / 2;

        // Add image to PDF
        const imgData = canvas.toDataURL('image/png', 1.0);
        pdf.addImage(imgData, 'PNG', x, y, imgWidth, imgHeight);

        // Generate filename and download
        const memberId = getMemberId();
        const filename = `mentora_card_${memberId}.pdf`;
        
        pdf.save(filename);
        
    } catch (error) {
        console.error('Error generating PDF:', error);
        alert('Ошибка при генерации PDF файла. Попробуйте еще раз.');
    } finally {
        hideLoading();
    }
}

// Add card hover effects
function initCardEffects() {
    const card = document.getElementById('card-content');
    if (!card) return;

    // Add subtle animation on load
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
        card.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
    }, 100);
}

// Add button click effects
function initButtonEffects() {
    const buttons = document.querySelectorAll('.download-btn');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Add ripple effect
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

// Add ripple effect styles
function addRippleStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .download-btn {
            position: relative;
            overflow: hidden;
        }
        
        .ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: scale(0);
            animation: ripple-animation 0.6s linear;
            pointer-events: none;
        }
        
        @keyframes ripple-animation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initCardEffects();
    initButtonEffects();
    addRippleStyles();
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case 'p':
                    e.preventDefault();
                    downloadPNG();
                    break;
                case 'd':
                    e.preventDefault();
                    downloadPDF();
                    break;
            }
        }
    });
    
    // Add touch support for mobile
    if ('ontouchstart' in window) {
        const card = document.getElementById('card-content');
        if (card) {
            card.addEventListener('touchstart', function() {
                this.style.transform = 'translateY(-4px) rotateX(2deg)';
            });
            
            card.addEventListener('touchend', function() {
                this.style.transform = 'translateY(0) rotateX(0)';
            });
        }
    }
});

// Export functions for global access
window.downloadPNG = downloadPNG;
window.downloadPDF = downloadPDF;





