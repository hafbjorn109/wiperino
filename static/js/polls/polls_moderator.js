document.addEventListener('DOMContentLoaded', async() => {
    const pollsContainer = document.getElementById('polls');
    const questionInput = document.getElementById('question-text');
    const answersWrapper = document.getElementById('answers-wrapper');
    const addAnswerBtn = document.getElementById('add-answer');
    const submitBtn = document.getElementById('submit-question');
    const moderatorToken = window.location.pathname.split('/')[3];

    const socket = new WebSocket(
        'ws://' + window.location.host + `/ws/polls/${moderatorToken}/`
    );

    socket.onopen = () => console.log("WebSocket connected");
    socket.onerror = (e) => console.error("WebSocket error:", e);
    socket.onmessage = (e) => {
        try{
            const data = JSON.parse(e.data);
            console.log("Received:", data);

            if (data.type === "error") {
                alert("Error: " + data.error);
            }

            if (data.type === "publish_question") {
                document.querySelectorAll('.question').forEach(div => div.classList.remove('active'));
                const el = document.getElementById(data.question_id);
                if (el) el.classList.add('active');
            }
        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    };

    await loadExistingQuestions();

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


    addAnswerBtn.addEventListener('click', () => {
        const input = document.createElement('input');
        input.className = 'answer-input';
        input.type = 'text';
        input.placeholder = `Answer ${answersWrapper.children.length + 1}`;
        answersWrapper.appendChild(input);
    });

    submitBtn.addEventListener('click', async() => {
        const question = questionInput.value.trim();
        const answers = Array.from(answersWrapper.querySelectorAll('input'))
        .map(input => input.value.trim())
        .filter(Boolean);
        if (!question || answers.length < 2) {
            alert('Question cannot be empty and must have at least 2 answers.');
            return;
        }

        try {
            const response = await fetch(`/api/polls/m/${moderatorToken}/add_poll/`, {
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
            addQuestionToDom(data.question_id, data.question, data.answers);
            questionInput.value = '';
            answersWrapper.innerHTML = '';
            addAnswerBtn.click();
            addAnswerBtn.click();
        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    });

    function addQuestionToDom(questionId, questionText, answers) {
        const div = document.createElement('div');
        div.className = 'question';
        div.id = questionId;
        const answersForDom = answers.map(answer => `<li>${answer}</li>`).join('');
        div.innerHTML = `
          <h3>${questionText}</h3>
          <ul>${answersForDom}</ul>
          <div class="button-container">
            <button class="btn-small" onclick="publish('${questionId}')">Publish</button>
            <button class="btn-small red" onclick="removeQuestion('${questionId}')">Delete</button>
          </div>
        `;
        pollsContainer.appendChild(div);
    }

    window.publish = (questionId) => {
        socket.send(JSON.stringify({
            type: "publish_question",
            question_id: questionId
        }));
    }

    window.removeQuestion = async function (questionId) {
        const confirmed = confirm("Are you sure you want to delete this question?");
        if (!confirmed) return;

        try {
            const response = await fetch(`/api/polls/m/${moderatorToken}/delete/${questionId}/`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                alert("Failed to delete question.");
                return;
            }

            const el = document.getElementById(questionId);
            if (el) el.remove();
        } catch (err) {
            console.error(err);
            alert("Something went wrong.");
        }
    }

})