// Handle form submissions and client-side validation for authentication
document.addEventListener("DOMContentLoaded", function() {
    // Login form handling
    const loginForm = document.querySelector("form[action*='login']");
    if (loginForm) {
        loginForm.addEventListener("submit", function(e) {
            e.preventDefault();
            const formData = new FormData(loginForm);
            
            fetch(loginForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/json'
                }
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    return response.json();
                }
            })
            .then(data => {
                if (data && data.error) {
                    showAuthError(data.error);
                }
            })
            .catch(error => {
                showAuthError("An error occurred during login");
            });
        });
    }

    // Create account form handling
    const createAccountForm = document.querySelector("form[action*='create_account']");
    if (createAccountForm) {
        createAccountForm.addEventListener("submit", function(e) {
            e.preventDefault();
            
            // Client-side validation
            const password = createAccountForm.querySelector('input[name="password"]').value;
            if (password.length < 8) {
                showAuthError("Password must be at least 8 characters");
                return;
            }

            const formData = new FormData(createAccountForm);
            
            fetch(createAccountForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/json'
                }
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    return response.json();
                }
            })
            .then(data => {
                if (data && data.error) {
                    showAuthError(data.error);
                }
            })
            .catch(error => {
                showAuthError("An error occurred during registration");
            });
        });
    }

    // Helper function to display errors
    function showAuthError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'auth-error';
        errorDiv.textContent = message;
        errorDiv.style.color = 'red';
        errorDiv.style.margin = '10px 0';
        
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            const existingError = form.querySelector('.auth-error');
            if (existingError) {
                form.removeChild(existingError);
            }
            form.prepend(errorDiv);
        });
    }
});