document.addEventListener("DOMContentLoaded", async() => {
    const runId = window.location.pathname.split('/')[3];
    const segmentsDiv = document.querySelector('#segments');
    const gameTitle = document.getElementById('game-title');
    const runName = document.getElementById('run-name');
    const overallTime = document.getElementById('overall-time');
    const runStatus = document.getElementById('run-status');
    const allSegments = [];
    const overlayActiveTimers = {};

    const socket = new WebSocket('ws://' + window.location.host + `/ws/overlay/runs/${runId}/timer/`);

    socket.onopen = () => console.log('[Overlay WS] Connected');
    socket.onerror = (e) => console.error('[Overlay WS] Error', e);
    socket.onclose = (e) => console.warn('[Overlay WS] Closed', e);

    socket.onmessage = (e) => {
        const data = JSON.parse(e.data);
        console.log('[Overlay WS] Message', data);

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

            case 'new_segment':
                allSegments.push({
                    id: Number(data.segment_id),
                    segment_name: data.segment_name,
                    elapsed_time: Number(data.elapsed_time),
                    is_finished: data.is_finished
                });

                renderSegmentList();
                updateOverall();
                break;

            case 'run_finished':
                document.getElementById('run-status').textContent = 'Finished';
                break;


            default:
                console.warn('[Overlay WS] Unknown type:', data.type);
        }
    }

    await fetchAndDisplayRun();

    async function fetchAndDisplayRun() {
        try {
            const responseRun = await fetch(`/public-api/runs/${runId}/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            const responseDataRun = await responseRun.json();

            gameTitle.textContent = responseDataRun.game_name;
            runName.textContent = responseDataRun.name;

            if (!responseRun.ok) {
                const errorText = Object.values(responseDataRun).flat().join(', ');
                alert(`Error: ${errorText}`);
                return;
            }

            const timerRes = await fetch(`/public-api/runs/${runId}/timers/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            const timerData = await timerRes.json();
            if (!timerRes.ok) {
                const errorText = Object.values(timerData).flat().join(', ');
                alert(`Error: ${errorText}`);
                return;
            }

            allSegments.push(...timerData);
            renderSegmentList();
            updateOverall();

        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }

    function renderSegmentList() {
        const lastSegments = allSegments.slice(-10);
        segmentsDiv.innerHTML = '';

        lastSegments.forEach(seg => {
            const row = document.createElement('tr');
            row.id = `segment-${seg.id}`;
            row.innerHTML = `
                <td class="segment-name">${seg.segment_name}</td>
                 <td class="segment-time" data-id="${seg.id}" data-time-raw="${seg.elapsed_time}">${formatTime(Number(seg.elapsed_time))}</td>
            `;
            segmentsDiv.appendChild(row);
        });
    }

    function updateOverall() {
        const cells = document.querySelectorAll('.segment-time');
        let total = 0;

        cells.forEach(cell => {
            const raw = parseFloat(cell.dataset.timeRaw || 0);
            total += isNaN(raw) ? 0 : raw;
        });

        overallTime.textContent = formatTime(total);
    }

    function handlePauseTimer(data) {
        const segmentId = Number(data.segment_id);
        if (overlayActiveTimers[segmentId]) {
            clearInterval(overlayActiveTimers[segmentId]);
            delete overlayActiveTimers[segmentId];
        }
        const seg = allSegments.find(s => Number(s.id) === Number(data.segment_id));
        if (seg) {
            seg.elapsed_time = Number(data.elapsed_time);

        const cell = document.querySelector(`[data-id="${segmentId}"]`);
        if (cell) {
            cell.dataset.timeRaw = seg.elapsed_time;
            cell.textContent = formatTime(seg.elapsed_time);
        }
            renderSegmentList();
            updateOverall();
        }
    }

    function handleFinishTimer(data) {
        const segmentId = Number(data.segment_id);

        if (overlayActiveTimers[segmentId]) {
            clearInterval(overlayActiveTimers[segmentId]);
            delete overlayActiveTimers[segmentId];
        }

        const seg = allSegments.find(s => Number(s.id) === Number(data.segment_id));
        if (seg) {
            seg.elapsed_time = Number(data.elapsed_time ?? seg.elapsed_time);
            seg.is_finished = true;
            renderSegmentList();
            updateOverall();
        }
    }

    function handleStartTimer(data) {
        const segmentId = Number(data.segment_id);
        const startTime = new Date(data.started_at).getTime();
        const baseElapsed = Number(data.elapsed_time || 0);

        if (overlayActiveTimers[segmentId]) {
            clearInterval(overlayActiveTimers[segmentId]);
        }

        overlayActiveTimers[segmentId] = setInterval(() => {
            const elapsed = (Date.now() - startTime) / 1000 + baseElapsed;

            const seg = allSegments.find(s => Number(s.id) === segmentId);
            if (seg) {
                seg.elapsed_time = elapsed;
                renderSegmentList();
                updateOverall();
            }
        },200);
    }

    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        const tenths = Math.floor((seconds % 1) * 10);
        return `${minutes}:${secs}.${tenths}`;
    }


})