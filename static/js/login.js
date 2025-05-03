document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById('login-form');
    const errorDiv = document.getElementById('error-msg');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorDiv.textContent = '';

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        try {
            const response = await fetch('/api/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            const responseData = await response.json();

            if (response.ok) {
                localStorage.setItem('access', responseData.access);
                localStorage.setItem('refresh', responseData.refresh);
                window.location.href = '/dashboard/';
            } else {
                const errorText = Object.values(responseData).flat().join(', ');
                errorDiv.textContent = `Login failed: ${errorText}`;
            }

        } catch (err) {
            errorDiv.textContent = 'Something went wrong. Try again.';
            console.error(err);
        }
    })
})