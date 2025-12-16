import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

DATABASE_URL = os.getenv("DATABASE_URL")

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_database():
    """Initialize database tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create restaurants table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS restaurants (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                whatsapp_phone_id VARCHAR(50) UNIQUE NOT NULL,
                owner_phone VARCHAR(20),
                admin_password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create menu_items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS menu_items (
                id SERIAL PRIMARY KEY,
                restaurant_id INTEGER REFERENCES restaurants(id) ON DELETE CASCADE,
                item_name VARCHAR(255) NOT NULL,
                price INTEGER NOT NULL,
                emoji VARCHAR(10) DEFAULT '🍽️',
                available BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(restaurant_id, item_name)
            )
        """)
        
        # Create index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_restaurant_phone 
            ON restaurants(whatsapp_phone_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_menu_restaurant 
            ON menu_items(restaurant_id)
        """)
        
        conn.commit()
        print("✅ Database initialized successfully!")

# Restaurant functions
def create_restaurant(name, whatsapp_phone_id, owner_phone, admin_password):
    """Create a new restaurant"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO restaurants (name, whatsapp_phone_id, owner_phone, admin_password)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (name, whatsapp_phone_id, owner_phone, admin_password))
        
        result = cursor.fetchone()
        return result['id']

def get_restaurant_by_phone_id(whatsapp_phone_id):
    """Get restaurant by WhatsApp phone ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM restaurants 
            WHERE whatsapp_phone_id = %s
        """, (whatsapp_phone_id,))
        
        return cursor.fetchone()

def get_all_restaurants():
    """Get all restaurants"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM restaurants ORDER BY created_at DESC")
        return cursor.fetchall()

# Menu functions
def add_menu_item(restaurant_id, item_name, price, emoji='🍽️'):
    """Add a menu item for a restaurant"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO menu_items (restaurant_id, item_name, price, emoji)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (restaurant_id, item_name) 
            DO UPDATE SET price = %s, emoji = %s
            RETURNING id
        """, (restaurant_id, item_name, price, emoji, price, emoji))
        
        result = cursor.fetchone()
        return result['id']

def get_menu_items(restaurant_id):
    """Get all menu items for a restaurant"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM menu_items 
            WHERE restaurant_id = %s AND available = TRUE
            ORDER BY item_name
        """, (restaurant_id,))
        
        return cursor.fetchall()

def update_menu_item_price(restaurant_id, item_name, new_price):
    """Update menu item price"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE menu_items 
            SET price = %s 
            WHERE restaurant_id = %s AND item_name = %s
            RETURNING id
        """, (new_price, restaurant_id, item_name))
        
        result = cursor.fetchone()
        return result is not None

def delete_menu_item(restaurant_id, item_name):
    """Delete a menu item"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM menu_items 
            WHERE restaurant_id = %s AND item_name = %s
            RETURNING id
        """, (restaurant_id, item_name))
        
        result = cursor.fetchone()
        return result is not None

def seed_default_data():
    """Seed database with default restaurant and menu"""
    try:
        # Check if we already have restaurants
        restaurants = get_all_restaurants()
        if restaurants:
            print("✅ Database already has data, skipping seed")
            return
        
        # Create default restaurant
        print("🌱 Seeding default restaurant...")
        restaurant_id = create_restaurant(
            name="Demo Restaurant",
            whatsapp_phone_id="DEMO_PHONE_ID",  # Replace with your actual phone ID
            owner_phone="+2341234567890",
            admin_password="admin123"
        )
        
        # Add default menu items
        default_menu = [
            ("Jollof Rice", 2500, "🍛"),
            ("Fried Rice", 2000, "🍚"),
            ("Chicken", 3000, "🍗"),
            ("Fried Plantain", 1000, "🍌")
        ]
        
        for item_name, price, emoji in default_menu:
            add_menu_item(restaurant_id, item_name, price, emoji)
        
        print(f"✅ Seeded restaurant '{restaurant_id}' with {len(default_menu)} menu items")
        
    except Exception as e:
        print(f"⚠️ Seeding error (may be normal if data exists): {e}")

if __name__ == "__main__":
    # Run this to initialize database
    init_database()
    seed_default_data()
