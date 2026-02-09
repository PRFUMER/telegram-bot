import os
import json
from datetime import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    JobQueue
)

# ------------------- ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ -------------------
TOKEN = os.getenv("BOT_TOKEN")       # Токен бота
GROUP_ID = int(os.getenv("GROUP_ID"))     # ID группы (например -1003863562437)

if not TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")

if not GROUP_ID:
    raise ValueError("GROUP_ID не найден в переменных окружения!")

GROUP_ID = int(GROUP_ID)


# ------------------- ХРАНЕНИЕ ОТВЕТОВ -------------------
ANSWERS_FILE = "answers.json"

try:
    with open(ANSWERS_FILE, "r") as f:
        answers = json.load(f)
except FileNotFoundError:
    answers = {}

# ------------------- ФУНКЦИЯ ОТПРАВКИ ОПРОСНИКА -------------------
async def send_poll(context: ContextTypes.DEFAULT_TYPE):
    """Отправка опросника с кнопками в группу"""
    days = ["Mon.", "Tue.", "Wed.", "Thu.", "Fri.", "Sat.", "Sun."]
    times_list = ["5:45 pm", "6:30 pm"]

    keyboard = []
    for day in days:
        row = [InlineKeyboardButton(f"{day} {t}", callback_data=f"{day} {t}") for t in times_list]
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text="Choose day and time to train:",
        reply_markup=reply_markup
    )

# ------------------- ОБРАБОТКА НАЖАТИЙ -------------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    selected = query.data

    # Сохраняем выбор пользователя
    answers[user_id] = selected
    with open(ANSWERS_FILE, "w") as f:
        json.dump(answers, f, indent=2)

    # Показываем пользователю, что выбор сохранён
    await query.edit_message_text(text=f"{query.from_user.first_name} chose: {selected}")

# ------------------- ТЕСТОВАЯ КОМАНДА -------------------
async def test_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /testpoll для ручной проверки опросника"""
    await send_poll(context)

# ------------------- ОСНОВНАЯ ЧАСТЬ -------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Обработчик кнопок
    app.add_handler(CallbackQueryHandler(button))

    # Команда для теста
    app.add_handler(CommandHandler("testpoll", test_poll))

    # JobQueue для опросника каждое воскресенье в 20:00
    job_queue: JobQueue = app.job_queue
    job_queue.run_daily(send_poll, time=time(20, 0), days=(6,))  # 6 = Sunday

    print("Бот запущен. Опросник будет отправляться каждое воскресенье в 20:00.")
    app.run_polling()

if __name__ == "__main__":
    main()
