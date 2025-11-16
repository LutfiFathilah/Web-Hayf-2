/**
 * KOPI HAYF - MAIN JAVASCRIPT
 * Handles cart functionality and all interactions
 * Version: 3.0 - Fixed CSRF Token
 */

// ==================== HELPER FUNCTIONS ====================

/**
 * Get CSRF token - FIXED VERSION
 * Priority: window.CSRF_TOKEN > meta tag > hidden input > cookie
 */
function getCookie(name) {
    // Method 1: Use global CSRF_TOKEN set by Django template (RECOMMENDED)
    if (typeof window.CSRF_TOKEN !== 'undefined' && window.CSRF_TOKEN) {
        return window.CSRF_TOKEN;
    }
    
    // Method 2: Try from meta tag
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta && csrfMeta.content) {
        return csrfMeta.content;
    }
    
    // Method 3: Try from hidden input
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (csrfInput && csrfInput.value) {
        return csrfInput.value;
    }
    
    // Method 4: Try from cookie (last resort)
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

/**
 * Update cart badge in header
 */
function updateCartBadge(cartCount) {
    const cartBadge = document.getElementById('cartBadge');
    const cartCountText = document.getElementById('cartCountText');
    
    if (cartCount > 0) {
        if (cartBadge) {
            cartBadge.textContent = cartCount;
            cartBadge.style.display = 'inline-flex';
        } else {
            // Create new badge if it doesn't exist
            const cartBtn = document.getElementById('cartBtn');
            if (cartBtn) {
                const newBadge = document.createElement('span');
                newBadge.className = 'cart-badge';
                newBadge.id = 'cartBadge';
                newBadge.textContent = cartCount;
                cartBtn.appendChild(newBadge);
            }
        }
        
        if (cartCountText) {
            cartCountText.textContent = `(${cartCount})`;
        }
    } else {
        if (cartBadge) {
            cartBadge.style.display = 'none';
        }
        if (cartCountText) {
            cartCountText.textContent = '(0)';
        }
    }
}

/**
 * Show notification message
 */
