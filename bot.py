import telebot
import pandas as pd
import requests
from io import StringIO

# التوكن الجديد الخاص بك
API_TOKEN = '8437315411:AAFUgppuQaaevTdfBPUmvZ0mlWF1LB3Cejw'
# رابط مستند مجمع السلام (المستند بأكمله)
CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vR85oUveKg_3fmBMQ2YjlhBhOlhosd-kTCNTi2ubaWy7fX7QnHty1fdZ4lu3TcKdkDJUySr3DzLCkYz/pub?output=csv'

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "✅ أهلاً بك في بوت مجمع السلام الرسمي\n"
        "--------------------------------\n"
        "🔍 للبحث عن معلومات، أرسل الاسم أو الرقم الآن..."
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def search_data(message):
    try:
        # إشعار المستخدم ببدء البحث
        wait_msg = bot.reply_to(message, "🔎 جاري فحص قاعدة البيانات...")
        
        # جلب البيانات من جوجل شيت
        response = requests.get(CSV_URL)
        response.encoding = 'utf-8'
        data = pd.read_csv(StringIO(response.text))
        
        query = message.text.strip().lower()
        
        # البحث في كافة الأعمدة
        results = data[data.apply(lambda row: row.astype(str).str.contains(query, case=False, na=False).any(), axis=1)]
        
        # حذف رسالة الانتظار
        bot.delete_message(message.chat.id, wait_msg.message_id)

        if not results.empty:
            for index, row in results.head(5).iterrows():
                response_text = "📋 **النتيجة المستخرجة:**\n\n"
                for col in data.columns:
                    val = row[col] if pd.notna(row[col]) else "—"
                    response_text += f"▪️ **{col}:** {val}\n"
                bot.send_message(message.chat.id, response_text, parse_mode='Markdown')
        else:
            bot.reply_to(message, "⚠️ لم يتم العثور على نتائج تطابق هذا الاسم أو الرقم.")
            
    except Exception as e:
        bot.reply_to(message, "❌ حدث خطأ فني أثناء جلب البيانات.")

bot.polling()
