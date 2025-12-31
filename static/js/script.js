// Global Variables
let currentUser = null;
let cartCount = 0;
let wishlistCount = 0;
let currentCartItems = [];

// API Base URL
const API_BASE = window.location.origin;

// DOM Elements
const elements = {
    // Navigation
    cartBtn: document.getElementById('cart-btn'),
    wishlistBtn: document.getElementById('wishlist-btn'),
    userBtn: document.getElementById('user-btn'),
    userDropdown: document.getElementById('user-dropdown'),
    cartCount: document.getElementById('cart-count'),
    wishlistCount: document.getElementById('wishlist-count'),
    
    // Authentication
    loginBtn: document.getElementById('login-btn'),
    registerBtn: document.getElementById('register-btn'),
    profileBtn: document.getElementById('profile-btn'),
    ordersBtn: document.getElementById('orders-btn'),
    logoutBtn: document.getElementById('logout-btn'),
    loginModal: document.getElementById('login-modal'),
    registerModal: document.getElementById('register-modal'),
    
    // Product Display
    homeProducts: document.getElementById('home-products'),
    categoryProducts: document.getElementById('category-products'),
    dealsProducts: document.getElementById('deals-products'),
    
    // Chatbot
    chatbotToggle: document.getElementById('chatbot-toggle'),
    chatbotClose: document.getElementById('chatbot-close'),
    chatbotContainer: document.getElementById('chatbot-container'),
    chatbotMessages: document.getElementById('chatbot-messages'),
    chatbotInput: document.getElementById('chatbot-input'),
    chatbotSend: document.getElementById('chatbot-send'),
    
    // Search
    searchInput: document.getElementById('search-input'),
    searchResults: document.getElementById('search-results'),
    searchBtn: document.getElementById('search-btn'),
    
    // Modals
    modals: document.querySelectorAll('.modal'),
    modalCloses: document.querySelectorAll('.modal-close'),
    
    // Category
    categoryLinks: document.querySelectorAll('.category-link'),
    filterBtns: document.querySelectorAll('.filter-btn'),
    currentCategory: document.getElementById('current-category'),
    
    // Category Cards
    categoryCards: document.querySelectorAll('.category-card'),
    
    // Hero buttons
    heroShopNow: document.querySelector('.hero-buttons .btn-primary'),
    heroViewDeals: document.querySelector('.hero-buttons .btn-outline')
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM loaded, initializing app...");
    initializeApp();
    setupEventListeners();
    loadInitialData();
});

function initializeApp() {
    console.log("Initializing app...");
    
    // Check authentication status
    checkAuthStatus();
    
    // Load cart and wishlist counts
    updateCartWishlistCounts();
    
    // Load deals products
    loadDealsProducts();
    
    // Set default active category
    setActiveCategory('Smartphones');
    loadCategoryProducts('Smartphones');
}