function showNotification(message, type = 'success') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification-toast');
    existingNotifications.forEach(notif => notif.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification-toast notification-${type}`;
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
            .notification-toast {
                position: fixed;
                bottom: 24px;
                right: 24px;
                background: white;
                padding: 16px 24px;
                border-radius: 12px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
                z-index: 10000;
                animation: slideInUp 0.3s ease;
                max-width: 400px;
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
                color: #1a1a1a;
                font-size: 14px;
                font-weight: 500;
            }
            
            .notification-success svg {
                color: #10b981;
                flex-shrink: 0;
            }
            
            .notification-error svg {
                color: #ef4444;
                flex-shrink: 0;
            }
            
            @keyframes slideInUp {
                from {
                    transform: translateY(100px);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }
            
            @keyframes slideOutDown {
                from {
                    transform: translateY(0);
                    opacity: 1;
                }
                to {
                    transform: translateY(100px);
                    opacity: 0;
                }
            }
            
            @media (max-width: 640px) {
                .notification-toast {
                    bottom: 16px;
                    right: 16px;
                    left: 16px;
                    max-width: none;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutDown 0.3s ease';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 4000);
}

// ==================== ADD TO CART FUNCTION ====================

/**
 * Add product to cart - FIXED VERSION
 * Works for landing page, catalog, and product detail
 */
function addToCart(productId, quantity = 1) {
    // Validate inputs
    if (!productId || productId <= 0) {
        console.error('Invalid product ID:', productId);
        showNotification('Produk tidak valid', 'error');
        return;
    }
    
    if (!quantity || quantity < 1) {
        quantity = 1;
    }
    
    console.log('🛒 Adding to cart:', { productId, quantity });
    
    // Get the button that was clicked (if available)
    const button = event?.currentTarget || document.querySelector(`[data-product-id="${productId}"]`);
    let originalContent = '';
    
    if (button) {
        // Disable button and show loading
        originalContent = button.innerHTML;
        button.disabled = true;
        button.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="animation: spin 0.8s linear infinite;">
                <circle cx="12" cy="12" r="10" opacity="0.25"/>
                <path d="M12 2a10 10 0 0 1 10 10" opacity="0.75"/>
            </svg>
            Menambahkan...
        `;
        
        // Add spin animation if not exists
        if (!document.getElementById('spin-animation')) {
            const spinStyle = document.createElement('style');
            spinStyle.id = 'spin-animation';
            spinStyle.textContent = `
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(spinStyle);
        }
    }
    
    // Get CSRF token
    const csrftoken = getCookie('csrftoken');
    
    console.log('🔑 CSRF Token:', csrftoken ? 'Found' : 'NOT FOUND');
    
    if (!csrftoken) {
        console.error('❌ CSRF token not found!');
        showNotification('Error: CSRF token tidak ditemukan. Silakan refresh halaman.', 'error');
        if (button) {
            button.innerHTML = originalContent;
            button.disabled = false;
        }
        return;
    }
    
    // Prepare form data
    const formData = new FormData();
    formData.append('quantity', quantity);
    
    // Send AJAX request
    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData,
        credentials: 'same-origin'  // Important for CSRF
    })
    .then(response => {
        console.log('📡 Response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('✅ Response data:', data);
        
        if (data.success) {
            // Update cart badge
            updateCartBadge(data.cart_count);
            
            // Show success notification
            showNotification(data.message || 'Produk berhasil ditambahkan ke keranjang!', 'success');
            
            // Update button to show success
            if (button) {
                button.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M20 6L9 17l-5-5"/>
                    </svg>
                    Berhasil!
                `;
                button.style.background = '#10B981';
                
                // Reset button after 2 seconds
                setTimeout(() => {
                    button.innerHTML = originalContent;
                    button.style.background = '';
                    button.disabled = false;
                }, 2000);
            }
            
            console.log('✅ Product added successfully!');
        } else {
            // Show error message
            console.error('❌ Server error:', data.error || data.message);
            showNotification(data.error || data.message || 'Gagal menambahkan produk ke keranjang', 'error');
            
            // Reset button
            if (button) {
                button.innerHTML = originalContent;
                button.disabled = false;
            }
        }
    })
    .catch(error => {
        console.error('❌ Error adding to cart:', error);
        showNotification('Terjadi kesalahan. Silakan coba lagi.', 'error');
        
        // Reset button
        if (button) {
            button.innerHTML = originalContent;
            button.disabled = false;
        }
    });
}

// ==================== CART SIDEBAR FUNCTIONS ====================

/**
 * Close cart sidebar
 */
function closeCart() {
    const cartSidebar = document.getElementById('cartSidebar');
    const cartOverlay = document.getElementById('cartOverlay');
    
    if (cartSidebar) {
        cartSidebar.classList.remove('active');
    }
    if (cartOverlay) {
        cartOverlay.classList.remove('active');
    }
}

// ==================== CART PAGE FUNCTIONS ====================

/**
 * Update cart quantity (for cart page)
 */
