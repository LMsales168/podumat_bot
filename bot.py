from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
    app.run(host='0.0.0.0', port=8080)

t = Thread(target=run)
t.start()
import os
import random
import telebot
import markovify
from flask import Flask
from threading import Thread

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Загружаем тексты Пелевина
with open("pelevin.txt", "r", encoding="utf-8") as f:
    pelevin_text = f.read()

# Создаём марковскую модель
text_model = markovify.Text(pelevin_text, state_size=2)

# Словарь для запоминания отправленных текстов
user_history = {}

# Функция генерации уникального текста
def generate_unique_text(user_id):
    for _ in range(9999):  # Пробуем 9999 раз найти новый текст
        new_text = text_model.make_sentence()
        if new_text and (user_id not in user_history or new_text not in user_history[user_id]):
            user_history.setdefault(user_id, []).append(new_text)
            return new_text
    return "Не удалось сгенерировать новый текст. Попробуй ещё раз."

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Напиши мне что-нибудь, и я сгенерирую текст.")

@bot.message_handler(func=lambda message: True)
def send_random_text(message):
    text = generate_unique_text(message.chat.id)
    bot.reply_to(message, text)

# Flask-сервер для работы 24/7
app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive"

def run():
    app.run(host='0.0.0.0', port=8080)

t = Thread(target=run)
t.start()

bot.polling()
