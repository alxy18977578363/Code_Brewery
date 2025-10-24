// main.js

document.addEventListener("DOMContentLoaded", function() {
    // Smooth scrolling for navigation links
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            targetElement.scrollIntoView({ behavior: 'smooth' });
        });
    });

    // Skill showcase animation
    const skills = document.querySelectorAll('.skill');
    skills.forEach(skill => {
        skill.addEventListener('mouseover', function() {
            this.classList.add('animate');
        });
        skill.addEventListener('mouseout', function() {
            this.classList.remove('animate');
        });
    });
});

window.addEventListener('scroll', function() {
  const navTexts = document.querySelectorAll('.nav-text');
  const navIcons = document.querySelectorAll('.nav-icon');
  if (window.scrollY === 0) {
    navTexts.forEach(text => text.style.display = 'inline');
    navIcons.forEach(icon => icon.style.display = 'none');
  } else {
    navTexts.forEach(text => text.style.display = 'none');
    navIcons.forEach(icon => icon.style.display = 'inline');
  }
});