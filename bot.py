import telebot
import pandas as pd
import requests
from io import StringIO

# التوكن الخاص بك تم وضعه هنا مباشرة
API_TOKEN = '7801319797:AAHMfiTQtV7_bt0ZzroVZecpkRdY3TOqZ48'
# رابط مستند مجمع السلام
CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vR85oUveKg_3fmBMQ2YjlhBhOlhosd-kTCNTi2ubaWy7fX7QnHty1fdZ4lu3TcKdkDJUySr3DzLCkYz/pub?output=csv'

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🌹 مرحباً بك في بوت مجمع السلام\n"
        "--------------------------------\n"
        "🔍 يمكنك البحث عن أي مستفيد بإرسال:\n"
        "• الاسم الكامل\n"
        "• أو رقم الهاتف\n"
        "• أو رقم التسلسل\n"
        "--------------------------------\n"
        "أرسل كلمة البحث الآن..."
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def search_data(message):
    try:
        # إرسال رسالة انتظار للمستخدم
        wait_msg = bot.reply_to(message, "⏳ جاري البحث في قاعدة البيانات...")
        
        # جلب البيانات من جوجل شيت
        response = requests.get(CSV_URL)
        response.encoding = 'utf-8'
        data = pd.read_csv(StringIO(response.text))
        
        # تنظيف البيانات من الفراغات
        query = message.text.strip().lower()
        
        # البحث في كافة الأعمدة
        results = data[data.apply(lambda row: row.astype(str).str.contains(query, case=False, na=False).any(), axis=1)]
        
        # حذف رسالة الانتظار
        bot.delete_message(message.chat.id, wait_msg.message_id)

        if not results.empty:
            # نأخذ أول 5 نتائج فقط لتجنب الرسائل الطويلة جداً
            for index, row in results.head(5).iterrows():
                response_text = "✅ **تم العثور على بيانات:**\n\n"
                for col in data.columns:
                    val = row[col] if pd.notna(row[col]) else "غير متوفر"
                    response_text += f"🔹 **{col}:** {val}\n"
                bot.send_message(message.chat.id, response_text, parse_mode='Markdown')
        else:
            bot.reply_to(message, "❌ عذراً، لم يتم العثور على أي معلومات تطابق بحثك.")
            
    except Exception as e:
        bot.reply_to(message, "⚠️ حدث خطأ فني، تأكد من اتصال قاعدة البيانات بالإنترنت.")

print("البوت يعمل الآن...")
bot.polling()
