document.addEventListener('DOMContentLoaded', () => {
    const createPollButton = document.getElementById('create-poll-btn');
    const linksDiv = document.getElementById('links');
    const moderatorInput = document.getElementById('moderator-url');
    const viewerInput = document.getElementById('viewer-url');
    const overlayInput = document.getElementById('overlay-url');

    createPollButton.addEventListener('click', async() => {
        try {
            const response = await fetch('/api/polls/create_session/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            });
            if(!response.ok) {
                alert(`Failed to create session`);
                return
            }
            const data = await response.json();
            linksDiv.classList.remove('hidden');

            const base = window.location.origin;
            moderatorInput.value = base + data.moderator_url;
            viewerInput.value = base + data.viewer_url;
            overlayInput.value = base + data.overlay_url;
        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    });
});