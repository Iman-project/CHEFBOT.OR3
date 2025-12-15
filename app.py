import os
from flask import Flask, request, jsonify
from agent import handle_message
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "devkey")

@app.route("/")
def home():
    return """
    <h1>🤖 ChefBot AI Agent</h1>
    <p>Status: ✅ Running</p>
    <p>WhatsApp webhook ready at /webhook</p>
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

if __name__ == "__main__":
    app.run(debug=True, port=10000)