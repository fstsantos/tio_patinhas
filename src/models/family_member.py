from sqlalchemy import Column, Integer, String, select
from sqlalchemy.orm import relationship, Session
from db import Base

class FamilyMember(Base):
    __tablename__ = "family_member"

    family_member_id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)

    earnings = relationship(
        "Earning",
        back_populates="family_member",
        cascade="all, delete-orphan"
    )

    spendings = relationship(
        "Spending",
        back_populates="family_member",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<FamilyMember id={self.family_member_id} name={self.name}>"
    
    @classmethod
    def get_id_by_name(cls, session: Session, name: str) -> int | None:
        stmt = select(cls.family_member_id).where(cls.name == name)
        return session.scalar(stmt)