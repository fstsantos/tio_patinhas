import enum
from datetime import date
from sqlalchemy import Column, Integer, String, DECIMAL, Date, Enum, ForeignKey, extract, func
from sqlalchemy.orm import relationship, Session
from db import Base

class SpendingType(enum.Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"
    PIX = "PIX"

class Spending(Base):
    __tablename__ = "spending"

    spending_id = Column(Integer, primary_key=True)
    family_member_id = Column(
        Integer,
        ForeignKey("family_member.family_member_id", ondelete="CASCADE"),
        nullable=False
    )
    description = Column(String(50), nullable=False)
    value = Column(DECIMAL(10, 2), nullable=False)
    dat_spent = Column(Date, nullable=False)
    type = Column(Enum(SpendingType), nullable=False)
    installment = Column(Integer, nullable=False, default=1)

    family_member = relationship(
        "FamilyMember",
        back_populates="spendings"
    )

    def __repr__(self):
        return (
            f"<Spending id={self.spending_id} description={self.description}, "
            f"value={self.value} dat_spent={self.dat_spent} type={self.type} installments={self.installment}>"
        )

    @classmethod
    def insert(cls, session: Session, family_member_id: int, description: str, value: float, dat_spent, type_str: str, installment: int = 1):
        type_upper = type_str.strip().upper()

        if type_upper in SpendingType.__members__:
            type_enum = SpendingType[type_upper]
        else:
            raise ValueError("Tipo inválido! Use 'debit', 'credit' ou 'pix'.")

        if type_enum != SpendingType.CREDIT:
            installment = 1
        elif installment < 1:
            raise ValueError("Número de parcelas deve ser pelo menos 1.")

        new_spending = cls(
            family_member_id=family_member_id,
            description=description,
            value=value,
            dat_spent=dat_spent,
            type=type_enum,
            installment=installment,
        )
        session.add(new_spending)
        session.commit()
        session.refresh(new_spending)
        return new_spending
    
    @classmethod
    def select_all(cls, session: Session):
        return session.query(cls).all()

    @classmethod
    def select_by_description(cls, session: Session, search_term: str):
        return session.query(cls).filter(
            cls.description.ilike(f"%{search_term}%")
        ).all()

    @classmethod
    def delete(cls, session: Session, spending_id: int):
        obj = session.get(cls, spending_id)
        if obj is None:
            raise ValueError(f"Gasto com id {spending_id} não encontrado.")
        session.delete(obj)
        session.commit()
        return obj

    @classmethod
    def update(cls, session: Session, spending_id: int, **fields):
        obj = session.get(cls, spending_id)
        if obj is None:
            raise ValueError(f"Gasto com id {spending_id} não encontrado.")

        if "type_str" in fields:
            type_upper = fields["type_str"].strip().upper()
            if type_upper in SpendingType.__members__:
                obj.type = SpendingType[type_upper]
            else:
                raise ValueError("Tipo inválido! Use 'debit', 'credit' ou 'pix'.")
            del fields["type_str"]

        if "installment" in fields:
            inst = int(fields["installment"])
            if inst < 1:
                raise ValueError("Número de parcelas deve ser pelo menos 1.")
            resulting_type = obj.type
            if "type_str" in fields:
                tp_upper = fields["type_str"].strip().upper()
                if tp_upper in SpendingType.__members__:
                    resulting_type = SpendingType[tp_upper]
            if resulting_type != SpendingType.CREDIT:
                raise ValueError("Parcelas só são permitidas para gastos do tipo credit.")
            obj.installment = inst
            del fields["installment"]

        for key, val in fields.items():
            if hasattr(obj, key):
                setattr(obj, key, val)
        session.commit()
        session.refresh(obj)
        return obj
    
    @classmethod
    def summary_by_description_month(cls, session: Session):
        today = date.today()
        return (
            session.query(
                cls.description,
                func.sum(cls.value).label("total")
            )
            .filter(
                extract("month", cls.dat_spent) == today.month,
                extract("year", cls.dat_spent) == today.year,
            )
            .group_by(cls.description)
            .order_by(func.sum(cls.value).desc())
            .all()
        )

    @classmethod
    def total_month(cls, session):
        today = date.today()
        return (
            session.query(func.coalesce(func.sum(cls.value), 0))
            .filter(
                extract("month", cls.dat_spent) == today.month,
                extract("year", cls.dat_spent) == today.year,
            )
            .scalar()
        )