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
        themeIcon.classList.add('fa-moon');
        themeIcon.style.color = '#6c757d'; // Dim gray for OFF (dark mode)
    } else {
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-lightbulb');
        themeIcon.style.color = '#ffc107'; // Bright yellow for ON (light mode)
    }

    // Toggle theme when button is clicked
    themeToggle.addEventListener('click', function() {
        if (body.classList.contains('dark-theme')) {
            // Switch to light theme (lantern ON)
            body.classList.remove('dark-theme');
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-lightbulb');
            themeIcon.style.color = '#ffc107'; // Bright yellow ON
            localStorage.setItem('theme', 'light');
        } else {
            // Switch to dark theme (lantern OFF)
            body.classList.add('dark-theme');
            themeIcon.classList.remove('fa-lightbulb');
            themeIcon.classList.add('fa-moon');
            themeIcon.style.color = '#6c757d'; // Dim gray OFF
            localStorage.setItem('theme', 'dark');
        }
    });
})();
