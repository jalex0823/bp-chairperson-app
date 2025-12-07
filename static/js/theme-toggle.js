// Theme Toggle Functionality
(function() {
    'use strict';

    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const body = document.body;

    // Check for saved theme preference or default to 'light'
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    // Apply the saved theme on page load
    if (currentTheme === 'dark') {
        body.classList.add('dark-theme');
        themeIcon.classList.remove('fa-lightbulb');
        themeIcon.classList.add('fa-lightbulb');
        themeIcon.style.opacity = '0.5'; // Dim for dark mode (off state)
    } else {
        themeIcon.style.opacity = '1'; // Bright for light mode (on state)
    }

    // Toggle theme when button is clicked
    themeToggle.addEventListener('click', function() {
        if (body.classList.contains('dark-theme')) {
            // Switch to light theme (lantern ON)
            body.classList.remove('dark-theme');
            themeIcon.style.opacity = '1';
            localStorage.setItem('theme', 'light');
        } else {
            // Switch to dark theme (lantern OFF)
            body.classList.add('dark-theme');
            themeIcon.style.opacity = '0.5';
            localStorage.setItem('theme', 'dark');
        }
    });
})();
