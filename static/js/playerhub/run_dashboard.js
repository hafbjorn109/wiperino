document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem('access');
    const runTitle = document.getElementById('run-info');
    const gameTitle = document.getElementById('game-info');
    const runId = window.location.pathname.split('/')[2];

    async function fetchAndDisplayRunDetails() {
        try {
            const response = await fetch(`/api/runs/${runId}/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });
            const responseData = await response.json();
            console.log(responseData);

            if(!response.ok) {
                const errorText = Object.values(responseData).flat().join(', ');
                alert(`Error: ${errorText}`);
                return;
            }

            runTitle.textContent = responseData.name;
            gameTitle.textContent = responseData.game;

        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }

    await fetchAndDisplayRunDetails();
})