document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('access_token');

    const profileBtn = document.getElementById('profile-btn');
    const dropdown = document.getElementById('profile-dropdown');

    if (profileBtn && dropdown) {
        profileBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = !dropdown.classList.contains('hidden');
            dropdown.classList.toggle('hidden', isOpen);
        });

        document.addEventListener('click', () => dropdown.classList.add('hidden'));

        const loginItem = document.getElementById('dropdown-login');
        const registerItem = document.getElementById('dropdown-register');
        const profileItem = document.getElementById('dropdown-profile');
        const dashboardItem = document.getElementById('dropdown-dashboard');
        const logoutItem = document.getElementById('dropdown-logout');

        if (token) {
            loginItem.classList.add('hidden');
            registerItem.classList.add('hidden');
            profileItem.classList.remove('hidden');
            logoutItem.classList.remove('hidden');
            logoutItem.addEventListener('click', logout);

            // Lien dashboard visible uniquement pour les administrateurs
            if (dashboardItem) {
                let isAdmin = false;
                try {
                    isAdmin = !!JSON.parse(localStorage.getItem('user') || '{}').is_admin;
                } catch (e) {}
                dashboardItem.classList.toggle('hidden', !isAdmin);
            }
        } else {
            loginItem.classList.remove('hidden');
            registerItem.classList.remove('hidden');
            profileItem.classList.add('hidden');
            logoutItem.classList.add('hidden');
        }
    }
    
    updateCartCount();
});

async function updateCartCount() {
    const token = localStorage.getItem('access_token');
    const cartCountEl = document.getElementById('cart-count');
    if (!token || !cartCountEl) return;

    try {
        const response = await fetch('/api/cart', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const data = await response.json();
            if (data.item_count > 0) {
                cartCountEl.textContent = data.item_count;
                cartCountEl.classList.remove('hidden');
            } else {
                cartCountEl.classList.add('hidden');
            }
        }
    } catch (e) {
        console.error('Error fetching cart count', e);
    }
}

function showToast(message, type) {
    const existing = document.querySelector('.toast-notification');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    const bgColor = type === 'error' ? 'bg-red-600' : 'bg-green-600';
    toast.innerHTML = message;
    toast.style.cssText = `
        position: fixed; bottom: 24px; right: 24px; z-index: 9999;
        padding: 12px 24px; border-radius: 8px; color: white;
        font-weight: 600; font-size: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
    `;
    toast.classList.add(bgColor);
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 300);
    }, 2500);
}

async function addToCartAPI(productId, quantity, event) {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    try {
        const response = await fetch('/api/cart/items', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ product_id: productId, quantity: quantity || 1 })
        });
        const data = await response.json();
        if (data.error) {
            showToast(data.error, 'error');
        } else {
            showToast('Ajouté au panier !', 'success');
            updateCartCount();
            if (event && event.target) {
                const btn = event.target.closest('button') || event.target;
                const originalText = btn.innerHTML;
                btn.innerHTML = 'Ajouté !';
                btn.style.backgroundColor = '#22c55e';
                btn.style.color = 'white';
                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.style.backgroundColor = '';
                    btn.style.color = '';
                }, 2000);
            }
        }
    } catch (e) {
        showToast('Erreur réseau', 'error');
    }
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/';
}
