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
        themeIcon.classList.remove('fa-toggle-off');
        themeIcon.classList.add('fa-toggle-on');
        themeIcon.style.color = '#6c757d'; // Gray for dark mode
    } else {
        themeIcon.classList.remove('fa-toggle-on');
        themeIcon.classList.add('fa-toggle-off');
        themeIcon.style.color = '#ffc107'; // Yellow for light mode
    }

    // Toggle theme when button is clicked
    themeToggle.addEventListener('click', function() {
        if (body.classList.contains('dark-theme')) {
            // Switch to light theme (toggle OFF = light on)
            body.classList.remove('dark-theme');
            themeIcon.classList.remove('fa-toggle-on');
            themeIcon.classList.add('fa-toggle-off');
            themeIcon.style.color = '#ffc107'; // Yellow
            localStorage.setItem('theme', 'light');
        } else {
            // Switch to dark theme (toggle ON = dark mode)
            body.classList.add('dark-theme');
            themeIcon.classList.remove('fa-toggle-off');
            themeIcon.classList.add('fa-toggle-on');
            themeIcon.style.color = '#6c757d'; // Gray
            localStorage.setItem('theme', 'dark');
        }
    });
})();
