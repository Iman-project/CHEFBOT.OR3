"""
Run this script ONCE after deploying to initialize your database.

You can run it:
1. Locally: python setup_db.py
2. On Render: Via shell or add to startup command
"""

from database import init_database, seed_default_data, create_restaurant, add_menu_item
import os

def setup():
    print("🚀 Setting up ChefBot database...")
    print("=" * 50)
    
    # Initialize tables
    print("\n1️⃣ Creating database tables...")
    init_database()
    
    # Seed default data
    print("\n2️⃣ Seeding default restaurant...")
    seed_default_data()
    
    print("\n" + "=" * 50)
    print("✅ Database setup complete!")
    print("\n📝 IMPORTANT: Update the DEMO_PHONE_ID in database.py")
    print("   with your actual WhatsApp Phone Number ID from Meta.")
    print("\n🔑 Default admin password: admin123")
    print("   Change this in the database for security!")
    
def add_new_restaurant(name, phone_id, owner_phone, password):
    """
    Helper function to add a new restaurant.
    
    Usage:
    add_new_restaurant(
        name="Mama's Kitchen",
        phone_id="123456789012345",  # From Meta Developer Console
        owner_phone="+2349012345678",
        password="secure_password_123"
    )
    """
    try:
        restaurant_id = create_restaurant(name, phone_id, owner_phone, password)
        print(f"✅ Created restaurant '{name}' with ID: {restaurant_id}")
        
        # Add some default menu items
        default_items = [
            ("Jollof Rice", 2500, "🍛"),
            ("Fried Rice", 2000, "🍚"),
            ("Chicken", 3000, "🍗"),
        ]
        
        for item_name, price, emoji in default_items:
            add_menu_item(restaurant_id, item_name, price, emoji)
        
        print(f"✅ Added {len(default_items)} menu items")
        return restaurant_id
        
    except Exception as e:
        print(f"❌ Error creating restaurant: {e}")
        return None

if __name__ == "__main__":
    setup()
    
    # OPTIONAL: Add your first real restaurant here
    # Uncomment and modify the lines below:
    
    # add_new_restaurant(
    #     name="Your Restaurant Name",
    #     phone_id="YOUR_WHATSAPP_PHONE_ID_FROM_META",
    #     owner_phone="+234XXXXXXXXXX",
    #     password="your_secure_password"
    # )
