document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById('register-form');
    const errorDiv = document.getElementById('error-msg');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorDiv.textContent = '';

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        try {
            const registerResponse = await fetch('/api/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

        const registerData = await registerResponse.json();

        if (!registerResponse.ok) {
            const errorText = Object.values(registerData).flat().join(', ');
            errorDiv.textContent = `Error: ${errorText}`;
            return;
        }

        const loginResponse = await fetch('/api/login/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              username: data.username,
              password: data.password
            })
        });


        const loginData = await loginResponse.json();

        if (loginResponse.ok) {
            localStorage.setItem('access', loginData.access);
            localStorage.setItem('refresh', loginData.refresh);
            window.location.href = '/dashboard/';
        } else {
            errorDiv.textContent = 'Registered, but failed to log in.';
        }

        } catch (error) {
          errorDiv.textContent = 'Something went wrong. Try again.';
          console.error(error);
        }
    });
})
