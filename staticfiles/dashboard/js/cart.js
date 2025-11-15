// cart-manager.js - Sistem Cart Terpadu
// File ini bisa digunakan di semua halaman (landing page, katalog, dll)

class CartManager {
    constructor() {
        this.storageKey = 'bakeryCart';
        this.cart = this.loadCart();
    }

    // Load cart dari localStorage
    loadCart() {
        try {
            const saved = localStorage.getItem(this.storageKey);
            return saved ? JSON.parse(saved) : [];
        } catch (error) {
            console.error('Error loading cart:', error);
            return [];
        }
    }

    // Save cart ke localStorage
    saveCart() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.cart));
            this.updateCartUI();
        } catch (error) {
            console.error('Error saving cart:', error);
        }
    }

    // Tambah produk ke cart
    addToCart(product) {
        // Normalisasi data produk
        const normalizedProduct = {
            id: product.id || product.productId || Date.now(),
            name: product.name || product.title,
            price: parseFloat(product.price) || 0,
            image: product.image || product.imageUrl || '/api/placeholder/80/80',
            type: product.type || product.category || 'Produk',
            quantity: 1
        };

        // Cek apakah produk sudah ada di cart
        const existingIndex = this.cart.findIndex(item => item.id === normalizedProduct.id);

        if (existingIndex > -1) {
            // Jika sudah ada, tambah quantity
            this.cart[existingIndex].quantity += 1;
        } else {
            // Jika belum ada, tambah produk baru
            this.cart.push(normalizedProduct);
        }

        this.saveCart();
        this.showNotification(`${normalizedProduct.name} ditambahkan ke keranjang`);
        return true;
    }

    // Update quantity produk
    updateQuantity(productId, quantity) {
        const index = this.cart.findIndex(item => item.id === productId);
        if (index > -1) {
            if (quantity <= 0) {
                this.removeFromCart(productId);
            } else {
                this.cart[index].quantity = quantity;
                this.saveCart();
            }
        }
    }

    // Hapus produk dari cart
    removeFromCart(productId) {
        this.cart = this.cart.filter(item => item.id !== productId);
        this.saveCart();
    }

    // Kosongkan cart
    clearCart() {
        this.cart = [];
        this.saveCart();
    }

    // Get total items
    getTotalItems() {
        return this.cart.reduce((total, item) => total + item.quantity, 0);
    }

    // Get total price
    getTotalPrice() {
        return this.cart.reduce((total, item) => total + (item.price * item.quantity), 0);
    }

    // Get cart items
    getCart() {
        return this.cart;
    }

    // Update cart badge di semua halaman
    updateCartUI() {
        const totalItems = this.getTotalItems();
        
        // Update badge
        const badges = document.querySelectorAll('.cart-badge');
        badges.forEach(badge => {
            badge.textContent = totalItems;
            badge.style.display = totalItems > 0 ? 'block' : 'none';
        });

        // Update cart count di sidebar
        const cartCounts = document.querySelectorAll('.cart-count');
        cartCounts.forEach(count => {
            count.textContent = totalItems;
        });

        // Trigger custom event untuk update UI lainnya
        window.dispatchEvent(new CustomEvent('cartUpdated', { 
            detail: { 
                items: this.cart, 
                total: this.getTotalPrice(),
                count: totalItems
            } 
        }));
    }

    // Show notification
    showNotification(message) {
        // Cek apakah sudah ada notification container
        let notification = document.querySelector('.cart-notification');
        
        if (!notification) {
            notification = document.createElement('div');
            notification.className = 'cart-notification';
            document.body.appendChild(notification);
        }

        notification.textContent = message;
        notification.classList.add('show');

        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }

    // Render cart sidebar content
    renderCartSidebar(container) {
        if (!container) return;

        if (this.cart.length === 0) {
            container.innerHTML = `
                <div class="empty-cart">
                    <div class="empty-cart-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="9" cy="21" r="1"></circle>
                            <circle cx="20" cy="21" r="1"></circle>
                            <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
                        </svg>
                    </div>
                    <h3>Keranjang Kosong</h3>
                    <p>Belum ada produk di keranjang Anda.<br>Yuk, mulai berbelanja!</p>
                    <button class="continue-shopping" onclick="cartManager.closeCart()">
                        Lanjut Belanja
                    </button>
                </div>
            `;
            return;
        }

        const itemsHTML = this.cart.map(item => `
            <div class="cart-item" data-id="${item.id}">
                <div class="cart-item-image">
                    <img src="${item.image}" alt="${item.name}">
                </div>
                <div class="cart-item-details">
                    <div class="cart-item-title">${item.name}</div>
                    <div class="cart-item-type">${item.type}</div>
                    <div class="cart-item-price">Rp ${item.price.toLocaleString('id-ID')}</div>
                    <div class="cart-item-actions">
                        <button class="qty-btn" onclick="cartManager.updateQuantity(${item.id}, ${item.quantity - 1})">-</button>
                        <span class="cart-item-qty">${item.quantity}</span>
                        <button class="qty-btn" onclick="cartManager.updateQuantity(${item.id}, ${item.quantity + 1})">+</button>
                        <button class="remove-item" onclick="cartManager.removeFromCart(${item.id})">Hapus</button>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = `
            <div class="cart-items">
                ${itemsHTML}
            </div>
        `;
    }

    // Open cart sidebar
    openCart() {
        const sidebar = document.querySelector('.cart-sidebar');
        const overlay = document.querySelector('.cart-overlay');
        
        if (sidebar && overlay) {
            sidebar.classList.add('active');
            overlay.classList.add('active');
            
            // Render cart content
            const cartContent = sidebar.querySelector('.cart-content');
            this.renderCartSidebar(cartContent);
            
            // Update footer total
            const totalPrice = sidebar.querySelector('.total-price');
            if (totalPrice) {
                totalPrice.textContent = `Rp ${this.getTotalPrice().toLocaleString('id-ID')}`;
            }
        }
    }

    // Close cart sidebar
    closeCart() {
        const sidebar = document.querySelector('.cart-sidebar');
        const overlay = document.querySelector('.cart-overlay');
        
        if (sidebar && overlay) {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        }
    }

    // Initialize cart functionality
    init() {
        // Update UI saat load
        this.updateCartUI();

        // Setup cart button click handler
        const cartButtons = document.querySelectorAll('.cart-btn');
        cartButtons.forEach(btn => {
            btn.addEventListener('click', () => this.openCart());
        });

        // Setup overlay click handler
        const overlay = document.querySelector('.cart-overlay');
        if (overlay) {
            overlay.addEventListener('click', () => this.closeCart());
        }

        // Setup close button click handler
        const closeBtn = document.querySelector('.cart-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closeCart());
        }

        // Setup checkout button
        const checkoutBtn = document.querySelector('.checkout-btn');
        if (checkoutBtn) {
            checkoutBtn.addEventListener('click', () => this.checkout());
        }

        // Listen for cart updates from other tabs
        window.addEventListener('storage', (e) => {
            if (e.key === this.storageKey) {
                this.cart = this.loadCart();
                this.updateCartUI();
            }
        });
    }

    // Checkout process
    checkout() {
        if (this.cart.length === 0) {
            alert('Keranjang masih kosong!');
            return;
        }

        // Di sini Anda bisa redirect ke halaman checkout
        // atau proses checkout lainnya
        alert(`Checkout ${this.getTotalItems()} produk dengan total Rp ${this.getTotalPrice().toLocaleString('id-ID')}`);
        
        // Uncomment jika ingin redirect ke halaman checkout
        // window.location.href = '/checkout.html';
    }
}

// Inisialisasi global cart manager
const cartManager = new CartManager();

// Auto initialize saat DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => cartManager.init());
} else {
    cartManager.init();
}

// Export untuk digunakan di module lain
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CartManager;
}