document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem('access');
    const runId = window.location.pathname.split('/')[2];
    const controllerSections = document.querySelectorAll('.form-section');

    /**
     * Fetches details about a specific run for the logged-in user and displays them in the table.
     * Disables a control panel if run is not active.
     */
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

            document.getElementById('run-info').textContent = responseData.name;
            document.getElementById('game-info').textContent = responseData.game_name;

            if (responseData.is_finished === true) {
               controllerSections.forEach(section => {
                   section.classList.add('hidden');
               });
            } else {
              controllerSections.forEach(section => {
                   section.classList.remove('hidden');
               });
            }

        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }

    // Initial data load
    await fetchAndDisplayRunDetails();
})