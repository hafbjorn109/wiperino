document.addEventListener('DOMContentLoaded', async() => {
    const addGameButton = document.getElementById('add-game-btn');
    const addGameSection = document.getElementById('add-game-section');
    const saveGameButton = document.getElementById('new-game-save-btn');
    const createButton = document.querySelector('.create-btn');
    const select = document.getElementById('game-select');
    const token = localStorage.getItem('access');

    /**
     * Fetches existing games from the API and populates the dropdown list.
     */
    async function fetchAndDisplayGames() {
        try {
        const response = await fetch('/api/games/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
            }
        })
        const responseData = await response.json();

        if(!response.ok) {
            const errorText = Object.values(responseData).flat().join(', ');
            alert(`Error: ${errorText}`);
            return;
        }

        responseData.forEach(game => {
        const option = document.createElement('option');
        option.value = game.id;
        option.textContent = game.name;
        select.appendChild(option);
        });

        } catch (err) {
        console.error(err);
        alert('Something went wrong. Try again.');
        }
    }


    /**
     * Submits a new game to the API and adds it to the dropdown list.
     */
    async function addNewGameHandler(e){
        e.preventDefault();
        const gameNameInput = document.getElementById('new-game-input').value;

        try {
            const response = await fetch('/api/games/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    name: gameNameInput
                    })
                });

            const responseData = await response.json();

            if(!response.ok) {
                const errorText = Object.values(responseData).flat().join(', ');
                alert(`Error: ${errorText}`);
                return;
            }

            console.log('Game Added');
            document.getElementById('new-game-input').value = '';
            addGameSection.classList.toggle('hidden');

            const select = document.getElementById('game-select');
            const option = document.createElement('option');
            option.value = responseData.id;
            option.textContent = responseData.name;
            select.appendChild(option);
            select.value = responseData.id;


        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }


    /**
     * Sends form data to the API to create a new run.
     */
    async function createRunHandler(e) {
        e.preventDefault();
          try {
            const response = await fetch('/api/runs/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    name: document.getElementById('run-name').value,
                    game: select.value,
                    mode: document.getElementById('mode-select').value,
                })
            });

            const responseData = await response.json();

            if(!response.ok) {
                const errorText = Object.values(responseData).flat().join(', ');
                alert(`Error: ${errorText}`);
                return;
            }
            window.location.href = `/runs/${responseData.id}/`;
        } catch (err) {
            console.error(err);
            alert('Something went wrong. Try again.');
        }
    }

    //Event listeners
    createButton.addEventListener('click', createRunHandler);

    saveGameButton.addEventListener('click', addNewGameHandler);

    addGameButton.addEventListener('click', () => {
        addGameSection.classList.toggle('hidden');
    })

    // Initial game list load
    await fetchAndDisplayGames();
})