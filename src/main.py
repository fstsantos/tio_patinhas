import os
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from db import SessionLocal
from models import FamilyMember

from handlers.earning_handler import handle_ganho
from handlers.spending_handler import handle_gasto
from handlers.summary_handler import handle_summary

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

session = SessionLocal()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    await update.message.reply_text(
        f"Olá grupo 👋\nChat ID: `{chat.id}`",
        parse_mode="Markdown")

def get_help():
    return 

async def handle_help(msg):
    await msg.reply_text(
"""Tio Patinhas Bot v0.1 💰
           
Comandos disponíveis:
- help - ajuda
- gasto [debit|credit|pix] [valor] [descrição]
- ganho [valor] [descrição]
- resumo ganhos
- resumo gastos""")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    chat = update.effective_chat

    if msg.date.timestamp() < context.application.bot_data.get("start_time", 0):
        return

    if chat.type not in ("group", "supergroup"):
        return

    family_member_id = FamilyMember.get_id_by_name(
        session=session,
        name=update.effective_user.first_name,
    )

    action = msg.text.lower().split(maxsplit=1)
    cmd = msg.text.lower()

    try:
        match action[0]:
            case "help":
                await handle_help(msg)
            case "ganho":
                await handle_ganho(msg, cmd, session, family_member_id)
            case "gasto":
                await handle_gasto(msg, cmd, session, family_member_id)
            case "resumo":
                    await handle_summary(msg, action, session)
            case _:
                await msg.reply_text("Comando não disponível, utilize help para ajuda")
    except ValueError as e:
        await msg.reply_text(str(e))

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.bot_data["start_time"] = __import__("time").time()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    print("Tio Patinhas bot rodando...")
    
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()