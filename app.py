from flask import Flask, request
import requests
import google.generativeai as genai

app = Flask(__name__)

# --- CONFIGURATION (FILL THESE IN!) ---
VERIFY_TOKEN = "burmesebotsecret2025" 
PAGE_ACCESS_TOKEN = "EAAL2ozvDJnsBQFcxhz4fVg6MoSka7mRMcohMy5XxvEPZAHPA3P9sTbpOQM1ZCo99BG1USSL7lkgCE6ZCNCQrZBl7Gw9EJsRyfwBKQNxL436Wu3KQxOFZBTBYHOaucmkUYMDicBXR2V10uNZC2uVdBFLNHfV4VcRJnGEgvbxWwuESka9q4uyGxmweNZC2ZBfFqEiJvpIXNgw5rO5A0QiAZC7Bg3tvI"
GEMINI_API_KEY = "AIzaSyCSdqA8Zdw1WD7uz2L0YKTqgE9QulrOz60"
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
- If you don't know the answer, ask them to call the numbers according to their city or ask them to leave their number if they don't want to call first.

Store Info:
- Opening Hours: 6 AM to 6 PM.
- We have  4 rice shops and 2 rice mills. 
- 1st rice shop address is ၄၁လမ်း၊၈၇*၈၈ကြား၊စိန်ပန်းရပ်ကွက်၊မဟာအောင်မြေမြို့နယ်၊ မန္တလေးမြို့
- 2nd rice shop address is စစ်ကိုင်း-မန္တလေးလမ်း၊တမ္ပဝတီရပ်ကွက်၊ချမ်းမြသာစည်မြို့နယ်၊မန္တလေးမြို့
- 3rd rice shop address is အမှတ်(၄၂၄+၄၂၅)၊ (၃)ရပ်ကွက်၊ ဗိုလ်မှူးဗထူးလမ်း၊ အ‌ရှေ့ဒဂုံမြို့နယ်၊ရန်ကုန်မြို့
- 4th rice shop address is အမှတ်(၈၁)၊ ‌ရွှေလှိုင်လမ်း၊ ကြည့်မြင်တိုင်ညစျေး၊ ရန်ကုန်မြို့
- 1st rice mill address is မုံရွာလမ်းထွက်၊အောင်ချမ်းသာရပ်၊ရေဦးမြို့၊ရွှေဘိုခရိုင်စစ်ကိုင်းတိုင်းဒေသကြီး
- 2nd rice mill address is ရွှေဘို-မန္တလေးလမ်း၊ စိုင်နိုင်လေး၊စစ်ကိုင်းတိုင်းဒေသကြီး
- Products: We sell rice.We provide free deilvery on rice purchases in Yangon and Mandalay. And if they don't like the rice they purchase we give them exchange for any rice of the price range or higher price range with additional charge. 
- If they ask for price or if they want to order any rice ask them to call 09-881177292 if they are from Yangon else if they are from Mandalay ask them to call 09-427070292.
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











