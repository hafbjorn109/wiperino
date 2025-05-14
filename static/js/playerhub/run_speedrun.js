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
        console.log("[Timer WS] onmessage", data)

        switch (data.type) {
            case 'start_timer':
                console.log(`[Start] Segment ${data.segment_id} started at ${data.started_at}`);
                handleStartTimer(data);
                break;

            case 'pause_timer':
                console.log(`[Pause] Segment ${data.segment_id} paused at ${data.elapsed_time}s`);
                handlePauseTimer(data);
                break;

            case 'finish_timer':
                console.log(`[Finish] Segment ${data.segment_id} finished at ${data.elapsed_time}s`);
                handleFinishTimer(data);
                break;

            default:
                console.warn('[Timer WS] Unknown type:', data.type);
        }
    }

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
        timeCell.textContent = (data.elapsed_time || 0).toFixed(1);

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

    function timerController(e) {
        const segmentRow = e.target.closest('tr');
        const segmentId = e.target.dataset.id;
        if (!segmentId) return;

        const now = new Date().toISOString();

        if (e.target.classList.contains('start-btn')) {
            const timeCell = document.getElementById(`time-segment-${segmentId}`)
            const elapsed = parseFloat(timeCell.textContent || 0.0);
            const now = new Date().toISOString();

            socket.send(JSON.stringify({
                type: 'start_timer',
                segment_id: segmentId,
                started_at: now,
                elapsed_time: elapsed
            }));
            console.log('[WS] Sent start_timer', segmentId)
        }

        if (e.target.classList.contains('pause-btn')) {
            const timeCell = document.getElementById(`time-segment-${segmentId}`)
            const elapsed = parseFloat(timeCell.textContent || 0.0);
            socket.send(JSON.stringify({
                type: 'pause_timer',
                segment_id: segmentId,
                elapsed_time: elapsed
            }));
            console.log('[WS] Sent pause_timer', segmentId)
        }

        if (e.target.classList.contains('finish-btn')) {
            const timeCell = document.getElementById(`time-segment-${segmentId}`);
            const elapsed = parseFloat(timeCell.textContent || 0.0);
            socket.send(JSON.stringify({
                type: 'finish_timer',
                segment_id: segmentId,
                elapsed_time: elapsed
            }));
            console.log('[WS] Sent finish_timer', segmentId)
        }
    }

    function handleStartTimer(data) {
        const segmentId = data.segment_id;
        const timeCell = document.getElementById(`time-segment-${segmentId}`)
        if (!timeCell) return;

        if(activeTimers[segmentId]) {
            clearInterval(activeTimers[segmentId]);
        }

        let startTimestamp = new Date(data.started_at).getTime();
        let baseElapsed = data.elapsed_time || 0.0;

        activeTimers[segmentId] = setInterval(() => {
            const now = Date.now();
            const elapsed = (now - startTimestamp) / 1000 + baseElapsed;
            timeCell.textContent = elapsed.toFixed(1);
            recalculateOverall();
        }, 100)
    }

    async function handlePauseTimer(data) {
        const segmentId = data.segment_id;

        if (activeTimers[segmentId]) {
            clearInterval(activeTimers[segmentId]);
            delete activeTimers[segmentId];
        }

        const timeCell = document.getElementById(`time-segment-${segmentId}`)
        if (!timeCell) return;

        const currentTime = parseFloat(timeCell.textContent);
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

            console.log('[WS] Sent pause_timer', responseData)

        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }

    async function handleFinishTimer(data) {
        const segmentId = data.segment_id;

        if (activeTimers[segmentId]) {
            clearInterval(activeTimers[segmentId]);
            delete activeTimers[segmentId];
        }

        const timeCell = document.getElementById(`time-segment-${segmentId}`);
        if (!timeCell) return;

        const finalTime = parseFloat(timeCell.textContent);
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

            socket.send(JSON.stringify({
                type: 'finish_timer',
                segment_id: segmentId,
                elapsed_time: finalTime
            }));
            console.log('[WS] Sent finish_timer', segmentId, finalTime);

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

            await closeAllSegments();

            socket.send(JSON.stringify({
                type: 'run_finished'
            }));

        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }

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

    function recalculateOverall() {
        let total = 0.0;
        document.querySelectorAll('.timer-table-body tr td:nth-child(3)').forEach(cell => {
            total += parseFloat(cell.textContent || 0);
        });
        document.getElementById('overall-time').textContent = total.toFixed(1);
    }

    function showObsUrl() {
        const url = window.location.origin + `/overlay/runs/${runId}/`;
        const obsUrl = document.getElementById('obs-url');
        obsUrl.value = url;
        obsUrl.classList.remove('hidden');
    }

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

            renderSegmentRow(responseData);
            recalculateOverall();

            document.getElementById('new-segment').value = '';

        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }


    tableBody.addEventListener('click', (e) => timerController(e));

    addSegmentButton.addEventListener('click', () => addSegment());

    finishRunButton.addEventListener('click', () => finishRun());

    obsUrlButton.addEventListener('click', () => showObsUrl());

    await fetchAndDisplayTimerSegments();
})