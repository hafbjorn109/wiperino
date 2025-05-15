document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem('access');
    const runId = window.location.pathname.split('/')[2];
    const controllerSections = document.querySelectorAll('.form-section');
    const exportButton = document.getElementById('export-btn');

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

    /**
     * Handles creating URL to communication with API to generate XLSX file with run data.
     */
    exportButton.addEventListener('click', async (e) => {
        e.preventDefault();

        try {
            const response = await fetch(`/api/runs/${runId}/export/`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok){
                const errorData = await response.json();
                const errorText = Object.values(errorData).flat().join(', ');
                alert(`Export failed: ${errorText}`);
                return;
            }

            const blob = await response.blob();
            const filename = response.headers.get('Content-Disposition')?.
            split('filename=')[1]?.replace(/"/g, '') || `export_${runId}.xlsx`;
            const url = window.URL.createObjectURL(blob)

            const tempLink = document.createElement('a');
            tempLink.href = url;
            tempLink.setAttribute('download', filename);
            document.body.appendChild(tempLink);
            tempLink.click();
            tempLink.remove();
            window.URL.revokeObjectURL(url);

        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    })

    // Initial data load
    await fetchAndDisplayRunDetails();
})