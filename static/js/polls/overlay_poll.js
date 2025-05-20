document.addEventListener('DOMContentLoaded', () => {
    const overlayToken = window.location.pathname.split('/')[3];
    const socket = new WebSocket(`ws://${window.location.host}/ws/polls/${overlayToken}/`);

    const questionEl = document.getElementById('overlay-question');
    const answersEl = document.getElementById('overlay-answers');

    let chartInstance = null;

    function renderChart(questionData) {
        const ctx = document.getElementById('votes-chart').getContext('2d');
        const labels = questionData.answers;
        const voteCounts = labels.map(answer => questionData.votes[answer]);
        const totalVotes = voteCounts.reduce((a, b) => a + b, 0);

        if (chartInstance) {
            chartInstance.destroy();
            chartInstance = null;
        }

        chartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    data: voteCounts,
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    barThickness: 60,
                }]
            },
            options: {
                indexAxis: 'y',
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false },
                    datalabels: {
                        color: '#fff',
                        align: 'center',
                        anchor: 'center',
                        formatter: (value, context) => {
                            if (value === 0) return '';
                            const label = context.chart.data.labels[context.dataIndex];
                            const percent = totalVotes ? ((value / totalVotes) * 100).toFixed(1) : 0;
                            return `${label} (${value}, ${percent}%)`;
                        },
                        font: {
                            size: 20,
                            weight: 'bold'
                        },
                        clip: true
                    }
                },
                scales: {
                    x: {
                        display: false,
                        grid: { display: false },

                    },
                    y: {
                        ticks: {
                            display: false
                        },
                        grid: {
                            display: false
                        }
                    }
                },
                layout: {
                    padding: {
                    }
                },
                responsive: true,
                maintainAspectRatio: false,
                categoryPercentage: 0.5,
                barPercentage: 0.8
            },
            plugins: [ChartDataLabels]
        });

        document.getElementById('chart-wrapper').classList.remove('hidden');
    }

    socket.onopen = () => console.log('WebSocket connected');
    socket.onerror = (e) => console.error('WebSocket error:', e);
    socket.onclose = (e) => console.warn('WebSocket closed:', e);

    socket.onmessage = (e) => {
        try {
            const data = JSON.parse(e.data);

            if (data.type === 'publish_question') {
                const question = data.question_data;

                questionEl.textContent = question.question;
                questionEl.classList.remove('hidden');

                renderChart(question);
            }

            if (data.type === 'unpublish_question') {
                questionEl.textContent = '';
                questionEl.classList.add('hidden');
                answersEl.innerHTML = '';
                answersEl.classList.add('hidden');


                if (chartInstance) {
                    chartInstance.destroy();
                    chartInstance = null;
                }
                document.getElementById('chart-wrapper').classList.add('hidden');
            }

            if (data.type === 'vote') {
                renderChart(data);
            }
        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }
})