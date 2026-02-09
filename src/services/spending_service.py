import re
from datetime import date
from models import Spending

class SpendingService:

    @staticmethod
    def create(session, family_member_id, value, description, type_str):
        Spending.insert(
            session=session,
            family_member_id=family_member_id,
            description=description,
            value=value,
            dat_spent=date.today(),
            type_str=type_str
        )

    @staticmethod
    def summary_by_description_month(session):
        return Spending.summary_by_description_month(session)

    @staticmethod
    def total_month(session):
        return Spending.total_month(session)
    
    @staticmethod
    def process_spending(cmd_str):
        pattern = r"^gasto\s+(\w+)\s+([0-9]+(?:[.,][0-9]{1,2})?)\s+(.+)$"
        match = re.match(pattern, cmd_str.strip())

        if not match:
            raise ValueError(
                "Comando inválido! "
                "Formato: gasto [debit|credit|pix] [valor] [descrição]"
            )

        return (
            match.group(1),
            float(match.group(2).replace(",", ".")),
            match.group(3),
        )