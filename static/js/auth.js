document.addEventListener('DOMContentLoaded', () => {
    const access = localStorage.getItem('access');
    const path = window.location.pathname;

    const isPublic = path.startsWith('/login') || path.startsWith('/register');

    if (!access) {
        if (!isPublic) {
            window.location.href = '/login/';
            console.log('No access token');
            return;
        }
    }
    const payload = JSON.parse(atob(access.split('.')[1]));

    const now = Math.floor(Date.now() / 1000);
    if (payload.exp < now) {
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        console.log('Token expired');
        window.location.href = '/login/';
    }
})