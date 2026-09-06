import logging
import os
import io
import json # Importa a biblioteca JSON
import threading
from datetime import datetime
from flask import Flask
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# --- BIBLIOTECAS DO GOOGLE ---
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# --- CONFIGURAÇÃO INICIAL ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- CONFIGURAÇÕES ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', 'SEU_TOKEN_AQUI')
NOME_DA_PLANILHA = 'Vendas da Loja de Bebidas'
ID_PASTA_DRIVE = os.environ.get('ID_PASTA_DRIVE', 'SEU_ID_DRIVE_AQUI')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

app = Flask(__name__)
@app.route('/')
def health_check():
    return "Bot está vivo e rodando!", 200

# --- LÓGICA DE AUTENTICAÇÃO SEGURA ---
creds = None
try:
    # Lê as credenciais da variável de ambiente
    google_creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    if google_creds_json is None:
        raise ValueError("A variável de ambiente GOOGLE_CREDENTIALS_JSON não foi encontrada.")
    
    # Converte o texto JSON em um dicionário Python
    creds_dict = json.loads(google_creds_json)
    
    # Cria as credenciais a partir do dicionário
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    gc = gspread.authorize(creds)
    drive_service = build('drive', 'v3', credentials=creds)
    logger.info("Autenticação com as APIs do Google bem-sucedida.")
except Exception as e:
    logger.error(f"Falha na autenticação com o Google: {e}")

# ... (O RESTANTE DO CÓDIGO PERMANECE IGUAL) ...

FUNCIONARIO, PRODUTO, VALOR, PAGAMENTO = range(4)

def salvar_no_sheets(dados_venda: dict):
    if not creds: return False
    try:
        spreadsheet = gc.open(NOME_DA_PLANILHA)
        worksheet = spreadsheet.sheet1
        linha_para_adicionar = [dados_venda['data_hora'], dados_venda['funcionario'], dados_venda['produto'], dados_venda['valor'], dados_venda['pagamento']]
        worksheet.append_row(linha_para_adicionar)
        logger.info(f"Venda adicionada com sucesso à planilha '{NOME_DA_PLANILHA}'.")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar no Google Sheets: {e}")
        return False

def salvar_no_drive(dados_venda: dict):
    if not creds: return False
    try:
        nome_arquivo = f"venda_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        conteudo_csv = "data_hora,funcionario,produto,valor,pagamento\n"
        conteudo_csv += f"\"{dados_venda['data_hora']}\",\"{dados_venda['funcionario']}\",\"{dados_venda['produto']}\",\"{dados_venda['valor']}\",\"{dados_venda['pagamento']}\""
        file_metadata = {'name': nome_arquivo, 'parents': [ID_PASTA_DRIVE]}
        media = MediaIoBaseUpload(io.BytesIO(conteudo_csv.encode('utf-8')), mimetype='text/csv', resumable=True)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        logger.info(f"Arquivo CSV '{nome_arquivo}' salvo com sucesso na pasta do Drive.")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar no Google Drive: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Olá! Sou o bot de registro de vendas. Use /novavenda para começar.")
async def novavenda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Qual o nome do funcionário?")
    return FUNCIONARIO
async def receber_funcionario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['funcionario'] = update.message.text
    await update.message.reply_text("Qual foi o produto vendido?")
    return PRODUTO
async def receber_produto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['produto'] = update.message.text
    await update.message.reply_text("Qual o valor total? (ex: 49.90)")
    return VALOR
async def receber_valor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['valor'] = update.message.text
    opcoes_pagamento = [['PIX', 'Cartão de Crédito'], ['Cartão de Débito', 'Dinheiro']]
    await update.message.reply_text("Qual a forma de pagamento?", reply_markup=ReplyKeyboardMarkup(opcoes_pagamento, one_time_keyboard=True, resize_keyboard=True))
    return PAGAMENTO
async def receber_pagamento(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['pagamento'] = update.message.text
    context.user_data['data_hora'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    dados_finais = context.user_data
    resumo_venda = (f"✅ *Venda Registrada com Sucesso!*\n\n*Funcionário:* {dados_finais['funcionario']}\n*Produto:* {dados_finais['produto']}\n*Valor:* R$ {dados_finais['valor']}\n*Pagamento:* {dados_finais['pagamento']}\n*Data/Hora:* {dados_finais['data_hora']}")
    await update.message.reply_text(resumo_venda, reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown')
    sheets_ok = salvar_no_sheets(dados_finais)
    drive_ok = salvar_no_drive(dados_finais)
    if not sheets_ok or not drive_ok:
        await update.message.reply_text("Atenção: falha ao registrar a venda nos sistemas do Google.")
    context.user_data.clear()
    return ConversationHandler.END
async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Registro cancelado.", reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def run_bot():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("novavenda", novavenda)],
        states={ FUNCIONARIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_funcionario)], PRODUTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_produto)], VALOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_valor)], PAGAMENTO: [MessageHandler(filters.Regex('^(PIX|Cartão de Crédito|Cartão de Débito|Dinheiro)$'), receber_pagamento)], },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
