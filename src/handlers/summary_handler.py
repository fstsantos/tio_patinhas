from services.earning_service import EarningService
from services.spending_service import SpendingService

async def handle_summary(msg, action, session):
    if len(action) < 2:
        await msg.reply_text("Use: resumo ganhos | resumo gastos")
        return

    if action[1] == "ganhos":
        earnings = EarningService.list_month(session)
        await msg.reply_text(
            format_earning_summary(earnings),
            parse_mode="Markdown",
        )

    elif action[1] == "gastos":
        spendings = SpendingService.summary_by_description_month(session)
        await msg.reply_text(
            format_spending_summary(
                spendings,
                EarningService.total_month(session),
                SpendingService.total_month(session),
            ),
            parse_mode="Markdown",
        )

def format_earning_summary(earnings):
    if not earnings:
        return "📭 Nenhum ganho registrado este mês."

    total = sum(e.value for e in earnings)
    lines = ["📈 *Ganhos do mês (família):*\n"]

    for e in earnings:
        lines.append(f"- {e.description}: R$ {e.value:.2f}")

    lines.append(f"\n💰 *Total de ganhos:* R$ {total:.2f}")
    return "\n".join(lines)


def format_spending_summary(spendings, total_earnings, total_spendings):
    if not spendings:
        return "📭 Nenhum gasto registrado este mês."

    saldo = total_earnings - total_spendings
    lines = ["📉 *Gastos do mês (por descrição):*\n"]

    for s in spendings:
        lines.append(f"- {s.description}: R$ {s.total:.2f}")

    lines.append("\n──────────────")
    lines.append(f"💰 *Ganhos:* R$ {total_earnings:.2f}")
    lines.append(f"💸 *Gastos:* R$ {total_spendings:.2f}")
    lines.append(
        f"✅ *Disponível:* R$ {saldo:.2f}"
        if saldo >= 0
        else f"🚨 *Déficit:* R$ {saldo:.2f}"
    )

    return "\n".join(lines)