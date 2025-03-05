from flask import Flask
from threading import Thread
import os
import telebot
import markovify
from collections import Counter
import random
import re

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
text_model = markovify.Text(pelevin_text, state_size=2, well_formed=True)  # Уменьшаем state_size для большей гибкости

# Словарь для хранения истории пользователей
user_history = {}

# Функция проверки текста на повторы
def filter_repetitions(text):
    words = text.lower().split()
    word_counts = Counter(words)
    return None if any(count > 2 for count in word_counts.values()) else text

# Простая постобработка текста для улучшения грамматики
def post_process_text(text):
    # Удаляем лишние пробелы и приводим к нормальному виду
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Исправляем заглавную букву в начале
    if text:
        text = text[0].upper() + text[1:]
    
    # Добавляем точку, если нет завершающего знака
    if not text.endswith(('.', '!', '?')):
        text += '.'
    
    # Исправляем некоторые типичные ошибки согласования (пример для русского языка)
    text = re.sub(r'который\s+мы', 'которого мы', text)  # Пример исправления падежа
    text = re.sub(r'но\s+зато', 'а зато', text)  # Логическая связка
    
    return text

# Функция генерации связного текста из нескольких предложений
def generate_unique_text(user_id):
    max_attempts = 1000  # Уменьшаем количество попыток для скорости
    min_words_total = 8  # Минимальное количество слов в итоговом тексте

    for _ in range(max_attempts):
        sentences = []
        for _ in range(random.randint(1, 2)):  # Генерируем 1-2 предложения для простоты
            sentence = text_model.make_short_sentence(100, tries=50)  # Уменьшаем длину и попытки
            if sentence and filter_repetitions(sentence):
                sentences.append(sentence)

        if sentences:
            combined_text = " ".join(sentences)
            if len(combined_text.split()) >= min_words_total:
                # Проверяем уникальность
                if user_id not in user_history or combined_text not in user_history[user_id]:
                    # Применяем постобработку
                    formatted_text = post_process_text(combined_text)
                    
                    # Сохраняем в историю
                    user_history.setdefault(user_id, set()).add(formatted_text)
                    return formatted_text

    return "Ку-ку. Не получилось ничего путного."

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Пиши что угодно, отвечу в духе Пелевина.")

@bot.message_handler(func=lambda message: True)
def send_random_text(message):
    text = generate_unique_text(message.chat.id)
    bot.reply_to(message, text)

if __name__ == "__main__":
    bot.polling(none_stop=True)
