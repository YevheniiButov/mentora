/**
 * Homepage animations and interactive elements
 */

document.addEventListener("DOMContentLoaded", function() {
    // Scroll animations
    const animateOnScroll = () => {
      const elements = document.querySelectorAll('.benefit-card, .hero-stat, .floating-card, .section-title, .section-subtitle, .hero-illustration');
      
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('animated');
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.2 });
      
      elements.forEach(element => {
        observer.observe(element);
      });
    };
    
    // Counter animation
    const animateCounters = () => {
      const counters = document.querySelectorAll('.stat-value');
      const speed = 200;
  
      counters.forEach(counter => {
        const targetText = counter.innerText;
        let target;
        let suffix = '';
        
        // Handle different formats (1000+, 95%, 4.8/5)
        if (targetText.includes('+')) {
          target = parseInt(targetText.replace('+', ''), 10);
          suffix = '+';
        } else if (targetText.includes('/')) {
          const parts = targetText.split('/');
          target = parseFloat(parts[0]);
          suffix = '/' + parts[1];
        } else if (targetText.includes('%')) {
          target = parseInt(targetText.replace('%', ''), 10);
          suffix = '%';
        } else {
          target = parseInt(targetText, 10);
        }
        
        // Set start at 0
        counter.innerText = '0' + suffix;
        
        let count = 0;
        const increment = target / speed;
        
        // Update counter every frame
        const updateCount = () => {
          if (count < target) {
            count += increment;
            // Handle decimal values (like 4.8/5)
            const displayValue = targetText.includes('.') 
              ? Math.min(parseFloat(count.toFixed(1)), target) 
              : Math.min(Math.floor(count), target);
            
            counter.innerText = displayValue + suffix;
            requestAnimationFrame(updateCount);
          } else {
            counter.innerText = targetText; // Set to original target text
          }
        };
        
        requestAnimationFrame(updateCount);
      });
    };
    
    // Floating animations for cards
    const initFloatingCards = () => {
      const cards = document.querySelectorAll('.floating-card');
      
      cards.forEach((card, index) => {
        // Set different animation delays for each card
        card.style.animationDelay = `${index * 0.5}s`;
      });
    };
    
    // Handle scroll animation for hero section
    const handleHeroScrollEffect = () => {
      const heroSection = document.querySelector('.hero-section');
      const heroContent = document.querySelector('.hero-content');
      const heroImage = document.querySelector('.hero-image');
      
      if (!heroSection || !heroContent || !heroImage) return;
      
      window.addEventListener('scroll', () => {
        const scrollPosition = window.scrollY;
        
        if (scrollPosition < heroSection.offsetHeight) {
          // Parallax effect
          heroContent.style.transform = `translateY(${scrollPosition * 0.1}px)`;
          heroImage.style.transform = `translateY(${scrollPosition * 0.05}px)`;
        }
      });
    };
    
    // Run initial animations
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateCounters();
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.2 });
    
    const statsSection = document.querySelector('.hero-stats');
    if (statsSection) {
      observer.observe(statsSection);
    }
    
    // Initialize all animations
    animateOnScroll();
    initFloatingCards();
    handleHeroScrollEffect();
    
    // Add CSS classes for animations
    document.body.classList.add('loaded');
  });
  
  // Simple animation for the counter on the stats section
  function simpleCounterAnimation() {
    const counters = document.querySelectorAll('.counter');
    
    counters.forEach(counter => {
      const target = parseInt(counter.getAttribute('data-target'));
      let count = 0;
      const speed = 2000 / target; // Adjust speed based on target value
      
      const updateCounter = () => {
        if (count < target) {
          count++;
          counter.innerText = count;
          setTimeout(updateCounter, speed);
        } else {
          counter.innerText = target;
        }
      };
      
      updateCounter();
    });
  }
  
  // Initialize counter animation when page loads
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', simpleCounterAnimation);
  } else {
    simpleCounterAnimation();
  }

  // Add to homepage.js
document.addEventListener("DOMContentLoaded", function() {
  // Smooth scroll animation for CTA buttons
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      document.querySelector(this.getAttribute('href')).scrollIntoView({
        behavior: 'smooth'
      });
    });
  });

  // Enhanced counter animation with easing
  const animateCounter = (counter, target) => {
    const duration = 2000;
    const startTime = performance.now();
    const startValue = 0;
    
    const update = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function for smooth animation
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      const current = Math.floor(startValue + (target - startValue) * easeOutQuart);
      
      counter.textContent = current;
      
      if (progress < 1) {
        requestAnimationFrame(update);
      }
    };
    
    requestAnimationFrame(update);
  };

  // Initialize enhanced counters
  document.querySelectorAll('.counter').forEach(counter => {
    const target = parseInt(counter.getAttribute('data-target'));
    animateCounter(counter, target);
  });
});