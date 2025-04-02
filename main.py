import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = os.getenv("BOT_TOKEN", "7069058142:AAEixiLxYdobVbfJ4haLR8VQUsS5DQbvHCY")
ADMIN_ID = 108629951

CHOOSING_BOT, ASKING_QUESTIONS = range(2)
user_data = {}
briefs = {
    "Консультация": [
        "Какой у вас проект/идея?",
        "Какие задачи вы хотите решить с помощью бота?",
        "Есть ли у вас Telegram-бот сейчас?",
        "Какие вопросы особенно вас волнуют?"
    ],
    "Бот для ленивых": [
        "Что будет делать бот?",
        "Для какого проекта он нужен?",
        "Какие поля/кнопки должны быть в нём?",
        "Есть ли у вас аккаунт на платформе (например, PuzzleBot)?"
    ],
    "Бот под ключ": [
        "Опишите, что вы хотите от бота. Прямо максимально подробно!",
        "Какую задачу он решает для пользователей?",
        "Что он должен уметь?",
        "Какие интеграции или данные должны быть внутри?",
        "Какая у вас желаемая дата запуска?"
    ]
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [["Консультация", "Бот для ленивых"], ["Бот под ключ"]]
    await update.message.reply_text(
        "Привет! На что ты хочешь забрифоваться?",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )
    return CHOOSING_BOT

async def choose_brief(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    choice = update.message.text
    if choice not in briefs:
        await update.message.reply_text("Выбери один из вариантов.")
        return CHOOSING_BOT

    user_data[chat_id] = {
        "brief": choice,
        "answers": [],
        "current_q": 0
    }

    first_q = briefs[choice][0]
    await update.message.reply_text(first_q)
    return ASKING_QUESTIONS

async def collect_answers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_text = update.message.text
    data = user_data.get(chat_id)

    if not data:
        await update.message.reply_text("Что-то пошло не так. Начни заново.")
        return ConversationHandler.END

    data["answers"].append(user_text)
    data["current_q"] += 1

if data["current_q"] < len(briefs[data["brief"]]):
    next_q = briefs[data["brief"]][data["current_q"]]
    await update.message.reply_text(next_q)
    return ASKING_QUESTIONS
else:
    # анкета завершена
    summary = f"Новая анкета по брифу: {data['brief']}\n\n"
    for i, answer in enumerate(data["answers"]):
        q = briefs[data["brief"]][i]
        summary += f"{q}\n→ {answer}\n\n"
    await update.message.reply_text("Спасибо! Анкета отправлена.")
    await context.bot.send_message(chat_id=ADMIN_ID, text=summary)
    user_data.pop(chat_id)
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_BOT: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_brief)],
            ASKING_QUESTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_answers)],
        },
        fallbacks=[]
    )
    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()
