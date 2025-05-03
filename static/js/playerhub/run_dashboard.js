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

            if (responseData.mode === 'WIPECOUNTER') {
                await fetchAndDisplayWipecounterDetails();
            }


        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }

    async function fetchAndDisplayWipecounterDetails() {
        try {
            const response = await fetch(`/api/runs/${runId}/wipecounters/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            })
            const responseData = await response.json();

            if (!response.ok) {
                const errorText = Object.values(responseData).flat().join(', ');
                alert(`Error: ${errorText}`);
                return;
            }

            const tableBody = document.querySelector('.wipecounter-table-body');
            tableBody.innerHTML = '';

            responseData.forEach(segment => {
                console.log(segment);
                const row = document.createElement('tr');
                const nameCell = document.createElement('td');
                const countCell = document.createElement('td');
                const finishedCell = document.createElement('td');
                const controllerCell = document.createElement('td');
                nameCell.textContent = segment.segment_name;
                finishedCell.textContent = segment.is_finished ? 'Finished' : 'In Progress';
                countCell.textContent = segment.count;
                if (segment.is_finished === false){
                    controllerCell.innerHTML = `
                        <button class="increment-btn btn-small" data-id="${segment.id}">+</button>
                        <button class="decrement-btn btn-small" data-id="${segment.id}">-</button>
                        <button class="finish-btn btn-small" data-id="${segment.id}">Finished</button>
                    `;
                }

                row.appendChild(nameCell);
                row.appendChild(finishedCell);
                row.appendChild(countCell);
                row.appendChild(controllerCell);
                tableBody.appendChild(row);
            })

        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }

    await fetchAndDisplayRunDetails();
})