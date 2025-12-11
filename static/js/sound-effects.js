/**
 * Sound Effects for Button Clicks and Mouse Interactions
 */

// Sound effect settings
const soundSettings = {
    enabled: localStorage.getItem('soundEnabled') !== 'false', // Default enabled
    volume: parseFloat(localStorage.getItem('soundVolume') || '0.3')
};

// Create audio elements for custom sounds
const clickAudio = new Audio('/static/audio/computer-mouse-click.mp3');
const coinAudio = new Audio('/static/audio/Coin.mp3');

// Button click sound using custom audio file
const buttonClickSound = () => {
    const sound = clickAudio.cloneNode();
    sound.volume = soundSettings.volume;
    sound.play().catch(err => console.log('Click sound blocked'));
};

// Create hover sound
const hoverSound = () => {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    // Subtle hover sound
    oscillator.frequency.value = 600;
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(soundSettings.volume * 0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.05);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.05);
};

// Create success sound (for form submissions)
const successSound = () => {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator1 = audioContext.createOscillator();
    const oscillator2 = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator1.connect(gainNode);
    oscillator2.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    // Two-tone success sound
    oscillator1.frequency.value = 800;
    oscillator2.frequency.value = 1000;
    oscillator1.type = 'sine';
    oscillator2.type = 'sine';
    
    gainNode.gain.setValueAtTime(soundSettings.volume * 0.5, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
    
    oscillator1.start(audioContext.currentTime);
    oscillator2.start(audioContext.currentTime + 0.1);
    oscillator1.stop(audioContext.currentTime + 0.15);
    oscillator2.stop(audioContext.currentTime + 0.25);
};

// Play sound if enabled
function playSound(soundFunction) {
    if (soundSettings.enabled) {
        try {
            soundFunction();
        } catch (error) {
            console.log('Audio playback not supported or blocked');
        }
    }
}

// Initialize sound effects on page load
document.addEventListener('DOMContentLoaded', function() {
    
    // Add click sound to all buttons
    document.querySelectorAll('button, .btn, a.btn').forEach(element => {
        element.addEventListener('click', function(e) {
            playSound(buttonClickSound);
        });
    });
    
    // Add hover sound to buttons (optional - can be disabled)
    const hoverEnabled = localStorage.getItem('hoverSoundEnabled') !== 'false';
    if (hoverEnabled) {
        let hoverTimeout;
        document.querySelectorAll('button, .btn, a.btn').forEach(element => {
            element.addEventListener('mouseenter', function() {
                // Debounce hover sound to avoid too many sounds
                clearTimeout(hoverTimeout);
                hoverTimeout = setTimeout(() => {
                    playSound(hoverSound);
                }, 100);
            });
        });
    }
    
    // Add click sound to links
    document.querySelectorAll('a:not(.btn)').forEach(element => {
        element.addEventListener('click', function(e) {
            if (this.href && !this.href.startsWith('#')) {
                playSound(buttonClickSound);
            }
        });
    });
    
    // Add success sound to form submissions
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            playSound(successSound);
        });
    });
    
    // Add sound to radio buttons and checkboxes
    document.querySelectorAll('input[type="radio"], input[type="checkbox"]').forEach(element => {
        element.addEventListener('change', function() {
            playSound(buttonClickSound);
        });
    });
    
    // Create sound toggle button (optional)
    createSoundToggle();
});

// Create a sound toggle button in the navbar
function createSoundToggle() {
    const navbar = document.querySelector('.navbar-nav');
    if (navbar) {
        const soundToggle = document.createElement('li');
        soundToggle.className = 'nav-item';
        soundToggle.innerHTML = `
            <a class="nav-link" href="#" id="soundToggle" title="Toggle sound effects">
                <i class="fas ${soundSettings.enabled ? 'fa-volume-up' : 'fa-volume-mute'}"></i>
            </a>
        `;
        navbar.appendChild(soundToggle);
        
        document.getElementById('soundToggle').addEventListener('click', function(e) {
            e.preventDefault();
            soundSettings.enabled = !soundSettings.enabled;
            localStorage.setItem('soundEnabled', soundSettings.enabled);
            this.querySelector('i').className = `fas ${soundSettings.enabled ? 'fa-volume-up' : 'fa-volume-mute'}`;
            
            // Play a sound to confirm toggle
            if (soundSettings.enabled) {
                playSound(successSound);
            }
        });
    }
}

// Export functions for use in other scripts
window.soundEffects = {
    playClick: () => playSound(buttonClickSound),
    playHover: () => playSound(hoverSound),
    playSuccess: () => playSound(successSound),
    toggle: () => {
        soundSettings.enabled = !soundSettings.enabled;
        localStorage.setItem('soundEnabled', soundSettings.enabled);
    },
    setVolume: (volume) => {
        soundSettings.volume = Math.max(0, Math.min(1, volume));
        localStorage.setItem('soundVolume', soundSettings.volume);
    }
};
