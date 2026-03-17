import os
import telebot
from google import genai
from PIL import Image
import io

# Токены
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

# --- Диагностика моделей (как и раньше) ---
print("🔍 Доступные модели (поддерживающие generateContent):")
try:
    model_list = list(client.models.list())
    available_models = [m.name for m in model_list if 'generateContent' in m.supported_actions]
    for name in available_models:
        print(f"  - {name}")
    if available_models:
        ACTIVE_MODEL = available_models[0]
        print(f"✅ Используем модель: {ACTIVE_MODEL}")
    else:
        ACTIVE_MODEL = "gemini-2.0-flash-exp"
        print("⚠️ Не найдено подходящих моделей, пробуем gemini-2.0-flash-exp")
except Exception as e:
    print(f"❌ Ошибка при получении списка моделей: {e}")
    ACTIVE_MODEL = "gemini-2.0-flash-exp"
    print(f"⚠️ Используем запасную модель: {ACTIVE_MODEL}")
# -------------------------------------------

@bot.message_handler(content_types=['text', 'photo'])
def handle_message(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Подготавливаем содержимое для Gemini
        contents = []
        
        # Если есть текст, добавляем его
        if message.text:
            contents.append(message.text)
        elif message.caption:  # если подпись к фото
            contents.append(message.caption)
        else:
            contents.append("Опиши это изображение подробно")  # запрос по умолчанию
        
        # Если есть фото, скачиваем и добавляем
        if message.photo:
            # Берем фото в наилучшем качестве (последнее в списке)
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            # Конвертируем в PIL Image для отправки в Gemini
            image = Image.open(io.BytesIO(downloaded_file))
            contents.append(image)
            
            print(f"📸 Получено фото, размер: {len(downloaded_file)} байт")
        
        # Отправляем запрос в Gemini
        response = client.models.generate_content(
            model=ACTIVE_MODEL,
            contents=contents
        )
        
        # Отправляем ответ
        if response and hasattr(response, 'text') and response.text:
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "🤔 Не удалось обработать изображение")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        bot.reply_to(message, f"⚠️ Ошибка при обработке: {e}")

print("✅ Мультимодальный бот запущен!")
print("📸 Можно отправлять фото с вопросами!")
bot.infinity_polling()
