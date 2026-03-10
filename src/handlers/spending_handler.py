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
    
    if installment > 1:
        await msg.reply_text(
            f"💳 Gasto de R$ {value:.2f} registrado em {installment}x parcelas de R$ {value/installment:.2f}!\n"
            f"As parcelas serão contabilizadas nos próximos meses."
        )
    else:
        await msg.reply_text("💸 Gasto registrado com sucesso!")

async def handle_lista_gastos(msg, session, search_term=None, family_member_id=None):
    if family_member_id:
        spendings = SpendingService.list_by_family_member_id(session, family_member_id)
    elif search_term:
        spendings = SpendingService.list_by_description(session, search_term)
    else:
        spendings = SpendingService.list_all(session)

    if not spendings:
        if family_member_id:
            await msg.reply_text(f"📭 Nenhum gasto encontrado para este membro da família.")
        elif search_term:
            await msg.reply_text(f"📭 Nenhum gasto encontrado com '{search_term}'.")
        else:
            await msg.reply_text("📭 Nenhum gasto registrado.")
        return

    lines = ["💸 *Lista de Gastos*\n"]
    total = 0
    processed_ids = set()

    for s in spendings:
        # Skip if this is an installment that was already processed with its parent
        if s.original_spending_id is not None:
            continue
        
        # Skip if already processed
        if s.spending_id in processed_ids:
            continue
        
        processed_ids.add(s.spending_id)
        
        # If this is a credit with multiple installments, aggregate them
        if s.installment > 1:
            # Get all installments of this spending
            from models import Spending
            installments = session.query(Spending).filter(
                (Spending.spending_id == s.spending_id) |
                (Spending.original_spending_id == s.spending_id)
            ).all()
            
            total_value = sum(inst.value for inst in installments)
            total += total_value
            
            lines.append(
                f"🆔 {s.spending_id} | {s.dat_spent.strftime('%d/%m/%Y')} | 👤 {s.family_member.name}\n"
                f"📄 {s.description.rsplit(' (', 1)[0]}\n"  # Remove the (1/10) suffix for clean display
                f"💰 R$ {total_value:.2f} ({s.type.value}) • {s.installment} parcelas\n"
                "──────────────"
            )
        else:
            # Single installment spending
            lines.append(
                f"🆔 {s.spending_id} | {s.dat_spent.strftime('%d/%m/%Y')} | 👤 {s.family_member.name}\n"
                f"📄 {s.description}\n"
                f"💰 R$ {s.value:.2f} ({s.type.value})\n"
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