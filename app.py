from flask import Flask, render_template, request, jsonify, session, make_response
from flask_cors import CORS
import sqlite3
import json
import os
from datetime import datetime
import random
import re
import hashlib

app = Flask(__name__)
app.secret_key = 'techstore-secret-key-2024'  # Change this in production
CORS(app, supports_credentials=True)

DATABASE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """Initialize database if not exists"""
    if not os.path.exists(DATABASE):
        print("Database not found. Please run database.py first.")
        return False
    return True

# Auth helper functions
def is_logged_in():
    return 'user_id' in session

def get_user_id():
    return session.get('user_id')

# Routes
@app.route('/')
def index():
    """Home page - shows only required sections"""
    return render_template('index.html')

@app.route('/product/<int:product_id>')
def product_details(product_id):
    """Product details page with template rendering"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get product details - FIXED: Use correct field names
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product_row = cursor.fetchone()
    
    if not product_row:
        conn.close()
        return render_template('index.html', product=None)
    
    # Convert row to dict
    product = dict(product_row)
    
    # Parse specs JSON
    product['specs'] = json.loads(product['specs']) if product.get('specs') else {}
    
    # Check if product is in user's wishlist (if logged in)
    product['in_wishlist'] = False
    if is_logged_in():
        user_id = get_user_id()
        cursor.execute('SELECT id FROM wishlist WHERE user_id = ? AND product_id = ?', 
                      (user_id, product_id))
        if cursor.fetchone():
            product['in_wishlist'] = True
    
    # Set additional fields expected by template - FIXED: Use correct field mapping
    product['title'] = product['name']  # HTML expects 'title' but we have 'name'
    
    # FIXED: Handle image field properly - check multiple possible field names
    image_field = None
    if product.get('image'):
        image_field = product['image']
    elif product.get('image_filename'):
        image_field = product['image_filename']
    
    # Set image path
    if image_field:
        product['image_url'] = f"/static/images/products/{image_field}"
    else:
        product['image_url'] = "/static/images/products/default.png"
    
    # Set other required fields with defaults
    product['original_price'] = product.get('original_price', product['price'] * 1.2)
    product['rating'] = product.get('rating', 4.5)
    product['review_count'] = product.get('review_count', 0)
    product['brand'] = product.get('brand', product['category'])
    product['in_stock'] = product.get('stock', 10) > 0
    
    # For additional images, you can add them if you have them in your database
    product['additional_images'] = []
    
    conn.close()
    
    # DEBUG: Print product data
    print(f"PRODUCT DETAILS: ID={product_id}, Name={product['name']}, Image={image_field}")
    
    # Render template with product data
    return render_template('index.html', product=product)

@app.route('/api/products')
def get_all_products():
    """Get all products - MISSING ENDPOINT"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    
    result = []
    for product in products:
        product_dict = dict(product)
        product_dict['specs'] = json.loads(product_dict['specs'])
        result.append(product_dict)
    
    conn.close()
    return jsonify(result)

@app.route('/api/deals')
def get_deals():
    """Get 10 mixed products on sale"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get 10 random products that are on sale
    cursor.execute('''
        SELECT * FROM products 
        WHERE on_sale = 1 
        ORDER BY RANDOM() 
        LIMIT 10
    ''')
    
    products = cursor.fetchall()
    result = []
    
    for product in products:
        product_dict = dict(product)
        # Parse JSON specs
        product_dict['specs'] = json.loads(product_dict['specs'])
        result.append(product_dict)
    
    conn.close()
    return jsonify(result)

@app.route('/api/products/category/<category>')
def get_products_by_category(category):
    """Get all products by category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM products WHERE category = ?', (category,))
    products = cursor.fetchall()
    
    result = []
    for product in products:
        product_dict = dict(product)
        product_dict['specs'] = json.loads(product_dict['specs'])
        result.append(product_dict)
    
    conn.close()
    return jsonify(result)

