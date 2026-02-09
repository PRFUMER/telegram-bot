import os
import json
from datetime import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# ==============================
# Получаем переменные из Railway
# ==============================

TOKEN = os.getenv("8555298355:AAGgRQ58Y6nVFtFkcLucCE9SUwP-1eaYbAA")
GROUP_ID = int(os.getenv("1003863562437"))

if not TOKEN:
    raise ValueError("TOKEN не найден в переменных окружения!")

if not GROUP_ID:
    raise ValueError("GROUP_ID не найден в переменных окружения!")

# ==============================
# Загружаем ответы
# ==============================

try:
    with open("answers.json", "r") as f:
        answers = json.load(f)
except:
    answers = {}

# ==============================
# Функция отправки опроса
# ==============================

async def send_poll(context: ContextTypes.DEFAULT_TYPE):
    days = ["Mon.", "Tue.", "Wed.", "Thu.", "Fri.", "Sat.", "Sun."]
    times_list = ["5:45 pm", "6:30 pm"]

    keyboard = []
    for day in days:
        row = [
            InlineKeyboardButton(
                f"{day} {t}",
                callback_data=f"{day} {t}"
            )
            for t in times_list
        ]
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text="Choose day and time foor training:",
        reply_markup=reply_markup
    )

# ==============================
# Команда /testpoll
# ==============================

async def test_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_poll(context)

# ==============================
# Обработка кнопок
# ==============================

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    selected = query.data

    answers[user_id] = selected

    with open("answers.json", "w") as f:
        json.dump(answers, f, indent=2)

    await query.edit_message_text(
        text=f"{query.from_user.first_name} chose: {selected}"
    )

# ==============================
# Запуск приложения
# ==============================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CallbackQueryHandler(button))
app.add_handler(CommandHandler("testpoll", test_poll))

# Воскресенье = 6
app.job_queue.run_daily(
    send_poll,
    time=time(20, 0),   # 20:00
    days=(6,)
)

print("Бот запущен. Опросник будет отправляться каждое воскресенье в 20:00.")

app.run_polling()