function setupEventListeners() {
    console.log("Setting up event listeners...");
    
    // User dropdown toggle
    if (elements.userBtn) {
        elements.userBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleUserDropdown();
        });
    }
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('#user-btn') && !e.target.closest('.user-dropdown')) {
            elements.userDropdown.classList.remove('show');
        }
    });
    
    // Authentication
    if (elements.loginBtn) {
        elements.loginBtn.addEventListener('click', (e) => {
            e.preventDefault();
            showModal('login-modal');
        });
    }
    
    if (elements.registerBtn) {
        elements.registerBtn.addEventListener('click', (e) => {
            e.preventDefault();
            showModal('register-modal');
        });
    }
    
    if (elements.profileBtn) {
        elements.profileBtn.addEventListener('click', (e) => {
            e.preventDefault();
            loadProfileData();
            showModal('profile-modal');
        });
    }
    
    if (elements.ordersBtn) {
        elements.ordersBtn.addEventListener('click', (e) => {
            e.preventDefault();
            loadOrders();
            showModal('orders-modal');
        });
    }
    
    if (elements.logoutBtn) {
        elements.logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            logoutUser();
        });
    }
    
    // Login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleLogin();
        });
    }
    
    // Register form
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleRegister();
        });
    }
    
    // Switch between login/register
    const switchToRegister = document.getElementById('switch-to-register');
    const switchToLogin = document.getElementById('switch-to-login');
    if (switchToRegister) {
        switchToRegister.addEventListener('click', (e) => {
            e.preventDefault();
            hideModal('login-modal');
            showModal('register-modal');
        });
    }
    if (switchToLogin) {
        switchToLogin.addEventListener('click', (e) => {
            e.preventDefault();
            hideModal('register-modal');
            showModal('login-modal');
        });
    }
    
    // Forgot password
    const forgotPassword = document.querySelector('.forgot-password');
    if (forgotPassword) {
        forgotPassword.addEventListener('click', (e) => {
            e.preventDefault();
            hideModal('login-modal');
            showModal('forgot-modal');
        });
    }
    
    // Cart and Wishlist buttons
    if (elements.cartBtn) {
        elements.cartBtn.addEventListener('click', () => {
            showModal('cart-modal');
            loadCartItems();
        });
    }
    
    if (elements.wishlistBtn) {
        elements.wishlistBtn.addEventListener('click', () => {
            showModal('wishlist-modal');
            loadWishlistItems();
        });
    }
    
    // Category navigation
    elements.categoryLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const category = link.dataset.category;
            console.log("Category link clicked:", category);
            setActiveCategory(category);
            loadCategoryProducts(category);
            
            // Scroll to category products section
            const categorySection = document.querySelector('.category-products-section');
            if (categorySection) {
                categorySection.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Category filter buttons
    elements.filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active button
            elements.filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Load category products
            const category = btn.dataset.category;
            console.log("Filter button clicked:", category);
            elements.currentCategory.textContent = category;
            loadCategoryProducts(category);
        });
    });
    
    // Category cards
    elements.categoryCards.forEach(card => {
        card.addEventListener('click', (e) => {
            // Don't trigger if clicking the button
            if (e.target.closest('.btn')) {
                return;
            }
            
            const category = card.dataset.category;
            console.log("Category card clicked:", category);
            setActiveCategory(category);
            loadCategoryProducts(category);
            
            // Scroll to category products section
            const categorySection = document.querySelector('.category-products-section');
            if (categorySection) {
                categorySection.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
        
        // Also handle the shop now button
        const shopBtn = card.querySelector('.btn');
        if (shopBtn) {
            shopBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const category = card.dataset.category;
                console.log("Shop now button clicked:", category);
                setActiveCategory(category);
                loadCategoryProducts(category);
                
                // Scroll to category products section
                const categorySection = document.querySelector('.category-products-section');
                if (categorySection) {
                    categorySection.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            });
        }
    });
    
    // Chatbot
    if (elements.chatbotToggle) {
        elements.chatbotToggle.addEventListener('click', (e) => {
            e.preventDefault();
            toggleChatbot();
        });
    }
    
    if (elements.chatbotClose) {
        elements.chatbotClose.addEventListener('click', (e) => {
            e.preventDefault();
            toggleChatbot();
        });
    }
    
    if (elements.chatbotSend) {
        elements.chatbotSend.addEventListener('click', (e) => {
            e.preventDefault();
            sendChatMessage();
        });
    }
    
    // Chatbot input enter key
    if (elements.chatbotInput) {
        elements.chatbotInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendChatMessage();
            }
        });
    }
    
    // Search
    if (elements.searchInput) {
        // Real-time search
        elements.searchInput.addEventListener('input', handleSearch);
        
        // Also handle enter key
        elements.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleSearch();
            }
        });
    }
    
    if (elements.searchBtn) {
        elements.searchBtn.addEventListener('click', handleSearch);
    }
    
    // Modal close buttons
    elements.modalCloses.forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = btn.closest('.modal');
            hideModal(modal.id);
        });
    });
    
    // Close modal on outside click
    elements.modals.forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                hideModal(modal.id);
            }
        });
    });
    
    // Continue shopping button
    const continueShopping = document.getElementById('continue-shopping');
    if (continueShopping) {
        continueShopping.addEventListener('click', () => {
            hideModal('cart-modal');
        });
    }
    
    // Browse products button
    const browseProducts = document.getElementById('browse-products');
    if (browseProducts) {
        browseProducts.addEventListener('click', () => {
            hideModal('wishlist-modal');
        });
    }
    
    // Hero buttons
    if (elements.heroShopNow) {
        elements.heroShopNow.addEventListener('click', (e) => {
            e.preventDefault();
            document.querySelector('.categories-section').scrollIntoView({
                behavior: 'smooth'
            });
        });
    }
    
    if (elements.heroViewDeals) {
        elements.heroViewDeals.addEventListener('click', (e) => {
            e.preventDefault();
            document.querySelector('.deals-section').scrollIntoView({
                behavior: 'smooth'
            });
        });
    }
    
    // Profile form
    const profileForm = document.getElementById('profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            e.preventDefault();
            updateProfile();
        });
    }
    
    // Forgot password OTP
    const sendOtpBtn = document.getElementById('send-otp-btn');
    if (sendOtpBtn) {
        sendOtpBtn.addEventListener('click', sendForgotPasswordOTP);
    }
    
    const resetPasswordBtn = document.getElementById('reset-password-btn');
    if (resetPasswordBtn) {
        resetPasswordBtn.addEventListener('click', resetPassword);
    }
    
    // Payment methods
    document.querySelectorAll('.payment-method').forEach(method => {
        method.addEventListener('click', () => {
            document.querySelectorAll('.payment-method').forEach(m => m.classList.remove('active'));
            method.classList.add('active');
        });
    });
    
    // Confirm payment
    const confirmPaymentBtn = document.getElementById('confirm-payment');
    if (confirmPaymentBtn) {
        confirmPaymentBtn.addEventListener('click', processPayment);
    }
    
    // Cancel payment
    const cancelPaymentBtn = document.getElementById('cancel-payment');
    if (cancelPaymentBtn) {
        cancelPaymentBtn.addEventListener('click', () => {
            hideModal('payment-modal');
        });
    }
    
    // Checkout button
    const checkoutBtn = document.getElementById('checkout-btn');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', () => {
            showPaymentModal();
        });
    }
    
    console.log("Event listeners setup complete");
}

