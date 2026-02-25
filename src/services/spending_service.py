import re
from datetime import date
from models import Spending

class SpendingService:

    @staticmethod
    def create(session, family_member_id, value, description, type_str, installment=1):
        Spending.insert(
            session=session,
            family_member_id=family_member_id,
            description=description,
            value=value,
            dat_spent=date.today(),
            type_str=type_str,
            installment=installment,
        )

    @staticmethod
    def summary_by_description_month(session):
        return Spending.summary_by_description_month(session)

    @staticmethod
    def total_month(session):
        return Spending.total_month(session)

    @staticmethod
    def list_all(session):
        return Spending.select_all(session)

    @staticmethod
    def list_by_description(session, search_term):
        return Spending.select_by_description(session, search_term)

    @staticmethod
    def edit(session, spending_id, **fields):
        return Spending.update(session, spending_id, **fields)

    @staticmethod
    def delete(session, spending_id):
        return Spending.delete(session, spending_id)
    
    @staticmethod
    def process_spending(cmd_str):
        pattern = r"""
        ^gasto\s+
        (?:
            (DEBIT|PIX)\s+
            ([0-9]+(?:[.,][0-9]{1,2})?)\s+
            (.+)
        |
            (CREDIT)\s+
            ([0-9]+(?:[.,][0-9]{1,2})?)\s+
            (\d+)\s+
            (.+)
        )
        $
        """
        match = re.match(pattern, cmd_str.strip(), re.IGNORECASE | re.VERBOSE)

        if not match:
            raise ValueError(
                "Comando inválido! "
                "Formato: gasto [debit|credit|pix] [valor] [parcelas?] [descrição]"
            )

        is_credit = match.group(4) is not None

        if is_credit:
            type_str = match.group(4)
            value = float(match.group(5).replace(",", "."))
            desc = match.group(7)
            installments = int(match.group(6))
        else:
            type_str = match.group(1)
            value = float(match.group(2).replace(",", "."))
            desc = match.group(3)
            installments = 1

        return type_str, installments, value, desc