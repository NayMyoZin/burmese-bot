from flask import Flask, request
import requests
import google.generativeai as genai

app = Flask(__name__)

# --- CONFIGURATION (FILL THESE IN!) ---
VERIFY_TOKEN = "burmesebotsecret2025" 
PAGE_ACCESS_TOKEN = "EAAL2ozvDJnsBQAcTzMhYZAL4bhKt0IqExEfhwdiKBGmdICZAfEfsaHjpkOYgMo1AKZCJyLl0ZCwhaAF9MZCV1hI8W4JGZBGeNGZAepOpuKK5fGpdael1KX8XOFSg8GXeGiTU7wEZAuXoZALB5Nest0o291qijo7NLzIRoCHNIy9qLxcev011ciYOkU5RPu702V3ANOsucAmPv8i9qGnC0XMx0sGJ5"
GEMINI_API_KEY = "AIzaSyDxKjta_j1-2i_bJ3StsEU_oJ6nd3Oz7Sk"
# --------------------------------------

# Configure the AI with your key
genai.configure(api_key=GEMINI_API_KEY)

# --- YOUR BOT'S PERSONALITY (The "Training") ---
# This is where you "train" the bot. You tell it who it is and what it knows.
# You can type as much instruction here as you want!
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
    Sends the user's message to Gemini AI and gets a smart reply.
    """
    try:
        # Create the model
        model = genai.GenerativeModel('gemini-2.0-flash-001')
        
        # Combine instructions with the user's message
        full_prompt = f"{SYSTEM_INSTRUCTION}\n\nCustomer says: {user_text}"
        
        # Ask the AI
        response = model.generate_content(full_prompt)
        
        # Return the AI's text
        return response.text.strip()
        
    except Exception as e:
        print(f"AI Error: {e}")
        return "ခေတ္တစောင့်ဆိုင်းပေးပါ၊ စနစ်ပိုင်းဆိုင်ရာ အနည်းငယ် နှောင့်နှေးနေပါသည်။" 
        # (Please wait, slight system delay.)

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
                    
                    # Call the AI function instead of the old logic
                    reply_text = get_ai_response(user_text)
                    
                    send_message(sender_id, reply_text)
    return "ok", 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)







