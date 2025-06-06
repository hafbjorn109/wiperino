document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem('access');
    const runId = window.location.pathname.split('/')[2];
    const tableBody = document.querySelector('.wipecounter-table-body');
    const overallWipesCountCell = document.getElementById('overall-wipes');
    const addSegmentButton = document.getElementById('add-segment-btn');
    const finishRunButton = document.getElementById('finish-run-btn');
    const controllerSections = document.querySelectorAll('.form-section');
    const obsUrlButton = document.getElementById('url-obs-btn');

    // Connect to WebSocket to receive live updates for the overlay
    const socket = new WebSocket(
        'ws://' + window.location.host + `/ws/runs/${runId}/?token=${token}`
    );

    socket.onopen = () => console.log("WebSocket connected");
    socket.onerror = (e) => console.error("WebSocket error:", e);
    socket.onclose = (e) => console.warn("WebSocket closed:", e);

    // Handle messages received via WebSocket
    socket.onmessage = (e) => {
        const data = JSON.parse(e.data);

        switch (data.type) {
            case 'new_segment':
                renderSegmentRow(data);
                recalculateWipes();
                break;

            case 'wipe_update':
                const allSegmentRows = document.querySelectorAll('.wipecounter-table-body tr');
                allSegmentRows.forEach(segmentRow => {
                    const id = segmentRow.querySelector('.btn-small')?.dataset?.id;
                    if (id && parseInt(id) === parseInt(data.segment_id)) {
                        const countCell = segmentRow.querySelector('td:nth-child(3)');
                        if (countCell) countCell.textContent = data.count;
                    }
                });
                recalculateWipes();
                break;

            case 'segment_finished':
                document.querySelectorAll('.wipecounter-table-body tr').forEach(row => {
                    const btns = row.querySelectorAll('.btn-small');
                    btns.forEach(btn => {
                        const id = btn.dataset?.id;
                        if (Number(id) === Number(data.segment_id)) {
                            const statusCell = row.querySelector('td:nth-child(2)');
                            const controllerCell = row.querySelector('td:nth-child(4)');
                            if (statusCell) statusCell.textContent = 'Finished';
                            if (controllerCell) controllerCell.innerHTML = '';
                        }
                    });
                });
                break;

            case 'run_finished':
                controllerSections.forEach(section => {
                    section.classList.add('hidden');
                });
                document.getElementById('overall-status').textContent = 'Finished';

                disableAllControllers()
                break;
        }
    }

    /**
     * Fetches wipe counter segments from the API and renders them in the table.
     * Calculates and updates the overall wipe count.
     */
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
            let overallWipesCount = 0;

            responseData.forEach(segment => {
                overallWipesCount += renderSegmentRow(segment);
            });

            overallWipesCountCell.textContent = overallWipesCount;

        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }

    /**
     * Handles button clicks in the wipe counter table: increment, decrement, finish.
     */
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

                    socket.send(JSON.stringify({
                        type: 'wipe_update',
                        segment_id: segmentId,
                        count: newCount,
                    }));

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

                    socket.send(JSON.stringify({
                        type: 'wipe_update',
                        segment_id: segmentId,
                        count: newCount,
                    }));

                } catch (err) {
                    console.error(err);
                    alert('Something went wrong. Try again.');
                }
            }
            if (e.target.id === 'finish-segment-btn') {
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

                    socket.send(JSON.stringify({
                        type: 'segment_finished',
                        segment_id: segmentId,
                    }));

                } catch (err) {
                    console.error(err);
                    alert('Something went wrong. Try again.');
                }
            }
        }
    }


    /**
     * Sends a POST request to add a new segment to the table.
     */
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

            socket.send(JSON.stringify({
                type: 'new_segment',
                segment_id: responseData.id,
                segment_name: responseData.segment_name,
                count: responseData.count,
                is_finished: responseData.is_finished,
            }));

            document.getElementById('new-segment').value = '';
        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }

    /**
     * Sends a PATCH request to mark a run as finished.
     */
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

            await closeAllSegments();
            socket.send(JSON.stringify({
                type: 'run_finished',
            }));

        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }


    /**
     * Sends a PATCH request to mark all segments connected with run as finished.
     */
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

            // Changing status to 'finished' in all segments connected to the run
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


        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }

    function renderSegmentRow(data) {
        const row = document.createElement('tr');

        const nameCell = document.createElement('td');
        nameCell.textContent = data.segment_name;
        nameCell.classList.add('segment-name-cell');

        const finishedCell = document.createElement('td');
        finishedCell.textContent = data.is_finished ? 'Finished' : 'In Progress';
        finishedCell.classList.add('hide-mobile');

        const countCell = document.createElement('td');
        countCell.textContent = data.count;

        const controllerCell = document.createElement('td');
        if (!data.is_finished) {
            controllerCell.innerHTML = `
                <div class="button-container">
                    <button id="increment-btn" class="btn-small" data-id="${data.segment_id || data.id}">+1</button>
                    <button id="decrement-btn" class="btn-small" data-id="${data.segment_id || data.id}">-1</button>
                    <button id="finish-segment-btn" class="btn-small" data-id="${data.segment_id || data.id}">Finish</button>
                </div>
            `;
        }

        row.appendChild(nameCell);
        row.appendChild(finishedCell);
        row.appendChild(countCell);
        row.appendChild(controllerCell);
        tableBody.appendChild(row);

        return data.count;
    }

    function recalculateWipes() {
        let total = 0;
        document.querySelectorAll(
            '.wipecounter-table-body tr td:nth-child(3)').
        forEach(cell => {
            total += parseInt(cell.textContent || 0);
        });
        overallWipesCountCell.textContent = total;
    }

    function disableAllControllers(){
        document.querySelectorAll('.wipecounter-table-body tr').forEach(row => {
        const controllerCell = row.querySelector('td:nth-child(4)');
        const statusCell = row.querySelector('td:nth-child(2)');
        if (controllerCell) controllerCell.innerHTML = '';
        if (statusCell) statusCell.textContent = 'Finished';
        });
    }

    function showObsUrl(){
        const url = window.location.origin + `/overlay/runs/${runId}/`;
        const obsUrl = document.getElementById('obs-url');
        obsUrl.value = url;
        obsUrl.classList.remove('hidden');
    }

    // Triggers actions after click on one of the buttons
    tableBody.addEventListener('click', (e) => wipecounterController(e));

    // Triggers function responsible for handling new segment request.
    addSegmentButton.addEventListener('click', () =>  addSegment());

    // Triggers function responsible for finishing run and connected segments.
    finishRunButton.addEventListener('click', () => finishRun());

    //Shows URL to copy-paste in OBS to activate overlay on stream
    obsUrlButton.addEventListener('click', () => {showObsUrl()});

    // Initial data load
    await fetchAndDisplayWipecounterDetails();
})