from flask import Flask
from threading import Thread
import os
import telebot
import markovify
from collections import Counter

# Инициализация Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

t = Thread(target=run_flask)
t.start()

# Инициализация бота
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Загрузка текста
with open("pelevin.txt", "r", encoding="utf-8") as f:
    pelevin_text = f.read()

# Создание марковской модели
text_model = markovify.Text(pelevin_text, state_size=2, well_formed=True)

# Словарь для хранения истории пользователей
user_history = {}

# Функция проверки и исправления текста
def filter_repetitions(text):
    words = text.split()
    word_counts = Counter(words)

    # Проверяем, нет ли слова, повторяющегося более 3 раз
    for word, count in word_counts.items():
        if count > 3:
            return None
    return text

# Функция генерации уникального текста
def generate_unique_text(user_id):
    max_attempts = 3698
    min_words = 5

    for _ in range(max_attempts):
        # Генерируем предложение
        new_text = text_model.make_sentence(tries=100)

        if new_text and len(new_text.split()) >= min_words:
            # Фильтруем повторы
            filtered_text = filter_repetitions(new_text)

            if filtered_text and (user_id not in user_history or 
                                filtered_text not in user_history[user_id]):
                # Форматируем текст
                formatted_text = filtered_text[0].upper() + filtered_text[1:]
                if not formatted_text.endswith(('.', '!', '?')):
                    formatted_text += '.'

                # Сохраняем в историю
                user_history.setdefault(user_id, set()).add(formatted_text)
                return formatted_text

    return "ку-ку. уникальное попозже будет"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "пиши, что хочешь, отвечу, что хочу")

@bot.message_handler(func=lambda message: True)
def send_random_text(message):
    text = generate_unique_text(message.chat.id)
    bot.reply_to(message, text)

if __name__ == "__main__":
    bot.polling(none_stop=True)
