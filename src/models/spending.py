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

    family_member = relationship(
        "FamilyMember",
        back_populates="spendings"
    )

    def __repr__(self):
        return f"<Spending id={self.spending_id} description={self.description}, value={self.value} type={self.type}>"

    @classmethod
    def insert(cls, session: Session, family_member_id: int, description: str, value: float, dat_spent, type_str: str):
        """
        Insere um registro convertendo type_str para SpendingType.
        type_str deve ser: 'debit', 'credit' ou 'pix' (case-insensitive)
        """
        type_upper = type_str.strip().upper()

        if type_upper in SpendingType.__members__:
            type_enum = SpendingType[type_upper]
        else:
            raise ValueError("Tipo inválido! Use 'debit', 'credit' ou 'pix'.")

        new_spending = cls(
            family_member_id=family_member_id,
            description=description,
            value=value,
            dat_spent=dat_spent,
            type=type_enum
        )
        session.add(new_spending)
        session.commit()
        session.refresh(new_spending)
        return new_spending
    
    @classmethod
    def select_all(cls, session: Session):
        return session.query(cls).all()
    
    @classmethod
    def summary_by_description_month(cls, session):
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