// Authentication Functions
async function checkAuthStatus() {
    try {
        console.log("Checking auth status...");
        const response = await fetch(`${API_BASE}/api/auth/check`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log("Auth check response:", data);
        
        if (data.logged_in) {
            currentUser = data.user;
            updateUserUI(true, data.user);
            cartCount = data.cart_count || 0;
            wishlistCount = data.wishlist_count || 0;
            updateCartWishlistUI();
        } else {
            updateUserUI(false);
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        updateUserUI(false);
    }
}

async function handleLogin() {
    const identifier = document.getElementById('login-identifier').value;
    const password = document.getElementById('login-password').value;
    
    if (!identifier || !password) {
        showNotification('Please enter email/phone and password', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        console.log("Attempting login...");
        const response = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ identifier, password }),
            credentials: 'include'
        });
        
        console.log("Login response status:", response.status);
        
        const data = await response.json();
        console.log("Login response data:", data);
        
        if (response.ok) {
            currentUser = data.user;
            updateUserUI(true, data.user);
            cartCount = data.cart_count || 0;
            wishlistCount = data.wishlist_count || 0;
            updateCartWishlistUI();
            hideModal('login-modal');
            showNotification('Login successful!', 'success');
            
            // Clear form
            document.getElementById('login-form').reset();
        } else {
            showNotification(data.error || 'Login failed. Please check your credentials.', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showNotification('Login failed. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

async function handleRegister() {
    const formData = {
        full_name: document.getElementById('register-name').value,
        email: document.getElementById('register-email').value,
        phone: document.getElementById('register-phone').value,
        address: document.getElementById('register-address').value,
        pincode: document.getElementById('register-pincode').value,
        password: document.getElementById('register-password').value
    };
    
    // Validate form data
    for (const [key, value] of Object.entries(formData)) {
        if (!value.trim()) {
            showNotification(`Please fill in ${key.replace('_', ' ')}`, 'error');
            return;
        }
    }
    
    // Validate terms acceptance
    if (!document.getElementById('terms').checked) {
        showNotification('Please accept terms and conditions', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        console.log("Attempting registration...");
        const response = await fetch(`${API_BASE}/api/auth/register`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(formData),
            credentials: 'include'
        });
        
        console.log("Register response status:", response.status);
        
        const data = await response.json();
        console.log("Register response data:", data);
        
        if (response.ok) {
            currentUser = data.user;
            updateUserUI(true, data.user);
            hideModal('register-modal');
            showNotification('Registration successful!', 'success');
            
            // Clear form
            document.getElementById('register-form').reset();
            
            // Load counts after registration
            setTimeout(() => {
                updateCartWishlistCounts();
            }, 1000);
        } else {
            showNotification(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showNotification('Registration failed. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

async function logoutUser() {
    try {
        const response = await fetch(`${API_BASE}/api/auth/logout`, {
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentUser = null;
            cartCount = 0;
            wishlistCount = 0;
            updateUserUI(false);
            updateCartWishlistUI();
            hideModal('cart-modal');
            hideModal('wishlist-modal');
            showNotification('Logged out successfully', 'success');
        }
    } catch (error) {
        console.error('Logout error:', error);
        showNotification('Logout failed', 'error');
    }
}

function updateUserUI(isLoggedIn, user = null) {
    const userInfo = document.getElementById('user-info');
    const userName = document.querySelector('.user-name');
    const userEmail = document.querySelector('.user-email');
    
    if (isLoggedIn && user) {
        // Update dropdown user info
        userName.textContent = `Welcome, ${user.name}`;
        userEmail.textContent = user.email;
        
        // Show/hide menu items
        document.getElementById('login-btn').style.display = 'none';
        document.getElementById('register-btn').style.display = 'none';
        document.getElementById('profile-btn').style.display = 'flex';
        document.getElementById('orders-btn').style.display = 'flex';
        document.getElementById('logout-btn').style.display = 'flex';
    } else {
        // Guest user
        userName.textContent = 'Welcome, Guest';
        userEmail.textContent = 'Sign in to your account';
        
        // Show/hide menu items
        document.getElementById('login-btn').style.display = 'flex';
        document.getElementById('register-btn').style.display = 'flex';
        document.getElementById('profile-btn').style.display = 'none';
        document.getElementById('orders-btn').style.display = 'none';
        document.getElementById('logout-btn').style.display = 'none';
    }
}

// Cart Functions
async function addToCart(productId) {
    if (!currentUser) {
        showNotification('Please login to add items to cart', 'error');
        showModal('login-modal');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/cart/add/${productId}`, {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            cartCount = data.cart_count;
            updateCartWishlistUI();
            showNotification('Added to cart!', 'success');
            
            // Reload cart if modal is open
            if (document.getElementById('cart-modal').classList.contains('active')) {
                loadCartItems();
            }
        } else {
            showNotification(data.error || 'Failed to add to cart', 'error');
        }
    } catch (error) {
        console.error('Add to cart error:', error);
        showNotification('Failed to add to cart', 'error');
    } finally {
        showLoading(false);
    }
}

async function removeFromCart(productId) {
    if (!currentUser) {
        showNotification('Please login to manage cart', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/cart/remove/${productId}`, {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            cartCount = data.cart_count;
            currentCartItems = data.cart_items;
            updateCartWishlistUI();
            showNotification('Removed from cart', 'info');
            
            // Update cart display
            updateCartDisplay(currentCartItems, data.cart_total);
        } else {
            showNotification(data.error || 'Failed to remove from cart', 'error');
        }
    } catch (error) {
        console.error('Remove from cart error:', error);
        showNotification('Failed to remove from cart', 'error');
    } finally {
        showLoading(false);
    }
}

async function updateCartQuantity(productId, newQuantity) {
    if (!currentUser) return;
    
    if (newQuantity < 1) {
        removeFromCart(productId);
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/cart/update/${productId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ quantity: newQuantity }),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            cartCount = data.cart_count;
            currentCartItems = data.cart_items;
            updateCartWishlistUI();
            
            // Update cart display
            updateCartDisplay(currentCartItems, data.cart_total);
            showNotification('Cart updated', 'success');
        }
    } catch (error) {
        console.error('Update cart quantity error:', error);
        showNotification('Failed to update quantity', 'error');
    } finally {
        showLoading(false);
    }
}

async function loadCartItems() {
    if (!currentUser) {
        showNotification('Please login to view cart', 'error');
        showModal('login-modal');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/cart`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error('Failed to load cart');
        }
        
        const cartItems = await response.json();
        currentCartItems = cartItems;
        
        updateCartDisplay(cartItems);
    } catch (error) {
        console.error('Load cart items error:', error);
        showNotification('Failed to load cart', 'error');
    } finally {
        showLoading(false);
    }
}

function updateCartDisplay(cartItems, cartTotal = null) {
    const cartItemsContainer = document.getElementById('cart-items');
    const cartEmpty = document.getElementById('cart-empty');
    const cartSummary = document.getElementById('cart-summary');
    
    if (!cartItems || cartItems.length === 0) {
        cartItemsContainer.innerHTML = '';
        cartEmpty.style.display = 'block';
        cartSummary.style.display = 'none';
        return;
    }
    
    cartEmpty.style.display = 'none';
    cartSummary.style.display = 'block';
    
    // Calculate totals if not provided
    let subtotal = 0;
    let html = '';
    
    cartItems.forEach(item => {
        const itemTotal = item.price * item.quantity;
        subtotal += itemTotal;
        
        // CORRECTED: Use item.image instead of item.image_filename
        const itemImage = item.image || 'default.png';
        
        html += `
            <div class="cart-item" data-product-id="${item.id}">
                <div class="cart-item-image">
                    <img src="/static/images/products/${itemImage}" alt="${item.name}">
                </div>
                <div class="cart-item-info">
                    <div class="cart-item-title">${item.name}</div>
                    <div class="cart-item-category">${item.category}</div>
                    <div class="cart-item-price">₹${item.price.toLocaleString()}</div>
                </div>
                <div class="cart-item-quantity">
                    <button class="quantity-btn decrease" onclick="updateCartQuantity(${item.id}, ${item.quantity - 1})">-</button>
                    <span class="quantity">${item.quantity}</span>
                    <button class="quantity-btn increase" onclick="updateCartQuantity(${item.id}, ${item.quantity + 1})">+</button>
                </div>
                <div class="cart-item-total">₹${itemTotal.toLocaleString()}</div>
                <button class="cart-item-remove" onclick="removeFromCart(${item.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
    });
    
    cartItemsContainer.innerHTML = html;
    
    // Calculate shipping and total
    const shipping = subtotal > 0 ? 99 : 0;
    const total = cartTotal || (subtotal + shipping);
    
    document.getElementById('cart-subtotal').textContent = `₹${subtotal.toLocaleString()}`;
    document.getElementById('cart-shipping').textContent = `₹${shipping.toLocaleString()}`;
    document.getElementById('cart-total').textContent = `₹${total.toLocaleString()}`;
    
    // Update checkout button
    const checkoutBtn = document.getElementById('checkout-btn');
    if (checkoutBtn) {
        checkoutBtn.disabled = cartItems.length === 0;
    }
}

// Wishlist Functions
async function addToWishlist(productId) {
    if (!currentUser) {
        showNotification('Please login to add items to wishlist', 'error');
        showModal('login-modal');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/wishlist/add/${productId}`, {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            wishlistCount = data.wishlist_count;
            updateCartWishlistUI();
            showNotification('Added to wishlist!', 'success');
            
            // Update wishlist button state
            updateWishlistButtonState(productId, true);
            
            // Reload wishlist if modal is open
            if (document.getElementById('wishlist-modal').classList.contains('active')) {
                loadWishlistItems();
            }
        } else {
            showNotification(data.error || 'Failed to add to wishlist', 'error');
        }
    } catch (error) {
        console.error('Add to wishlist error:', error);
        showNotification('Failed to add to wishlist', 'error');
    } finally {
        showLoading(false);
    }
}

async function removeFromWishlist(productId) {
    if (!currentUser) {
        showNotification('Please login to manage wishlist', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/wishlist/remove/${productId}`, {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            wishlistCount = data.wishlist_count;
            updateCartWishlistUI();
            showNotification('Removed from wishlist', 'info');
            
            // Update wishlist button state
            updateWishlistButtonState(productId, false);
            
            // Update wishlist display if modal is open
            if (document.getElementById('wishlist-modal').classList.contains('active')) {
                loadWishlistItems();
            }
        } else {
            showNotification(data.error || 'Failed to remove from wishlist', 'error');
        }
    } catch (error) {
        console.error('Remove from wishlist error:', error);
        showNotification('Failed to remove from wishlist', 'error');
    } finally {
        showLoading(false);
    }
}

function updateWishlistButtonState(productId, isInWishlist) {
    const wishlistBtns = document.querySelectorAll(`[onclick*="${productId}"]`);
    wishlistBtns.forEach(btn => {
        if (btn.classList.contains('wishlist-btn')) {
            btn.innerHTML = `<i class="${isInWishlist ? 'fas' : 'far'} fa-heart"></i>`;
            btn.classList.toggle('active', isInWishlist);
            
            // Update onclick handler
            btn.onclick = () => {
                if (isInWishlist) {
                    removeFromWishlist(productId);
                } else {
                    addToWishlist(productId);
                }
            };
        }
    });
}

async function loadWishlistItems() {
    if (!currentUser) {
        showNotification('Please login to view wishlist', 'error');
        showModal('login-modal');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/wishlist`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error('Failed to load wishlist');
        }
        
        const wishlistItems = await response.json();
        
        const wishlistContainer = document.getElementById('wishlist-items');
        const wishlistEmpty = document.getElementById('wishlist-empty');
        
        if (!wishlistItems || wishlistItems.length === 0) {
            wishlistContainer.innerHTML = '';
            wishlistEmpty.style.display = 'block';
            return;
        }
        
        wishlistEmpty.style.display = 'none';
        let html = '';
        
        for (const item of wishlistItems) {
            html += await createProductCard(item, true);
        }
        
        wishlistContainer.innerHTML = html;
        
        // Add event listeners to new product cards
        setTimeout(() => {
            setupProductCardListeners();
        }, 100);
        
    } catch (error) {
        console.error('Load wishlist items error:', error);
        showNotification('Failed to load wishlist', 'error');
    } finally {
        showLoading(false);
    }
}

// Product Functions - CORRECTED IMAGE PATH
async function createProductCard(product, includeWishlistButton = true) {
    // Check if product is in wishlist (for logged-in users)
    let isInWishlist = false;
    if (currentUser) {
        try {
            const wishlistResponse = await fetch(`${API_BASE}/api/wishlist`, {
                credentials: 'include'
            });
            if (wishlistResponse.ok) {
                const wishlistItems = await wishlistResponse.json();
                isInWishlist = wishlistItems.some(item => item.id === product.id);
            }
        } catch (error) {
            console.error('Error checking wishlist status:', error);
        }
    }
    
    const originalPrice = product.on_sale ? product.price * 1.2 : null;
    
    // CORRECTED: Use product.image instead of product.image_filename
    const imageFilename = product.image || 'default.png';
    
    return `
        <div class="product-card" data-product-id="${product.id}">
            ${product.on_sale ? '<span class="discount-badge">20% OFF</span>' : ''}
            <div class="product-image">
                <img src="/static/images/products/${imageFilename}" 
                     alt="${product.name}" 
                     onclick="showProductModal(${product.id})">
            </div>
            <div class="product-info">
                <span class="product-category">${product.category}</span>
                <h3 class="product-title" onclick="showProductModal(${product.id})" style="cursor: pointer;">${product.name}</h3>
                <p class="product-description">${product.description.substring(0, 100)}${product.description.length > 100 ? '...' : ''}</p>
                <div class="product-price">
                    ${originalPrice ? 
                        `<span class="original-price">₹${Math.round(originalPrice).toLocaleString()}</span>` : 
                        ''
                    }
                    <span class="current-price">₹${product.price.toLocaleString()}</span>
                </div>
                <div class="product-actions">
                    <button class="btn btn-primary" onclick="addToCart(${product.id})">
                        <i class="fas fa-shopping-cart"></i> Add to Cart
                    </button>
                    ${includeWishlistButton ? `
                    <button class="wishlist-btn ${isInWishlist ? 'active' : ''}" 
                            onclick="${isInWishlist ? `removeFromWishlist(${product.id})` : `addToWishlist(${product.id})`}">
                        <i class="${isInWishlist ? 'fas' : 'far'} fa-heart"></i>
                    </button>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

async function showProductModal(productId) {
    try {
        const response = await fetch(`${API_BASE}/api/products/${productId}`);
        const product = await response.json();
        
        if (product.error) {
            showNotification('Product not found', 'error');
            return;
        }
        
        // Create modal content
        const modalContent = document.getElementById('product-modal-content');
        const specs = product.specs || {};
        
        // CORRECTED: Use product.image instead of product.image_filename
        const productImage = product.image || 'default.png';
        
        let specsHtml = '';
        for (const [key, value] of Object.entries(specs)) {
            specsHtml += `
                <div class="spec-item">
                    <span class="spec-label">${key.replace('_', ' ').toUpperCase()}</span>
                    <span class="spec-value">${value}</span>
                </div>
            `;
        }
        
        modalContent.innerHTML = `
            <div class="product-modal">
                <div class="product-modal-left">
                    <img src="/static/images/products/${productImage}" 
                         alt="${product.name}" 
                         class="product-modal-image">
                </div>
                <div class="product-modal-right">
                    <h1>${product.name}</h1>
                    <span class="product-modal-category">${product.category}</span>
                    <div class="product-modal-price">₹${product.price.toLocaleString()}</div>
                    <p>${product.description}</p>
                    
                    <div class="product-modal-specs">
                        <h3>Specifications</h3>
                        <div class="specs-grid">
                            ${specsHtml}
                        </div>
                    </div>
                    
                    <div class="product-modal-actions">
                        <button class="btn btn-primary" onclick="addToCart(${product.id})">
                            <i class="fas fa-shopping-cart"></i> Add to Cart
                        </button>
                        <button class="btn btn-secondary" onclick="showProductModal(${product.id})">
                            <i class="fas fa-info-circle"></i> View Details
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        showModal('product-modal');
        
    } catch (error) {
        console.error('Show product modal error:', error);
        showNotification('Failed to load product details', 'error');
    }
}

async function loadDealsProducts() {
    try {
        console.log("Loading deals products...");
        const response = await fetch(`${API_BASE}/api/deals`);
        const products = await response.json();
        
        if (elements.dealsProducts && products.length > 0) {
            let html = '';
            
            for (const product of products) {
                html += await createProductCard(product);
            }
            
            elements.dealsProducts.innerHTML = html;
            
            // Add event listeners to product cards
            setTimeout(() => {
                setupProductCardListeners();
            }, 100);
        } else {
            elements.dealsProducts.innerHTML = `
                <div class="no-products">
                    <i class="fas fa-box-open fa-3x"></i>
                    <h3>No deals available at the moment</h3>
                    <p>Check back soon for exciting offers!</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Load deals products error:', error);
        elements.dealsProducts.innerHTML = `
            <div class="no-products">
                <i class="fas fa-exclamation-triangle fa-3x"></i>
                <h3>Failed to load deals</h3>
                <p>Please try again later</p>
            </div>
        `;
    }
}

async function loadCategoryProducts(category) {
    try {
        console.log(`Loading ${category} products...`);
        const response = await fetch(`${API_BASE}/api/products/category/${category}`);
        const products = await response.json();
        
        if (elements.categoryProducts && products.length > 0) {
            let html = '';
            
            for (const product of products) {
                html += await createProductCard(product);
            }
            
            elements.categoryProducts.innerHTML = html;
            
            // Add event listeners to product cards
            setTimeout(() => {
                setupProductCardListeners();
            }, 100);
        } else {
            elements.categoryProducts.innerHTML = `
                <div class="no-products">
                    <i class="fas fa-box-open fa-3x"></i>
                    <h3>No products found in ${category}</h3>
                    <p>Check back soon for new arrivals!</p>
                </div>
            `;
        }
    } catch (error) {
        console.error(`Load ${category} products error:`, error);
        elements.categoryProducts.innerHTML = `
            <div class="no-products">
                <i class="fas fa-exclamation-triangle fa-3x"></i>
                <h3>Failed to load ${category}</h3>
                <p>Please try again later</p>
            </div>
        `;
    }
}

function setupProductCardListeners() {
    // Add click listeners to product images for modal
    document.querySelectorAll('.product-image img').forEach(img => {
        const productCard = img.closest('.product-card');
        if (productCard) {
            const productId = productCard.dataset.productId;
            img.addEventListener('click', () => showProductModal(parseInt(productId)));
        }
    });
    
    // Add click listeners to product titles for modal
    document.querySelectorAll('.product-title').forEach(title => {
        const productCard = title.closest('.product-card');
        if (productCard) {
            const productId = productCard.dataset.productId;
            title.addEventListener('click', () => showProductModal(parseInt(productId)));
        }
    });
}

// Category Functions
function setActiveCategory(category) {
    console.log("Setting active category:", category);
    
    // Update active category link
    elements.categoryLinks.forEach(link => {
        if (link.dataset.category === category) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
    
    // Update filter buttons
    elements.filterBtns.forEach(btn => {
        if (btn.dataset.category === category) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // Update current category text
    elements.currentCategory.textContent = category;
}

// Search Functions - CORRECTED IMAGE PATH
async function handleSearch() {
    const query = elements.searchInput.value.trim();
    
    if (query.length < 2) {
        elements.searchResults.style.display = 'none';
        elements.searchResults.innerHTML = '';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/products/search?q=${encodeURIComponent(query)}`);
        const products = await response.json();
        
        if (products.length === 0) {
            elements.searchResults.innerHTML = `
                <div class="no-results">
                    <p>No products found for "${query}"</p>
                </div>
            `;
            elements.searchResults.style.display = 'block';
            return;
        }
        
        let html = '';
        products.forEach(product => {
            // CORRECTED: Use product.image instead of product.image_filename
            const productImage = product.image || 'default.png';
            
            html += `
                <a href="#" class="search-result" onclick="showProductModal(${product.id}); event.preventDefault();">
                    <img src="/static/images/products/${productImage}" alt="${product.name}">
                    <div>
                        <h4>${product.name}</h4>
                        <div class="price">₹${product.price.toLocaleString()}</div>
                        <span class="category">${product.category}</span>
                    </div>
                </a>
            `;
        });
        
        elements.searchResults.innerHTML = html;
        elements.searchResults.style.display = 'block';
    } catch (error) {
        console.error('Search error:', error);
        elements.searchResults.innerHTML = `
            <div class="no-results">
                <p>Error searching products</p>
            </div>
        `;
        elements.searchResults.style.display = 'block';
    }
}

// Chatbot Functions
function toggleChatbot() {
    elements.chatbotContainer.classList.toggle('active');
    if (elements.chatbotContainer.classList.contains('active')) {
        elements.chatbotInput.focus();
    }
}

async function sendChatMessage() {
    const message = elements.chatbotInput.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addChatMessage(message, 'user');
    elements.chatbotInput.value = '';
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/chatbot`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ message }),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Add bot response to chat
            addChatMessage(data.response, 'bot');
        } else {
            addChatMessage('Sorry, I encountered an error. Please try again.', 'bot');
        }
    } catch (error) {
        console.error('Chatbot error:', error);
        addChatMessage('Sorry, I am having trouble connecting. Please try again later.', 'bot');
    } finally {
        showLoading(false);
    }
}

function addChatMessage(message, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chatbot-message ${sender}`;
    messageDiv.innerHTML = `<div class="message-content">${message}</div>`;
    
    elements.chatbotMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    elements.chatbotMessages.scrollTop = elements.chatbotMessages.scrollHeight;
}

// Profile Functions
async function loadProfileData() {
    if (!currentUser) return;
    
    document.getElementById('profile-name').value = currentUser.name || '';
    document.getElementById('profile-email').value = currentUser.email || '';
    document.getElementById('profile-phone').value = currentUser.phone || '';
    document.getElementById('profile-address').value = currentUser.address || '';
    document.getElementById('profile-pincode').value = currentUser.pincode || '';
}

async function updateProfile() {
    if (!currentUser) return;
    
    const formData = {
        full_name: document.getElementById('profile-name').value,
        email: document.getElementById('profile-email').value,
        phone: document.getElementById('profile-phone').value,
        address: document.getElementById('profile-address').value,
        pincode: document.getElementById('profile-pincode').value
    };
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/auth/update-profile`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Update current user data
            currentUser = { ...currentUser, ...formData };
            updateUserUI(true, currentUser);
            hideModal('profile-modal');
            showNotification('Profile updated successfully!', 'success');
        } else {
            showNotification(data.error || 'Failed to update profile', 'error');
        }
    } catch (error) {
        console.error('Update profile error:', error);
        showNotification('Failed to update profile', 'error');
    } finally {
        showLoading(false);
    }
}

// Order Functions
async function loadOrders() {
    try {
        const response = await fetch(`${API_BASE}/api/orders`, {
            credentials: 'include'
        });
        const orders = await response.json();
        
        const ordersContainer = document.getElementById('orders-container');
        
        if (!orders || orders.length === 0) {
            ordersContainer.innerHTML = `
                <div class="no-orders">
                    <i class="fas fa-box-open fa-3x"></i>
                    <h3>No orders yet</h3>
                    <p>Start shopping to see your orders here!</p>
                </div>
            `;
            return;
        }
        
        let html = '';
        orders.forEach(order => {
            const products = JSON.parse(order.products || '[]');
            let productsHtml = '';
            
            products.forEach(product => {
                productsHtml += `
                    <div class="order-product">
                        <div class="order-product-info">
                            <div class="order-product-name">${product.name}</div>
                            <div class="order-product-quantity">Quantity: ${product.quantity}</div>
                            <div class="order-product-price">Price: ₹${product.price.toLocaleString()}</div>
                        </div>
                    </div>
                `;
            });
            
            html += `
                <div class="order-item">
                    <div class="order-header">
                        <div class="order-id">Order #${order.order_id}</div>
                        <div class="order-status ${order.status}">${order.status}</div>
                    </div>
                    <div class="order-products">
                        ${productsHtml}
                    </div>
                    <div class="order-summary">
                        <div class="order-total">Total: ₹${order.total_amount.toLocaleString()}</div>
                        <div class="order-date">${new Date(order.created_at).toLocaleDateString()}</div>
                    </div>
                </div>
            `;
        });
        
        ordersContainer.innerHTML = html;
    } catch (error) {
        console.error('Load orders error:', error);
        document.getElementById('orders-container').innerHTML = `
            <div class="no-orders">
                <i class="fas fa-exclamation-triangle fa-3x"></i>
                <h3>Failed to load orders</h3>
                <p>Please try again later</p>
            </div>
        `;
    }
}

// Payment Functions
function showPaymentModal() {
    const cartTotal = document.getElementById('cart-total')?.textContent || '₹0';
    
    // Update payment summary
    const paymentSummary = document.getElementById('payment-summary');
    paymentSummary.innerHTML = `
        <h3>Order Summary</h3>
        <div class="payment-summary-row">
            <span>Total Amount</span>
            <span>${cartTotal}</span>
        </div>
    `;
    
    showModal('payment-modal');
}

async function processPayment() {
    const selectedMethod = document.querySelector('.payment-method.active');
    if (!selectedMethod) {
        showNotification('Please select a payment method', 'error');
        return;
    }
    
    const paymentMethod = selectedMethod.dataset.method;
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/orders`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ payment_method: paymentMethod }),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            hideModal('payment-modal');
            hideModal('cart-modal');
            
            // Update cart count
            cartCount = data.cart_count || 0;
            updateCartWishlistUI();
            
            showNotification(`Order placed successfully! Order ID: ${data.order_id}`, 'success');
        } else {
            showNotification(data.error || 'Payment failed', 'error');
        }
    } catch (error) {
        console.error('Payment error:', error);
        showNotification('Payment failed. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

// Forgot Password Functions
async function sendForgotPasswordOTP() {
    const identifier = document.getElementById('forgot-identifier').value;
    
    if (!identifier) {
        showNotification('Please enter your email or phone number', 'error');
        return;
    }
    
    showNotification('OTP sent to your email/phone (demo only)', 'info');
    
    // In a real app, you would make an API call here
    // For demo, just show step 2
    document.getElementById('forgot-step-1').style.display = 'none';
    document.getElementById('forgot-step-2').style.display = 'block';
}

async function resetPassword() {
    const otp = document.getElementById('forgot-otp').value;
    const newPassword = document.getElementById('new-password').value;
    
    if (!otp || !newPassword) {
        showNotification('Please enter OTP and new password', 'error');
        return;
    }
    
    // In a real app, you would verify OTP and update password via API
    // For demo, just show success
    hideModal('forgot-modal');
    showNotification('Password reset successful! You can now login with your new password.', 'success');
}

// UI Helper Functions
function updateCartWishlistCounts() {
    if (currentUser) {
        // Counts are already updated when user logs in
        return;
    } else {
        cartCount = 0;
        wishlistCount = 0;
        updateCartWishlistUI();
    }
}

function updateCartWishlistUI() {
    if (elements.cartCount) {
        elements.cartCount.textContent = cartCount;
        elements.cartCount.style.display = cartCount > 0 ? 'flex' : 'none';
    }
    
    if (elements.wishlistCount) {
        elements.wishlistCount.textContent = wishlistCount;
        elements.wishlistCount.style.display = wishlistCount > 0 ? 'flex' : 'none';
    }
}

function toggleUserDropdown() {
    elements.userDropdown.classList.toggle('show');
}

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
}

function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    if (!notification) {
        // Create notification element if it doesn't exist
        const notificationDiv = document.createElement('div');
        notificationDiv.id = 'notification';
        notificationDiv.className = `notification ${type}`;
        notificationDiv.innerHTML = `
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        `;
        document.body.appendChild(notificationDiv);
        notificationDiv.style.display = 'flex';
        
        setTimeout(() => {
            notificationDiv.style.display = 'none';
            notificationDiv.remove();
        }, 3000);
        return;
    }
    
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)}"></i>
        <span>${message}</span>
    `;
    
    notification.style.display = 'flex';
    
    // Hide after 3 seconds
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

function getNotificationIcon(type) {
    switch(type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        case 'warning': return 'exclamation-triangle';
        default: return 'info-circle';
    }
}

function showLoading(show) {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = show ? 'flex' : 'none';
    }
}

function loadInitialData() {
    console.log("Loading initial data...");
    
    // Load deals on page load
    loadDealsProducts();
    
    // Load smartphones by default
    loadCategoryProducts('Smartphones');
}

// Global functions for onclick handlers
window.addToCart = addToCart;
window.addToWishlist = addToWishlist;
window.removeFromWishlist = removeFromWishlist;
window.removeFromCart = removeFromCart;
window.showProductModal = showProductModal;
window.updateCartQuantity = updateCartQuantity;
window.setActiveCategory = setActiveCategory;
window.showNotification = showNotification;

// Close search results when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-box') && elements.searchResults) {
        elements.searchResults.style.display = 'none';
    }
});

console.log("JavaScript loaded successfully!");