@app.route('/api/products/<int:product_id>')
def get_product(product_id):
    """Get single product details for API (used by JavaScript)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    
    if product:
        product_dict = dict(product)
        product_dict['specs'] = json.loads(product_dict['specs'])
        conn.close()
        return jsonify(product_dict)
    
    conn.close()
    return jsonify({'error': 'Product not found'}), 404

@app.route('/api/products/search')
def search_products():
    """Search products by name, category, or description"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify([])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    search_term = f'%{query}%'
    cursor.execute('''
        SELECT * FROM products 
        WHERE name LIKE ? 
        OR category LIKE ? 
        OR description LIKE ?
        LIMIT 20
    ''', (search_term, search_term, search_term))
    
    products = cursor.fetchall()
    result = []
    
    for product in products:
        product_dict = dict(product)
        product_dict['specs'] = json.loads(product_dict['specs'])
        result.append(product_dict)
    
    conn.close()
    return jsonify(result)

# User Authentication
@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['full_name', 'email', 'phone', 'address', 'pincode', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate phone number (10 digits)
        if not re.match(r'^\d{10}$', str(data['phone'])):
            return jsonify({'error': 'Phone number must be 10 digits'}), 400
        
        # Validate pincode (6 digits)
        if not re.match(r'^\d{6}$', str(data['pincode'])):
            return jsonify({'error': 'Pincode must be 6 digits'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Check if email or phone already exists
            cursor.execute('SELECT id FROM users WHERE email = ? OR phone = ?', 
                          (data['email'], data['phone']))
            if cursor.fetchone():
                conn.close()
                return jsonify({'error': 'Email or phone already registered'}), 400
            
            # Create user with hashed password
            hashed_password = hash_password(data['password'])
            cursor.execute('''
                INSERT INTO users (full_name, email, phone, address, pincode, password)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (data['full_name'], data['email'], data['phone'], 
                  data['address'], data['pincode'], hashed_password))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            # Set session
            session['user_id'] = user_id
            session['user_name'] = data['full_name']
            session['user_email'] = data['email']
            
            # Get initial counts
            cursor.execute('SELECT COUNT(*) as count FROM cart WHERE user_id = ?', (user_id,))
            cart_count = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM wishlist WHERE user_id = ?', (user_id,))
            wishlist_count = cursor.fetchone()['count']
            
            conn.close()
            
            # Create response
            response = jsonify({
                'success': True,
                'message': 'Registration successful',
                'user': {
                    'id': user_id,
                    'name': data['full_name'],
                    'email': data['email'],
                    'phone': data['phone'],
                    'address': data['address'],
                    'pincode': data['pincode']
                },
                'cart_count': cart_count,
                'wishlist_count': wishlist_count
            })
            
            return response
            
        except Exception as e:
            conn.close()
            print(f"Database error: {str(e)}")
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login with email/phone"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        identifier = data.get('identifier', '').strip()
        password = data.get('password', '').strip()
        
        if not identifier or not password:
            return jsonify({'error': 'Identifier and password are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Try to find user by email or phone
        cursor.execute('''
            SELECT id, full_name, email, phone, address, pincode, password
            FROM users 
            WHERE (email = ? OR phone = ?)
        ''', (identifier, identifier))
        
        user = cursor.fetchone()
        
        if user:
            # Verify password
            hashed_password = hash_password(password)
            if user['password'] == hashed_password:
                # Set session
                session['user_id'] = user['id']
                session['user_name'] = user['full_name']
                session['user_email'] = user['email']
                
                # Get cart and wishlist counts
                cursor.execute('SELECT COUNT(*) as count FROM cart WHERE user_id = ?', (user['id'],))
                cart_count = cursor.fetchone()['count']
                
                cursor.execute('SELECT COUNT(*) as count FROM wishlist WHERE user_id = ?', (user['id'],))
                wishlist_count = cursor.fetchone()['count']
                
                conn.close()
                
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'user': {
                        'id': user['id'],
                        'name': user['full_name'],
                        'email': user['email'],
                        'phone': user['phone'],
                        'address': user['address'],
                        'pincode': user['pincode']
                    },
                    'cart_count': cart_count,
                    'wishlist_count': wishlist_count
                })
        
        conn.close()
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/auth/logout')
def logout():
    """Logout user"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/auth/check')
def check_auth():
    """Check if user is logged in"""
    if is_logged_in():
        user_id = get_user_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT full_name, email, phone, address, pincode FROM users WHERE id = ?', 
                      (user_id,))
        user = cursor.fetchone()
        
        if user:
            # Get counts
            cursor.execute('SELECT COUNT(*) as count FROM cart WHERE user_id = ?', (user_id,))
            cart_count = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM wishlist WHERE user_id = ?', (user_id,))
            wishlist_count = cursor.fetchone()['count']
            
            conn.close()
            
            return jsonify({
                'logged_in': True,
                'user': {
                    'name': user['full_name'],
                    'email': user['email'],
                    'phone': user['phone'],
                    'address': user['address'],
                    'pincode': user['pincode']
                },
                'cart_count': cart_count,
                'wishlist_count': wishlist_count
            })
        conn.close()
    
    return jsonify({'logged_in': False})

@app.route('/api/auth/update-profile', methods=['POST'])
def update_profile():
    """Update user profile - MISSING ENDPOINT"""
    if not is_logged_in():
        return jsonify({'error': 'Please login first'}), 401
    
    try:
        data = request.get_json()
        user_id = get_user_id()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET full_name = ?, email = ?, phone = ?, address = ?, pincode = ?
            WHERE id = ?
        ''', (
            data.get('full_name'),
            data.get('email'),
            data.get('phone'),
            data.get('address'),
            data.get('pincode'),
            user_id
        ))
        
        conn.commit()
        
        # Get updated user
        cursor.execute('SELECT full_name, email, phone, address, pincode FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        
        # Update session
        session['user_name'] = user['full_name']
        session['user_email'] = user['email']
        
        return jsonify({
            'success': True,
            'message': 'Profile updated',
            'user': dict(user)
        })
        
    except Exception as e:
        print(f"Update profile error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Cart Management
@app.route('/api/cart')
def get_cart():
    """Get user's cart items"""
    if not is_logged_in():
        return jsonify([])
    
    user_id = get_user_id()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT c.id, c.quantity, p.*
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    ''', (user_id,))
    
    cart_items = cursor.fetchall()
    result = []
    
    for item in cart_items:
        item_dict = dict(item)
        item_dict['specs'] = json.loads(item_dict['specs'])
        result.append(item_dict)
    
    conn.close()
    return jsonify(result)

@app.route('/api/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    """Add product to cart"""
    if not is_logged_in():
        return jsonify({'error': 'Please login first'}), 401
    
    user_id = get_user_id()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if product exists
        cursor.execute('SELECT id FROM products WHERE id = ?', (product_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Product not found'}), 404
        
        # Check if already in cart
        cursor.execute('SELECT id, quantity FROM cart WHERE user_id = ? AND product_id = ?', 
                      (user_id, product_id))
        existing = cursor.fetchone()
        
        if existing:
            # Update quantity
            cursor.execute('''
                UPDATE cart SET quantity = quantity + 1 
                WHERE id = ?
            ''', (existing['id'],))
        else:
            # Add new item
            cursor.execute('''
                INSERT INTO cart (user_id, product_id, quantity) 
                VALUES (?, ?, 1)
            ''', (user_id, product_id))
        
        conn.commit()
        
        # Get new count
        cursor.execute('SELECT COUNT(*) as count FROM cart WHERE user_id = ?', (user_id,))
        count = cursor.fetchone()['count']
        
        conn.close()
        return jsonify({
            'success': True,
            'message': 'Added to cart',
            'cart_count': count
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/cart/update/<int:product_id>', methods=['PUT', 'POST'])
def update_cart_quantity(product_id):
    """Update cart item quantity"""
    if not is_logged_in():
        return jsonify({'error': 'Please login first'}), 401
    
    user_id = get_user_id()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        data = request.get_json()
        if not data or 'quantity' not in data:
            return jsonify({'error': 'Quantity is required'}), 400
        
        quantity = int(data['quantity'])
        if quantity < 1:
            # If quantity is 0 or less, remove the item
            return remove_from_cart(product_id)
        
        # Check if item exists in cart
        cursor.execute('SELECT id FROM cart WHERE user_id = ? AND product_id = ?', 
                      (user_id, product_id))
        
        item = cursor.fetchone()
        if not item:
            conn.close()
            return jsonify({'error': 'Item not found in cart'}), 404
        
        # Update quantity
        cursor.execute('UPDATE cart SET quantity = ? WHERE id = ?', 
                      (quantity, item['id']))
        
        conn.commit()
        
        # Get updated cart
        cursor.execute('''
            SELECT c.id, c.quantity, p.*
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = ?
        ''', (user_id,))
        
        cart_items = cursor.fetchall()
        result = []
        
        for item in cart_items:
            item_dict = dict(item)
            item_dict['specs'] = json.loads(item_dict['specs'])
            result.append(item_dict)
        
        # Calculate total
        total = sum(item['price'] * item['quantity'] for item in result)
        
        # Get cart count
        cursor.execute('SELECT COUNT(*) as count FROM cart WHERE user_id = ?', (user_id,))
        count = cursor.fetchone()['count']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Cart updated',
            'cart_items': result,
            'cart_total': total,
            'cart_count': count
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/cart/remove/<int:product_id>', methods=['DELETE', 'POST'])
def remove_from_cart(product_id):
    """Remove product from cart"""
    if not is_logged_in():
        return jsonify({'error': 'Please login first'}), 401
    
    user_id = get_user_id()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if item exists in cart
        cursor.execute('SELECT id FROM cart WHERE user_id = ? AND product_id = ?', 
                      (user_id, product_id))
        
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Item not found in cart'}), 404
        
        # Remove from cart
        cursor.execute('DELETE FROM cart WHERE user_id = ? AND product_id = ?', 
                      (user_id, product_id))
        
        conn.commit()
        
        # Get updated cart
        cursor.execute('''
            SELECT c.id, c.quantity, p.*
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = ?
        ''', (user_id,))
        
        cart_items = cursor.fetchall()
        result = []
        
        for item in cart_items:
            item_dict = dict(item)
            item_dict['specs'] = json.loads(item_dict['specs'])
            result.append(item_dict)
        
        # Calculate total
        total = sum(item['price'] * item['quantity'] for item in result)
        
        # Get new count
        cursor.execute('SELECT COUNT(*) as count FROM cart WHERE user_id = ?', (user_id,))
        count = cursor.fetchone()['count']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Removed from cart',
            'cart_items': result,
            'cart_total': total,
            'cart_count': count
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/cart/clear', methods=['DELETE', 'POST'])
def clear_cart():
    """Clear all items from cart"""
    if not is_logged_in():
        return jsonify({'error': 'Please login first'}), 401
    
    user_id = get_user_id()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Clear cart for this user
        cursor.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
        conn.commit()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Cart cleared',
            'cart_items': [],
            'cart_total': 0,
            'cart_count': 0
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

# Wishlist Management
@app.route('/api/wishlist')
def get_wishlist():
    """Get user's wishlist"""
    if not is_logged_in():
        return jsonify([])
    
    user_id = get_user_id()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT w.id, p.*
        FROM wishlist w
        JOIN products p ON w.product_id = p.id
        WHERE w.user_id = ?
    ''', (user_id,))
    
    wishlist_items = cursor.fetchall()
    result = []
    
    for item in wishlist_items:
        item_dict = dict(item)
        item_dict['specs'] = json.loads(item_dict['specs'])
        result.append(item_dict)
    
    conn.close()
    return jsonify(result)

@app.route('/api/wishlist/add/<int:product_id>', methods=['POST'])
def add_to_wishlist(product_id):
    """Add product to wishlist"""
    if not is_logged_in():
        return jsonify({'error': 'Please login first'}), 401
    
    user_id = get_user_id()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if product exists
        cursor.execute('SELECT id FROM products WHERE id = ?', (product_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Product not found'}), 404
        
        # Check if already in wishlist
        cursor.execute('SELECT id FROM wishlist WHERE user_id = ? AND product_id = ?', 
                      (user_id, product_id))
        
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Already in wishlist'}), 400
        
        # Add to wishlist
        cursor.execute('''
            INSERT INTO wishlist (user_id, product_id) 
            VALUES (?, ?)
        ''', (user_id, product_id))
        
        conn.commit()
        
        # Get new count
        cursor.execute('SELECT COUNT(*) as count FROM wishlist WHERE user_id = ?', (user_id,))
        count = cursor.fetchone()['count']
        
        conn.close()
        return jsonify({
            'success': True,
            'message': 'Added to wishlist',
            'wishlist_count': count
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/wishlist/remove/<int:product_id>', methods=['DELETE', 'POST'])
def remove_from_wishlist(product_id):
    """Remove product from wishlist"""
    if not is_logged_in():
        return jsonify({'error': 'Please login first'}), 401
    
    user_id = get_user_id()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if item exists in wishlist
        cursor.execute('SELECT id FROM wishlist WHERE user_id = ? AND product_id = ?', 
                      (user_id, product_id))
        
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Item not found in wishlist'}), 404
        
        # Remove from wishlist
        cursor.execute('DELETE FROM wishlist WHERE user_id = ? AND product_id = ?', 
                      (user_id, product_id))
        
        conn.commit()
        
        # Get new count
        cursor.execute('SELECT COUNT(*) as count FROM wishlist WHERE user_id = ?', (user_id,))
        count = cursor.fetchone()['count']
        
        conn.close()
        return jsonify({
            'success': True,
            'message': 'Removed from wishlist',
            'wishlist_count': count
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

# Chatbot
@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    """Rule-based chatbot"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No message provided'}), 400
        
        message = data.get('message', '').strip().lower()
        user_id = session.get('user_id', 0)
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Simple rule-based responses
        responses = {
            'greeting': [
                "Hello! 👋 I'm your AI shopping assistant. How can I help you today?",
                "Hi there! Welcome to TechStore. How can I assist you?",
                "Greetings! I'm here to help you with your shopping needs."
            ],
            'help': [
                "I can help you with: • Product information • Category details • Price & deals • Delivery info • Return policy",
                "I can assist you with: 1. Finding products 2. Checking prices 3. Delivery information 4. Return policies"
            ],
            'smartphones': [
                "We have a wide range of smartphones from Apple, Samsung, OnePlus, Google, and more. Check our smartphone category for the latest models!",
                "Looking for smartphones? We have iPhones, Samsung Galaxy, Google Pixel, and other premium brands with various price ranges."
            ],
            'laptops': [
                "We offer laptops for every need: MacBook for professionals, gaming laptops from Asus and MSI, and ultrabooks from Dell and HP.",
                "Browse our laptop collection featuring MacBooks, Dell XPS, HP Spectre, gaming laptops, and budget-friendly options."
            ],
            'headphones': [
                "We have noise-cancelling headphones from Sony and Bose, premium audio from Sennheiser, and gaming headsets.",
                "Check out our headphone selection including Sony WH-1000XM5, Bose QC45, Apple AirPods Max, and more!"
            ],
            'earbuds': [
                "Our earbuds collection includes Apple AirPods Pro, Sony WF-1000XM5, Samsung Galaxy Buds, and Bose QuietComfort.",
                "We have true wireless earbuds from top brands with features like noise cancellation and long battery life."
            ],
            'price': [
                "Prices vary by product and specifications. You can check individual product pages for current prices and deals.",
                "We offer competitive prices across all categories. Check our deals section for special offers!"
            ],
            'delivery': [
                "We offer free shipping on orders above ₹5000. Delivery usually takes 3-7 business days across India.",
                "Standard delivery: 5-7 days • Express delivery: 2-3 days (extra charges apply) • Free shipping on orders above ₹5000"
            ],
            'return': [
                "We have a 10-day return policy for unused products in original packaging. Refunds are processed within 5-7 business days.",
                "Returns are accepted within 10 days of delivery. Products must be unused with original packaging and accessories."
            ],
            'contact': [
                "You can contact us at: • Phone: 1800-123-4567 • Email: support@techstore.com • Address: 123 Tech Street, Mumbai",
                "Reach us at support@techstore.com or call 1800-123-4567. We're available 9 AM to 8 PM, Monday to Saturday."
            ],
            'budget phone': [
                "For budget smartphones, check out Nothing Phone 2 (₹44,999) or OnePlus 11 5G (₹56,999). Great value for money!",
                "Best budget options: Nothing Phone 2 (₹44,999) offers great features at an affordable price."
            ],
            'camera phone': [
                "For best camera: iPhone 15 Pro (₹1,29,999), Samsung S23 Ultra (₹1,24,999), or Google Pixel 8 Pro (₹1,06,999).",
                "Top camera phones: Samsung S23 Ultra with 200MP camera or iPhone 15 Pro with advanced photography features."
            ],
            'battery': [
                "For long battery life: Samsung S23 Ultra (5000mAh), OnePlus 11 (5000mAh), or iPhone 15 Pro (3274mAh).",
                "Best battery life in smartphones: Samsung Galaxy series and OnePlus models typically have large batteries."
            ],
            'storage': [
                "Most smartphones come with 128GB, 256GB, or 512GB storage options. Some high-end models offer 1TB.",
                "Storage options vary: Entry-level: 128GB • Mid-range: 256GB • Premium: 512GB-1TB • Choose based on your needs."
            ],
            'default': [
                "I'm not sure I understand. Could you rephrase your question?",
                "I'm here to help with shopping queries. Try asking about products, prices, or delivery!",
                "Please ask me about our products, categories, prices, or store policies."
            ]
        }
        
        # Determine response category based on keywords
        response_category = 'default'
        
        if any(word in message for word in ['hello', 'hi', 'hey', 'greeting']):
            response_category = 'greeting'
        elif any(word in message for word in ['help', 'what can you do', 'assist']):
            response_category = 'help'
        elif any(word in message for word in ['phone', 'smartphone', 'iphone', 'samsung', 'mobile']):
            response_category = 'smartphones'
        elif any(word in message for word in ['laptop', 'macbook', 'notebook', 'computer']):
            response_category = 'laptops'
        elif any(word in message for word in ['headphone', 'headset', 'earphone']):
            response_category = 'headphones'
        elif any(word in message for word in ['earbud', 'airpod', 'wireless earbud']):
            response_category = 'earbuds'
        elif any(word in message for word in ['price', 'cost', 'how much', 'expensive']):
            response_category = 'price'
        elif any(word in message for word in ['delivery', 'shipping', 'deliver', 'ship']):
            response_category = 'delivery'
        elif any(word in message for word in ['return', 'refund', 'exchange', 'warranty']):
            response_category = 'return'
        elif any(word in message for word in ['contact', 'email', 'phone', 'address', 'call']):
            response_category = 'contact'
        elif any(word in message for word in ['budget', 'cheap', 'affordable', 'economical']):
            response_category = 'budget phone'
        elif any(word in message for word in ['camera', 'photo', 'picture', 'photography']):
            response_category = 'camera phone'
        elif any(word in message for word in ['battery', 'charge', 'power', 'backup']):
            response_category = 'battery'
        elif any(word in message for word in ['storage', 'memory', 'gb', 'space']):
            response_category = 'storage'
        
        # Get random response from category
        import random
        response = random.choice(responses[response_category])
        
        # Log the interaction
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chatbot_logs (user_id, message, response)
            VALUES (?, ?, ?)
        ''', (user_id, message, response))
        
        conn.commit()
        conn.close()
        
        return jsonify({'response': response})
        
    except Exception as e:
        print(f"Chatbot error: {str(e)}")
        return jsonify({'error': f'Chatbot error: {str(e)}'}), 500

# Order Management
@app.route('/api/orders', methods=['GET', 'POST'])
def orders():
    """Get user orders or create new order - MISSING ENDPOINT"""
    if not is_logged_in():
        return jsonify({'error': 'Please login first'}), 401
    
    user_id = get_user_id()
    
    if request.method == 'GET':
        # Get user orders
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM orders 
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        orders = cursor.fetchall()
        result = []
        
        for order in orders:
            order_dict = dict(order)
            result.append(order_dict)
        
        conn.close()
        return jsonify(result)
    
    elif request.method == 'POST':
        # Create new order from cart
        data = request.get_json()
        payment_method = data.get('payment_method', 'cod')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get cart items
            cursor.execute('''
                SELECT c.quantity, p.*
                FROM cart c
                JOIN products p ON c.product_id = p.id
                WHERE c.user_id = ?
            ''', (user_id,))
            
            cart_items = cursor.fetchall()
            
            if not cart_items:
                conn.close()
                return jsonify({'error': 'Cart is empty'}), 400
            
            # Calculate total
            total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
            
            # Create order
            cursor.execute('''
                INSERT INTO orders (user_id, total_amount, payment_method, status)
                VALUES (?, ?, ?, 'Pending')
            ''', (user_id, total_amount, payment_method,))
            
            order_id = cursor.lastrowid
            
            # Add order items
            for item in cart_items:
                cursor.execute('''
                    INSERT INTO order_items (order_id, product_id, quantity, price)
                    VALUES (?, ?, ?, ?)
                ''', (order_id, item['id'], item['quantity'], item['price']))
            
            # Clear cart
            cursor.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
            
            conn.commit()
            
            # Get cart count after clearing
            cursor.execute('SELECT COUNT(*) as count FROM cart WHERE user_id = ?', (user_id,))
            cart_count = cursor.fetchone()['count']
            
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Order placed successfully',
                'order_id': order_id,
                'cart_count': cart_count
            })
            
        except Exception as e:
            conn.close()
            print(f"Order creation error: {str(e)}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get specific order details - MISSING ENDPOINT"""
    if not is_logged_in():
        return jsonify({'error': 'Please login first'}), 401
    
    user_id = get_user_id()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get order
    cursor.execute('SELECT * FROM orders WHERE id = ? AND user_id = ?', (order_id, user_id))
    order = cursor.fetchone()
    
    if not order:
        conn.close()
        return jsonify({'error': 'Order not found'}), 404
    
    # Get order items
    cursor.execute('''
        SELECT oi.*, p.name, p.image
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    ''', (order_id,))
    
    items = cursor.fetchall()
    
    result = {
        'order': dict(order),
        'items': [dict(item) for item in items]
    }
    
    conn.close()
    return jsonify(result)

# Test route for debugging images
@app.route('/test_images')
def test_images():
    """Test route to debug image issues"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all products to check
    cursor.execute("SELECT id, name, image FROM products LIMIT 10")
    products = cursor.fetchall()
    
    html = """
    <html>
    <head>
        <title>Image Test</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .product { border: 1px solid #ddd; padding: 15px; margin: 10px; }
            img { max-width: 200px; height: auto; border: 1px solid #ccc; }
            .error { color: red; }
            .success { color: green; }
        </style>
    </head>
    <body>
        <h1>Image Test Page</h1>
        <p>Testing if images are accessible from the database</p>
    """
    
    for product in products:
        product_id, name, image = product
        image_path = f"/static/images/products/{image}" if image else "/static/images/products/default.png"
        
        html += f"""
        <div class="product">
            <h3>ID: {product_id} - {name}</h3>
            <p>Image field: <code>{image}</code></p>
            <p>Image path: <code>{image_path}</code></p>
            <img src="{image_path}" alt="{name}">
            <p>Image URL: <a href="{image_path}" target="_blank">{image_path}</a></p>
            <p>Product page: <a href="/product/{product_id}">/product/{product_id}</a></p>
        </div>
        """
    
    html += """
    </body>
    </html>
    """
    
    conn.close()
    return html

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

# CORS headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

if __name__ == '__main__':
    # Initialize database
    if init_db():
        print("Database initialized successfully")
        print("Visit /test_images to check if images are working")
        print("Available API endpoints:")
        print("  GET  /api/products")
        print("  GET  /api/deals")
        print("  GET  /api/products/category/<category>")
        print("  GET  /api/products/<id>")
        print("  GET  /api/products/search?q=<query>")
        print("  POST /api/auth/register")
        print("  POST /api/auth/login")
        print("  GET  /api/auth/logout")
        print("  GET  /api/auth/check")
        print("  POST /api/auth/update-profile")
        print("  GET  /api/cart")
        print("  POST /api/cart/add/<id>")
        print("  POST /api/cart/update/<id>")
        print("  POST /api/cart/remove/<id>")
        print("  POST /api/cart/clear")
        print("  GET  /api/wishlist")
        print("  POST /api/wishlist/add/<id>")
        print("  POST /api/wishlist/remove/<id>")
        print("  POST /api/chatbot")
        print("  GET  /api/orders")
        print("  POST /api/orders")
        print("  GET  /api/orders/<id>")
    else:
        print("Warning: Database not found")
        print("Please run database.py first to create the database")
    
    # Run the app
    app.run(debug=True, port=5000, host='0.0.0.0')