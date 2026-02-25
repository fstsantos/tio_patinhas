from services.spending_service import SpendingService
from datetime import datetime

async def handle_gasto(msg, cmd, session, family_member_id):
    type_str, installment, value, desc = SpendingService.process_spending(cmd)
    SpendingService.create(
        session,
        family_member_id,
        value,
        desc,
        type_str,
        installment=installment,
    )
    await msg.reply_text("💸 Gasto registrado com sucesso!")

async def handle_lista_gastos(msg, session, search_term=None):
    if search_term:
        spendings = SpendingService.list_by_description(session, search_term)
    else:
        spendings = SpendingService.list_all(session)

    if not spendings:
        if search_term:
            await msg.reply_text(f"📭 Nenhum gasto encontrado com '{search_term}'.")
        else:
            await msg.reply_text("📭 Nenhum gasto registrado.")
        return

    lines = ["💸 *Lista de Gastos*\n"]
    total = 0

    for s in spendings:
        lines.append(
            f"🆔 {s.spending_id} | {s.dat_spent.strftime('%d/%m/%Y')}\n"
            f"📄 {s.description}\n"
            f"💰 R$ {s.value:.2f} ({s.type.value})"
            + (f" • {s.installment}x" if s.installment > 1 else "")
            + "\n"
            "──────────────"
        )
        total += s.value

    lines.append(f"\n💰 *Total:* R$ {total:.2f}")
    await msg.reply_text("\n".join(lines), parse_mode="Markdown")


async def handle_editar_gasto(msg, cmd, session, family_member_id):
    pattern = r"^editar\s+gasto\s+(\d+)\s+(descricao|valor|tipo|parcelas|data)\s+(.+)$"
    import re

    match = re.match(pattern, cmd.strip(), flags=re.IGNORECASE)
    if not match:
        raise ValueError(
            "Formato inválido. Use: editar gasto <id> <campo> <valor>"
        )

    spending_id = int(match.group(1))
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
    elif field == "tipo":
        fields["type_str"] = value
    elif field == "parcelas":
        try:
            fields["installment"] = int(value)
        except ValueError:
            raise ValueError("Número de parcelas inválido.")
    elif field == "data":
        try:
            fields["dat_spent"] = datetime.strptime(value, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Data deve estar no formato DD/MM/YYYY.")

    SpendingService.edit(session, spending_id, **fields)
    await msg.reply_text(f"Gasto {spending_id} atualizado com sucesso!")


async def handle_apagar_gasto(msg, cmd, session, family_member_id):
    import re
    match = re.match(r"^apagar\s+gasto\s+(\d+)$", cmd.strip(), flags=re.IGNORECASE)
    if not match:
        raise ValueError("Formato inválido. Use: apagar gasto <id>")
    spending_id = int(match.group(1))
    SpendingService.delete(session, spending_id)
    await msg.reply_text(f"Gasto {spending_id} removido com sucesso!")