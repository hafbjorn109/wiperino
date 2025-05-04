document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem('access');
    const runId = window.location.pathname.split('/')[2];
    const tableBody = document.querySelector('.wipecounter-table-body');
    const overallWipesCountCell = document.getElementById('overall-wipes');
    const addSegmentButton = document.getElementById('add-segment-btn');
    const finishRunButton = document.getElementById('finish-run-btn');

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

            tableBody.innerHTML = '';

            let overallWipesCount = parseInt(overallWipesCountCell.textContent);

            responseData.forEach(segment => {
                console.log(segment);
                const row = document.createElement('tr');
                const nameCell = document.createElement('td');
                const countCell = document.createElement('td');
                const finishedCell = document.createElement('td');
                const controllerCell = document.createElement('td');
                nameCell.textContent = segment.segment_name;
                nameCell.classList.add('segment-name-cell');
                finishedCell.textContent = segment.is_finished ? 'Finished' : 'In Progress';
                finishedCell.classList.add('hide-mobile');
                countCell.textContent = segment.count;
                overallWipesCount += segment.count;
                overallWipesCountCell.textContent = overallWipesCount;
                if (segment.is_finished === false){
                    controllerCell.innerHTML = `
                        <div class="button-container">
                            <button id="increment-btn" class="btn-small" data-id="${segment.id}">+1</button>
                            <button id="decrement-btn" class="btn-small" data-id="${segment.id}">-1</button>
                            <button id="finish-segment-btn" class="btn-small" data-id="${segment.id}">Finish</button>
                        </div>
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

    async function wipecounterController(e) {
        const segmentRow = e.target.closest('tr');
        const segmentId = e.target.dataset.id;

        if (!segmentId) return;

        if (e.target.classList.contains('btn-small')) {
            if (e.target.id === 'increment-btn') {
                const countCell = segmentRow.querySelector('td:nth-child(3)');
                const currentCount = parseInt(countCell.textContent);
                const newCount = currentCount + 1

                try {
                    const response = await fetch(`/api/runs/${runId}/wipecounters/${segmentId}/`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        count: newCount
                    })
                });
                    const responseData = await response.json();

                    if (!response.ok) {
                        const errorText = Object.values(responseData).flat().join(', ');
                        alert(`Error: ${errorText}`);
                        return;
                    }
                    countCell.textContent = responseData.count;
                    overallWipesCountCell.textContent = `${parseInt(overallWipesCountCell.textContent) + 1}`;
                    } catch (err) {
                        console.error(err);
                        alert('Something went wrong. Try again.');
                    }
            }
            if (e.target.id === 'decrement-btn') {
                const countCell = segmentRow.querySelector('td:nth-child(3)');
                const currentCount = parseInt(countCell.textContent);
                if (currentCount === 0) return;
                const newCount = currentCount - 1
                try {
                    const response = await fetch(`/api/runs/${runId}/wipecounters/${segmentId}/`, {
                        method: 'PATCH',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({
                        count: newCount
                        })
                    })
                    const responseData = await response.json();
                    if (!response.ok) {
                        const errorText = Object.values(responseData).flat().join(', ');
                        alert(`Error: ${errorText}`);
                        return;
                    }
                    countCell.textContent = responseData.count;
                    overallWipesCountCell.textContent = `${parseInt(overallWipesCountCell.textContent) - 1}`;
                } catch (err) {
                    console.error(err);
                    alert('Something went wrong. Try again.');
                }
            }
            if (e.target.id === 'finish-segment-btn') {
                const statusCell = segmentRow.querySelector('td:nth-child(2)');
                const controllerCell = segmentRow.querySelector('td:nth-child(4)');

                try {
                    const response = await fetch(`/api/runs/${runId}/wipecounters/${segmentId}/`, {
                        method: 'PATCH',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({
                            is_finished: true
                        })
                    })

                    const responseData = await response.json();
                    if (!response.ok) {
                        const errorText = Object.values(responseData).flat().join(', ');
                        alert(`Error: ${errorText}`);
                        return;
                    }
                    statusCell.textContent = 'Finished';
                    controllerCell.innerHTML = '';
                } catch (err) {
                    console.error(err);
                    alert('Something went wrong. Try again.');
                }
            }
        }
    }

    async function addSegment() {
        const segmentNameInput = document.getElementById('new-segment').value;

        try {
            const response = await fetch(`/api/runs/${runId}/wipecounters/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    "segment_name": segmentNameInput,
                    "count": 0,
                    "is_finished": false,
                    "run": runId,
                })
            })
            const responseData = await response.json();
            if (!response.ok) {
                const errorText = Object.values(responseData).flat().join(', ');
                alert(`Error: ${errorText}`);
                return;
            }

            const row = document.createElement('tr');
            const nameCell = document.createElement('td');
            const countCell = document.createElement('td');
            const finishedCell = document.createElement('td');
            const controllerCell = document.createElement('td');

            nameCell.textContent = segmentNameInput;
            finishedCell.textContent = 'In Progress';
            finishedCell.classList.add('hide-mobile');
            countCell.textContent = `0`;
            controllerCell.innerHTML = `
                <div class="button-container">
                    <button id="increment-btn" class="btn-small" data-id="${responseData.id}">+1</button>
                    <button id="decrement-btn" class="btn-small" data-id="${responseData.id}">-1</button>
                    <button id="finish-segment-btn" class="btn-small" data-id="${responseData.id}">Finish</button>
                </div>
            `;
            row.appendChild(nameCell);
            row.appendChild(finishedCell);
            row.appendChild(countCell);
            row.appendChild(controllerCell);
            tableBody.appendChild(row);

            document.getElementById('new-segment').value = '';
        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }

    async function finishRun() {
        try {
            const response = await fetch(`/api/runs/${runId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    is_finished: true
                })
            });
            const responseData = await response.json();

            if (!response.ok) {
                const errorText = Object.values(responseData).flat().join(', ');
                alert(`Error: ${errorText}`);
                return;
            }
        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
        await closeAllSegments();
    }

    async function closeAllSegments() {

        try {
            const response = await fetch(`/api/runs/${runId}/wipecounters/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
            const responseData = await response.json();
            if (!response.ok) {
                const errorText = Object.values(responseData).flat().join(', ');
                alert(`Error: ${errorText}`);
                return;
            }

            const finishRun = responseData.map(async(segment) => {
                const response = await fetch(`/api/runs/${runId}/wipecounters/${segment.id}/`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        is_finished: true
                    })
                });
                    const responseData = await response.json();
                    if (!response.ok) {
                        const errorText = Object.values(responseData).flat().join(', ');
                        alert(`Error: ${errorText}`);
                        return;
                    }
            })

            await Promise.all(finishRun);
            await fetchAndDisplayWipecounterDetails();


        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }

    tableBody.addEventListener('click', async(e) => {
        await wipecounterController(e);
    })

    addSegmentButton.addEventListener('click', async() => {
        await addSegment();
    })

    finishRunButton.addEventListener('click', async() => {
        await finishRun();
    })


    await fetchAndDisplayWipecounterDetails();
})