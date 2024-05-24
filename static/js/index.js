import { toggleModal } from './errorModal.js';

document.getElementById('loginForm').addEventListener('submit', async (event) => {
    event.preventDefault();

    const username = event.target.username.value;
    const password = event.target.password.value;

    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    try {
        const response = await fetch('/', {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            window.location.replace("/user");
        } else {
            const errorData = await response.json();
            toggleModal(event, 'Error logging in: ' + errorData.error);
        }
    } catch (error) {
        toggleModal(event, 'Unknown error');
    }
  });


document.getElementById('modal-example').addEventListener('click', (event) => {
    toggleModal(event);
});