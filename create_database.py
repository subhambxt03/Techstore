import sqlite3
import json
from datetime import datetime

def create_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Drop tables if they exist (for clean recreation)
    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('DROP TABLE IF EXISTS products')
    cursor.execute('DROP TABLE IF EXISTS cart')
    cursor.execute('DROP TABLE IF EXISTS wishlist')
    cursor.execute('DROP TABLE IF EXISTS orders')
    cursor.execute('DROP TABLE IF EXISTS chatbot_logs')
    
    # Create users table
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        address TEXT NOT NULL,
        pincode TEXT NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create products table - FIXED: Using 'image' field (not image_filename)
    cursor.execute('''
    CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        description TEXT NOT NULL,
        specs TEXT NOT NULL,
        image TEXT,  -- FIXED: Changed from image_filename to image
        stock INTEGER DEFAULT 10,
        on_sale BOOLEAN DEFAULT 0,
        rating REAL DEFAULT 4.5,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create cart table
    cursor.execute('''
    CREATE TABLE cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER DEFAULT 1,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    ''')
    
    # Create wishlist table
    cursor.execute('''
    CREATE TABLE wishlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    ''')
    
    # Create orders table
    cursor.execute('''
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        products TEXT NOT NULL,
        total_amount REAL NOT NULL,
        shipping_address TEXT NOT NULL,
        payment_method TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # Create chatbot_logs table
    cursor.execute('''
    CREATE TABLE chatbot_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT NOT NULL,
        response TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Sample products data - FIXED: Using 'image' field
    products = [
        # Smartphones (8 products)
        ('iPhone 15 Pro', 'Smartphones', 129999.00,
         'The most powerful iPhone ever with A17 Pro chip',
         json.dumps({
             'ram': '8GB', 
             'storage': '256GB', 
             'camera': '48MP Main + 12MP Ultra Wide + 12MP Telephoto',
             'battery': '3274 mAh',
             'display': '6.1-inch Super Retina XDR',
             'processor': 'A17 Pro'
         }),
         'phone1.png', True, 4.7),
        
        ('Samsung Galaxy S23 Ultra', 'Smartphones', 124999.00,
         'Ultimate smartphone with S Pen included',
         json.dumps({
             'ram': '12GB',
             'storage': '512GB',
             'camera': '200MP Main + 12MP Ultra Wide + 10MP Telephoto x2',
             'battery': '5000 mAh',
             'display': '6.8-inch Dynamic AMOLED 2X',
             'processor': 'Snapdragon 8 Gen 2'
         }),
         'phone2.png', True, 4.8),
        
        ('OnePlus 11 5G', 'Smartphones', 56999.00,
         'Flagship killer with Hasselblad camera',
         json.dumps({
             'ram': '16GB',
             'storage': '256GB',
             'camera': '50MP Main + 48MP Ultra Wide + 32MP Telephoto',
             'battery': '5000 mAh',
             'display': '6.7-inch Fluid AMOLED',
             'processor': 'Snapdragon 8 Gen 2'
         }),
         'phone3.png', False, 4.6),
        
        ('Google Pixel 8 Pro', 'Smartphones', 106999.00,
         'The best of Google AI in a smartphone',
         json.dumps({
             'ram': '12GB',
             'storage': '128GB',
             'camera': '50MP Main + 48MP Ultra Wide + 48MP Telephoto',
             'battery': '5050 mAh',
             'display': '6.7-inch LTPO OLED',
             'processor': 'Google Tensor G3'
         }),
         'phone4.png', True, 4.5),
        
        ('Xiaomi 13 Pro', 'Smartphones', 79999.00,
         'Professional-grade camera system',
         json.dumps({
             'ram': '12GB',
             'storage': '256GB',
             'camera': '50.3MP Main + 50MP Ultra Wide + 50MP Telephoto',
             'battery': '4820 mAh',
             'display': '6.73-inch AMOLED',
             'processor': 'Snapdragon 8 Gen 2'
         }),
         'phone5.png', False, 4.4),
        
        ('iPhone 14', 'Smartphones', 69900.00,
         'All-day battery life and advanced camera',
         json.dumps({
             'ram': '6GB',
             'storage': '128GB',
             'camera': '12MP Main + 12MP Ultra Wide',
             'battery': '3279 mAh',
             'display': '6.1-inch Super Retina XDR',
             'processor': 'A15 Bionic'
         }),
         'phone6.png', True, 4.6),
        
        ('Samsung Galaxy Z Flip5', 'Smartphones', 99999.00,
         'Compact foldable smartphone',
         json.dumps({
             'ram': '8GB',
             'storage': '256GB',
             'camera': '12MP Main + 12MP Ultra Wide',
             'battery': '3700 mAh',
             'display': '6.7-inch Foldable Dynamic AMOLED 2X',
             'processor': 'Snapdragon 8 Gen 2'
         }),
         'phone7.png', False, 4.3),
        
        ('Nothing Phone 2', 'Smartphones', 44999.00,
         'Unique glyph interface design',
         json.dumps({
             'ram': '12GB',
             'storage': '256GB',
             'camera': '50MP Main + 50MP Ultra Wide',
             'battery': '4700 mAh',
             'display': '6.7-inch LTPO OLED',
             'processor': 'Snapdragon 8+ Gen 1'
         }),
         'phone8.png', True, 4.4),
        
        # Laptops (8 products)
        ('MacBook Pro 16-inch M2 Max', 'Laptops', 329900.00,
         'Extreme performance for professionals',
         json.dumps({
             'ram': '32GB',
             'storage': '1TB SSD',
             'display': '16.2-inch Liquid Retina XDR',
             'processor': 'M2 Max 12-core',
             'graphics': '38-core GPU',
             'battery': 'Up to 22 hours'
         }),
         'laptop1.png', True, 4.9),
        
        ('Dell XPS 15 9530', 'Laptops', 219990.00,
         'Premium Windows laptop with OLED display',
         json.dumps({
             'ram': '32GB',
             'storage': '1TB SSD',
             'display': '15.6-inch 3.5K OLED',
             'processor': 'Intel Core i9-13900H',
             'graphics': 'NVIDIA RTX 4070',
             'battery': '86Whr'
         }),
         'laptop2.png', False, 4.7),
        
        ('HP Spectre x360 16', 'Laptops', 189990.00,
         'Convertible laptop with stunning design',
         json.dumps({
             'ram': '16GB',
             'storage': '1TB SSD',
             'display': '16-inch 3K+ OLED',
             'processor': 'Intel Core i7-1360P',
             'graphics': 'Intel Iris Xe',
             'battery': '83Whr'
         }),
         'laptop3.png', True, 4.6),
        
        ('Lenovo Yoga 9i Gen 8', 'Laptops', 164990.00,
         'Premium 2-in-1 laptop with soundbar',
         json.dumps({
             'ram': '16GB',
             'storage': '512GB SSD',
             'display': '14-inch 2.8K OLED',
             'processor': 'Intel Core i7-1360P',
             'graphics': 'Intel Iris Xe',
             'battery': '75Whr'
         }),
         'laptop4.png', False, 4.5),
        
        ('Asus ROG Zephyrus G14', 'Laptops', 149990.00,
         'Powerful gaming laptop in compact form',
         json.dumps({
             'ram': '16GB',
             'storage': '1TB SSD',
             'display': '14-inch 2.5K 165Hz',
             'processor': 'AMD Ryzen 9 7940HS',
             'graphics': 'NVIDIA RTX 4060',
             'battery': '76Whr'
         }),
         'laptop5.png', True, 4.7),
        
        ('Microsoft Surface Laptop Studio', 'Laptops', 209990.00,
         'Innovative design for creators',
         json.dumps({
             'ram': '32GB',
             'storage': '1TB SSD',
             'display': '14.4-inch PixelSense Flow',
             'processor': 'Intel Core i7-11370H',
             'graphics': 'NVIDIA RTX 3050 Ti',
             'battery': 'Up to 18 hours'
         }),
         'laptop6.png', False, 4.4),
        
        ('Acer Swift X SFX14', 'Laptops', 89990.00,
         'Thin and light creator laptop',
         json.dumps({
             'ram': '16GB',
             'storage': '512GB SSD',
             'display': '14-inch 2.2K IPS',
             'processor': 'AMD Ryzen 7 5800U',
             'graphics': 'NVIDIA RTX 3050 Ti',
             'battery': '59Whr'
         }),
         'laptop7.png', True, 4.3),
        
        ('MSI Creator Z16 HX Studio', 'Laptops', 289990.00,
         'Mobile workstation for professionals',
         json.dumps({
             'ram': '64GB',
             'storage': '2TB SSD',
             'display': '16-inch 2.5K 165Hz',
             'processor': 'Intel Core i9-13980HX',
             'graphics': 'NVIDIA RTX 4070',
             'battery': '90Whr'
         }),
         'laptop8.png', False, 4.8),
        
        # Headphones (8 products)
        ('Sony WH-1000XM5', 'Headphones', 29990.00,
         'Industry-leading noise cancellation',
         json.dumps({
             'type': 'Over-ear',
             'battery': '30 hours',
             'noise_cancellation': 'Yes',
             'wireless': 'Yes',
             'microphone': 'Yes',
             'bluetooth': '5.2'
         }),
         'headphones1.png', True, 4.8),
        
        ('Bose QuietComfort 45', 'Headphones', 28990.00,
         'World-class noise cancellation',
         json.dumps({
             'type': 'Over-ear',
             'battery': '24 hours',
             'noise_cancellation': 'Yes',
             'wireless': 'Yes',
             'microphone': 'Yes',
             'bluetooth': '5.1'
         }),
         'headphones2.png', False, 4.7),
        
        ('Sennheiser Momentum 4', 'Headphones', 29990.00,
         'Premium sound with 60-hour battery',
         json.dumps({
             'type': 'Over-ear',
             'battery': '60 hours',
             'noise_cancellation': 'Yes',
             'wireless': 'Yes',
             'microphone': 'Yes',
             'bluetooth': '5.2'
         }),
         'headphones3.png', True, 4.6),
        
        ('Apple AirPods Max', 'Headphones', 59900.00,
         'High-fidelity audio with spatial audio',
         json.dumps({
             'type': 'Over-ear',
             'battery': '20 hours',
             'noise_cancellation': 'Yes',
             'wireless': 'Yes',
             'microphone': 'Yes',
             'bluetooth': '5.0'
         }),
         'headphones4.png', False, 4.5),
        
        ('JBL Tour One M2', 'Headphones', 22990.00,
         'Smart ambient aware technology',
         json.dumps({
             'type': 'Over-ear',
             'battery': '50 hours',
             'noise_cancellation': 'Yes',
             'wireless': 'Yes',
             'microphone': 'Yes',
             'bluetooth': '5.3'
         }),
         'headphones5.png', True, 4.4),
        
        ('Beats Studio Pro', 'Headphones', 34990.00,
         'Personalized spatial audio',
         json.dumps({
             'type': 'Over-ear',
             'battery': '40 hours',
             'noise_cancellation': 'Yes',
             'wireless': 'Yes',
             'microphone': 'Yes',
             'bluetooth': '5.3'
         }),
         'headphones6.png', False, 4.3),
        
        ('Audio-Technica ATH-M50xBT2', 'Headphones', 17990.00,
         'Studio monitor quality wireless',
         json.dumps({
             'type': 'Over-ear',
             'battery': '50 hours',
             'noise_cancellation': 'No',
             'wireless': 'Yes',
             'microphone': 'Yes',
             'bluetooth': '5.0'
         }),
         'headphones7.png', True, 4.7),
        
        ('Bowers & Wilkins PX7 S2', 'Headphones', 39990.00,
         'Premium materials with exceptional sound',
         json.dumps({
             'type': 'Over-ear',
             'battery': '30 hours',
             'noise_cancellation': 'Yes',
             'wireless': 'Yes',
             'microphone': 'Yes',
             'bluetooth': '5.2'
         }),
         'headphones8.png', False, 4.6),
        
        # Earbuds (8 products)
        ('Apple AirPods Pro 2', 'Earbuds', 24900.00,
         'Active Noise Cancellation with Transparency mode',
         json.dumps({
             'type': 'In-ear',
             'battery': '6 hours (30 with case)',
             'noise_cancellation': 'Yes',
             'wireless': 'Yes',
             'microphone': 'Yes',
             'bluetooth': '5.3'
         }),
         'ear1.png', True, 4.8),
        
        ('Sony WF-1000XM5', 'Earbuds', 29990.00,
         'Best-in-class noise cancellation',
         json.dumps({
             'type': 'In-ear',
             'battery': '8 hours (24 with case)',
             'noise_cancellation': 'Yes',
             'wireless': 'Yes',
             'microphone': 'Yes',
             'bluetooth': '5.3'
         }),
         'ear2.png', False, 4.7),
        
        ('Samsung Galaxy Buds2 Pro', 'Earbuds', 16990.00,
         'Hi-Fi 24bit audio with ANC',
         json.dumps({
             'type': 'In-ear',
             'battery': '5 hours (18 with case)',
             'noise_cancellation': 'Yes',
             'wireless': 'Yes',
             'microphone': 'Yes',
             'bluetooth': '5.3'
         }),
         'ear3.png', True, 4.6),
        
        ('Bose QuietComfort Earbuds II', 'Earbuds', 27990.00,
         'Customizable noise cancellation',
         json.dumps({
             'type': 'In-ear',
             'battery': '6 hours (18 with case)',
             'noise_cancellation': 'Yes',
             'wireless': 'Yes',
             'microphone': 'Yes',
             'bluetooth': '5.3'
         }),
         'ear4.png', False, 4.5),
        
        ('Jabra Elite 10', 'Earbuds', 19990.00,
         'Dolby Atmos with head tracking',
         json.dumps({
             'type': 'In-ear',
             'battery': '6 hours (27 with case)',
             'noise_cancellation': 'Yes',
             'wireless': 'Yes',
             'microphone': 'Yes',
             'bluetooth': '5.3'
         }),
         'ear5.png', True, 4.4),
        
        ('Google Pixel Buds Pro', 'Earbuds', 19990.00,
         'Google Assistant integration',
         json.dumps({
             'type': 'In-ear',
             'battery': '7 hours (20 with case)',
             'noise_cancellation': 'Yes',
             'wireless': 'Yes',
             'microphone': 'Yes',
             'bluetooth': '5.0'
         }),
         'ear6.png', False, 4.3),
        
        ('OnePlus Buds Pro 2', 'Earbuds', 11999.00,
         'Dual drivers with spatial audio',
         json.dumps({
             'type': 'In-ear',
             'battery': '6 hours (22 with case)',
             'noise_cancellation': 'Yes',
             'wireless': 'Yes',
             'microphone': 'Yes',
             'bluetooth': '5.2'
         }),
         'ear7.png', True, 4.5),
        
        ('Beats Fit Pro', 'Earbuds', 19990.00,
         'Secure-fit wingtips for active lifestyle',
         json.dumps({
             'type': 'In-ear',
             'battery': '6 hours (24 with case)',
             'noise_cancellation': 'Yes',
             'wireless': 'Yes',
             'microphone': 'Yes',
             'bluetooth': '5.0'
         }),
         'ear8.png', False, 4.4),
    ]
    
    # Insert sample products - FIXED: Insert into 'image' column
    cursor.executemany('''
    INSERT INTO products (name, category, price, description, specs, image, on_sale, rating)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', products)
    
    # Create a sample user (for testing)
    cursor.execute('''
    INSERT INTO users (full_name, email, phone, address, pincode, password)
    VALUES ('John Doe', 'john@example.com', '9876543210', 
            '123 Main Street, Mumbai, Maharashtra', '400001', 'password123')
    ''')
    
    conn.commit()
    
    # Verify the data was inserted correctly
    cursor.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT id, name, image FROM products LIMIT 5")
    sample_products = cursor.fetchall()
    
    conn.close()
    
    print(f"Database created successfully with {product_count} products!")
    print("\nSample products:")
    for product in sample_products:
        print(f"  ID: {product[0]}, Name: {product[1]}, Image: {product[2]}")
    
    print("\nIMPORTANT: Make sure you have these image files in /static/images/products/ folder:")
    print("  phone1.png, phone2.png, ..., phone8.png")
    print("  laptop1.png, laptop2.png, ..., laptop8.png")
    print("  headphones1.png, headphones2.png, ..., headphones8.png")
    print("  ear1.png, ear2.png, ..., ear8.png")
    print("  default.png (as fallback)")

if __name__ == '__main__':
    create_database()