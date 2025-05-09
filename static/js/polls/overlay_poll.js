document.addEventListener('DOMContentLoaded', () => {
    const overlayToken = window.location.pathname.split('/')[3];
    const socket = new WebSocket(`ws://${window.location.host}/ws/polls/${overlayToken}/`);

    const questionEl = document.getElementById('overlay-question');
    const answersEl = document.getElementById('overlay-answers');

    socket.onopen = () => console.log('WebSocket connected');
    socket.onerror = (e) => console.error('WebSocket error:', e);
    socket.onclose = (e) => console.warn('WebSocket closed:', e);

    socket.onmessage = (e) => {
        try{
            const data = JSON.parse(e.data);
            console.log('Received:', data);
            if (data.type === 'publish_question') {
                const question = JSON.parse(data.question_data);

                questionEl.textContent = question.question;
                questionEl.classList.remove('hidden');

                answersEl.innerHTML = '';
                question.answers.forEach(answer => {
                    const li = document.createElement('li');
                    li.textContent = `${answer} - ${question.votes[answer] || 0} votes`;
                    answersEl.appendChild(li);
                });
                answersEl.classList.remove('hidden');
            }

            if (data.type === 'unpublish_question') {
                questionEl.textContent = '';
                questionEl.classList.add('hidden');
                answersEl.innerHTML = '';
                answersEl.classList.add('hidden');
            }
        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }
})