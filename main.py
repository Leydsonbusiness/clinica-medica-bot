#.\venv\Scripts\activate
#python meu_bot.py

#imports
import re
import os 
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, date, time
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
)
from google_integration import get_free_slots_for_date, create_appointment

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

#Banco de dados
from database import criar_tabela, inserir_paciente, identificar_cpf

# ==================== CONFIGURAÇÕES ====================

#chat_id medico
Chat_id_medico = int(os.getenv("Chat_id_medico"))

# STATES
(
    PROCESSAR_ENTRADA, CPF, NOME, DATA_NASC, GENERO, GENERO_OUTRO, TELEFONE, PERGUNTAS_OPC, DOENCAS, REMEDIOS, ALERGIAS, MENU, AGENDAR_CONSU, AGENDAR_HORARIO, CONFIRMAR_AGENDAMENTO, DUVIDAS, MOTIVO_CONT) = range(17)

# ==================== VALIDAÇÕES ====================

def validar_cpf(cpf: str) -> bool:
    cpf = re.sub(r'\D', '', cpf) 
    return bool(re.fullmatch(r'\d{11}', cpf))

def validar_data_nasc(data_nasc: str) -> bool:
    return re.fullmatch(r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/[0-9]{4}$', data_nasc) is not None

def validar_telefone(telefone: str) -> bool:
    telefone_brasileiro = r'^\(?(\d{2})\)?\s?(\d{4,5})[-.\s]?(\d{4})$'
    return re.fullmatch(telefone_brasileiro, telefone) is not None

def primeiro_nome(paciente):
    if not paciente:
        return ""

    nome_completo = paciente[0][1]
    nome = nome_completo.split()[0]
    return nome
    

# ==================== BANCO ====================

bd_temp = {
    "nome": None,
    "cpf": None,
    "data_nasc": None,
    "genero": None,
    "telefone": None,
    "idade": None,
    "doencas": None,
    "remedios": None,
    "alergias": None,
}

# ==================== CADASTRO ====================

async def receber_cpf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    cpf = update.message.text.strip()
    
    if not validar_cpf(cpf):
        await update.message.reply_text (f"Ops! o CPF {cpf} é inválido. Digite apenas 11 números, por favor.")
        return CPF
    
    context.user_data["cpf"] = cpf

    paciente = identificar_cpf(cpf)

    if paciente:
        nome = primeiro_nome(paciente)
        context.user_data["primeiro_nome"] = nome

        await update.message.reply_text (
            f"Que bom te ver por aqui, {nome} 😄! Em que posso lhe ajudar hoje?")
        return await mostrar_menu(update,context)
    
    else:
        bd_temp["cpf"] = cpf

        await update.message.reply_text ("Notei que você não possui cadastro, você vai precisar responder só algumas perguntinhas, vamos lá?😄")
        await update.message.reply_text ("Me informe seu *NOME COMPLETO*. [etapa 2/6]", parse_mode= 'Markdown')
        return NOME

# ==================== DATA_NASC ====================

async def receber_nome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nome = update.message.text.strip()

    bd_temp["nome"] = nome
    await update.message.reply_text ("Perfeito, acabei de anotar aqui. Agora me diga qual a sua *DATA DE NASCIMENTO* (use o fomado DD/MM/AAAA). [Etapa 3/6]", parse_mode= 'Markdown')
    return DATA_NASC


async def receber_data_nasc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    data_nasc = update.message.text.strip()

    if validar_data_nasc(data_nasc):
        data_nasc_date = datetime.strptime(data_nasc, "%d/%m/%Y").date()
        hoje = date.today()

        idade = hoje.year - data_nasc_date.year - ((hoje.month, hoje.day) < (data_nasc_date.month, data_nasc_date.day))
        
        bd_temp["data_nasc"] = data_nasc_date
        bd_temp["idade"] = idade

        await update.message.reply_text (f"Entendi, você tem {idade} anos, certo?")
        return await pedir_genero(update, context)
    
    else:
        await update.message.reply_text("Ops, data inválida! Digite no formato DD/MM/AAAA (Lembre-se de colocar as barras)")
        return DATA_NASC
    
# ==================== GENERO ======================
    
async def pedir_genero(update: Update,context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
            [KeyboardButton("Masculino")],
            [KeyboardButton("Feminino")],
            [KeyboardButton("Outro")],
            [KeyboardButton("Prefiro não responder")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Agora preciso que você me informe seu *GÊNERO*. [Etapa 4/6]", parse_mode= 'Markdown', reply_markup=reply_markup)
    return GENERO

# ==================== GENERO PERSONALIZADO ====================

async def receber_genero(update: Update,context: ContextTypes.DEFAULT_TYPE) -> int:
    opcao = update.message.text.strip()

    if opcao in["Masculino", "Feminino", "Prefiro não responder"]:
        bd_temp["genero"] = opcao
        await update.message.reply_text ("Perfeito! Agora me informe seu *NÚMERO DE TELEFONE*. [ETAPA 5/6]", parse_mode= "Markdown")
        return TELEFONE
    
    elif opcao == "Outro":
        await update.message.reply_text ("Ok, com qual gênero você se identifica?")
        return GENERO_OUTRO 

    else:
        await update.message.reply_text ("Por favor, escolha uma das opções abaixo.")
        return GENERO
    
async def receber_genero_pers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    bd_temp["genero"] = update.message.text.strip()

    await update.message.reply_text ("Perfeito! Agora me informe seu *NÚMERO DE TELEFONE*. [ETAPA 5/6]", parse_mode= "Markdown")
    return TELEFONE

# ==================== TELEFONE ====================

async def receber_telefone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    telefone = update.message.text.strip()

    if validar_telefone(telefone):
        context.user_data["telefone"] = telefone.strip()

        keyboard = [
            [KeyboardButton("Sim")],
            [KeyboardButton("Não quero responder")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Seu cadastro está praticamente concluído. Tenho as últimas 3 perguntas que são opcionais, mas se você responder já vai adiantar boa parte da consulta com seu médico.", reply_markup=reply_markup)
        await update.message.reply_text("São elas: \n" \
        "🤒*Você possui alguma doença?*\n" \
        "💊*Você toma algum remédio todos os dias?*\n" \
        "⚠️*Você possui alguma alergia?*\n\n" \
        "Deseja respondê-las?", parse_mode= "Markdown")
        return PERGUNTAS_OPC
    
    else:
        await update.message.reply_text(f"Ops! O telefone {telefone} é inválido. Por favor, digite como no seguinte exemplo: *84123456789*.", parse_mode= 'Markdown')
        return TELEFONE
    
# ==================== PERGUNTAS OPCIONAIS ====================
    
async def confirmar_op(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    perguntas_op = update.message.text.strip()

    if perguntas_op == "Sim":
        await update.message.reply_text("Perfeito! Vamos começar!")
        await update.message.reply_text("Qual(is) doença(s) você possui? [Etapa 1/3]")
        return DOENCAS
    
    elif perguntas_op == "Não quero responder":
        bd_temp["doencas"] = "Não quis responder"
        bd_temp["remedios"] = "Não quis responder"
        bd_temp["alergias"] = "Não quis responder"

        inserir_paciente(**bd_temp)
        await update.message.reply_text("Cadastro concuído com sucesso! ✅")
        await update.message.reply_text("Seja bem vindo(a) a Clínica Heitor Góes, estarei sempre a sua disposição! 😊")
        return await mostrar_menu(update, context)
    
    else: 
        await update.message.reply_text("Opção inválida! Escolha uma das opções abaixo, por favor")
        return await PERGUNTAS_OPC(update,context)
    
async def receber_doencas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bd_temp["doencas"] = update.message.text.strip()
    await update.message.reply_text("Anotado! Agora me informe, quais remédios você toma diariamente? [Etapa 2/3]")
    return REMEDIOS

async def receber_remedios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bd_temp["remedios"] = update.message.text.strip()
    await update.message.reply_text("Entendido! agora me responda a útima pergunta, Você possui alguma alérgia? se sim, quais? [Etapa 3/3]")
    return ALERGIAS

async def receber_alergias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bd_temp["alergias"] = update.message.text.strip()

    inserir_paciente(**bd_temp)
    await update.message.reply_text("Cadastro concluído com sucesso! ✅")
    await update.message.reply_text("Seja bem vindo(a) a Clínica Heitor Góes, estarei sempre a sua disposição! 😊")
    return await mostrar_menu(update, context)

# ==================== MENU PRINCIPAL ====================

async def mostrar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [KeyboardButton("Agendar consulta")],
        [KeyboardButton("Conheça quem é Dr. Heitor Góes")],
        [KeyboardButton("Tirar dúvidas")],
        [KeyboardButton("Contatar Dr. Heitor diretamente")],
        [KeyboardButton("Finalizar atendimento")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Escolha uma das opções abaixo:", reply_markup=reply_markup)
    return MENU
# ==================== START ==================== 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    await update.message.reply_text(
        "Olá, seja muito bem vindo! Espero que esteja tendo um ótimo dia! Me chamo Zara, sou a assistente virtual do Dr. Heitor Góes e estou à sua disposição para ajudar no que precisar. 😊"  
    )
    await update.message.reply_text("Para iniciarmos preciso que me informe seu CPF, por favor.")
    keyboard = [
        [KeyboardButton("Entrar")],
        [KeyboardButton("Entrar sem cadastro")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text("Ou se preferir, poderá ter acesso sem cadatro, mas será com funções limitadas. O que você deseja?", reply_markup=reply_markup)
    return PROCESSAR_ENTRADA

# =============== PROCESSAR ENTRADA =================

async def processar_entrada(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    opcao = update.message.text

    if opcao == "Entrar":
        await update.message.reply_text("Certo, agora me informe seu CPF, por favor")
        return CPF
    
    elif opcao == "Entrar sem cadastro":
        await update.message.reply_text("Em que posso te ajudar hoje?")
        return await mostrar_menu(update, context)
    
    else:
        await update.message.reply_text("Opção inválida! Escolha uma das opções abaixo, por favor")
        return PROCESSAR_ENTRADA

# =============== PROCESSAR MENU PRINCCPAL =================

async def menuopt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    opcao = update.message.text

    if opcao == "Agendar consulta":
        await update.message.reply_text("Ok, para qual dia você quer marcar sua consulta?📅\n " \
        "Digite no formato *DD/MM/AAAA* (ex: 25/01/2026).", parse_mode="Markdown")
        return AGENDAR_CONSU
    
    elif opcao == "Conheça quem é Dr. Heitor Góes":
        await update.message.reply_text("O Dr. Heitor Góes é médico clínico geral, formado em 2022, e desde então tem se dedicado a oferecer um atendimento próximo e de confiança. Sua atuação é voltada para entender o paciente como um todo, valorizando a escuta atenta e buscando soluções práticas para cada situação")
        return MENU
    
    elif opcao == "Contatar Dr. Heitor diretamente":
        nome = context.user_data.get("primeiro_nome", "")

        await update.message.reply_text(
            f"Sem problemas {nome}, vou avisá-lo sim! Mas antes preciso que me informe o motivo para que ele saiba abordar da melhor maneira. \n\n"

            "Qual o motivo do contato com Dr. Heitor?"
        )
        return MOTIVO_CONT

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
        return DUVIDAS
    
    elif opcao == "Finalizar atendimento":
        await update.message.reply_text("Obrigado pelo contato! 😊 Se precisar de algo mais, é só me chamar. Cuide-se! 💙")
        return ConversationHandler.END

    else:
        await update.message.reply_text("Opção inválida. Por favor, escolha uma opção do menu 😉")
        return await mostrar_menu(update, context)
    
# =============== PROCESSAR MENSAGEM PARA O MÉDICO =================

async def mnsg_contato(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    motivo_contato = update.message.text.strip()
    context.user_data["contato"] = motivo_contato

    cpf = context.user_data.get("cpf")
    if not cpf:
        await update.message.reply_text("Pra falar com o médico, preciso que você entre com CPF primeiro. Use /start ✅")
        return ConversationHandler.END

    paciente = identificar_cpf(cpf)
    if not paciente:
        await update.message.reply_text("Não encontrei seu cadastro. Use /start e faça o cadastro rapidinho 🙂")
        return ConversationHandler.END
    
    nome_completo = paciente[0][1]  
    telefone = paciente[0][5]

    await context.bot.send_message(chat_id= Chat_id_medico, text=
    "📣 Olá Heitor, Tem um(a) paciente querendo falar com você! \n"
    f"Paciente: {nome_completo}\n"
    f"Telefone: {telefone}\n"
    f"❗Motivo: {motivo_contato}")

    await update.message.reply_text("Pronto! Ja avisei ao Dr. Heitor e logo logo ele entrará em contato com você. 😉\n\n"
                                    
    "Posso te ajudar com algo mais?")
    return await mostrar_menu(update, context)


# =============== PROCESSAR AGENDAMENTO =================

async def processar_agendamento(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    texto = update.message.text.strip()

    if texto == "Voltar ao menu":
        await update.message.reply_text("Tudo bem 😊")
        return await mostrar_menu(update, context)
    
    if not re.fullmatch(r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/[0-9]{4}$', texto):
        await update.message.reply_text("Data inválida. Por favor, digite no formato *DD/MM/AAAA* (Lembre-se das barras).", parse_mode="Markdown") 
        return AGENDAR_CONSU

    # converte pra YYYY-MM-DD e pega a data atual
    data_escolhida = datetime.strptime(texto, "%d/%m/%Y").date()
    context.user_data["data_agendamento"] = data_escolhida
    hoje = date.today()
    feriados = {date(2026,1,1), date(2026,2,13), date(2026,2,16), date(2026,2,17), date(2026,2,18), date(2026,5,1), date(2026,9,7), date(2026,10,12), date(2026,11,2), date(2026,11,15), date(2026,11,20), date(2026,12,25),}

    # recusa marcações no mesmo dia e em dias que já passaram
    if data_escolhida <= hoje:
        await update.message.reply_text(
            f"Poxa 😕, não encontrei horários disponíveis para *{texto}*.\n"
            "Por favor, tente outra data",
            parse_mode="Markdown"
        )
        return AGENDAR_CONSU

    # recusa finais de semana 
    elif data_escolhida.weekday() >= 5:
        await update.message.reply_text(
            f"Não atendemos em finais de semana! Por favor, escolha um dia de segunda a sexta 😊",
            parse_mode="Markdown"
        )
        return AGENDAR_CONSU
    
    # recusa feriados brasileiros
    elif data_escolhida in feriados:
        await update.message.reply_text(
            f"Pelo que eu vi aqui *{texto}* cai em um feriado.\n"
            "Por favor, escolha outra data 😊",
            parse_mode="Markdown"
        )
        return AGENDAR_CONSU
    
    data_escolhida_2 = datetime.strptime(texto, "%d/%m/%Y").date().isoformat()
    context.user_data["data_agendamento"] = data_escolhida_2

    # busca horários livres no Google Calendar
    slots = get_free_slots_for_date(data_escolhida_2)  # lista de datetime
    if not slots:
        await update.message.reply_text(
            f"Poxa 😕 não encontrei horários disponíveis para *{texto}*.\n"
            "Por favor, tente outra data",
            parse_mode="Markdown"
        )
        return AGENDAR_CONSU

    horarios = [dt.strftime("%H:%M") for dt in slots]
    context.user_data["horarios_disponiveis"] = horarios

    keyboard = [[KeyboardButton(h)] for h in horarios]
    keyboard.append([KeyboardButton("Voltar ao menu")])
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        f"Horários disponíveis para *{texto}*:\nEscolha um horário 👇",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    return AGENDAR_HORARIO

# =============== ESCOLHER HORÁRIO =================

async def escolher_horario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    horario = update.message.text.strip()

    if horario == "Voltar ao menu":
        await update.message.reply_text("Tudo bem 😊")
        return await mostrar_menu(update, context)

    disponiveis = context.user_data.get("horarios_disponiveis", [])
    if horario not in disponiveis:
        await update.message.reply_text("Escolhe um horário da lista, por favor 🙂")
        return AGENDAR_HORARIO

    context.user_data["horario_agendamento"] = horario

    keyboard = [[KeyboardButton("Confirmar")], [KeyboardButton("Cancelar")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    data_escolhida = context.user_data["data_agendamento"]
    data_br = datetime.fromisoformat(data_escolhida).strftime("%d/%m/%Y")

    await update.message.reply_text(
        f"Posso confirmar sua consulta em *{data_br}* às *{horario}*?",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    return CONFIRMAR_AGENDAMENTO

# =============== CONFIRMAR AGENDAMENTO =================

async def confirmar_agendamento(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    opcao = update.message.text.strip()

    if opcao == "Cancelar":
        await update.message.reply_text("Beleza! Agendamento cancelado ✅")
        return await mostrar_menu(update, context)

    if opcao != "Confirmar":
        await update.message.reply_text("Escolha *Confirmar* ou *Cancelar* 🙂", parse_mode="Markdown")
        return CONFIRMAR_AGENDAMENTO

    cpf = context.user_data.get("cpf")
    if not cpf:
        await update.message.reply_text("Pra agendar, preciso que você entre com CPF primeiro. Use /start ✅")
        return ConversationHandler.END

    paciente = identificar_cpf(cpf)
    if not paciente:
        await update.message.reply_text("Não encontrei seu cadastro. Use /start e faça o cadastro rapidinho 🙂")
        return ConversationHandler.END

    nome_completo = paciente[0][1]  
    telefone = paciente[0][5]

    data_escolhida = context.user_data["data_agendamento"]
    horario = context.user_data["horario_agendamento"]

    # cria evento no Calendar
    create_appointment(data_escolhida, horario, patient_name=nome_completo, patient_telefone=telefone)

    data_br = datetime.fromisoformat(data_escolhida).strftime("%d/%m/%Y")
    nome = context.user_data.get("primeiro_nome", "")

    await update.message.reply_text(
        f"Perfeito, {nome}! Agendado com sucesso ✅\n📅 {data_br} às {horario}\nAté lá! 😊"
    )
    return await mostrar_menu(update, context)

# =============== PROCESSAR DUVIDAS =================

async def processar_duvidas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    opcao = update.message.text
    
    respostas = {
        "Aceita plano de saúde?": "Sim, aceitamos os principais planos de saúde. Entre em contato para confirmar se aceitamos o seu.",

        "Horários de funcionamento": "Atendemos de Segunda a Sexta, das 08h às 18h, e aos Sábados das 08h às 12h.",
        
        "Valores das consultas": "Os valores variam de acordo com o tipo de consulta. Entre em contato para mais informações.",

        "O valor da consulta é com retorno?": "Consultas de retorno têm valor diferenciado quando realizadas em até 30 dias após a consulta inicial.",

        "Como é feita a consulta virtual": "Minutos antes da sua consulta Dr. Heitor entrará em contato com você pelo Whatsapp. A consulta seguirá os mesmos padrões de um atendimento presencial: avaliação dos sintomas, esclarecimento de dúvidas e orientações médicas personalizadas diretamente da chamada de vídeo..",

        "Voltar ao menu": "Tudo bem 😊"
    }
    if opcao in respostas:
        await update.message.reply_text(f"{respostas[opcao]}")
        if opcao == "Voltar ao menu":
            return await mostrar_menu(update, context)
    
    else:
        await update.message.reply_text("Opção inválida. Por favor, escolha uma opção do menu.")
        return DUVIDAS
    return DUVIDAS

# =============== MENSSAGEM DIÁRIA PARA O MÉDICO =================
from daily_job import agenda_daily
from datetime import time
from zoneinfo import ZoneInfo

def setup_jobs(app):
    app.bot_data["CHAT_ID_MEDICO"] = Chat_id_medico

    TZ = ZoneInfo("America/Fortaleza")

    #PRODUÇÃO
    app.job_queue.run_daily(
    agenda_daily, 
    time=time(hour=7, minute=0, tzinfo=TZ),
    name="agenda_diaria_medico"
    )

    #TESTE
    # app.job_queue.run_repeating(
    # agenda_daily, 
    # interval=30,
    # first=5,
    # name="agenda_teste"
    # )

# =============== CHAT_ID MEDICO =================

async def medico_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    user = update.effective_user

    await update.message.reply_text(
        f"Seu chat_id é: {chat_id}\n"
        f"Usuário: {user.full_name}"
        + (f"\nUsername: @{user.username}" if user.username else "")
    )


# =============== TOKEN BOT =================

def main():
    token = os.getenv("BOT_TOKEN")

    app = ApplicationBuilder().token(token).build()


# =============== HANDLERS =================

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PROCESSAR_ENTRADA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, processar_entrada)
                ],
            CPF: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receber_cpf)
                ],
            NOME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receber_nome)
                ],
            DATA_NASC: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receber_data_nasc)
                ],
            GENERO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receber_genero)
                ],
            GENERO_OUTRO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receber_genero_pers)
                ],
            TELEFONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receber_telefone)
                ],
            PERGUNTAS_OPC: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, confirmar_op)
                ],
            DOENCAS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receber_doencas)
                ],
            REMEDIOS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receber_remedios)
                ],
            ALERGIAS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receber_alergias)
                ],
            MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, menuopt)
                ],
            MOTIVO_CONT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, mnsg_contato)
                ],
            AGENDAR_CONSU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, processar_agendamento)
                ],
            AGENDAR_HORARIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, escolher_horario)
                ],
            CONFIRMAR_AGENDAMENTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmar_agendamento)
                ],
            DUVIDAS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, processar_duvidas)
                ]
        },
        fallbacks=[CommandHandler("start", start)]
        #fallbacks=[CommandHandler("menu", menu_command)]
    )

    app.add_handler(CommandHandler("id", medico_id))
    app.add_handler(conv_handler)
    setup_jobs(app)

    print("Bot rodando")
    app.run_polling()

if __name__ == "__main__":
    main()