document.addEventListener("DOMContentLoaded", async() => {
    const token = localStorage.getItem('access');
    const runId = window.location.pathname.split('/')[2];
    const tableBody = document.querySelector('.timer-table-body');
    const addSegmentButton = document.getElementById('add-segment-btn');
    const finishRunButton = document.getElementById('finish-run-btn');
    const obsUrlButton = document.getElementById('url-obs-btn');

    const socket = new WebSocket(
        `ws://` + window.location.host + `/ws/runs/${runId}/timer/?token=${token}`);

    socket.onopen = () => console.log("WebSocket connected");
    socket.onerror = (e) => console.error("WebSocket error:", e);
    socket.onclose = (e) => console.warn("WebSocket closed:", e);

    const activeTimers = {};

    socket.onmessage = (e) => {
        const data = JSON.parse(e.data);

        switch (data.type) {
            case 'start_timer':
                handleStartTimer(data);
                break;

            case 'pause_timer':
                handlePauseTimer(data);
                break;

            case 'finish_timer':
                handleFinishTimer(data);
                break;

            case 'run_finished':
                handleRunFinished();
                break;

            case 'new_segment':
                renderSegmentRow(data);
                recalculateOverall();
                break;

            default:
                console.warn('[Timer WS] Unknown type:', data.type);
        }
    }

    /**
     * Renders a single segment row in the table.
     */
    function renderSegmentRow(data) {
        const row = document.createElement('tr');

        const nameCell = document.createElement('td');
        nameCell.textContent = data.segment_name;
        nameCell.classList.add('segment-name-cell');

        const statusCell = document.createElement('td');
        statusCell.textContent = data.is_finished ? 'Finished' : 'In progress';
        statusCell.classList.add('hide-mobile');

        const timeCell = document.createElement('td');
        timeCell.id = `time-segment-${data.segment_id || data.id}`;
        timeCell.setAttribute('data-time-raw', data.elapsed_time || 0);
        timeCell.textContent = formatTime(data.elapsed_time || 0);

        const controllerCell = document.createElement('td');
        if (!data.is_finished) {
            controllerCell.innerHTML = `
                <div class="button-container">
                    <button class="btn-small start-btn" data-id="${data.segment_id || data.id}">Start</button>
                    <button class="btn-small pause-btn" data-id="${data.segment_id || data.id}">Pause</button>
                    <button class="btn-small finish-btn" data-id="${data.segment_id || data.id}">Finish</button>
                </div>
            `;
        }

        row.appendChild(nameCell);
        row.appendChild(statusCell);
        row.appendChild(timeCell);
        row.appendChild(controllerCell);
        tableBody.appendChild(row);
    }

    /**
     * Fetches all timer segments for the current run and renders them in the table.
     * Also calculates the overall time.
     */
    async function fetchAndDisplayTimerSegments() {
        try {
            const response = await fetch(`/api/runs/${runId}/timers/`, {
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

            const tableBody = document.querySelector('.timer-table-body');
            tableBody.innerHTML = '';
            let overallTime = 0;

            responseData.forEach(segment => {
                renderSegmentRow(segment);
                overallTime += segment.elapsed_time || 0;
            })

            document.getElementById('overall-time').textContent = overallTime.toFixed(1);

        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }

    /**
     * Handles start, pause, and finish button clicks in the segment row.
     * Sends corresponding WebSocket messages.
     */
    function timerController(e) {
        const segmentId = e.target.dataset.id;
        if (!segmentId) return;

        const now = new Date().toISOString();

        if (e.target.classList.contains('start-btn')) {

            const timeCell = document.getElementById(`time-segment-${segmentId}`)
            const elapsed = parseFloat(timeCell.dataset.timeRaw || 0.0);
            const now = new Date().toISOString();

            socket.send(JSON.stringify({
                type: 'start_timer',
                segment_id: segmentId,
                started_at: now,
                elapsed_time: elapsed
            }));
        }

        if (e.target.classList.contains('pause-btn')) {
            const timeCell = document.getElementById(`time-segment-${segmentId}`)
            const elapsed = parseFloat(timeCell.dataset.timeRaw);
            socket.send(JSON.stringify({
                type: 'pause_timer',
                segment_id: segmentId,
                elapsed_time: elapsed
            }));
        }

        if (e.target.classList.contains('finish-btn')) {
            const timeCell = document.getElementById(`time-segment-${segmentId}`);
            const elapsed = parseFloat(timeCell.textContent || 0.0);
            socket.send(JSON.stringify({
                type: 'finish_timer',
                segment_id: segmentId,
                elapsed_time: elapsed
            }));
        }
    }

    /**
     * Starts a timer for a given segment.
     * Sets up setInterval and updates the UI.
     */
    function handleStartTimer(data) {
        const segmentId = data.segment_id;
        const timeCell = document.getElementById(`time-segment-${segmentId}`)
        if (!timeCell) return;

        if(activeTimers[segmentId]) {
            clearInterval(activeTimers[segmentId]);
        }

        let startTimestamp = new Date(data.started_at).getTime();
        let existingElapsed = parseFloat(timeCell.dataset.timeRaw || "0");
        let baseElapsed = (typeof data.elapsed_time === 'number') ? data.elapsed_time : existingElapsed;

        activeTimers[segmentId] = setInterval(() => {
            const now = Date.now();
            const elapsed = (now - startTimestamp) / 1000 + baseElapsed;
            timeCell.textContent = formatTime(elapsed);
            timeCell.dataset.timeRaw = `${elapsed}`;
            recalculateOverall();
        }, 100)
    }

    /**
     * Pauses a timer and sends updated elapsed_time to the backend via PATCH.
     */
    async function handlePauseTimer(data) {
        const segmentId = data.segment_id;

        if (activeTimers[segmentId]) {
            clearInterval(activeTimers[segmentId]);
            delete activeTimers[segmentId];
        }

        const timeCell = document.getElementById(`time-segment-${segmentId}`)
        if (!timeCell) return;

        const currentTime = parseFloat(timeCell.dataset.timeRaw || "0");
        if (isNaN(currentTime)) return;

        try {
            const response = await fetch(`/api/runs/${runId}/timers/${segmentId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    elapsed_time: currentTime
                })
            })
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
    }

    /**
     * Finishes a timer segment, clears interval, updates backend and UI.
     */
    async function handleFinishTimer(data) {
        const segmentId = data.segment_id;

        if (activeTimers[segmentId]) {
            clearInterval(activeTimers[segmentId]);
            delete activeTimers[segmentId];
        }

        const timeCell = document.getElementById(`time-segment-${segmentId}`);
        if (!timeCell) return;

        const finalTime = parseFloat(timeCell.dataset.timeRaw || "0");
        if (isNaN(finalTime)) return;

        try {

            const response = await fetch(`/api/runs/${runId}/timers/${segmentId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    elapsed_time: finalTime,
                    is_finished: true
                })
            });

            const responseData = await response.json();
            if (!response.ok) {
                const errorText = Object.values(responseData).flat().join(', ');
                alert(`Error: ${errorText}`);
                return;
            }

            const row = timeCell.closest('tr');
            const statusCell = row.querySelector('td:nth-child(2)');
            const controllerCell = row.querySelector('td:nth-child(4)');

            if (statusCell) statusCell.textContent = 'Finished';
            if (controllerCell) controllerCell.innerHTML = '';

        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }

    /**
     * Finishes the entire run and all its segments.
     * Updates backend and notifies all clients via WebSocket.
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
                type: 'run_finished'
            }));

        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }

    /**
     * Closes all segment timers by sending PATCH with is_finished = true.
     */
    async function closeAllSegments() {
        try {
            const response = await fetch(`/api/runs/${runId}/timers/`, {
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

            const finishCalls = responseData.map(async (segment) => {
                return fetch(`/api/runs/${runId}/timers/${segment.id}/`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        is_finished: true
                    })
                });
            });

            await Promise.all(finishCalls);

        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }



    /**
     * Recalculates total elapsed time of all visible segments and updates UI.
     */
    function recalculateOverall() {
        let total = 0.0;
        document.querySelectorAll('.timer-table-body tr td:nth-child(3)').forEach(cell => {
            const raw = parseFloat(cell.dataset.timeRaw || 0);
            total += isNaN(raw) ? 0 : raw;
        });
        document.getElementById('overall-time').textContent = formatTime(total);
    }

    /**
     * Shows the OBS overlay URL input field with prefilled value.
     */
    function showObsUrl() {
        const url = window.location.origin + `/overlay/runs/${runId}/timer/`;
        const obsUrl = document.getElementById('obs-url');
        obsUrl.value = url;
        obsUrl.classList.remove('hidden');
    }

    /**
     * Adds a new timer segment via POST and broadcasts it via WebSocket.
     */
    async function addSegment() {
        const segmentNameInput = document.getElementById('new-segment').value;

        try {
            const response = await fetch(`/api/runs/${runId}/timers/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    "segment_name": segmentNameInput,
                    "elapsed_time": 0.0,
                    "is_finished": false
                })
            });

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
                elapsed_time: responseData.elapsed_time,
                is_finished: responseData.is_finished
            }));

            document.getElementById('new-segment').value = '';

        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }

    /**
     * Handles UI updates when the run is marked as finished.
     * Disables controls and sets all statuses to "Finished".
     */
    function handleRunFinished() {
        document.querySelectorAll('.form-section').forEach(section => {
            section.classList.add('hidden');
        });

        document.getElementById('overall-status').textContent = 'Finished';

        document.querySelectorAll('.timer-table-body tr').forEach(row => {
            const controllerCell = row.querySelector('td:nth-child(4)');
            const statusCell = row.querySelector('td:nth-child(2)');
            if (controllerCell) controllerCell.innerHTML = '';
            if (statusCell) statusCell.textContent = 'Finished';
        });
    }

    /**
     * Handles time formatting for MM:SS:TT
     */
    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        const tenths = Math.floor((seconds % 1) * 10);
        return `${minutes}:${secs}.${tenths}`;
    }


    /**
     * Handles click events for segment controls (Start, Pause, Finish).
     */
    tableBody.addEventListener('click', (e) => timerController(e));

    /**
     * Handles click on "Add Segment" button to create and broadcast new segment.
     */
    addSegmentButton.addEventListener('click', () => addSegment());


    /**
     * Handles click on "Finish Run" button to mark run and segments as finished.
     */
    finishRunButton.addEventListener('click', () => finishRun());


    /**
     * Handles click on "OBS URL" button to show prefilled overlay URL.
     */
    obsUrlButton.addEventListener('click', () => showObsUrl());

    /**
     * Fetches and displays existing timer segments when the page loads.
     */
    await fetchAndDisplayTimerSegments();
})