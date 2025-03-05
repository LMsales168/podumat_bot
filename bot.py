from flask import Flask
from threading import Thread
import os
import random
import telebot
import markovify

# Инициализация Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Запуск Flask в отдельном потоке
t = Thread(target=run_flask)
t.start()

# Инициализация бота
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Загрузка и подготовка текста
with open("pelevin.txt", "r", encoding="utf-8") as f:
    pelevin_text = f.read()

# Создание марковской модели с улучшенными параметрами
text_model = markovify.Text(pelevin_text, state_size=2, well_formed=True)

# Словарь для хранения истории всех пользователей
user_history = {}

# Функция генерации уникального текста
def generate_unique_text(user_id):
    max_attempts = 999  # Ограничение попыток
    min_words = 5      # Минимальное количество слов для осмысленности
    
    for _ in range(max_attempts):
        # Генерируем предложение
        new_text = text_model.make_sentence(tries=100)
        
        if new_text and len(new_text.split()) >= min_words:  # Проверяем длину
            # Убеждаемся, что текст уникален для пользователя
            if (user_id not in user_history or 
                new_text not in user_history[user_id]):
                
                # Исправляем пунктуацию и капитализацию
                new_text = new_text[0].upper() + new_text[1:]
                if not new_text.endswith(('.', '!', '?')):
                    new_text += '.'
                    
                # Добавляем в историю
                user_history.setdefault(user_id, set()).add(new_text)
                return new_text
    
    return "Не удалось сгенерировать уникальный текст. Попробуй позже."

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Пиши что хочешь, я отвечу в духе Пелевина!")

@bot.message_handler(func=lambda message: True)
def send_random_text(message):
    text = generate_unique_text(message.chat.id)
    bot.reply_to(message, text)

# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)
