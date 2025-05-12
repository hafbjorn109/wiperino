document.addEventListener('DOMContentLoaded', async() => {
    const viewerToken = window.location.pathname.split('/')[3];
    const pollsContainer = document.getElementById('polls');

    const voterIdKey = 'voter_id';
    let voterId = localStorage.getItem(voterIdKey);
    if (!voterId) {
        voterId = crypto.randomUUID();
        localStorage.setItem(voterIdKey, voterId);
    }

    const votedKey = 'voted_questions';
    const votedQuestions = JSON.parse(localStorage.getItem(votedKey) || '{}');

    const socket = new WebSocket('ws://' + window.location.host + `/ws/polls/${viewerToken}/`);
    socket.onopen = () => console.log('WebSocket connected');
    socket.onerror = e => console.error('WebSocket connection error', e);
    socket.onclose = e => console.warn('WebSocket closed:', e);

    socket.onmessage = e => {
        try {
            const data = JSON.parse(e.data);
            if (data.type === 'error') {
                console.error('Error occurred:', data.error);
                alert('Error occurred: ' + (data.error.message || JSON.stringify(data.error)));
            }

            if (data.type === 'new_question') {
                console.log('[WS] New question payload:', data.question);
                renderQuestion(data.question);
            }

            if (data.type === 'vote_update') {
                alert('Your votes have been submitted!');
                window.location.reload();
            }

            if (data.type === 'delete_question') {
                const question = document.getElementById(data.question_id);
                if (question) question.remove();
            }

        } catch (err) {
            console.error('Error occurred:', err);
            alert('Error occurred: ' + (err.message || JSON.stringify(err)));
        }
    };

    async function loadQuestions() {
        try {
            const response = await fetch(`/api/polls/v/${viewerToken}/`);
            const questions = await response.json();
            if (!response.ok){
                alert(`Failed to get question`);
                return;
            }
            questions.forEach(renderQuestion);
        } catch (err) {
            console.error('Error occurred:', err);
            alert('Error occurred: ' + (err.message || JSON.stringify(err)));
        }
    }

    function renderQuestion(q) {
        if (document.getElementById(q.id)) return;
        const div = document.createElement('div');
        div.className = 'question-block';
        div.id = q.id;
        const hasVoted = votedQuestions[q.id];

        div.innerHTML = `
          <h3>${q.question}</h3>
          ${
            hasVoted
              ? `<p style="opacity: 0.7; font-style: italic;">Your answer to this question has been submitted.</p>`
              : q.answers
                  .map(ans => `
                    <label>
                      <input type="radio" name="q-${q.id}" value="${ans}" /> ${ans}
                    </label><br>
                  `).join('')
          }
          <hr>
        `;

        pollsContainer.appendChild(div);
    }

    document.getElementById('poll-form').addEventListener('submit', e => {
        e.preventDefault();
        const votes = {};
        const inputs = document.querySelectorAll('input[type=radio]:checked');

        inputs.forEach(input => {
            const qid = input.name.replace('q-', '');
            if (!votedQuestions[qid]) {
            votes[qid] = input.value;
            }
        });

        if (Object.keys(votes).length === 0) {
          alert('No new votes selected.');
          return;
        }

        console.log('VOTING PAYLOAD:', {
          type: 'vote',
          voter_id: voterId,
          votes: votes
        });

        Object.entries(votes).forEach(([question_id, answer]) => {
            socket.send(JSON.stringify({
                type: 'vote',
                voter_id: voterId,
                question_id,
                answer
            }));
        })

        Object.keys(votes).forEach(qid => {
            votedQuestions[qid] = true
            const questionDiv = document.getElementById(qid);
            if (questionDiv) {
                questionDiv.innerHTML = `
                    <h3>${questionDiv.querySelector('h3')?.textContent || ''}</h3>
                    <p style="opacity: 0.7; font-style: italic;">Your answer to this question has been submitted.</p>
                    <hr>
                `;
            }
        });
        localStorage.setItem(votedKey, JSON.stringify(votedQuestions));
    });

    await loadQuestions();
})