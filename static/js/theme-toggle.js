// Theme Toggle Functionality
(function() {
    'use strict';

    // Safari on macOS has had rendering quirks with our dark theme.
    // Force light theme there and disable the toggle.
    const ua = navigator.userAgent || '';
    const isMac = /Macintosh|Mac OS X/.test(ua);
    const isSafari = /Safari\//.test(ua) && !/Chrome\//.test(ua) && !/Chromium\//.test(ua) && !/Edg\//.test(ua);
    const disableDarkMode = isMac && isSafari;

    if (disableDarkMode) {
        try { localStorage.setItem('theme', 'light'); } catch (e) {}
        document.documentElement.classList.add('safari-macos');
        document.documentElement.classList.add('light-theme');
        document.documentElement.classList.remove('dark-theme');
        document.body.classList.add('light-theme');
        document.body.classList.remove('dark-theme');
        const themeToggleEl = document.getElementById('themeToggle');
        if (themeToggleEl) themeToggleEl.style.display = 'none';
        return;
    }

    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const body = document.body;

    if (!themeToggle || !themeIcon) {
        console.log('Theme toggle elements not found');
        return;
    }

    // Check for saved theme preference or default to 'light'
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    // Apply the saved theme on page load
    if (currentTheme === 'dark') {
        body.classList.add('dark-theme');
        body.classList.remove('light-theme');
        document.documentElement.classList.add('dark-theme');
        document.documentElement.classList.remove('light-theme');
        themeIcon.textContent = '🌙';
    } else {
        // Explicitly set light theme to override system preference
        body.classList.add('light-theme');
        body.classList.remove('dark-theme');
        document.documentElement.classList.add('light-theme');
        document.documentElement.classList.remove('dark-theme');
        themeIcon.textContent = '☀️';
    }

    // Toggle theme when button is clicked
    themeToggle.addEventListener('click', function() {
        // Play lamp switch sound
        if (window.soundEffects && typeof window.soundEffects.playLampToggle === 'function') {
            window.soundEffects.playLampToggle();
        }
        
        if (body.classList.contains('dark-theme')) {
            // Switch to light theme
            body.classList.remove('dark-theme');
            body.classList.add('light-theme');
            document.documentElement.classList.remove('dark-theme');
            document.documentElement.classList.add('light-theme');
            themeIcon.textContent = '☀️';
            localStorage.setItem('theme', 'light');
        } else {
            // Switch to dark theme
            body.classList.remove('light-theme');
            body.classList.add('dark-theme');
            document.documentElement.classList.remove('light-theme');
            document.documentElement.classList.add('dark-theme');
            themeIcon.textContent = '🌙';
            localStorage.setItem('theme', 'dark');
        }
    });
})();
