from sqlalchemy import Integer, String, Float, BIGINT, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from database.entities.enums import AnnotatedTypes
from database.entities.core import Base


class Worker(Base):
    __tablename__ = "workers"
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'packer', 'manager', 'loader', 'pending') OR role IS NULL"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=True, unique=True)
    second_name: Mapped[str] = mapped_column(String(64), nullable=True, unique=True)
    phone_number: Mapped[str] = mapped_column(String(64), nullable=True, unique=True)
    payment_details: Mapped[str] = mapped_column(String(64), nullable=True, unique=True)
    bank_name: Mapped[str] = mapped_column(String(64), nullable=True, unique=True)
    role: Mapped[str] = mapped_column(String(256), nullable=True)
    tg_id: Mapped[int] = mapped_column(BIGINT, unique=True)
    salary: Mapped[int] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(256), nullable=True)
