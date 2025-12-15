## 1. Prepare environment
- Install Python 3.10+ and Postgres.
- Create a Postgres DB: e.g., serveai_db
- Copy `.env.example` to `.env` and fill values.

## 2. Install dependencies
pip install -r requirements.txt

## 3. Seed demo data
python seed.py

## 4. Run locally
# for development
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000

OR
python app.py

## 5. Expose local server to internet (ngrok)
# In another terminal
ngrok http 5000

# note the public URL: https://abcd1234.ngrok.io

## 6. Configure Meta (WhatsApp) Webhook
- In Meta Developer App > WhatsApp > Webhooks: set Callback URL to:
  https://<your-ngrok>.io/webhook
- Set Verify Token to match WHATSAPP_VERIFY_TOKEN in `.env`
- Subscribe to messages and message_status.

## 7. Test from WhatsApp (use test phone number assigned by Meta)
- Send: "Hi" -> CHEFBOT should reply with greeting.
- Send: "Menu" -> CHEFBOTreturns today's menu.
- Send: "I want 1 Jollof Rice and 2 Grilled Chicken for pickup" -> ServeAI replies with order summary and asks for confirmation.
- Reply "YES" -> (you can build this flow to update order status to confirmed)

## 8. Notes
- Replace LLaMA wrapper calls with the real API (Meta LLaMA or hosted LLM).
- For production, use HTTPS, secure tokens, and do not store long-lived tokens in code.
- Register WhatsApp message templates for proactive notifications (order_ready, reservation_reminder).

