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

from handlers.earning_handler import (
    handle_ganho,
    handle_lista_ganhos,
    handle_editar_ganho,
    handle_apagar_ganho,
)
from handlers.spending_handler import (
    handle_gasto,
    handle_lista_gastos,
    handle_editar_gasto,
    handle_apagar_gasto,
)
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
"""Tio Patinhas Bot v0\.1 💰
           
*Comandos disponíveis:*

*Gastos*
    \- gasto [debit\|credit\|pix] [valor] [parcelas \(só para crédito\)] [descrição]
    \- editar gasto \<id\> \<campo\> \<valor\>  \(campos: descricao, valor, tipo, parcelas, data\)
    \- apagar gasto \<id\>
    \- lista gastos [busca \(opcional\)]

*Ganhos*
    \- ganho [valor] [descrição]
    \- lista ganhos
    \- editar ganho \<id\> \<campo\> \<valor\>  \(campos: descricao, valor, data\)
    \- apagar ganho \<id\>

*Resumo*
\- resumo ganhos
\- resumo gastos

\- help \- ajuda""",
    parse_mode="MarkdownV2")

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
    parts = msg.text.lower().split()

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
            case "lista":
                if len(action) > 1:
                    if action[1].startswith("gastos"):
                        search_term = None
                        if len(parts) > 2:
                            search_term = " ".join(parts[2:])
                        await handle_lista_gastos(msg, session, search_term)
                    elif action[1].startswith("ganhos"):
                        await handle_lista_ganhos(msg, session)
                    else:
                        await msg.reply_text("Use: lista gastos [busca (opcional)] ou lista ganhos")
                else:
                    await msg.reply_text("Use: lista gastos [busca (opcional)] ou lista ganhos")
            case "editar":
                if len(action) > 1:
                    if action[1].startswith("gasto"):
                        await handle_editar_gasto(msg, cmd, session, family_member_id)
                    elif action[1].startswith("ganho"):
                        await handle_editar_ganho(msg, cmd, session, family_member_id)
                    else:
                        await msg.reply_text("Use: editar gasto <id> <campo> <valor> ou editar ganho <id> <campo> <valor>")
                else:
                    await msg.reply_text("Use: editar gasto <id> <campo> <valor> ou editar ganho <id> <campo> <valor>")
            case "apagar":
                if len(action) > 1:
                    if action[1].startswith("gasto"):
                        await handle_apagar_gasto(msg, cmd, session, family_member_id)
                    elif action[1].startswith("ganho"):
                        await handle_apagar_ganho(msg, cmd, session, family_member_id)
                    else:
                        await msg.reply_text("Use: apagar gasto <id> ou apagar ganho <id>")
                else:
                    await msg.reply_text("Use: apagar gasto <id> ou apagar ganho <id>")
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