import os
from flask import Flask, request, jsonify
from agent import handle_message
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "devkey")

# Initialize database on startup
try:
    from database import init_database, seed_default_data
    print("🔄 Initializing database...")
    init_database()
    seed_default_data()
    print("✅ Database ready!")
except Exception as e:
    print(f"⚠️ Database initialization: {e}")
    # App continues to run even if DB init fails (might already be initialized)

@app.route("/")
def home():
    return """
    <h1>🤖 ChefBot AI Agent - Multi-Restaurant</h1>
    <p>Status: ✅ Running</p>
    <p>WhatsApp webhook ready at /webhook</p>
    <p>Database: ✅ Connected</p>
    """

# WhatsApp webhook verification
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    verify_token = os.getenv("VERIFY_TOKEN")
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if mode == "subscribe" and token == verify_token:
        print("✅ Webhook verified!")
        return challenge, 200
    print("❌ Webhook verification failed")
    return "Verification failed", 403

# WhatsApp incoming messages
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📩 Webhook received:")
    print(data)
    handle_message(data)
    return jsonify({"status": "ok"}), 200

# Manual database setup endpoint (optional - for troubleshooting)
@app.route("/setup-db")
def setup_db():
    """
    Visit this URL once to manually initialize database
    Example: https://chefbot-or3.onrender.com/setup-db
    """
    try:
        from database import init_database, seed_default_data
        init_database()
        seed_default_data()
        return jsonify({
            "status": "success",
            "message": "Database initialized successfully!"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Add restaurant endpoint (for adding new restaurants without shell access)
@app.route("/add-restaurant", methods=["POST"])
def add_restaurant():
    """
    Add a new restaurant via HTTP POST
    
    Example using curl:
    curl -X POST https://chefbot-or3.onrender.com/add-restaurant \
      -H "Content-Type: application/json" \
      -d '{
        "name": "Mama Kitchen",
        "phone_id": "123456789012345",
        "owner_phone": "+2349012345678",
        "password": "secure_password"
      }'
    
    Or visit in browser with query params:
    /add-restaurant?name=MamaKitchen&phone_id=123456789&owner_phone=+234xxx&password=secure123
    """
    try:
        from database import create_restaurant, add_menu_item
        
        # Get data from JSON body or query params
        if request.is_json:
            data = request.get_json()
        else:
            data = {
                "name": request.args.get("name"),
                "phone_id": request.args.get("phone_id"),
                "owner_phone": request.args.get("owner_phone"),
                "password": request.args.get("password")
            }
        
        # Validate required fields
        required = ["name", "phone_id", "owner_phone", "password"]
        missing = [f for f in required if not data.get(f)]
        if missing:
            return jsonify({
                "status": "error",
                "message": f"Missing required fields: {', '.join(missing)}"
            }), 400
        
        # Create restaurant
        restaurant_id = create_restaurant(
            data["name"],
            data["phone_id"],
            data["owner_phone"],
            data["password"]
        )
        
        # Add default menu items
        default_items = [
            ("Jollof Rice", 2500, "🍛"),
            ("Fried Rice", 2000, "🍚"),
            ("Chicken", 3000, "🍗"),
            ("Fried Plantain", 1000, "🍌")
        ]
        
        for item_name, price, emoji in default_items:
            add_menu_item(restaurant_id, item_name, price, emoji)
        
        return jsonify({
            "status": "success",
            "message": f"Restaurant '{data['name']}' created successfully!",
            "restaurant_id": restaurant_id,
            "menu_items_added": len(default_items)
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
