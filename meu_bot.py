#.\venv\Scripts\activate
#python meu_bot.py

#imports
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton #opções do menu e botão
from telegram.ext import (ApplicationBuilder,CommandHandler,MessageHandler,filters,ContextTypes,ConversationHandler) # telebot
import re  #função para expressao regular 
import asyncio
#import pandas as pd
#import imageio.v3 as iio #receber fotos 
#import PyPDF2 #receber pdf

menu_principal = range(1)

"""
# Dicionários para armazenar os dados -->fazer com SQLite 
banco = {} 

cpf_solicitado, nome_solicitado, dataNasc_solicitada, genero_solicitado, telefone_solicitado, menu_principal = range(1) #etapas

#Expressoes regulares para validações
def validar_cpf(cpf: str) -> bool:
    if re.fullmatch(r'^\d{11}$', cpf):
        return True
    else:
        return False

def validar_nasc(data: str) -> bool:
    return re.fullmatch(r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/[0-9]{4}$', data) is not None

def validar_telefone(telefone: str) -> bool:
    telefone_brasileiro = r'^\(?(\d{2})\)?\s?(\d{4,5})[-.\s]?(\d{4})$'
    return re.fullmatch(telefone_brasileiro, telefone) is not None
"""

#menu
async def mostrar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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

# inicio do bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá, espero que esteja tendo um ótimo dia! Sou a assistente virtual do Dr. Heitor Góes e estou a sua disposição para ajudar no que precisar.😊")#update envia mensagem de volta para o usuário
    return await mostrar_menu(update, context)
    #await update.message.reply_text("Para começarmos, me informe seu CPF, por favor.(Somente números)")
    #return cpf_solicitado

# ---- CADASTRO ----
""" 
async def identificar_cadastro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cpf_digitado = update.message.text.strip()

    if validar_cpf(cpf_digitado):
        context.user_data['cpf_temp'] = cpf_digitado
        
        if cpf_digitado in banco:
            primeiro_nome = banco[cpf_digitado].get("nome").split()[0]
            await update.message.reply_text(f"Olá {primeiro_nome}! Que bom te ver por aqui, em que posso lhe ajudar hoje?")
            await mostrar_menu(update, context); return menu_principal
        else:
            await update.message.reply_text("Para iniciarmos o atendimento preciso fazer um pequeno cadastro, vamos lá?")
            await update.message.reply_text("Me informe seu *NOME COMPLETO*. [etapa 1/4]", parse_mode= 'Markdown')
            return nome_solicitado
    else: 
        await update.message.reply_text(f"Ops! o CPF {cpf_digitado} é inválido. Digite apenas 11 números, por favor")
        return cpf_solicitado

async def receber_nome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nome_digitado = update.message.text.strip()
    cpf = context.user_data.get('cpf_temp')

    if cpf and cpf in banco: 
        banco[cpf]["nome"] = nome_digitado 
        await update.message.reply_text("Obrigada! Agora, me informe sua *DATA DE NASCIMENTO* no formato DD/MM/AAAA. [etapa 2/4]", parse_mode='Markdown')
        return dataNasc_solicitada

async def receber_data_nasc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    data_digitada = update.message.text.strip()
    cpf = context.user_data.get('cpf_temp')

    if validar_nasc(data_digitada):
        if cpf and cpf in banco:
            banco[cpf]["data_nascimento"] = data_digitada
            keyboard = [
                [KeyboardButton("Masculino")],
                [KeyboardButton("Feminino")],
                [KeyboardButton("Transgênero")],
                [KeyboardButton("Prefiro não informar")],
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text("Quase lá! Agora, me informe seu *GÊNERO*. [etapa 3/4]", reply_markup=reply_markup, parse_mode='Markdown')
            return genero_solicitado
    else:
        await update.message.reply_text(f"Ops! A data {data_digitada} é inválida. Por favor, digite no formato DD/MM/AAAA.")
        return dataNasc_solicitada

async def receber_genero(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    genero_digitado = update.message.text.strip()
    cpf = context.user_data.get('cpf_temp')

    if cpf and cpf in banco:
        banco[cpf]['genero'] = genero_digitado
    await update.message.reply_text("E por último, = me informe seu *TELEFONE COM DDD*, por favor [Etapa 4/4]", parse_mode= 'markdown')
    return telefone_solicitado

async def receber_telefone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    telefone_digitado = update.message.text.strip()
    cpf = context.user_data.get('cpf_temp')

    if validar_telefone(telefone_digitado):
        if cpf and cpf in banco:
            banco[cpf]['telefone'] = telefone_digitado
            del context.user_data['cpf_temp']

            await update.message. reply_text(
                f"Cadastro concluído com sucesso! ✅\n\n"
                f"**CPF**: {cpf}\n"
                f"**Nome**: {banco[cpf]['nome']}\n"
                f"**Data de Nascimento**: {banco[cpf]['data_nascimento']}\n"
                f"**Gênero**: {banco[cpf]['genero']}\n"
                f"**Telefone**: {banco[cpf]['telefone']}",
                parse_mode= 'Markdown' 
            )
            await mostrar_menu(update, context); 

        else:
            await update.message.reply_text(f"Ops! O telefone {telefone_digitado} é inválido. Por favor, digite como no seguinte exemplo:*84123456789*.", parse_mode= 'Markdown')
"""

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
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Ok, para qual dia você prefere marcar sua consulta?", reply_markup=reply_markup)
        #await update.message.reply_text("Perfeito! Deixarei sua consulta agendada para o dia {dia} às {hora} como você pediu. Até lá 😉)


    elif opcao == "consulta virtual":
        await update.message.reply_text("O que você deseja?")
        keyboard = [
            [KeyboardButton("Agendar consulta virtual")],
            [KeyboardButton("Como funciona a consulta virtual?")]
        ]
                   
    elif opcao == "Tirar dúvidas":
        await update.message.reply_text("Qual seria sua Dúvida?")
        keyboard = [
         [KeyboardButton("Aceita plano de saúde?")],
         [KeyboardButton("Horários de funcionamento")],
         [KeyboardButton("Valores das consultas")],
         [KeyboardButton("Retorno")],
         [KeyboardButton("como é feita a consulta online")]
        ]
        if opcao == 'Aceita plano de saúde?':
            await update.message.reply_text("Sim! Nós aceitamos plano de saúde")
        if opcao == "Horários de funcionamento":
            await update.message.reply_text("Irei te enviar os horários, aproveite para vir nos fazer uma visita.")
            await update.message.reply_text(
                "Segunda-feira: 08:00 às 12:00 e das 14:00 às 18:00\n"
                "Terça-feira: 08:00 às 12:00 e das 14:00 às 18:00\n"
                "Quarta-feira: 08:00 às 12:00 e das 14:00 às 18:00\n"
                "Quinta-feira: 08:00 às 12:00 e das 14:00 às 18:00\n"
                "Sexta-feira: 08:00 às 12:00 e das 14:00 às 18:00\n"
                "Sábado: 08:00 às 11:00\n"
                "Domingo: Não atendemos"
            )
    else:
        await update.message.reply_text("Opção inválida. Por favor, escolha uma opção do menu 😉")
        return "tirar duvidas"
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Atendimento cancelado. Digite /start se quiser começar novamente.")
    return ConversationHandler.END


# ---- Faz o bot rodar ----
async def main():
    if __name__ == '__main__':
        app = ApplicationBuilder().token("").build()

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                menu_principal: [MessageHandler(filters.TEXT & ~filters.COMMAND, menuopt)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )

        app.add_handler(conv_handler)

        print("Bot rodando e aguardando mensagens no Telegram...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
