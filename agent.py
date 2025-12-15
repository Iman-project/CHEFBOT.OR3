import requests
import os
from groq import Groq

# API Keys
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key='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')

def send_whatsapp_message(to, text):
    """Send message via WhatsApp Cloud API"""
    url = f"https://graph.facebook.com/v17.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text}
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"✅ Message sent: {response.status_code}")
        return response.json()
    except Exception as e:
        print(f"❌ WhatsApp send error: {e}")
        return None

def get_llama_response(user_message):
    """Generate AI response using Llama 3.3 via Groq"""
    
    system_prompt = """You are ChefBot, an AI restaurant assistant on WhatsApp.

Today's Menu:
🍛 Jollof Rice - ₦2,500
🍚 Fried Rice - ₦2,000  
🍗 Chicken - ₦3,000
🍌 Fried Plantain - ₦1,000

Your role:
- Help customers with menu inquiries
- Take and confirm food orders
- Answer questions about the restaurant

IMPORTANT: Keep responses SHORT (2-3 sentences max) since this is WhatsApp."""

    try:
        print(f"🦙 Sending to Llama: {user_message}")
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=150,
        )
        
        ai_reply = chat_completion.choices[0].message.content
        print(f"✅ Llama responded: {ai_reply[:100]}...")
        
        return ai_reply
    
    except Exception as e:
        print(f"❌ Groq/Llama Error: {e}")
        return "Sorry, I'm having trouble right now. Please try again! 🤖"

def handle_message(data):
    """Process incoming WhatsApp messages"""
    try:
        # Extract message data
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        
        # Check if there are messages
        if "messages" not in value:
            print("No messages in webhook data")
            return
        
        message = value["messages"][0]
        user_number = message["from"]
        
        # Handle text messages only
        if message["type"] != "text":
            print(f"Non-text message type: {message['type']}")
            send_whatsapp_message(user_number, "Sorry, I can only understand text messages right now! 📱")
            return
        
        user_text = message["text"]["body"]

        print(f"\n📨 Message from {user_number}: {user_text}")

        # Get AI response from Llama
        ai_reply = get_llama_response(user_text)

        print(f"🤖 Sending reply: {ai_reply}\n")

        # Send response back to user
        send_whatsapp_message(user_number, ai_reply)

    except KeyError as e:
        print(f"❌ Webhook data error: Missing key {e}")
    except Exception as e:
        print(f"❌ Error handling message: {e}")