function updateCartQuantity(productId, newQuantity) {
    if (newQuantity < 1) {
        if (confirm('Hapus produk ini dari keranjang?')) {
            window.location.href = `/cart/remove/${productId}/`;
        }
        return;
    }
    
    const csrftoken = getCookie('csrftoken');
    
    fetch(`/cart/update/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ quantity: newQuantity })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Reload page to update totals
            window.location.reload();
        } else {
            showNotification(data.message || 'Gagal memperbarui keranjang', 'error');
        }
    })
    .catch(error => {
        console.error('Error updating cart:', error);
        showNotification('Terjadi kesalahan. Silakan coba lagi.', 'error');
    });
}

// ==================== PRODUCT DETAIL PAGE ====================

/**
 * Add to cart from product detail page
 */
function addToCartDetail() {
    const quantityInput = document.getElementById('quantity');
    const quantity = quantityInput ? parseInt(quantityInput.value) : 1;
    const productId = quantityInput ? parseInt(quantityInput.dataset.productId) : null;
    
    if (!productId) {
        // Try to get from page context
        const detailPage = document.querySelector('[data-product-id]');
        if (detailPage) {
            addToCart(parseInt(detailPage.dataset.productId), quantity);
        } else {
            console.error('Product ID not found');
            showNotification('Produk tidak valid', 'error');
        }
        return;
    }
    
    addToCart(productId, quantity);
}

// ==================== DOCUMENT READY ====================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Kopi Hayf - Script loaded successfully');
    console.log('🔑 CSRF Token available:', typeof window.CSRF_TOKEN !== 'undefined' ? 'YES' : 'NO');
    
    // ==================== CART SIDEBAR ====================
    const cartBtn = document.getElementById('cartBtn');
    const cartSidebar = document.getElementById('cartSidebar');
    const cartOverlay = document.getElementById('cartOverlay');
    const cartClose = document.getElementById('cartClose');
    const continueShoppingBtn = document.getElementById('continueShoppingBtn');

    // Open cart
    if (cartBtn && cartSidebar && cartOverlay) {
        cartBtn.addEventListener('click', function(e) {
            e.preventDefault();
            cartSidebar.classList.add('active');
            cartOverlay.classList.add('active');
        });
    }

    // Close cart
    if (cartClose) {
        cartClose.addEventListener('click', closeCart);
    }

    if (cartOverlay) {
        cartOverlay.addEventListener('click', closeCart);
    }

    if (continueShoppingBtn) {
        continueShoppingBtn.addEventListener('click', closeCart);
    }

    // Close cart on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeCart();
        }
    });

    // ==================== ADD TO CART BUTTONS ====================
    
    // Initialize all "Add to Cart" buttons
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    console.log(`📦 Found ${addToCartButtons.length} add-to-cart buttons`);
    
    addToCartButtons.forEach(button => {
        // Remove any existing onclick handlers
        button.removeAttribute('onclick');
        
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Get product ID from data attribute
            const productId = this.getAttribute('data-product-id');
            
            if (productId && productId !== '') {
                console.log('🛒 Button clicked for product:', productId);
                addToCart(parseInt(productId), 1);
            } else {
                console.error('❌ Product ID not found on button:', this);
                showNotification('Produk tidak valid', 'error');
            }
        });
    });

    // ==================== PRODUCT DETAIL QUANTITY CONTROLS ====================
    
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
    
    // Validate quantity input
    if (qtyInput) {
        qtyInput.addEventListener('change', function() {
            let value = parseInt(this.value) || 1;
            const max = parseInt(this.getAttribute('max')) || 999;
            
            if (value < 1) value = 1;
            if (value > max) value = max;
            
            this.value = value;
        });
    }

    // ==================== SMOOTH SCROLL ====================
    
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId !== '#' && targetId !== '#!') {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    e.preventDefault();
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // ==================== SEARCH FORM ====================
    
    const searchInput = document.getElementById('search-input');
    
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const form = this.closest('form');
                if (form) {
                    form.submit();
                }
            }
        });
    }

    // ==================== AUTO-DISMISS MESSAGES ====================
    
    const messagesContainer = document.querySelector('.messages-container');
    if (messagesContainer) {
        setTimeout(() => {
            messagesContainer.style.opacity = '0';
            messagesContainer.style.transition = 'opacity 0.5s';
            setTimeout(() => messagesContainer.remove(), 500);
        }, 5000);
    }

    // ==================== HEADER SCROLL EFFECT ====================
    
    let lastScroll = 0;
    const header = document.querySelector('.header');
    
    if (header) {
        window.addEventListener('scroll', () => {
            const currentScroll = window.pageYOffset;
            
            if (currentScroll > 50) {
                header.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.1)';
            } else {
                header.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.05)';
            }
            
            lastScroll = currentScroll;
        });
    }

    // ==================== INITIALIZE CART BADGE ====================
    
    const cartBadge = document.getElementById('cartBadge');
    if (cartBadge) {
        const count = parseInt(cartBadge.textContent);
        if (count === 0) {
            cartBadge.style.display = 'none';
        }
    }

    console.log('✅ All event listeners attached successfully');
});

// ==================== EXPORT FOR GLOBAL USE ====================

// Make functions available globally
window.addToCart = addToCart;
window.addToCartDetail = addToCartDetail;
window.updateCartQuantity = updateCartQuantity;
window.updateCartBadge = updateCartBadge;
window.showNotification = showNotification;
window.getCookie = getCookie;
window.closeCart = closeCart;

console.log('✅ Kopi Hayf JavaScript Module Loaded');