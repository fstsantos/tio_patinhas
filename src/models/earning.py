from datetime import date
from sqlalchemy import Column, Integer, String, DECIMAL, Date, ForeignKey, extract, func
from sqlalchemy.orm import relationship, Session
from db import Base

class Earning(Base):
    __tablename__ = "earning"

    earning_id = Column(Integer, primary_key=True)
    family_member_id = Column(
        Integer,
        ForeignKey("family_member.family_member_id", ondelete="CASCADE"),
        nullable=False
    )
    description = Column(String(50), nullable=False)
    value = Column(DECIMAL(10, 2), nullable=False)
    dat_received = Column(Date, nullable=False)

    family_member = relationship(
        "FamilyMember",
        back_populates="earnings"
    )

    def __repr__(self):
        return f"<Earning id={self.earning_id} description={self.description}, value={self.value}>"

    @classmethod
    def insert(cls, session: Session, family_member_id: int, description: str, value: float, dat_received):
        """
        Insere um registro convertendo type_str para SpendingType.
        """
    
        new_earning = cls(
            family_member_id=family_member_id,
            description=description,
            value=value,
            dat_received =dat_received,
        )
        session.add(new_earning)
        session.commit()
        session.refresh(new_earning)
        return new_earning
    
    @classmethod
    def list_month(cls, session):
        today = date.today()
        return (
            session.query(cls)
            .filter(
                extract("month", cls.dat_received) == today.month,
                extract("year", cls.dat_received) == today.year,
            )
            .all()
        )

    @classmethod
    def total_month(cls, session):
        today = date.today()
        return (
            session.query(func.coalesce(func.sum(cls.value), 0))
            .filter(
                extract("month", cls.dat_received) == today.month,
                extract("year", cls.dat_received) == today.year,
            )
            .scalar()
        )