from services.earning_service import EarningService

async def handle_ganho(msg, cmd, session, family_member_id):
    value, desc = EarningService.process_earning(cmd)
    EarningService.create(session, family_member_id, value, desc)
    await msg.reply_text("💰 Ganho registrado com sucesso!")