/**
 * Утилита для автоматического выбора WebP изображений с fallback
 */

class ImageOptimizer {
    constructor() {
        this.supportsWebP = this.checkWebPSupport();
        this.init();
    }

    checkWebPSupport() {
        // Проверяем поддержку WebP
        const canvas = document.createElement('canvas');
        canvas.width = 1;
        canvas.height = 1;
        return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
    }

    init() {
        // Заменяем все изображения на оптимизированные версии
        this.optimizeImages();
    }

    optimizeImages() {
        const images = document.querySelectorAll('img[data-src], img[src*=".png"], img[src*=".jpg"], img[src*=".jpeg"]');
        
        images.forEach(img => {
            this.optimizeImage(img);
        });
    }

    optimizeImage(img) {
        const currentSrc = img.src || img.getAttribute('data-src');
        if (!currentSrc) return;

        // Определяем путь к WebP версии
        const webpSrc = this.getWebPSrc(currentSrc);
        
        if (this.supportsWebP && webpSrc) {
            // Создаем новый элемент для предзагрузки
            const webpImg = new Image();
            
            webpImg.onload = () => {
                // WebP загружен успешно, заменяем src
                img.src = webpSrc;
                img.classList.add('webp-loaded');
            };
            
            webpImg.onerror = () => {
                // WebP не найден, оставляем оригинал

            };
            
            webpImg.src = webpSrc;
        }
    }

    getWebPSrc(originalSrc) {
        // Заменяем расширение на .webp
        const baseName = originalSrc.replace(/\.(png|jpg|jpeg)$/i, '');
        return `${baseName}_optimized.webp`;
    }

    // Метод для ручной оптимизации конкретного изображения
    static optimize(src, callback) {
        const optimizer = new ImageOptimizer();
        const webpSrc = optimizer.getWebPSrc(src);
        
        if (optimizer.supportsWebP) {
            const testImg = new Image();
            testImg.onload = () => callback(webpSrc);
            testImg.onerror = () => callback(src);
            testImg.src = webpSrc;
        } else {
            callback(src);
        }
    }
}

// Автоматическая инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    new ImageOptimizer();
});

// Экспорт для использования в других скриптах
window.ImageOptimizer = ImageOptimizer;
