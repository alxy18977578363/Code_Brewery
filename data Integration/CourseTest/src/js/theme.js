// theme.js

const themeToggleButton = document.getElementById('theme-toggle');
const body = document.body;

// Load the saved theme from localStorage
const currentTheme = localStorage.getItem('theme');
if (currentTheme) {
    body.classList.add(currentTheme);
}

// Toggle theme function
const toggleTheme = () => {
    body.classList.toggle('dark-theme');
    const theme = body.classList.contains('dark-theme') ? 'dark-theme' : 'light-theme';
    localStorage.setItem('theme', theme);
};

// Event listener for the theme toggle button
themeToggleButton.addEventListener('click', toggleTheme);