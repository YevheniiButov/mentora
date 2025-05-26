/**
 * Simple counter animation for statistics
 * This script animates numeric counters on the page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Find all elements with the counter class
    const counters = document.querySelectorAll('.counter');
    
    // Function to animate a single counter
    function animateCounter(counter) {
      // Get the target value from the data-target attribute
      const target = parseInt(counter.getAttribute('data-target'));
      // Start from 0
      let count = 0;
      // Calculate speed based on target value (higher targets animate faster)
      const duration = 2000; // 2 seconds total duration
      const frameRate = 30; // frames per second
      const totalFrames = duration / 1000 * frameRate;
      const increment = target / totalFrames;
      
      // Update the counter text at regular intervals
      const timer = setInterval(() => {
        count += increment;
        
        // Check if we've reached the target
        if (count >= target) {
          counter.innerText = target; // Set to final value
          clearInterval(timer); // Stop the interval
        } else {
          counter.innerText = Math.floor(count); // Update with current count
        }
      }, 1000 / frameRate);
    }
    
    // Function to check if element is in viewport
    function isInViewport(element) {
      const rect = element.getBoundingClientRect();
      return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
      );
    }
    
    // Set up intersection observer to animate counters when they come into view
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          observer.unobserve(entry.target); // Stop observing once animated
        }
      });
    }, { threshold: 0.1 }); // Trigger when at least 10% of the element is visible
    
    // Start observing each counter
    counters.forEach(counter => {
      observer.observe(counter);
    });
    
    // Also handle counters that are already in view on page load
    counters.forEach(counter => {
      if (isInViewport(counter)) {
        animateCounter(counter);
      }
    });
  });