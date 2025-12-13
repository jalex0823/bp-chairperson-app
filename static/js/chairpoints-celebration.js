/**
 * ChairPoints Celebration Animation System
 * Displays celebration when user earns new ChairPoints
 */

(function() {
  'use strict';

  // Check if user has new ChairPoints since last visit
  function checkForNewChairPoints() {
    const currentPoints = parseInt(document.getElementById('currentChairPoints')?.dataset.points || 0);
    const lastSeenPoints = parseInt(localStorage.getItem('lastSeenChairPoints') || 0);
    
    if (currentPoints > lastSeenPoints) {
      const pointsEarned = currentPoints - lastSeenPoints;
      showCelebration(pointsEarned, currentPoints);
    }
    
    // Update last seen points
    localStorage.setItem('lastSeenChairPoints', currentPoints);
  }

  // Create and show celebration animation
  function showCelebration(pointsEarned, totalPoints) {
    // Create celebration container
    const celebration = document.createElement('div');
    celebration.className = 'chairpoints-celebration active';
    celebration.innerHTML = `
      <div class="celebration-message">
        <div>🎉 Congratulations! 🎉</div>
        <div class="points-earned">+${pointsEarned} ChairPoint${pointsEarned > 1 ? 's' : ''}!</div>
        <div>Total: <span style="font-size: 2rem; vertical-align: middle; margin: 0 0.3em;">🪙</span> ${totalPoints} ChairPoints</div>
        <button class="close-btn" onclick="this.closest('.chairpoints-celebration').remove()">
          Awesome!
        </button>
      </div>
    `;
    
    document.body.appendChild(celebration);
    
    // Add confetti
    createConfetti(celebration);
    
    // Add sparkles
    createSparkles(celebration);
    
    // Add floating coins
    createFloatingCoins(celebration, pointsEarned);
    
    // Play celebration sound (optional - if enabled)
    playChimeSound();
    
    // Auto-close after 10 seconds
    setTimeout(() => {
      celebration.style.opacity = '0';
      celebration.style.transition = 'opacity 1s';
      setTimeout(() => celebration.remove(), 1000);
    }, 10000);
    
    // Highlight the ChairPoints value
    highlightChairPointsValue();
  }

  // Create confetti effect
  function createConfetti(container) {
    const colors = ['#FFD700', '#FFA500', '#28a745', '#007bff', '#dc3545'];
    
    for (let i = 0; i < 50; i++) {
      const confetti = document.createElement('div');
      confetti.className = 'confetti';
      confetti.style.left = `${Math.random() * 100}%`;
      confetti.style.top = '-100px';
      confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
      confetti.style.animationDelay = `${Math.random() * 0.5}s`;
      confetti.style.animationDuration = `${2 + Math.random() * 2}s`;
      container.appendChild(confetti);
    }
  }

  // Create sparkle effect
  function createSparkles(container) {
    for (let i = 0; i < 30; i++) {
      const sparkle = document.createElement('div');
      sparkle.className = 'sparkle';
      sparkle.style.left = `${20 + Math.random() * 60}%`;
      sparkle.style.top = `${20 + Math.random() * 60}%`;
      sparkle.style.animationDelay = `${Math.random() * 1}s`;
      container.appendChild(sparkle);
    }
  }

  // Create floating coin animations
  function createFloatingCoins(container, count) {
    const maxCoins = Math.min(count, 5); // Show up to 5 coins
    
    for (let i = 0; i < maxCoins; i++) {
      const coin = document.createElement('div');
      coin.className = 'gold-coin';
      coin.innerHTML = '<img src="/static/img/chairpoint-coin.png" style="width: 100%; height: 100%; object-fit: contain;">';
      coin.style.left = `${20 + (i * 15)}%`;
      coin.style.top = '60%';
      coin.style.animationDelay = `${i * 0.2}s`;
      container.appendChild(coin);
    }
  }

  // Play chime sound (optional)
  function playChimeSound() {
    // Only play if user has interacted with page (browser requirement)
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      oscillator.frequency.value = 800;
      oscillator.type = 'sine';
      
      gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
      
      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.5);
    } catch (e) {
      // Silent fail if audio not supported
    }
  }

  // Highlight ChairPoints value with animation
  function highlightChairPointsValue() {
    const chairPointsElements = document.querySelectorAll('#chairPointsValue, [data-chairpoints-display]');
    
    chairPointsElements.forEach(element => {
      element.classList.add('chairpoints-highlight');
      element.parentElement.classList.add('chairpoints-countup');
      
      setTimeout(() => {
        element.classList.remove('chairpoints-highlight');
        element.parentElement.classList.remove('chairpoints-countup');
      }, 2000);
    });
  }

  // Animate number count-up
  function animateCountUp(element, start, end, duration) {
    const startTime = performance.now();
    
    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      const current = Math.floor(start + (end - start) * progress);
      element.textContent = current;
      
      if (progress < 1) {
        requestAnimationFrame(update);
      }
    }
    
    requestAnimationFrame(update);
  }

  // Initialize on page load
  document.addEventListener('DOMContentLoaded', function() {
    // Check for new points after a short delay to ensure page is ready
    setTimeout(checkForNewChairPoints, 500);
  });

  // Manual trigger function (for testing)
  window.triggerChairPointsCelebration = function(points = 1) {
    const currentPoints = parseInt(document.getElementById('currentChairPoints')?.dataset.points || 0);
    showCelebration(points, currentPoints + points);
  };

  // Reset last seen points (for testing)
  window.resetChairPointsTracking = function() {
    localStorage.removeItem('lastSeenChairPoints');
    console.log('ChairPoints tracking reset. Reload page to see celebration.');
  };

})();
