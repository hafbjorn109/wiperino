document.addEventListener("DOMContentLoaded", async() => {
    const token = localStorage.getItem('access');
    const tableBody = document.querySelector('.run-list-body');

    async function fetchAndDisplayRuns() {
        try {
            const response = await fetch('/api/runs/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });
            const responseData = await response.json();
            if(!response.ok) {
                const errorText = Object.values(responseData).flat().join(', ');
                alert(`Error: ${errorText}`);
                return;
            }
            tableBody.innerHTML = '';
            responseData.forEach(run => {
                const runRow = document.createElement('tr');
                const runNameCell = document.createElement('td');
                const gameCell = document.createElement('td');
                const modeCell = document.createElement('td');
                const statusCell = document.createElement('td');
                const controllerCell = document.createElement('td');
                const continueButton = document.createElement('button');
                const deleteButton = document.createElement('button');

                runNameCell.textContent = run.name;
                gameCell.textContent = run.game_name;
                modeCell.textContent = run.mode;
                statusCell.textContent = run.is_finished ? 'Finished' : 'In Progress';
                continueButton.type = 'button';
                continueButton.classList.add('continue-btn', 'btn-small');
                continueButton.dataset.id = run.id;
                continueButton.textContent = run.is_finished ? 'See results' : 'Continue';
                deleteButton.type = 'button';
                deleteButton.classList.add('delete-btn', 'btn-small');
                deleteButton.dataset.id = run.id;
                deleteButton.textContent = 'Delete';

                runRow.appendChild(runNameCell);
                runRow.appendChild(gameCell);
                runRow.appendChild(modeCell);
                runRow.appendChild(statusCell);
                controllerCell.appendChild(continueButton);
                controllerCell.appendChild(deleteButton);
                runRow.appendChild(controllerCell);
                tableBody.appendChild(runRow);
            })
        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }

    async function deleteRun(runId) {
        try {
            const response = await fetch(`/api/runs/${runId}/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });

            if(response.status === 204 || response.ok) {
                await fetchAndDisplayRuns();
                return;
            }
            alert(`Error`);

        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }



    tableBody.addEventListener('click', (e) => {
        if (e.target.classList.contains('continue-btn')) {
            window.location.href = `/runs/${e.target.dataset.id}/`;
        }

        if (e.target.classList.contains('delete-btn')) {
            if(window.confirm('Are you sure tou want to delete this run? This action cannot be undone.')) {
                deleteRun(e.target.dataset.id);
            }
        }
    })

    await fetchAndDisplayRuns()
});