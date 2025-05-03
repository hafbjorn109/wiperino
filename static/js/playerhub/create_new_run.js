document.addEventListener('DOMContentLoaded', () => {
    const addGameButton = document.getElementById('add-game-btn');
    const addGameSection = document.getElementById('add-game-section');

    addGameButton.addEventListener('click', () => {
        addGameSection.classList.toggle('hidden');

        const gameNameInput = document.getElementById('new-game-input').value;
        const saveGameButton = document.getElementById('new-game-save-btn');

        saveGameButton.addEventListener('click', () => {
            console.log('Save game');
            console.log(gameNameInput)
            addGameSection.classList.toggle('hidden');


        })

    })
})