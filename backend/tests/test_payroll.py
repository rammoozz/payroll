import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, FamilyOffice, Employee, PayrollRun, PayrollStatus
from tasks import calculate_net_pay
from auth import create_access_token, authenticate_user


# Test database setup
@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestSessionLocal()
    yield db
    db.close()


def test_calculate_net_pay():
    """Test that net pay is calculated correctly (80% of gross)"""
    assert calculate_net_pay(100000) == 80000.0
    assert calculate_net_pay(50000) == 40000.0
    assert calculate_net_pay(75000) == 60000.0
    assert calculate_net_pay(0) == 0.0


def test_multi_tenant_isolation(test_db):
    """Test that family offices can't see each other's data"""
    # Create two family offices
    smith_office = FamilyOffice(name="Smith Family")
    jones_office = FamilyOffice(name="Jones Family")
    test_db.add_all([smith_office, jones_office])
    test_db.commit()
    
    # Add employees to each
    smith_employee = Employee(
        family_office_id=smith_office.id,
        name="John Smith",
        salary=100000
    )
    jones_employee = Employee(
        family_office_id=jones_office.id,
        name="Jane Jones",
        salary=90000
    )
    test_db.add_all([smith_employee, jones_employee])
    test_db.commit()
    
    # Query employees for Smith family
    smith_employees = test_db.query(Employee).filter(
        Employee.family_office_id == smith_office.id
    ).all()
    
    # Should only see Smith employee
    assert len(smith_employees) == 1
    assert smith_employees[0].name == "John Smith"
    
    # Query employees for Jones family
    jones_employees = test_db.query(Employee).filter(
        Employee.family_office_id == jones_office.id
    ).all()
    
    # Should only see Jones employee
    assert len(jones_employees) == 1
    assert jones_employees[0].name == "Jane Jones"


def test_payroll_run_status_transitions(test_db):
    """Test that payroll run status transitions work correctly"""
    # Create family office and payroll run
    office = FamilyOffice(name="Test Office")
    test_db.add(office)
    test_db.commit()
    
    payroll_run = PayrollRun(
        family_office_id=office.id,
        status=PayrollStatus.PENDING
    )
    test_db.add(payroll_run)
    test_db.commit()
    
    # Check initial status
    assert payroll_run.status == PayrollStatus.PENDING
    assert payroll_run.completed_at is None
    
    # Update to processing
    payroll_run.status = PayrollStatus.PROCESSING
    test_db.commit()
    assert payroll_run.status == PayrollStatus.PROCESSING
    
    # Update to completed
    payroll_run.status = PayrollStatus.COMPLETED
    payroll_run.completed_at = datetime.utcnow()
    test_db.commit()
    assert payroll_run.status == PayrollStatus.COMPLETED
    assert payroll_run.completed_at is not None


def test_jwt_authentication():
    """Test JWT token creation and authentication"""
    # Test successful authentication
    user = authenticate_user("smith@demo.com", "demo123")
    assert user is not None
    assert user["family_office_id"] == 1
    
    # Test failed authentication
    user = authenticate_user("smith@demo.com", "wrongpassword")
    assert user is None
    
    user = authenticate_user("nonexistent@demo.com", "demo123")
    assert user is None
    
    # Test token creation
    token = create_access_token({"email": "test@demo.com", "family_office_id": 1})
    assert isinstance(token, str)
    assert len(token) > 0


def test_employee_salary_validation(test_db):
    """Test that employee salaries are stored and retrieved correctly"""
    office = FamilyOffice(name="Test Office")
    test_db.add(office)
    test_db.commit()
    
    # Test various salary amounts
    employees = [
        Employee(family_office_id=office.id, name="Low Salary", salary=30000),
        Employee(family_office_id=office.id, name="Mid Salary", salary=75000.50),
        Employee(family_office_id=office.id, name="High Salary", salary=150000),
    ]
    test_db.add_all(employees)
    test_db.commit()
    
    # Retrieve and verify
    stored_employees = test_db.query(Employee).filter(
        Employee.family_office_id == office.id
    ).order_by(Employee.salary).all()
    
    assert len(stored_employees) == 3
    assert float(stored_employees[0].salary) == 30000.0
    assert float(stored_employees[1].salary) == 75000.50
    assert float(stored_employees[2].salary) == 150000.0