import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler

TOKEN = os.getenv("BOT_TOKEN", "7069058142:AAEixiLxYdobVbfJ4haLR8VQUsS5DQbvHCY")
ADMIN_ID = 108629951

CHOOSING_BOT, ASKING_QUESTIONS, ASKING_CONTACT = range(3)
user_data = {}
briefs = {
    "Консультация": [
        "Какой у вас проект/идея?",
        "Какие задачи вы хотите решить с помощью бота?",
        "Есть ли у вас бот сейчас?",
        "Какие вопросы особенно вас волнуют?",
        "Планируете делать бота сами или хотите передать мне?"
    ],
    "Бот для ленивых": [
        "Что должен делать бот?\n\nНапример: <i>выдавать материалы, собирать заявки, фильтровать клиентов, выдавать ссылку на оплату, вести по FAQ...</i>",
        "В каком мессенджере вы хотите использовать бота?\n\n<i>Instagram, Telegram, WhatsApp...</i>",
        "Для какого проекта он нужен?",
        "Какая цель у бота?\n\nНапример: <i>повысить продажи, сэкономить время, создать вау-эффект, просто удобно общаться с аудиторией</i>",
        "Какие поля/кнопки должны быть в нём?",
        "Есть ли у вас тексты/контент для бота? (Если нет — помогу сформулировать)",
        "Есть ли у вас аккаунт на платформе для сборки?\n\nНапример: <i>SalesBot, PuzzleBot, SMMBot</i>",
        "Примеры ботов, которые вам нравятся (если есть):"
    ],
    "Бот под ключ": [
        "Продукты и услуги компании\n\nЧтобы глубже понять вашу задачу, расскажите чем вы занимаетесь.\n\nНапример: <i>Продаем электротехнику. Точки продажи по все России. Есть свой интернет-магазин: example.ru</i>",
        "Какие задачи бмзнеса вы хотите решить с помощью чат-бота?\n\nСкорее всего, вы бы не задумались платить за чат-бота без причины. Постарайтесь перечислить, какие проблемы компании вы хотели бы решить с помощью него",
        "Почему для решения этих задач вы хотите использовать именно чат-бот?\n\nДля решения задач существует множество возможных способов. В моих интересах улучшать бизнес клиентов, а значит, подбирать лучшие инструменты. Я хочу быть уверена, что именно мои услуги могут вам помочь",
        "Опишите, пожалуйста, целевую аудиторию чат-бота.\n\nЧтобы научить бота понимать пользователей, нужно знать как пользователи говорят. Это зависит от места жительства, социального статуса, уровня образования, интересов и много другого. Пожалуйста, опишите целевую аудиторию бота как можно подробнее",
        "Какую пользу аудитории принесет бот?\n\nКлиенты не будут пользоваться ботом, если он не приносит пользы. Сформулируйте выгоды, которые бот даст пользователям. Бесполезный бот — пустое вложение денег.\т\тНапример: <i>он позволит клиентам получать ответы на их вопросы в любое время. Он сократит время ожидания ответа. Сможет помочь клиенту с выбором товара прямо на сайте магазина</i>",
        "Сколько пользователей одновременно смогут пользоваться чат-ботом?\n\nНагрузка на бот — главный критерий для подбора мощности сервера. Если не правильно её оценить, то возникнут проблемы: недооценим и бот упадет под нагрузкой, переоценим — будет работать надежно, но заплатите больше необходимого. Рекомендуем перезаложиться на 20-30%. Если пользователей окажется меньше — перевезем бота на сервер попроще.\n\nНапример: <i>около 100 человек</i>",
        "Нужна ли интеграция с вашим API? Если да, то расскажите о его функционале и по-возможности приложите ссылку на документацию",
        "Нужна ли интеграция с вашей базой данных? Если да, расскажите о ней подробнее.\n\nНапример: <i>Каталог товаров на MySQL</i>",
        "По каким параметрам вы планируете оценивать эффективность бота?\n\nМне важно знать, как мы с вами будем оценивать успешность проделанной работы.\n\nНапример: <i>Улучшение конверсии, изменение нагрузки на отдел техподдержки</i>",
        "Предполагаемый бюджет\n\nЗная бюджет я смогу предложить решение, которое в него вписывается, и сэкономить время на подготовке предложений, которые вам не подходят",
        "Желаемые сроки завершения проекта\n\nНапример: <i>6 месяцев. Через 6 месяцев конференция, на которой нужно презентовать бота</i>",
        "Будут ли изменяться сценарии бота в будущем? Требуется ли техническая поддержка бота в долгосрочной перспективе?\n\nСценарии со сложной логикой часто редактируются только через код",
        "Нужна ли разработка отдельной админ-панели для управления ботом? Если да, то опишите ее",
        "Есть ли у вас карта бота или диаграмма рабочего процесса?",
        "Есть ли у вас сценарии общения, по которым будет работать бот или их необходимо разработать?",
        "Есть ли у вас готовый контент для бота? Это как тексты, так и графика, презентации, стикеры и другие контентные элементы",
        "Примеры ботов, которые вам нравятся (если есть):"
    ]
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [["Консультация", "Бот для ленивых"], ["Бот под ключ"]]
    await update.message.reply_text(
        "Привет! Выберите, пожалуйста, на что вы хочтите забрифоваться?",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )
    return CHOOSING_BOT

async def choose_brief(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    choice = update.message.text
    if choice not in briefs:
        await update.message.reply_text("Выберте один из вариантов")
        return CHOOSING_BOT

    user_data[chat_id] = {
        "brief": choice,
        "answers": [],
        "current_q": 0
    }

    first_q = briefs[choice][0]
    await update.message.reply_text(first_q, reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')
    return ASKING_QUESTIONS

async def collect_answers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_text = update.message.text
    data = user_data.get(chat_id)

    if not data:
        await update.message.reply_text("Что-то пошло не так. Начните заново, пожалуйста")
        return ConversationHandler.END

    data["answers"].append(user_text)
    data["current_q"] += 1

    if data["current_q"] < len(briefs[data["brief"]]):
        next_q = briefs[data["brief"]][data["current_q"]]
        await update.message.reply_text(next_q, parse_mode='HTML')
        return ASKING_QUESTIONS
    else:
        await update.message.reply_text("И напоследок: кто будет принимать итоговые решения по поводу бота и выступать контактным лицом? Оставьте, пожалуйста, контакт для связи (телеграм, почта или телефон):")
        return ASKING_CONTACT

async def collect_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    contact_info = update.message.text
    data = user_data.get(chat_id)

    summary = f"Новая анкета по брифу: {data['brief']}\n\n"
    for i, answer in enumerate(data["answers"]):
        q = briefs[data["brief"]][i]
        summary += f"{q}\n→ {answer}\n\n"
    summary += f"Контакт для связи:\n→ {contact_info}\n\n"

    await update.message.reply_text("Спасибо за усилия и уделенное время! Теперь мне будет намного проще спланировать дальнейшую разработку. Я ознакомлюсь с ответами и вернусь к вам с дальнейшими шагами.")
    await context.bot.send_message(chat_id=ADMIN_ID, text=summary)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ещё один бриф", callback_data="new_brief")]
    ])
    await update.message.reply_text("Хотите заполнить ещё один бриф?", reply_markup=keyboard)

    user_data.pop(chat_id)
    return ConversationHandler.END

async def restart_brief(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    kb = [["Консультация", "Бот для ленивых"], ["Бот под ключ"]]
    await query.message.reply_text(
        "Хорошо, начнём заново. Выберите формат:",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )
    return CHOOSING_BOT

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(restart_brief, pattern="^new_brief$")
        ],
        states={
            CHOOSING_BOT: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_brief)],
            ASKING_QUESTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_answers)],
            ASKING_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_contact)],
        },
        fallbacks=[],
        allow_reentry=True
    )
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(restart_brief, pattern="^new_brief$"))
    app.run_polling()

if __name__ == "__main__":
    main()
