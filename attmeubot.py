#.\venv\Scripts\activate
#python meu_bot.py

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

Menu_principal = 1
Agendar_consu = 2
Consulta_virtual = 3
Duvidas = 4

# --- MENU ---
async def mostrar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [KeyboardButton("Agendar consulta")],
        [KeyboardButton("Conheça quem é Dr. Heitor Góes")],
        [KeyboardButton("Contatar Dr. Heitor diretamente")],
        [KeyboardButton("Tirar dúvidas")],
        [KeyboardButton("Finalizar atendimento")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Escolha uma das opções abaixo:", reply_markup=reply_markup)
    return Menu_principal

# --- START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá, espero que esteja tendo um ótimo dia! Me chamo Zara, sou a assistente virtual do Dr. Heitor Góes e estou à sua disposição para ajudar no que precisar. 😊"
    )
    return await mostrar_menu(update, context)

# --- RESPOSTAS ---
async def menuopt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    opcao = update.message.text

    if opcao == "Agendar consulta":
        keyboard = [
            [KeyboardButton("Segunda-feira")],
            [KeyboardButton("Terça-feira")],
            [KeyboardButton("Quarta-feira")],
            [KeyboardButton("Quinta-feira")],
            [KeyboardButton("Sexta-feira")],
            [KeyboardButton("Sábado")],
            [KeyboardButton("Voltar ao menu")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Ok, para qual dia você prefere marcar sua consulta?", reply_markup=reply_markup)
        return Agendar_consu
    
    elif opcao == "Conheça quem é Dr. Heitor Góes":
        await update.message.reply_text("O Dr. Heitor Góes é médico clínico geral, formado em 2023, e desde então tem se dedicado a oferecer um atendimento próximo e de confiança. Sua atuação é voltada para entender o paciente como um todo, valorizando a escuta atenta e buscando soluções práticas para cada situação")
        return Menu_principal

    elif opcao == "Consulta virtual":
        keyboard = [
            [KeyboardButton("Agendar consulta virtual")],
            [KeyboardButton("Como funciona a consulta virtual?")],
            [KeyboardButton("Voltar ao menu")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("No dia e horário marcados, o médico entrará em contato com você pelo Google Meet. A consulta seguirá os mesmos padrões de um atendimento presencial: avaliação dos sintomas, esclarecimento de dúvidas e orientações médicas personalizadas diretamente da chamada de vídeo.", reply_markup=reply_markup)
        return Consulta_virtual
    
    elif opcao == "Contatar Dr. Heitor diretamente":
        await update.message.reply_text(
            "Você pode entrar em contato diretamente pelo telefone:(84)9702-8081\n"
            "ou pode enviar um email: heitorgoes@gmail.com"
        )
        return Menu_principal

    elif opcao == "Tirar dúvidas":
        keyboard = [
            [KeyboardButton("Aceita plano de saúde?")],
            [KeyboardButton("Horários de funcionamento")],
            [KeyboardButton("Valores das consultas")],
            [KeyboardButton("O valor da consulta é com retorno?")],
            [KeyboardButton("Como é feita a consulta virtual")],
            [KeyboardButton("Voltar ao menu")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Qual seria sua dúvida?", reply_markup=reply_markup)
        return Duvidas

    else:
        await update.message.reply_text("Opção inválida. Por favor, escolha uma opção do menu 😉")
        return await mostrar_menu(update, context)

# --- Processar agendamento ---
async def processar_agendamento(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    dia = update.message.text

    if dia == "Voltar ao menu":
        await update.message.reply_text("Ok")
        return await mostrar_menu(update, context)
    
    await update.message.reply_text(
        f"Ótimo! Você escolheu {dia}. Em breve entraremos em contato para confirmar os horários disponíveis"
    )
    return Menu_principal

# --- Processar consulta virtual ---
async def processar_consv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    opcao = update.message.text

    if opcao == "Voltar ao menu":
        return await mostrar_menu(update, context)

    if opcao == "Agendar consulta virtual":
        await update.message.reply_text(
            "Para agendar sua consulta virtual, por favor entre em contato pelo telefone (XX) XXXXX-XXXX.\n\n"
            "Digite /menu para voltar ao menu principal."
        )
    elif opcao == "Como funciona a consulta virtual?":
        await update.message.reply_text(
            "A consulta virtual é realizada por videochamada, com a mesma qualidade de atendimento presencial.\n"
            "Você receberá um link de acesso no horário agendado.\n\n"
            "Digite /menu para voltar ao menu principal."
        )
    else:
        await update.message.reply_text("Opção inválida. Por favor, escolha uma opção do menu.")
        return Consulta_virtual

    return Menu_principal

# --- processar duvidas ---
async def processar_duvidas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    opcao = update.message.text

    if opcao == "voltar ao menu":
        return await mostrar_menu(update, context)
    
    respostas = {
        "Aceita plano de saúde?": "Sim, aceitamos os principais planos de saúde. Entre em contato para confirmar se aceitamos o seu.",
        "Horários de funcionamento": "Atendemos de Segunda a Sexta, das 8h às 18h, e aos Sábados das 8h às 12h.",
        "Valores das consultas": "Os valores variam de acordo com o tipo de consulta. Entre em contato para mais informações.",
        "Retorno": "Consultas de retorno têm valor diferenciado quando realizadas em até 30 dias após a consulta inicial.",
        "Como é feita a consulta online": "A consulta online é feita por videochamada através de plataforma segura. Você receberá o link no momento do agendamento."
    }

    if opcao in respostas:
        await update.message.reply_text(f"{respostas[opcao]}\n\nDigite /menu para voltar ao menu principal.")
    else:
        await update.message.reply_text("Opção inválida. Por favor, escolha uma opção do menu.")
        return Duvidas

    return Menu_principal
    
# --- Comando menu ---
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await mostrar_menu(update, context)

# --- CANCEL ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Tudo certo por hoje! 🩺 Estou à disposição para qualquer dúvida ou nova consulta. Cuide-se!")
    return ConversationHandler.END

# --- RODAR BOT ---
def main():
    app = ApplicationBuilder().token("7555781086:AAEBmqqdACvSLBJvEqiCIF7G9KssTkZRGcs").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            Menu_principal: [MessageHandler(filters.TEXT & ~filters.COMMAND, menuopt)],
            Agendar_consu: [MessageHandler(filters.TEXT & ~filters.COMMAND, processar_agendamento)],
            Consulta_virtual: [MessageHandler(filters.TEXT & ~filters.COMMAND, processar_consv)],
            Duvidas: [MessageHandler(filters.TEXT & ~filters.COMMAND, processar_duvidas)]
        },
        fallbacks=[CommandHandler("cancel", cancel),
        CommandHandler("menu", menu_command)
        ]
    )

    app.add_handler(conv_handler)

    print("Bot rodando")
    app.run_polling()

if __name__ == "__main__":
    main()
