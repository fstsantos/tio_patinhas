from services.earning_service import EarningService
from services.spending_service import SpendingService
from datetime import date, datetime
from calendar import monthrange

async def handle_summary(msg, action, session):
    if len(action) < 2:
        await msg.reply_text("Use: resumo ganhos | resumo gastos [data: DD/MM/YYYY]")
        return

    if action[1].startswith("ganhos"):
        earnings = EarningService.list_month(session)
        await msg.reply_text(
            format_earning_summary(earnings),
            parse_mode="Markdown",
        )

    elif action[1].startswith("gastos"):
        parts = action[1].split()
        start_date = None
        
        if len(parts) > 1:
            try:
                start_date = datetime.strptime(parts[1], "%d/%m/%Y").date()
            except ValueError:
                await msg.reply_text("❌ Data inválida! Use o formato DD/MM/YYYY")
                return
        
        spendings = SpendingService.summary_by_description_month(session, start_date)
        await msg.reply_text(
            format_spending_summary(
                spendings,
                EarningService.total_month(session),
                SpendingService.total_month(session, start_date),
                start_date,
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


def format_spending_summary(spendings, total_earnings, total_spendings, start_date=None):
    if not spendings:
        if start_date:
            return f"Nenhum gasto registrado desde {start_date.strftime('%d/%m/%Y')}."
        return "Nenhum gasto registrado este mês."

    saldo = total_earnings - total_spendings
    
    if start_date:
        period_text = f"Gastos desde {start_date.strftime('%d/%m/%Y')} (por descrição)"
    else:
        period_text = "Gastos do mês (por descrição)"
    
    lines = [f"📉 *{period_text}:*\n"]

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

    # Only show suggested average spending if no custom date is given
    if not start_date:
        today = date.today()
        last_day = monthrange(today.year, today.month)[1]
        days_remaining = (last_day - today.day) + 1
        
        if days_remaining > 0 and saldo > 0:
            average_spending = saldo / days_remaining
            lines.append(f"\n💡 *Gasto médio sugerido:* R$ {average_spending:.2f}/dia ({days_remaining} dias restantes no mês)")

    return "\n".join(lines)