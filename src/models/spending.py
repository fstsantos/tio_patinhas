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
    original_spending_id = Column(Integer, nullable=True)

    family_member = relationship(
        "FamilyMember",
        back_populates="spendings"
    )

    def __repr__(self):
        installment_info = ""
        if self.original_spending_id is not None:
            installment_info = f" [Parcela {self.original_spending_id}]"
        elif self.installment > 1:
            installment_info = f" ({self.installment}x)"
        
        return (
            f"<Spending id={self.spending_id} description={self.description}, "
            f"value={self.value} dat_spent={self.dat_spent} type={self.type}{installment_info}>"
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

        from dateutil.relativedelta import relativedelta
        
        # Create one record for each installment
        if type_enum == SpendingType.CREDIT and installment > 1:
            installment_value = value / installment
            
            # Create first installment with original date
            desc_with_installment = f"{description} (1/{installment})"
            new_spending = cls(
                family_member_id=family_member_id,
                description=desc_with_installment,
                value=installment_value,
                dat_spent=dat_spent,
                type=type_enum,
                installment=installment,
                original_spending_id=None
            )
            session.add(new_spending)
            session.commit()
            session.refresh(new_spending)
            
            original_id = new_spending.spending_id
            
            # Create remaining installments for subsequent months
            for i in range(1, installment):
                inst_date = dat_spent + relativedelta(months=i)
                desc_with_installment = f"{description} ({i+1}/{installment})"
                inst = cls(
                    family_member_id=family_member_id,
                    description=desc_with_installment,
                    value=installment_value,
                    dat_spent=inst_date,
                    type=type_enum,
                    installment=installment,
                    original_spending_id=original_id
                )
                session.add(inst)
            
            session.commit()
        else:
            # For non-credit or single installment, create normal spending
            new_spending = cls(
                family_member_id=family_member_id,
                description=description,
                value=value,
                dat_spent=dat_spent,
                type=type_enum,
                installment=installment,
                original_spending_id=None
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
    def select_by_family_member_id(cls, session: Session, family_member_id: int):
        return session.query(cls).filter(
            cls.family_member_id == family_member_id
        ).all()

    @classmethod
    def delete(cls, session: Session, spending_id: int):
        obj = session.get(cls, spending_id)
        if obj is None:
            raise ValueError(f"Gasto com id {spending_id} não encontrado.")
        
        # Only the original spending can be deleted
        if obj.original_spending_id is not None:
            raise ValueError("Não é permitido deletar parcelas geradas. Delete a transação original.")
        
        # If it's an original credit spending with installments, delete all related installments
        if obj.type == SpendingType.CREDIT and obj.installment > 1:
            related_installments = session.query(cls).filter(
                cls.original_spending_id == spending_id
            ).all()
            for inst in related_installments:
                session.delete(inst)
        
        session.delete(obj)
        session.commit()
        return obj

    @classmethod
    def update(cls, session: Session, spending_id: int, **fields):
        obj = session.get(cls, spending_id)
        if obj is None:
            raise ValueError(f"Gasto com id {spending_id} não encontrado.")
        
        if obj.original_spending_id is not None:
            raise ValueError("Não é permitido editar parcelas geradas. Edite a transação original.")

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

        # If value is being updated and there are installments, update all records
        if "value" in fields and obj.type == SpendingType.CREDIT and obj.installment > 1:
            new_value = fields["value"]
            inst_value = new_value / obj.installment
            # Update the original spending with the new installment value
            fields["value"] = inst_value
            # Update all related installments
            related_installments = session.query(cls).filter(
                cls.original_spending_id == spending_id
            ).all()
            for inst in related_installments:
                inst.value = inst_value
        
        for key, val in fields.items():
            if hasattr(obj, key):
                setattr(obj, key, val)
        session.commit()
        session.refresh(obj)
        return obj
    
    @classmethod
    def summary_by_description_month(cls, session: Session, start_date: date = None):
        query = session.query(
            cls.description,
            func.sum(cls.value).label("total")
        )
        
        if start_date is None:
            # Default: only current month
            today = date.today()
            query = query.filter(
                extract("month", cls.dat_spent) == today.month,
                extract("year", cls.dat_spent) == today.year,
            )
        else:
            # Custom date: all spendings from start_date up to today (inclusive)
            today = date.today()
            query = query.filter(
                cls.dat_spent >= start_date,
                cls.dat_spent <= today
            )
        
        return (
            query.group_by(cls.description)
            .order_by(func.sum(cls.value).desc())
            .all()
        )

    @classmethod
    def total_month(cls, session, start_date: date = None):
        query = session.query(func.coalesce(func.sum(cls.value), 0))
        
        if start_date is None:
            # Default: only current month
            today = date.today()
            query = query.filter(
                extract("month", cls.dat_spent) == today.month,
                extract("year", cls.dat_spent) == today.year,
            )
        else:
            # Custom date: all spendings from start_date up to today (inclusive)
            today = date.today()
            query = query.filter(
                cls.dat_spent >= start_date,
                cls.dat_spent <= today
            )
        
        return query.scalar()