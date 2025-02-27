import os
import random
import telebot

TOKEN = os.getenv("BOT_TOKEN")  # Читаем токен из переменных окружения
bot = telebot.TeleBot(TOKEN)

texts = [
    "Привет! Это случайный текст.",
    "Сегодня твой день!",
    "Случайные слова для вдохновения.",
    "Ты молодец!",
    "Держи еще один случайный текст."
]

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Напиши мне что-нибудь, и я отправлю случайный текст.")

@bot.message_handler(func=lambda message: True)
def send_random_text(message):
    bot.reply_to(message, random.choice(texts))

bot.polling()