// This file implements the contact form validation functionality to ensure user input is valid.

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('contact-form');
    const nameInput = document.getElementById('name');
    const emailInput = document.getElementById('email');
    const messageInput = document.getElementById('message');
    const submitButton = document.getElementById('submit');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        let valid = true;

        // Clear previous error messages
        clearErrors();

        // Validate name
        if (nameInput.value.trim() === '') {
            showError(nameInput, 'Name is required.');
            valid = false;
        }

        // Validate email
        if (emailInput.value.trim() === '') {
            showError(emailInput, 'Email is required.');
            valid = false;
        } else if (!validateEmail(emailInput.value.trim())) {
            showError(emailInput, 'Please enter a valid email address.');
            valid = false;
        }

        // Validate message
        if (messageInput.value.trim() === '') {
            showError(messageInput, 'Message is required.');
            valid = false;
        }

        // If valid, you can submit the form or perform further actions
        if (valid) {
            // Form submission logic here
            alert('Form submitted successfully!');
            form.reset();
        }
    });

    function showError(input, message) {
        const error = document.createElement('div');
        error.className = 'error-message';
        error.textContent = message;
        input.parentElement.appendChild(error);
    }

    function clearErrors() {
        const errorMessages = document.querySelectorAll('.error-message');
        errorMessages.forEach(function(error) {
            error.remove();
        });
    }

    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    }
});