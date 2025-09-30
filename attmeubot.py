#.\venv\Scripts\activate
#python meu_bot.py

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

menu_principal = range(1)

# --- MENU ---
async def mostrar_menu(update: Update,      context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [KeyboardButton("Agendar consulta")],
        [KeyboardButton("Consulta virtual")],
        [KeyboardButton("Acompanhamento de tratamento")],
        [KeyboardButton("Contatar Dr. Heitor diretamente")],
        [KeyboardButton("Tirar dúvidas")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Escolha uma das opções abaixo:", reply_markup=reply_markup)
    return menu_principal

# --- START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá, espero que esteja tendo um ótimo dia! Sou a assistente virtual do Dr. Heitor Góes e estou à sua disposição para ajudar no que precisar. 😊"
    )
    await mostrar_menu(update, context)   
    return mostrar_menu

# --- MENU OPÇÕES ---
async def menuopt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    opcao = update.message.text

    if opcao == "Agendar consulta":
        keyboard = [
            [KeyboardButton("Segunda-feira")],
            [KeyboardButton("Terça-feira")],
            [KeyboardButton("Quarta-feira")],
            [KeyboardButton("Quinta-feira")],
            [KeyboardButton("Sexta-feira")],
            [KeyboardButton("Sábado")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Ok, para qual dia você prefere marcar sua consulta?", reply_markup=reply_markup)

    elif opcao == "Consulta virtual":
        keyboard = [
            [KeyboardButton("Agendar consulta virtual")],
            [KeyboardButton("Como funciona a consulta virtual?")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("O que você deseja?", reply_markup=reply_markup)

    elif opcao == "Tirar dúvidas":
        keyboard = [
            [KeyboardButton("Aceita plano de saúde?")],
            [KeyboardButton("Horários de funcionamento")],
            [KeyboardButton("Valores das consultas")],
            [KeyboardButton("Retorno")],
            [KeyboardButton("Como é feita a consulta online")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Qual seria sua dúvida?", reply_markup=reply_markup)

    else:
        await update.message.reply_text("Opção inválida. Por favor, escolha uma opção do menu 😉")
        return menu_principal

    return menu_principal

# --- CANCEL ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Atendimento cancelado. Digite /start se quiser começar novamente.")
    return ConversationHandler.END

# --- RODAR BOT ---
def main():
    app = ApplicationBuilder().token("7555781086:AAEBmqqdACvSLBJvEqiCIF7G9KssTkZRGcs").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            menu_principal: [MessageHandler(filters.TEXT & ~filters.COMMAND, menuopt)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)

    print("Bot rodando")
    app.run_polling()

if __name__ == "__main__":
    main()
