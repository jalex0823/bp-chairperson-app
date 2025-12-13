/**
 * Coin Page Transition Animation
 * Shows spinning, bouncing coin with sound during page navigation
 */

// Settings
const transitionSettings = {
    enabled: localStorage.getItem('coinTransitionEnabled') !== 'false',
    soundEnabled: localStorage.getItem('soundEnabled') !== 'false'
};

// Create coin transition overlay
function createCoinOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'coin-transition-overlay';
    overlay.innerHTML = `
        <div class="coin-container">
            <img src="/static/img/chairpoint-coin.png" alt="ChairPoint Coin" class="transition-coin">
        </div>
    `;
    document.body.appendChild(overlay);
}

// Show coin transition
function showCoinTransition() {
    if (!transitionSettings.enabled) return;
    
    const overlay = document.getElementById('coin-transition-overlay');
    if (overlay) {
        overlay.classList.add('active');
        
        // Play coin sound
        if (transitionSettings.soundEnabled) {
            const coinSound = new Audio('/static/audio/Coin.mp3');
            coinSound.volume = 0.4;
            coinSound.play().catch(err => console.log('Coin sound blocked'));
        }
    }
}

// Hide coin transition
function hideCoinTransition() {
    const overlay = document.getElementById('coin-transition-overlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Create overlay
    createCoinOverlay();
    
    // Hide transition after page loads
    setTimeout(hideCoinTransition, 100);
    
    // Intercept link clicks for smooth transitions
    document.querySelectorAll('a:not([target="_blank"]):not([href^="#"]):not(.no-transition)').forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Skip if it's a hash link, external, or download
            if (!href || href.startsWith('#') || href.startsWith('javascript:') || 
                this.hasAttribute('download') || this.getAttribute('target') === '_blank') {
                return;
            }
            
            // Show transition and navigate
            e.preventDefault();
            showCoinTransition();
            
            setTimeout(() => {
                window.location.href = href;
            }, 600); // Delay to show animation
        });
    });
    
    // Handle back/forward navigation
    window.addEventListener('pageshow', function(event) {
        if (event.persisted) {
            hideCoinTransition();
        }
    });
});

// Export for programmatic use
window.coinTransition = {
    show: showCoinTransition,
    hide: hideCoinTransition,
    toggle: () => {
        transitionSettings.enabled = !transitionSettings.enabled;
        localStorage.setItem('coinTransitionEnabled', transitionSettings.enabled);
    }
};
