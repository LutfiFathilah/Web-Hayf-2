// Cart functionality
document.addEventListener('DOMContentLoaded', function() {
    const cartBtn = document.getElementById('cartBtn');
    const cartSidebar = document.getElementById('cartSidebar');
    const cartOverlay = document.getElementById('cartOverlay');
    const cartClose = document.getElementById('cartClose');
    const continueShoppingBtn = document.getElementById('continueShoppingBtn');

    // Open cart
    if (cartBtn) {
        cartBtn.addEventListener('click', function() {
            cartSidebar.classList.add('active');
            cartOverlay.classList.add('active');
            loadCartItems();
        });
    }

    // Close cart
    function closeCart() {
        cartSidebar.classList.remove('active');
        cartOverlay.classList.remove('active');
    }

    if (cartClose) {
        cartClose.addEventListener('click', closeCart);
    }

    if (cartOverlay) {
        cartOverlay.addEventListener('click', closeCart);
    }

    if (continueShoppingBtn) {
        continueShoppingBtn.addEventListener('click', closeCart);
    }

    // Load cart items from server
    function loadCartItems() {
        // Jika ada endpoint API untuk cart, load di sini
        // Untuk sementara kita gunakan session-based cart
        console.log('Cart loaded');
    }

    // Add to cart functionality
    window.addToCart = function(productId, quantity = 1) {
        // Get CSRF token
        const csrftoken = getCookie('csrftoken');
        
        fetch(`/cart/add/${productId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken
            },
            body: `quantity=${quantity}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update cart badge
                const cartBadge = document.getElementById('cartBadge');
                const cartCountText = document.getElementById('cartCountText');
                
                if (cartBadge) {
                    cartBadge.textContent = data.cart_count;
                }
                if (cartCountText) {
                    cartCountText.textContent = `(${data.cart_count})`;
                }
                
                // Show success message
                showNotification(data.message, 'success');
                
                // Open cart sidebar
                cartSidebar.classList.add('active');
                cartOverlay.classList.add('active');
                loadCartItems();
            } else {
                showNotification(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Terjadi kesalahan. Silakan coba lagi.', 'error');
        });
    };

    // Update cart quantity
    window.updateCartQuantity = function(productId, quantity) {
        const csrftoken = getCookie('csrftoken');
        
        fetch(`/cart/update/${productId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken
            },
            body: `quantity=${quantity}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload(); // Reload page to update cart
            } else {
                showNotification(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    };

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Show notification
    function showNotification(message, type = 'success') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    ${type === 'success' 
                        ? '<path d="M20 6L9 17l-5-5"/>' 
                        : '<path d="M18 6L6 18M6 6l12 12"/>'}
                </svg>
                <span>${message}</span>
            </div>
        `;
        
        // Add styles if not exists
        if (!document.getElementById('notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                .notification {
                    position: fixed;
                    bottom: 24px;
                    right: 24px;
                    background: white;
                    padding: 16px 24px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                    z-index: 10000;
                    animation: slideIn 0.3s ease;
                }
                
                .notification-success {
                    border-left: 4px solid #10b981;
                }
                
                .notification-error {
                    border-left: 4px solid #ef4444;
                }
                
                .notification-content {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                
                .notification-success svg {
                    color: #10b981;
                }
                
                .notification-error svg {
                    color: #ef4444;
                }
                
                @keyframes slideIn {
                    from {
                        transform: translateX(400px);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && document.querySelector(href)) {
                e.preventDefault();
                document.querySelector(href).scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Product detail - Quantity controls
document.addEventListener('DOMContentLoaded', function() {
    const qtyInput = document.getElementById('quantity');
    const qtyMinus = document.getElementById('qtyMinus');
    const qtyPlus = document.getElementById('qtyPlus');
    
    if (qtyMinus && qtyInput) {
        qtyMinus.addEventListener('click', function() {
            let value = parseInt(qtyInput.value) || 1;
            if (value > 1) {
                qtyInput.value = value - 1;
            }
        });
    }
    
    if (qtyPlus && qtyInput) {
        qtyPlus.addEventListener('click', function() {
            let value = parseInt(qtyInput.value) || 1;
            const max = parseInt(qtyInput.getAttribute('max')) || 999;
            if (value < max) {
                qtyInput.value = value + 1;
            }
        });
    }
});