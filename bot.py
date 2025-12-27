import telebot
import pandas as pd
import requests
from io import StringIO

API_TOKEN = '8437315411:AAFUgppuQaaevTdfBPUmvZ0mlWF1LB3Cejw'
CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vR85oUveKg_3fmBMQ2YjlhBhOlhosd-kTCNTi2ubaWy7fX7QnHty1fdZ4lu3TcKdkDJUySr3DzLCkYz/pub?output=csv'

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✅ البوت متصل الآن بنجاح.\nأرسل الاسم للبحث في قاعدة بيانات مجمع السلام.")

@bot.message_handler(func=lambda message: True)
def search_data(message):
    try:
        # جلب البيانات مع التأكد من ترميز اللغة العربية
        response = requests.get(CSV_URL)
        response.encoding = 'utf-8' 
        
        # قراءة البيانات وتحويل كل شيء لنصوص لتسهيل البحث
        data = pd.read_csv(StringIO(response.text))
        data = data.astype(str) 

        query = message.text.strip() # حذف الفراغات من بحث المستخدم

        # البحث الذكي: يبحث عن الكلمة في أي مكان داخل الصف
        results = data[data.apply(lambda row: row.str.contains(query, case=False, na=False).any(), axis=1)]

        if not results.empty:
            for index, row in results.head(3).iterrows():
                response_text = "📌 **البيانات الموجودة:**\n"
                for col in data.columns:
                    # تنظيف النصوص الظاهرة من أي علامات غريبة
                    val = row[col].strip()
                    response_text += f"▪️ **{col}:** {val}\n"
                bot.send_message(message.chat.id, response_text, parse_mode='Markdown')
        else:
            bot.reply_to(message, f"❌ لم أجد '{query}' في قاعدة البيانات.\nتأكد من كتابة الاسم بشكل صحيح كما هو في الجدول.")
            
    except Exception as e:
        bot.reply_to(message, "⚠️ عذراً، هنالك مشكلة في الوصول لبيانات جوجل حالياً.")

bot.polling()
