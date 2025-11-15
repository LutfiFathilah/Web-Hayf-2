// ============================================
// KATALOG.JS - KOPI HAYF
// ============================================

(function() {
    'use strict';

    // Data produk kopi
    const products = [
        {
            id: 1,
            title: "Kopi Susu Hayf",
            type: "Minuman Signature",
            origin: "Indonesia",
            volume: "250ml",
            description: "Espresso pekat disajikan susu lembut dan aroma kacang yang creamy.",
            price: 15000,
            rating: 4.9,
            image: "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=600&h=600&fit=crop",
            stock: 25
        },
        {
            id: 2,
            title: "Kopi Aren",
            type: "Minuman Traditional",
            origin: "Indonesia",
            volume: "250ml",
            description: "Kombinasi kopi dan madu alami gula aren memberikan aroma smoky karam.",
            price: 15000,
            rating: 4.7,
            image: "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=600&h=600&fit=crop",
            stock: 18
        },
        {
            id: 3,
            title: "Salted Caramel",
            type: "Minuman Premium",
            origin: "International",
            volume: "250ml",
            description: "Rasa manis karamel berpadu gurih lembut, menciptakan sensasi salted.",
            price: 15000,
            rating: 4.8,
            image: "https://images.unsplash.com/photo-1579888944880-d98341245702?w=600&h=600&fit=crop",
            stock: 12
        },
        {
            id: 4,
            title: "Spanish Latte",
            type: "Minuman International",
            origin: "Spanyol",
            volume: "250ml",
            description: "Minuman lembut berasa rasa manis alami dengan sentuhan khas ala Spanyol.",
            price: 15000,
            rating: 4.6,
            image: "https://images.unsplash.com/photo-1577968897966-3d4325b36b61?w=600&h=600&fit=crop",
            stock: 20
        },
        {
            id: 5,
            title: "Moccacino Latte",
            type: "Minuman Premium",
            origin: "International",
            volume: "250ml",
            description: "Perpaduan espresso pekat dengan cokelat yang kaya aroma vanilla.",
            price: 15000,
            rating: 4.8,
            image: "https://images.unsplash.com/photo-1534687941688-651ccaafbff8?w=600&h=600&fit=crop",
            stock: 15
        },
        {
            id: 6,
            title: "Americano",
            type: "Minuman Klasik",
            origin: "Amerika",
            volume: "250ml",
            description: "Minuman klasik dengan rasa kopi murni yang clean dan strong, pilihan tepat.",
            price: 13000,
            rating: 4.5,
            image: "https://images.unsplash.com/photo-1551030173-122aabc4489c?w=600&h=600&fit=crop",
            stock: 30
        },
        {
            id: 7,
            title: "Vanilla Latte",
            type: "Minuman Premium",
            origin: "International",
            volume: "250ml",
            description: "Espresso halus dengan aroma vanilla manis yang lembut, menciptakan rasa.",
            price: 15000,
            rating: 4.7,
            image: "https://images.unsplash.com/photo-1572590407445-ac6252f1a5b1?w=600&h=600&fit=crop",
            stock: 22
        },
        {
            id: 8,
            title: "Moka Brown Sugar",
            type: "Minuman Premium",
            origin: "International",
            volume: "250ml",
            description: "Kombinasi espresso dan cokelat dengan sentuhan manis brown sugar.",
            price: 15000,
            rating: 4.6,
            image: "https://images.unsplash.com/photo-1580661869408-55ab23f2ca6e?w=600&h=600&fit=crop",
            stock: 18
        }
    ];

    // ============================================
    // SHOPPING CART STATE
    // ============================================
    let cart = [];

    // ============================================
    // PRODUCT RENDERING FUNCTIONS
    // ============================================
    
    function renderProducts(productsToRender) {
        const productGrid = document.getElementById('product-grid');
        
        if (!productGrid) {
            console.error('Product grid element not found!');
            return;
        }
        
        productGrid.innerHTML = '';
        
        productsToRender.forEach(product => {
            const productCard = document.createElement('div');
            productCard.className = 'product-card';
            
            productCard.innerHTML = `
                <div class="product-image">
                    <img src="${product.image}" alt="${product.title}">
                    <div class="product-badge">Stok: ${product.stock}</div>
                </div>
                <div class="product-details">
                    <h3 class="product-title">${product.title}</h3>
                    <div class="product-info">
                        <span>${product.origin} • ${product.volume}</span>
                        <div class="product-rating">
                            <span class="star">⭐</span>
                            <span class="rating-value">${product.rating}</span>
                        </div>
                    </div>
                    <p class="product-description">${product.description}</p>
                    <div class="product-footer">
                        <div class="product-price">Rp ${product.price.toLocaleString('id-ID')}</div>
                        <div class="product-type">${product.type}</div>
                    </div>
                    <button class="add-to-cart" data-product-id="${product.id}">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M9 22C9.55228 22 10 21.5523 10 21C10 20.4477 9.55228 20 9 20C8.44772 20 8 20.4477 8 21C8 21.5523 8.44772 22 9 22Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M20 22C20.5523 22 21 21.5523 21 21C21 20.4477 20.5523 20 20 20C19.4477 20 19 20.4477 19 21C19 21.5523 19.4477 22 20 22Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M1 1H5L7.68 14.39C7.77144 14.8504 8.02191 15.264 8.38755 15.5583C8.75318 15.8526 9.2107 16.009 9.68 16H19.4C19.8693 16.009 20.3268 15.8526 20.6925 15.5583C21.0581 15.264 21.3086 14.8504 21.4 14.39L23 6H6" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        Tambah ke Keranjang
                    </button>
                </div>
            `;
            
            productGrid.appendChild(productCard);
        });
        
        // Update product count
        const productCountEl = document.getElementById('product-count');
        const totalProductsEl = document.getElementById('total-products');
        
        if (productCountEl) productCountEl.textContent = productsToRender.length;
        if (totalProductsEl) totalProductsEl.textContent = products.length;
        
        // Add event listeners to all add-to-cart buttons
        document.querySelectorAll('.add-to-cart').forEach(button => {
            button.addEventListener('click', function() {
                const productId = parseInt(this.getAttribute('data-product-id'));
                addToCart(productId);
            });
        });
        
        console.log(`Rendered ${productsToRender.length} products`);
    }

    // ============================================
    // CART FUNCTIONS
    // ============================================
    
    function updateCartBadge() {
        const cartBadge = document.getElementById('cartBadge');
        const cartCountText = document.getElementById('cartCountText');
        
        if (!cartBadge || !cartCountText) return;
        
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
        
        if (totalItems === 0) {
            cartBadge.style.display = 'none';
        } else {
            cartBadge.style.display = 'block';
            cartBadge.textContent = totalItems;
        }
        cartCountText.textContent = `(${totalItems})`;
    }

    function updateCartDisplay() {
        const emptyCart = document.getElementById('emptyCart');
        const cartItems = document.getElementById('cartItems');
        const cartFooter = document.getElementById('cartFooter');
        
        if (!emptyCart || !cartItems || !cartFooter) return;
        
        if (cart.length === 0) {
            emptyCart.style.display = 'flex';
            cartItems.style.display = 'none';
            cartFooter.style.display = 'none';
        } else {
            emptyCart.style.display = 'none';
            cartItems.style.display = 'flex';
            cartFooter.style.display = 'block';
            renderCartItems();
            updateCartTotal();
        }
    }

    function renderCartItems() {
        const cartItemsContainer = document.getElementById('cartItems');
        if (!cartItemsContainer) return;
        
        cartItemsContainer.innerHTML = '';
        
        cart.forEach(item => {
            const cartItem = document.createElement('div');
            cartItem.className = 'cart-item';
            cartItem.innerHTML = `
                <div class="cart-item-image">
                    <img src="${item.image}" alt="${item.title}">
                </div>
                <div class="cart-item-details">
                    <div class="cart-item-title">${item.title}</div>
                    <div class="cart-item-type">${item.type}</div>
                    <div class="cart-item-price">Rp ${item.price.toLocaleString('id-ID')}</div>
                    <div class="cart-item-actions">
                        <button class="qty-btn decrease-qty" data-product-id="${item.id}">-</button>
                        <span class="cart-item-qty">${item.quantity}</span>
                        <button class="qty-btn increase-qty" data-product-id="${item.id}">+</button>
                        <button class="remove-item" data-product-id="${item.id}">Hapus</button>
                    </div>
                </div>
            `;
            cartItemsContainer.appendChild(cartItem);
        });

        // Add event listeners for cart item actions
        document.querySelectorAll('.decrease-qty').forEach(btn => {
            btn.addEventListener('click', function() {
                const productId = parseInt(this.getAttribute('data-product-id'));
                decreaseQuantity(productId);
            });
        });

        document.querySelectorAll('.increase-qty').forEach(btn => {
            btn.addEventListener('click', function() {
                const productId = parseInt(this.getAttribute('data-product-id'));
                increaseQuantity(productId);
            });
        });

        document.querySelectorAll('.remove-item').forEach(btn => {
            btn.addEventListener('click', function() {
                const productId = parseInt(this.getAttribute('data-product-id'));
                removeFromCart(productId);
            });
        });
    }

    function updateCartTotal() {
        const totalPriceEl = document.getElementById('totalPrice');
        if (!totalPriceEl) return;
        
        const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        totalPriceEl.textContent = `Rp ${total.toLocaleString('id-ID')}`;
    }

    function addToCart(productId) {
        const product = products.find(p => p.id === productId);
        if (!product) {
            console.error('Product not found:', productId);
            return;
        }
        
        const existingItem = cart.find(item => item.id === productId);
        
        if (existingItem) {
            existingItem.quantity++;
        } else {
            cart.push({
                ...product,
                quantity: 1
            });
        }
        
        updateCartBadge();
        updateCartDisplay();
        openCart();
        
        console.log('Added to cart:', product.title);
    }

    function increaseQuantity(productId) {
        const item = cart.find(item => item.id === productId);
        if (item) {
            item.quantity++;
            updateCartBadge();
            updateCartDisplay();
        }
    }

    function decreaseQuantity(productId) {
        const item = cart.find(item => item.id === productId);
        if (item && item.quantity > 1) {
            item.quantity--;
            updateCartBadge();
            updateCartDisplay();
        }
    }

    function removeFromCart(productId) {
        cart = cart.filter(item => item.id !== productId);
        updateCartBadge();
        updateCartDisplay();
        
        console.log('Removed from cart, product ID:', productId);
    }

    function openCart() {
        const cartOverlay = document.getElementById('cartOverlay');
        const cartSidebar = document.getElementById('cartSidebar');
        
        if (cartOverlay && cartSidebar) {
            cartOverlay.classList.add('active');
            cartSidebar.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }

    function closeCart() {
        const cartOverlay = document.getElementById('cartOverlay');
        const cartSidebar = document.getElementById('cartSidebar');
        
        if (cartOverlay && cartSidebar) {
            cartOverlay.classList.remove('active');
            cartSidebar.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    // ============================================
    // SEARCH FUNCTIONALITY
    // ============================================
    
    function setupSearch() {
        const searchInput = document.getElementById('search-input');
        if (!searchInput) return;
        
        searchInput.addEventListener('input', () => {
            const searchTerm = searchInput.value.toLowerCase().trim();
            
            if (searchTerm === '') {
                renderProducts(products);
                return;
            }
            
            const filteredProducts = products.filter(product => 
                product.title.toLowerCase().includes(searchTerm) || 
                product.description.toLowerCase().includes(searchTerm) ||
                product.type.toLowerCase().includes(searchTerm) ||
                product.origin.toLowerCase().includes(searchTerm)
            );
            
            renderProducts(filteredProducts);
        });
    }

    // ============================================
    // FILTER FUNCTIONALITY
    // ============================================
    
    function setupFilter() {
        const filterBtn = document.querySelector('.filter-btn');
        if (!filterBtn) return;
        
        filterBtn.addEventListener('click', () => {
            const sortedProducts = [...products].sort((a, b) => b.rating - a.rating);
            renderProducts(sortedProducts);
        });
    }

    // ============================================
    // CART EVENT LISTENERS
    // ============================================
    
    function setupCartListeners() {
        const cartBtn = document.getElementById('cartBtn');
        const cartClose = document.getElementById('cartClose');
        const cartOverlay = document.getElementById('cartOverlay');
        const continueShoppingBtn = document.getElementById('continueShoppingBtn');
        
        if (cartBtn) cartBtn.addEventListener('click', openCart);
        if (cartClose) cartClose.addEventListener('click', closeCart);
        if (cartOverlay) cartOverlay.addEventListener('click', closeCart);
        if (continueShoppingBtn) continueShoppingBtn.addEventListener('click', closeCart);
        
        // Close cart with Escape key
        document.addEventListener('keydown', (e) => {
            const cartSidebar = document.getElementById('cartSidebar');
            if (e.key === 'Escape' && cartSidebar && cartSidebar.classList.contains('active')) {
                closeCart();
            }
        });
    }

    // ============================================
    // INITIALIZATION
    // ============================================
    
    function initializePage() {
        console.log('🚀 Initializing Katalog Page...');
        
        // Render products
        renderProducts(products);
        
        // Setup features
        setupSearch();
        setupFilter();
        setupCartListeners();
        
        // Initialize cart display
        updateCartBadge();
        updateCartDisplay();
        
        console.log('✅ Katalog Page initialized successfully!');
        console.log('📦 Total products:', products.length);
    }

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializePage);
    } else {
        // DOM is already ready
        initializePage();
    }

})();