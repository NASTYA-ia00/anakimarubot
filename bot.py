from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8034423761:AAGBruwgeuZktNh9miV6r5CMzo54mRV98QU"

# --- Главное меню ---
main_menu = ReplyKeyboardMarkup(
    [["📚 Каталог", "💬 О нас"], ["📝 Запрос перевода"]],
    resize_keyboard=True
)

# --- Приветствие (/start) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text=(
            f"Привет, {update.effective_user.first_name or 'гость'}!\n\n"
            "Добро пожаловать в команду *Anakimaru* 💫\n\n"
            "Здесь вы можете насладиться чтением переведённых нами манг и манхв в жанре яой 💕"
        ),
        reply_markup=main_menu,
        parse_mode="Markdown"
    )

# --- Обработка кнопки «Каталог» ---
async def show_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1. Любимый папой-волком 🐺", callback_data="project_wolfdad")],
        # сюда можно добавлять больше тайтлов ↓
        # [InlineKeyboardButton("2. Второй проект", callback_data="project_2")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📖 *Выберите проект:*", parse_mode="Markdown", reply_markup=reply_markup)

# --- Обработка выбора проекта ---
async def handle_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "project_wolfdad":
        await query.edit_message_text(
            "🐺 *Любимый папой-волком*\n\n"
            "Жанр: Яой, романтика, ГГ мужчина, Зверолюди 💕\n\n"
            "Перевод: продолжается\n\n"
            "📖 [Глава 1.1](https://te.legra.ph/LYUBIMYJ-PAPOJ-VOLKOM-Glava-11-11-03)",
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

# --- Обработка нижнего меню ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📚 Каталог":
        await show_catalog(update, context)
    elif text == "💬 О нас":
        await update.message.reply_text(
            "💬 Мы — команда *Anakimaru*!\n"
            "Переводим мангу и манхву с любовью к сюжету и персонажам 💞",
            parse_mode="Markdown"
        )
    elif text == "📝 Запрос перевода":
        await update.message.reply_text(
            "📝 Хотите предложить перевод?\n"
            "Отправьте название тайтла и ссылку — мы всё рассмотрим!"
        )
    else:
        await update.message.reply_text("Не понимаю команду 😅")

# --- Запуск бота ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_project))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()
