from services.earning_service import EarningService
from datetime import datetime
import re

async def handle_ganho(msg, cmd, session, family_member_id):
    value, desc = EarningService.process_earning(cmd)
    EarningService.create(session, family_member_id, value, desc)
    await msg.reply_text("💰 Ganho registrado com sucesso!")


async def handle_lista_ganhos(msg, session):
    earnings = EarningService.list_all(session)

    if not earnings:
        await msg.reply_text("📭 Nenhum ganho registrado.")
        return

    lines = ["💰 *Lista de Ganhos*\n"]

    for e in earnings:
        lines.append(
            f"🆔 {e.earning_id} | {e.dat_received.strftime('%d/%m/%Y')}\n"
            f"📄 {e.description}\n"
            f"💵 R$ {e.value:.2f}"
            + "\n"
            "──────────────"
        )

    await msg.reply_text("\n".join(lines), parse_mode="Markdown")


async def handle_editar_ganho(msg, cmd, session, family_member_id):
    pattern = r"^editar\s+ganho\s+(\d+)\s+(descricao|valor|data)\s+(.+)$"

    match = re.match(pattern, cmd.strip(), flags=re.IGNORECASE)
    if not match:
        raise ValueError(
            "Formato inválido. Use: editar ganho <id> <campo> <valor>"
        )

    earning_id = int(match.group(1))
    field = match.group(2).lower()
    value = match.group(3).strip()

    fields = {}
    if field == "descricao":
        fields["description"] = value
    elif field == "valor":
        try:
            fields["value"] = float(value.replace(",", "."))
        except ValueError:
            raise ValueError("Valor inválido.")
    elif field == "data":
        try:
            fields["dat_received"] = datetime.strptime(value, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Data deve estar no formato DD/MM/YYYY.")

    EarningService.edit(session, earning_id, **fields)
    await msg.reply_text(f"Ganho {earning_id} atualizado com sucesso!")


async def handle_apagar_ganho(msg, cmd, session, family_member_id):
    match = re.match(r"^apagar\s+ganho\s+(\d+)$", cmd.strip(), flags=re.IGNORECASE)
    if not match:
        raise ValueError("Formato inválido. Use: apagar ganho <id>")
    earning_id = int(match.group(1))
    EarningService.delete(session, earning_id)
    await msg.reply_text(f"Ganho {earning_id} removido com sucesso!")