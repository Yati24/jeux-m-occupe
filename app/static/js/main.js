document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('access_token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    // Update nav links
    const authContainer = document.getElementById('auth-container');
    if (token && user.username) {
        authContainer.innerHTML = `
            <span class="text-sm">${user.username}</span>
            <a href="/compte" class="btn-primary text-sm">Compte</a>
            <button onclick="logout()" class="btn-secondary text-sm">Déconnexion</button>
        `;
    }
});

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/';
}
