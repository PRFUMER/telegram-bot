import json
from datetime import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CallbackContext,
    JobQueue,
    CommandHandler
)

TOKEN = "8555298355:AAGgRQ58Y6nVFtFkcLucCE9SUwP-1eaYbAA"
GROUP_ID = -1003863562437  # вставь сюда ID вашей группы

# Словарь для хранения ответов
try:
    with open("answers.json", "r") as f:
        answers = json.load(f)
except FileNotFoundError:
    answers = {}

# --- Функция опросника --- #
async def send_poll(update_or_context, context: CallbackContext = None):
    """
    Универсальная функция для JobQueue и CommandHandler.
    Если вызывается через JobQueue, update_or_context = context
    Если через команду, update_or_context = update, context = context
    """
    if context is None:
        context = update_or_context  # для JobQueue

    days = ["Mon.", "Tue.", "Wed.", "Thu.", "Fri.", "Sat.", "Sun."]
    times_list = ["5:45 pm", "6:30 pm"]

    keyboard = []
    for day in days:
        row = [InlineKeyboardButton(f"{day} {t}", callback_data=f"{day} {t}") for t in times_list]
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем опросник в группу
    await context.bot.send_message(
        chat_id=GROUP_ID,
        text="Choose day and time for trainning:",
        reply_markup=reply_markup
    )

# --- Обработка нажатий кнопок --- #
async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    selected = query.data

    # Сохраняем выбор пользователя
    answers[user_id] = selected
    with open("answers.json", "w") as f:
        json.dump(answers, f, indent=2)

    # Редактируем сообщение, чтобы показать выбор
    await query.edit_message_text(text=f"{query.from_user.first_name} chose: {selected}")

# --- Основная часть --- #
app = ApplicationBuilder().token(TOKEN).build()

# Обработчик нажатий кнопок
app.add_handler(CallbackQueryHandler(button))

# Тестовый командный обработчик для опросника
app.add_handler(CommandHandler("testpoll", send_poll))

# JobQueue для опросника каждое воскресенье в 20:00 (8 вечера)
job_queue: JobQueue = app.job_queue
job_queue.run_daily(send_poll, time=time(20, 0), days=(6,))  # 6 = воскресенье

print("Бот запущен. Опросник будет отправлен в группу каждое воскресенье в 20:00.")
app.run_polling()
