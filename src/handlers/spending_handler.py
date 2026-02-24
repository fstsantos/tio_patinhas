from services.spending_service import SpendingService

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

async def handle_lista_gastos(msg, session):
    spendings = SpendingService.list_all(session)

    if not spendings:
        await msg.reply_text("📭 Nenhum gasto registrado.")
        return

    lines = [
        "💸 *Lista de Gastos*\n",
        "```",
        "ID  | Descrição                                          | Valor    | Tipo   | Parcelas | Data",
        "─" * 96,
    ]

    for s in spendings:
        lines.append(
            f"{s.spending_id:<3} | {s.description:<50} | "
            f"R$ {s.value:>7.2f} | {s.type.value:<6} | "
            f"{s.installment:<2} | {s.dat_spent.strftime('%d/%m/%Y'):<10}"
        )

    lines.append("```")

    await msg.reply_text("\n".join(lines), parse_mode="Markdown")