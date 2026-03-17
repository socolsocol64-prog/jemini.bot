import os
import telebot
import google.generativeai as genai
from flask import Flask
from threading import Thread

# --- БЛОК АНТИ-СНА ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ---------------------

# Получаем токены из настроек Render (Environment Variables)
TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Настройка Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

bot = telebot.TeleBot(TOKEN)

# Обработка команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я твой бот на базе Gemini. Напиши мне любой вопрос!")

# Обработка текстовых сообщений
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        # Отправляем текст в Gemini
        response = model.generate_content(message.text)
        
        # Пробуем разные способы достать текст (защита от ошибок библиотеки)
        if hasattr(response, 'text'):
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, response.candidates[0].content.parts[0].text)
            
    except Exception as e:
        # Теперь бот пришлет саму ошибку, чтобы мы поняли, в чем дело
        bot.reply_to(message, f"Ошибка Gemini: {str(e)}")
        print(f"Error: {e}")

# Запуск бота
if __name__ == "__main__":
    print("Запуск сервера анти-сна...")
    keep_alive()
    print("Бот запущен!")
    bot.polling(none_stop=True)
