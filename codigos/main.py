#.\venv\Scripts\activate
#python meu_bot.py

#imports
import re
import os 
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)

token = os.getenv("BOT_TOKEN")

from datetime import datetime, date
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
)

from pathlib import Path
from dotenv import load_dotenv
import os

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
print("ENV_PATH:", ENV_PATH)

load_dotenv(ENV_PATH)

print("BOT_TOKEN:", repr(os.getenv("BOT_TOKEN")))


#Banco de dados
from database import criar_tabela, inserir_paciente, identificar_cpf

# ==================== CONFIGURAÇÕES ====================

# Estados de conversação
(
    PROCESSAR_ENTRADA, CPF, NOME, DATA_NASC, GENERO, GENERO_OUTRO, TELEFONE, PERGUNTAS_OPC, DOENCAS, REMEDIOS, ALERGIAS, MENU, AGENDAR_CONSU, CONSULTA_VIRT, DUVIDAS) = range(15)

# ==================== VALIDAÇÕES ====================

def validar_cpf(cpf: str) -> bool:
    cpf = re.sub(r'\D', '', cpf) 
    return bool(re.fullmatch(r'\d{11}', cpf))

def validar_data_nasc(data_nasc: str) -> bool:
    return re.fullmatch(r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/[0-9]{4}$', data_nasc) is not None

def validar_telefone(telefone: str) -> bool:
    telefone_brasileiro = r'^\(?(\d{2})\)?\s?(\d{4,5})[-.\s]?(\d{4})$'
    return re.fullmatch(telefone_brasileiro, telefone) is not None

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

    paciente = identificar_cpf(cpf)

    if paciente:
        nome_completo = paciente[0][1]
        primeiro_nome = nome_completo.split()[0]
        await update.message.reply_text (
            f"Que bom te ver por aqui, {primeiro_nome}😄! Em que posso lhe ajudar hoje?")
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
        bd_temp["telefone"] = update.message.text.strip()

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
    return await mostrar_menu(update, context)

# ==================== MENU PRINCIPAL ====================

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

# --- PROCESSAR MENU PRINCIPAL ---
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
        return AGENDAR_CONSU
    
    elif opcao == "Conheça quem é Dr. Heitor Góes":
        await update.message.reply_text("O Dr. Heitor Góes é médico clínico geral, formado em 2022, e desde então tem se dedicado a oferecer um atendimento próximo e de confiança. Sua atuação é voltada para entender o paciente como um todo, valorizando a escuta atenta e buscando soluções práticas para cada situação")
        return MENU

    elif opcao == "Consulta virtual":
        keyboard = [
            [KeyboardButton("Agendar consulta virtual")],
            [KeyboardButton("Como funciona a consulta virtual?")],
            [KeyboardButton("Voltar ao menu")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("No dia e horário marcados, o médico entrará em contato com você pelo Google Meet. A consulta seguirá os mesmos padrões de um atendimento presencial: avaliação dos sintomas, esclarecimento de dúvidas e orientações médicas personalizadas diretamente da chamada de vídeo.", reply_markup=reply_markup)
        return CONSULTA_VIRT
    
    elif opcao == "Contatar Dr. Heitor diretamente":
        await update.message.reply_text(
            "Você pode entrar em contato diretamente pelo telefone:(84)9702-8081\n"
            "ou pode enviar um email: heitorgoes@gmail.com"
        )
        return MENU

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

# --- Processar agendamento ---
async def processar_agendamento(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    opcao = update.message.text
    dia = update.message.text

    if opcao == "Voltar ao menu":
        await update.message.reply_text("Ok")
        return await mostrar_menu(update, context)

    await update.message.reply_text(
        f"Ótimo! Você escolheu {dia}. Em breve entraremos em contato para confirmar os horários disponíveis"
    )
    return await mostrar_menu(update, context)

# --- Processar consulta virtual ---
async def processar_consv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    opcao = update.message.text

    if opcao == "Voltar ao menu":
        await update.message.reply_text("Ok")
        return await mostrar_menu(update, context)

    if opcao == "Agendar consulta virtual":
        return await menuopt(update, context)
    
    elif opcao == "Como funciona a consulta virtual?":
        await update.message.reply_text(
            "A consulta virtual é realizada por videochamada, com a mesma qualidade de atendimento presencial.\n"
            "Você receberá um link de acesso no horário agendado."
        )
    else:
        await update.message.reply_text("Opção inválida. Por favor, escolha uma opção do menu.")
        return CONSULTA_VIRT

    return MENU

# --- processar duvidas ---
async def processar_duvidas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    opcao = update.message.text
    
    respostas = {
        "Aceita plano de saúde?": "Sim, aceitamos os principais planos de saúde. Entre em contato para confirmar se aceitamos o seu.",

        "Horários de funcionamento": "Atendemos de Segunda a Sexta, das 08h às 18h, e aos Sábados das 08h às 12h.",
        
        "Valores das consultas": "Os valores variam de acordo com o tipo de consulta. Entre em contato para mais informações.",

        "O valor da consulta é com retorno?": "Consultas de retorno têm valor diferenciado quando realizadas em até 30 dias após a consulta inicial.",

        "Como é feita a consulta virtual": "A consulta virtual é feita por videochamada através de plataforma segura. Você receberá o link no momento do agendamento.",

        "Voltar ao menu": "Ok"
    }
    if opcao in respostas:
        await update.message.reply_text(f"{respostas[opcao]}")
        if opcao == "Voltar ao menu":
            return await mostrar_menu(update, context)
    
    else:
        await update.message.reply_text("Opção inválida. Por favor, escolha uma opção do menu.")
        return DUVIDAS
    return DUVIDAS
    
# --- Comando menu ---
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await mostrar_menu(update, context)



# --- RODAR BOT ---
def main():
    token = os.getenv("BOT_TOKEN")

    app = ApplicationBuilder().token(token).build()
    print("TOKEN:", repr(token))

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
            AGENDAR_CONSU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, processar_agendamento)
                ],
            CONSULTA_VIRT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, processar_consv)
                ],
            DUVIDAS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, processar_duvidas)
                ]
        },
        fallbacks=[CommandHandler("start", start)]
        #fallbacks=[CommandHandler("menu", menu_command)]
    )

    app.add_handler(conv_handler)

    print("Bot rodando")
    app.run_polling()

if __name__ == "__main__":
    main()