from services.spending_service import SpendingService

async def handle_gasto(msg, cmd, session, family_member_id):
    type_str, value, desc = SpendingService.process_spending(cmd)
    SpendingService.create(
        session,
        family_member_id,
        value,
        desc,
        type_str,
    )
    await msg.reply_text("💸 Gasto registrado com sucesso!")