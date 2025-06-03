import json
import asyncio
import nest_asyncio

from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)

nest_asyncio.apply()

GET_NAME, GET_SURNAME = range(2)

DATA_FILE = 'users.json'

def load_token():
    with open('config.json', 'r') as f:
        config = json.load(f)
    return config['TELEGRAM_BOT_TOKEN']

def load_users():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Стартовая команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_users()

    if user_id in users:
        await update.message.reply_text(f"Привет, {users[user_id]['name']} 👋")
        await update.message.reply_text("Вы уже зарегистрированы — всё на месте.")
        return ConversationHandler.END

    await update.message.reply_text("Привет! Давай познакомимся \nКак тебя зовут?")
    return GET_NAME

# Получаем имя
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text.strip()
    await update.message.reply_text("Отлично, а теперь напиши свою фамилию.")
    return GET_SURNAME

# Получаем фамилию
async def get_surname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    surname = update.message.text.strip()
    name = context.user_data.get('name')
    user_id = str(update.effective_user.id)

    users = load_users()
    users[user_id] = {
        "name": name,
        "surname": surname,
        "registered": True
    }
    save_users(users)

    await update.message.reply_text(
        f"Приятно познакомиться, {name} {surname}!\n"
        f"Теперь можешь указать свои пожелания по графику."
    )
    return ConversationHandler.END

# Главная точка входа
async def main():
    token = load_token()
    app = ApplicationBuilder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_surname)],
        },
        fallbacks=[],
    )

    app.add_handler(conv_handler)

    print("Бот запущен...")
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
