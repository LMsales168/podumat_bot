from flask import Flask
from threading import Thread
import os
import telebot
import markovify
from collections import Counter
import random

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
text_model = markovify.Text(pelevin_text, state_size=3, well_formed=True)

# Словарь для хранения истории пользователей
user_history = {}

# Функция проверки текста на повторы
def filter_repetitions(text):
    words = text.lower().split()
    word_counts = Counter(words)
    return None if any(count > 2 for count in word_counts.values()) else text

# Функция генерации связного текста из нескольких предложений
def generate_unique_text(user_id):
    max_attempts = 3698
    min_words_total = 6  # Минимальное количество слов в итоговом тексте

    for _ in range(max_attempts):
        # Генерируем 2-3 коротких предложения
        sentences = []
        for _ in range(random.randint(2, 3)):  # Случайно выбираем 2 или 3 предложения
            sentence = text_model.make_short_sentence(140, tries=100)  # Ограничение длины
            if sentence and filter_repetitions(sentence):
                sentences.append(sentence)

        # Объединяем предложения в текст
        if sentences:
            combined_text = " ".join(sentences)
            if len(combined_text.split()) >= min_words_total:
                # Проверяем уникальность и осмысленность
                if user_id not in user_history or combined_text not in user_history[user_id]:
                    # Форматируем текст
                    formatted_text = combined_text[0].upper() + combined_text[1:]
                    if not formatted_text.endswith(('.', '!', '?')):
                        formatted_text += '.'

                    # Сохраняем в историю
                    user_history.setdefault(user_id, set()).add(formatted_text)
                    return formatted_text

    return "ку-ку. не могу уникально"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "пиши, что хочешь, я отвечу, что хочу")

@bot.message_handler(func=lambda message: True)
def send_random_text(message):
    text = generate_unique_text(message.chat.id)
    bot.reply_to(message, text)

if __name__ == "__main__":
    bot.polling(none_stop=True)
