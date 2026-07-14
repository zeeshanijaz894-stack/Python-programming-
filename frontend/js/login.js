// Login functionality
const loginForm = document.getElementById('loginForm');

if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        try {
            // For demo purposes, show validation
            if (email && password) {
                // Save to localStorage
                localStorage.setItem('user', JSON.stringify({
                    email: email,
                    loggedIn: true
                }));
                
                // Redirect to dashboard
                window.location.href = 'dashboard.html';
            }
        } catch (error) {
            console.error('Login error:', error);
        }
    });
}