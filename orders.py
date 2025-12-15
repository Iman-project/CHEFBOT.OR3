import json
from datetime import datetime

def log_order(restaurant_id, customer_phone, order_text, bot_response):
    """Log orders for tracking"""
    try:
        order_data = {
            "timestamp": datetime.now().isoformat(),
            "restaurant_id": restaurant_id,
            "customer": customer_phone,
            "message": order_text,
            "response": bot_response
        }
        
        with open('orders_log.json', 'a') as f:
            f.write(json.dumps(order_data) + '\n')
        
        print(f"📝 Order logged")
    except Exception as e:
        print(f"⚠️ Could not log order: {e}")