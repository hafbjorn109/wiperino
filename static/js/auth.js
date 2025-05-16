document.addEventListener('DOMContentLoaded', () => {
    const access = localStorage.getItem('access');
    const path = window.location.pathname;

    const isPublic = path.startsWith('/login') || path.startsWith('/register');

    if (!access) {
        if (!isPublic) {
            window.location.href = '/login/';
            return;
        }
    }
    const payload = JSON.parse(atob(access.split('.')[1]));

    const now = Math.floor(Date.now() / 1000);
    if (payload.exp < now) {
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        window.location.href = '/login/';
    }

    async function refreshToken() {
        const refresh = localStorage.getItem('refresh');
        if (!refresh) return;

        try {
            const response = await fetch('/api/token/refresh/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    refresh: refresh
                })
            });
            if (!response.ok) {
                localStorage.removeItem('access');
                localStorage.removeItem('refresh');
                window.location.href = '/login/';
                return;
            }
            const responseData = await response.json();
            localStorage.setItem('access', responseData.access);
        } catch(err) {
            console.error(err);
        }
    }

    setInterval(refreshToken, 180000);
})