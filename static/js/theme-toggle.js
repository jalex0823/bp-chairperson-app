// Theme Toggle Functionality
(function() {
    'use strict';

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
        themeIcon.classList.remove('fa-adjust');
        themeIcon.classList.add('fa-moon');
    } else {
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-adjust');
    }

    // Toggle theme when button is clicked
    themeToggle.addEventListener('click', function() {
        if (body.classList.contains('dark-theme')) {
            // Switch to light theme
            body.classList.remove('dark-theme');
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-adjust');
            localStorage.setItem('theme', 'light');
        } else {
            // Switch to dark theme
            body.classList.add('dark-theme');
            themeIcon.classList.remove('fa-adjust');
            themeIcon.classList.add('fa-moon');
            localStorage.setItem('theme', 'dark');
        }
    });
})();
