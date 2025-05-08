    document.addEventListener('DOMContentLoaded', () => {
        const moderatorToken = window.location.pathname.split('/')[3];

        const socket = new WebSocket(
            'ws://' + window.location.host + `/ws/polls/${moderatorToken}/`
        );

        socket.onopen = () => console.log("WebSocket connected");
        socket.onerror = (e) => console.error("WebSocket error:", e);
        socket.onmessage = (e) => {
            const data = JSON.parse(e.data);
            console.log("Received:", data);

            if (data.type === "error") {
                alert("Błąd: " + data.error);
            }

            if (data.type === "publish_question") {
                alert(`Pytanie "${data.question_data.question}" has been published!`);
            }
        };

            const sampleQuestions = [
                { id: 'q-test123', question: 'Test question 1', answers: ['Yes', 'No'] },
                { id: 'q-test456', question: 'Test question 2', answers: ['PC', 'Pc1'] },
            ];

            container = document.getElementById('polls');
            sampleQuestions.forEach(question => {
                const questionDiv = document.createElement('div');
                questionDiv.classList.add('question');
                questionDiv.id = question.id;
                questionDiv.innerHTML = `
                <h3>${question.question}</h3>
                <button class="btn-small" onclick="publish('${question.id}')">Publish</button>           
                `;
                container.appendChild(questionDiv);
            })

            window.publish = (questionId) => {
             socket.send(JSON.stringify({
                type: 'publish_question',
                question_id: questionId,
             }))
        }
    })