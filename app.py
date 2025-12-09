from flask import Flask, request
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
# (I have kept your keys here so it works instantly. 
# TOMORROW: Please generate new keys for security!)
VERIFY_TOKEN = "burmesebotsecret2025" 
PAGE_ACCESS_TOKEN = "EAAL2ozvDJnsBQAJyVSkAdiXj0JfPjHPNq8KtSzBlDDLo2M3SDBje9ZAIXN2VYLwanY9bqiokYe3lj5wmuLhGdJ0AVSsLocKZBYQVHO4QHEsNmr7ki1zlQUWNq8WM0TlBpf6tFQibw5F51yC8GH06FXsNZByEoldhcWKDSBZB5s6koLenUeZCtkJA6JFBZCkgmyYRMMohGFVH1Bdtnd5o2GfEis"
GEMINI_API_KEY = "AIzaSyCMPylk2J1qMpyTUiUvU8ZC5Q44qGy-9Ic"
# ---------------------

# --- YOUR RICE SHOP INSTRUCTIONS ---
SYSTEM_INSTRUCTION = """
You are a helpful, polite, and professional customer service assistant for a shop in Myanmar.
Your goal is to answer customer questions briefly and clearly in Burmese.
- If the user writes in Zawgyi, you understand it but reply in standard Unicode Burmese.
- Be friendly but professional.
- If you don't know the answer, ask them to wait for a human agent.

Store Info:
- Opening Hours: 6 AM to 6 PM.
- Address: 41st 87stx88st, Mandalay.
- Products: We sell rice.
"""

def get_ai_response(user_text):
    """
    DIRECT CONNECTION: Bypasses the broken library.
    """
    # We use the standard API URL directly
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"{SYSTEM_INSTRUCTION}\n\nCustomer says: {user_text}"
            }]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        
        # Check if Google gave a valid 200 OK response
        if response.status_code == 200:
            result = response.json()
            # Extract the text from the answer
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"Google Error: {response.text}")
            return "စနစ်ပိုင်းဆိုင်ရာ အမှားအယွင်းရှိနေပါသည်။ (Google API Error)"

    except Exception as e:
        print(f"Connection Error: {e}")
        return "ခေတ္တစောင့်ဆိုင်းပေးပါ၊ စနစ်ပိုင်းဆိုင်ရာ အနည်းငယ် နှောင့်နှေးနေပါသည်။"

def send_message(recipient_id, text):
    """Sends the reply back to Facebook"""
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "message": {"text": text},
        "recipient": {"id": recipient_id},
        "notification_type": "REGULAR"
    }
    requests.post("https://graph.facebook.com/v19.0/me/messages", params=params, headers=headers, json=data)

# --- WEBHOOK ROUTES ---
@app.route('/webhook', methods=['GET'])
def webhook_verification():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "OK", 200

@app.route('/webhook', methods=['POST'])
def webhook_handle():
    data = request.get_json()
    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                if messaging_event.get('message') and messaging_event['message'].get('text'):
                    sender_id = messaging_event['sender']['id']
                    user_text = messaging_event['message']['text']
                    reply_text = get_ai_response(user_text)
                    send_message(sender_id, reply_text)
    return "ok", 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
