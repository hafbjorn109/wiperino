document.addEventListener('DOMContentLoaded', async() => {
    const pollsContainer = document.getElementById('polls');
    const questionInput = document.getElementById('question-text');
    const answersWrapper = document.getElementById('answers-wrapper');
    const addAnswerBtn = document.getElementById('add-answer');
    const submitBtn = document.getElementById('submit-question');
    const moderatorToken = window.location.pathname.split('/')[3];


    // Connect to WebSocket to receive live updates for the overlay
    const socket = new WebSocket(
        'ws://' + window.location.host + `/ws/polls/${moderatorToken}/`
    );

    socket.onopen = () => console.log('WebSocket connected');
    socket.onerror = (e) => console.error('WebSocket error:', e);
    socket.onclose = (e) => console.warn('WebSocket closed:', e);

    // Handle messages received via WebSocket
    socket.onmessage = (e) => {
        try{
            const data = JSON.parse(e.data);

            if (data.type === 'error') {
                alert('Error: ' + data.error);
            }

            if (data.type === 'publish_question') {
                document.querySelectorAll('.question').forEach(div => div.classList.remove('active'));
                const el = document.getElementById(data.question_id);
                if (el) el.classList.add('active');
            }

        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    };

    //Initial load of questions
    await loadExistingQuestions();

    /**
    * Loads all previously submitted questions for the current session from the backend.
    */
    async function loadExistingQuestions() {
        try {
            const response = await fetch(`/api/polls/m/${moderatorToken}/`);

            if (!response.ok) {
                console.warn('Could not load existing questions');
                return;
            }
            const questions = await response.json();
            questions.forEach(q => addQuestionToDom(q.id, q.question, q.answers));
        } catch (err) {
            console.error('Error loading questions:', err);
        }
    }


    /**
     * Adds a new answer input field dynamically to the UI.
     */
    addAnswerBtn.addEventListener('click', () => {
        const input = document.createElement('input');
        input.className = 'answer-input';
        input.type = 'text';
        input.placeholder = `Answer ${answersWrapper.children.length + 1}`;
        answersWrapper.appendChild(input);
    });


    /**
    * Submits a new poll question and its possible answers to the backend.
    */
    submitBtn.addEventListener('click', async() => {
        const question = questionInput.value.trim();
        const answers = Array.from(answersWrapper.querySelectorAll('input'))
        .map(input => input.value.trim())
        .filter(Boolean);
        const tooLong = answers.find(a => a.length > 30);
        if (tooLong) {
            alert(`Each answer must be at most 30 characters. Too long: ${tooLong}`);
            return;
        }
        if (!question || answers.length < 2 || question.length > 300) {
            alert('Question cannot be empty and ' +
                'must have at least 2 answers or no more than 300 characters.');
            return;
        }

        try {
            const response = await fetch(`/api/polls/m/${moderatorToken}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question, answers})
            });

            if (!response.ok) {
                alert(`Failed to submit question`);
                return;
            }

            const data = await response.json();
            addQuestionToDom(data.id, data.question, data.answers);
            questionInput.value = '';
            answersWrapper.innerHTML = '';
            addAnswerBtn.click();
            addAnswerBtn.click();

            socket.send(JSON.stringify({
                type: 'sync_questions'
            }));

        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    });

    /**
     * Adds a question block to the DOM with answer list and control buttons.
     */
    function addQuestionToDom(questionId, questionText, answers) {
        const div = document.createElement('div');
        div.className = 'question';
        div.id = questionId;
        const answersForDom = answers.map(answer => `<li>${answer}</li>`).join('');
        div.innerHTML = `
          <h3>${questionText}</h3>
          <ul>${answersForDom}</ul>
          <div class='button-container'>
            <button class='btn-small publish-btn' onclick="publish('${questionId}')">Publish</button>
            <button class='btn-small unpublish-btn hidden' onclick="unpublish('${questionId}')">Unpublish</button>
            <button class='btn-small red' onclick="removeQuestion('${questionId}')">Delete</button>
          </div>
        `;
        pollsContainer.appendChild(div);
    }

    /**
     * Sends a WebSocket message to publish the selected question.
     */
    window.publish = (questionId) => {
        socket.send(JSON.stringify({
            type: 'publish_question',
            question_id: questionId
        }));

        document.querySelectorAll('.publish-btn').forEach(btn => btn.classList.remove('hidden'));
        document.querySelectorAll('.unpublish-btn').forEach(btn => btn.classList.add('hidden'));


        const div = document.getElementById(questionId);
        if (div) {
            div.querySelector('.publish-btn').classList.add('hidden');
            div.querySelector('.unpublish-btn').classList.remove('hidden');
        }
    }

    /**
     * Sends a WebSocket message to unpublish the currently visible question.
     */
    window.unpublish = (questionId) => {
        socket.send(JSON.stringify({
            type: 'unpublish_question',
            question_id: questionId
        }));


        document.querySelectorAll('.question').forEach(div => {
            div.querySelector('.publish-btn').classList.remove('hidden');
            div.querySelector('.unpublish-btn').classList.add('hidden');
        });
    }

    /**
     * Sends a DELETE request to remove the selected question from the backend and UI.
     */
    window.removeQuestion = async function (questionId) {
        const confirmed = confirm('Are you sure you want to delete this question?');
        if (!confirmed) return;

        try {
            const response = await fetch(`/api/polls/m/${moderatorToken}/delete/${questionId}/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
            });

            if (!response.ok) {
                alert('Failed to delete question.');
                return;
            }

            socket.send(JSON.stringify({
                type: 'delete_question',
                question_id: questionId,
            }))

            const el = document.getElementById(questionId);
            if (el) el.remove();
        } catch (err) {
            console.error(err);
            alert('Something went wrong.');
        }
    }
})