document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById('forgot-password-form');
    const errorDiv = document.getElementById('error-msg');
    const emailInput = document.getElementById('email');
    const successMsg = document.getElementById('success-msg');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        errorDiv.textContent = '';
        successMsg.textContent = '';

        try {
            const response = await fetch('/api/password-reset-request/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: emailInput.value
                })
            });

            const data = await response.json();
            if(!response.ok) {
                const errorText = Object.values(data).flat().join(', ');
                errorDiv.textContent = `Error: ${errorText}`;
                return;
            }

            successMsg.textContent = 'Check your email for a password reset link.';
            emailInput.value = '';
        } catch (err) {
            console.error(err);
            errorDiv.textContent = 'Something went wrong. Try again.';
        }
    })
})