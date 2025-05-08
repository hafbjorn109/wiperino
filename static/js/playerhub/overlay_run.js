document.addEventListener('DOMContentLoaded', async() => {
    const runId = window.location.pathname.split('/')[3];
    const segmentsDiv = document.querySelector('#segments');
    const gameTitle = document.getElementById('game-title');
    const runName = document.getElementById('run-name');
    const overallWipes = document.getElementById('overall-wipes');
    const runStatus = document.getElementById('run-status');
    const allSegments = [];

    const socket = new WebSocket(
        'ws://' + window.location.host + `/ws/overlay/runs/${runId}/`
    );

    socket.onopen = () => console.log("WebSocket connected");
    socket.onerror = (e) => console.error("WebSocket error:", e);
    socket.onclose = (e) => console.warn("WebSocket closed:", e);

    //
    socket.onmessage = (e) => {
        const data = JSON.parse(e.data);

        switch(data.type) {
            case 'wipe_update':
                updateSegmentCount(data.segment_id, data.count);
                updateOverall();
                break;

            case 'segment_finished':
                finishSegment(data.segment_id);
                break;

            case 'new_segment':
                allSegments.push(data);
                renderSegment(data);
                updateOverall();
                break;

            case 'run_finished':
                runStatus.textContent = 'Finished';
                break;
        }
    }

    async function fetchAndDisplayRunDetails() {
        try {
            const responseRun = await fetch(`/public-api/runs/${runId}/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            const responseDataRun = await responseRun.json();
            if (!responseRun.ok) {
                const errorText = Object.values(responseDataRun).flat().join(', ');
                alert(`Error: ${errorText}`);
                return;
            }

            gameTitle.textContent = responseDataRun.game_name;
            runName.textContent = responseDataRun.name;

            const responseWipecounter = await fetch(`/public-api/runs/${runId}/wipecounters/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            })

            const responseDataWipecounter = await responseWipecounter.json();
            if (!responseWipecounter.ok) {
                const errorText = Object.values(responseDataWipecounter).flat().join(', ');
                alert(`Error: ${errorText}`);
                return;
            }

            allSegments.push(...responseDataWipecounter);
            renderSegment();
            updateOverall();

        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }

    function renderSegment() {
        const lastSegments = allSegments.slice(-10);
        segmentsDiv.innerHTML = '';
        lastSegments.forEach(seg => {
            const row = document.createElement('tr');
            row.id = `segment-${seg.id}`;
            row.innerHTML = `
                <td class="segment-name">${seg.segment_name}</td>
                <td class="segment-count" data-id="${seg.id}">${Number(seg.count)}</td>
            `;
            segmentsDiv.appendChild(row);
        });
    }

    function updateSegmentCount(segmentId, count) {
        const segmentEl = document.querySelector(`[data-id="${segmentId}"]`);
        if (segmentEl) {
            segmentEl.textContent = count;
        } else {
            console.warn('Segment not found for update:', segmentId);
        }


        const seg = allSegments.find(s => s.id === Number(segmentId));
        if (seg) seg.count = Number(count);
    }

    function finishSegment(segmentId) {
        const segment = document.getElementById(`segment-${segmentId}`);
        if (segment) {
            if (segment.querySelector('.segment-status')) {
                segment.querySelector('.segment-status').textContent = 'Finished';
            }
        }
    }

    function updateOverall() {
                const total = allSegments.reduce((sum, seg) => sum + seg.count, 0);
        overallWipes.textContent = `${total}`;
    }


    await fetchAndDisplayRunDetails();
});