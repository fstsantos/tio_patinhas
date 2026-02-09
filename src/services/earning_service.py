import re
from datetime import date
from models import Earning

class EarningService:

    @staticmethod
    def create(session, family_member_id, value, description):
        Earning.insert(
            session=session,
            family_member_id=family_member_id,
            description=description,
            value=value,
            dat_received=date.today()
        )

    @staticmethod
    def list_month(session):
        return Earning.list_month(session)

    @staticmethod
    def total_month(session):
        return Earning.total_month(session)
    
    @staticmethod
    def process_earning(cmd_str):
        pattern = r"^ganho\s+([0-9]+(?:[.,][0-9]{1,2})?)\s+(.+)$"
        match = re.match(pattern, cmd_str.strip())

        if not match:
            raise ValueError(
                "Comando inválido! Formato: ganho [valor] [descrição]"
            )

        return (
            float(match.group(1).replace(",", ".")),
            match.group(2),
        )