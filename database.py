import json
import os
from datetime import datetime

RESTAURANT_FILE = 'restaurants.json'

def load_restaurants():
    """Load all restaurants from JSON file"""
    if not os.path.exists(RESTAURANT_FILE):
        return {"restaurants": {}}
    
    try:
        with open(RESTAURANT_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"restaurants": {}}

def save_restaurants(data):
    """Save restaurants to JSON file"""
    with open(RESTAURANT_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def create_restaurant(restaurant_data):
    """
    Register a new restaurant
    Returns: (success, restaurant_id or error_message)
    """
    try:
        all_data = load_restaurants()
        restaurants = all_data.get("restaurants", {})
        
        # Generate unique restaurant ID
        restaurant_id = f"rest_{len(restaurants) + 1:03d}"
        
        # Use WhatsApp phone as key (will be provided after registration)
        temp_key = f"pending_{restaurant_id}"
        
        # Create restaurant record
        restaurants[temp_key] = {
            "id": restaurant_id,
            "name": restaurant_data["name"],
            "description": restaurant_data.get("description", ""),
            "menu": restaurant_data["menu"],
            "delivery_time": restaurant_data.get("delivery_time", "30-45 minutes"),
            "contact": restaurant_data.get("contact", ""),
            "currency": restaurant_data.get("currency", "₦"),
            "active": True,
            "created_at": datetime.now().isoformat(),
            "whatsapp_connected": False,
            "pending_setup": True
        }
        
        all_data["restaurants"] = restaurants
        save_restaurants(all_data)
        
        return True, restaurant_id
    
    except Exception as e:
        return False, str(e)

def update_restaurant_whatsapp(restaurant_id, whatsapp_phone):
    """
    Link WhatsApp phone number to restaurant after setup
    """
    try:
        all_data = load_restaurants()
        restaurants = all_data.get("restaurants", {})
        
        # Find restaurant by ID
        temp_key = None
        restaurant_data = None
        
        for key, data in restaurants.items():
            if data["id"] == restaurant_id:
                temp_key = key
                restaurant_data = data
                break
        
        if not restaurant_data:
            return False, "Restaurant not found"
        
        # Move from pending to actual WhatsApp phone key
        restaurant_data["whatsapp_connected"] = True
        restaurant_data["pending_setup"] = False
        restaurant_data["whatsapp_phone"] = whatsapp_phone
        
        # Remove old key, add with WhatsApp phone as key
        del restaurants[temp_key]
        restaurants[whatsapp_phone] = restaurant_data
        
        all_data["restaurants"] = restaurants
        save_restaurants(all_data)
        
        return True, "WhatsApp connected successfully"
    
    except Exception as e:
        return False, str(e)

def get_restaurant_by_id(restaurant_id):
    """Get restaurant details by ID"""
    all_data = load_restaurants()
    restaurants = all_data.get("restaurants", {})
    
    for data in restaurants.values():
        if data["id"] == restaurant_id:
            return data
    
    return None

def update_restaurant_menu(restaurant_id, new_menu):
    """Update restaurant menu"""
    try:
        all_data = load_restaurants()
        restaurants = all_data.get("restaurants", {})
        
        # Find and update restaurant
        for key, data in restaurants.items():
            if data["id"] == restaurant_id:
                data["menu"] = new_menu
                data["updated_at"] = datetime.now().isoformat()
                break
        
        all_data["restaurants"] = restaurants
        save_restaurants(all_data)
        
        return True, "Menu updated successfully"
    
    except Exception as e:
        return False, str(e)