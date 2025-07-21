from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class PayrollStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FamilyOffice(Base):
    __tablename__ = "family_offices"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    employees = relationship("Employee", back_populates="family_office")
    payroll_runs = relationship("PayrollRun", back_populates="family_office")


class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True)
    family_office_id = Column(Integer, ForeignKey("family_offices.id"), nullable=False)
    name = Column(String(100), nullable=False)
    salary = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    family_office = relationship("FamilyOffice", back_populates="employees")


class PayrollRun(Base):
    __tablename__ = "payroll_runs"
    
    id = Column(Integer, primary_key=True)
    family_office_id = Column(Integer, ForeignKey("family_offices.id"), nullable=False)
    status = Column(Enum(PayrollStatus), default=PayrollStatus.PENDING)
    pdf_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    family_office = relationship("FamilyOffice", back_populates="payroll_runs")