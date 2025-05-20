document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('reset-password-form');
    const errorDiv = document.getElementById('error-msg');
    const token = window.location.pathname.split('/')[3];
    const uid = window.location.pathname.split('/')[2];

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorDiv.textContent = '';

        const password1 = document.getElementById('password1').value;
        const password2 = document.getElementById('password2').value;

        try {
            const response = await fetch(`/api/password-reset-confirm/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    uid: uid,
                    token: token,
                    password: password1,
                    password2: password2
                })
            });

            const data = await response.json();
            if (!response.ok) {
                const errorText = Object.values(data).flat().join(', ');
                errorDiv.textContent = `Error: ${errorText}`;
                return;
            }

            alert('Password reset successful. Redirecting to login page.')
            window.location.href = '/login/';

        } catch (err) {
            console.error(err);
            errorDiv.textContent = 'Something went wrong. Try again.';
        }
    })
})