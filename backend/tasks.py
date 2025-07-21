from celery import Celery
import os
import time
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from database import SessionLocal
from models import PayrollRun, PayrollStatus, Employee

# Celery configuration
celery_app = Celery(
    'payroll',
    broker=os.getenv('CELERY_BROKER_URL', 'amqp://rabbitmq_user:rabbitmq_pass@localhost:5672//'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    result_expires=3600,
    timezone='UTC',
    enable_utc=True,
)


def calculate_net_pay(gross_salary):
    """Simple calculation: 20% tax deduction"""
    return float(gross_salary) * 0.8


def generate_pay_stub_pdf(employee, net_pay, pdf_path):
    """Generate a simple PDF pay stub"""
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(1 * inch, height - 1 * inch, "Pay Stub")
    
    # Date
    c.setFont("Helvetica", 12)
    c.drawString(1 * inch, height - 1.5 * inch, f"Date: {datetime.now().strftime('%B %Y')}")
    
    # Employee info
    c.drawString(1 * inch, height - 2 * inch, f"Employee: {employee.name}")
    c.drawString(1 * inch, height - 2.3 * inch, f"Employee ID: {employee.id}")
    
    # Separator line
    c.line(1 * inch, height - 2.5 * inch, width - 1 * inch, height - 2.5 * inch)
    
    # Payment details
    c.drawString(1 * inch, height - 3 * inch, "Earnings:")
    c.drawString(2 * inch, height - 3.3 * inch, f"Gross Salary: ${employee.salary:,.2f}")
    
    c.drawString(1 * inch, height - 4 * inch, "Deductions:")
    c.drawString(2 * inch, height - 4.3 * inch, f"Federal Tax (20%): ${float(employee.salary) * 0.2:,.2f}")
    
    # Total
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, height - 5 * inch, f"Net Pay: ${net_pay:,.2f}")
    
    # Footer
    c.setFont("Helvetica", 10)
    c.drawString(1 * inch, 1 * inch, "This is a computer-generated document.")
    
    c.save()


@celery_app.task(bind=True)
def process_payroll(self, payroll_run_id):
    """Process payroll for all employees in a family office"""
    db = SessionLocal()
    
    try:
        # Get payroll run
        payroll_run = db.query(PayrollRun).filter(PayrollRun.id == payroll_run_id).first()
        if not payroll_run:
            raise Exception(f"Payroll run {payroll_run_id} not found")
        
        # Update status to processing
        payroll_run.status = PayrollStatus.PROCESSING
        db.commit()
        
        # Get all employees for this family office
        employees = db.query(Employee).filter(
            Employee.family_office_id == payroll_run.family_office_id
        ).all()
        
        # Simulate processing time (2 seconds per employee)
        total_employees = len(employees)
        
        # Create directory for PDFs
        pdf_dir = f"/storage/family_office_{payroll_run.family_office_id}/payroll_run_{payroll_run_id}"
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Process each employee
        pay_stubs = []
        for i, employee in enumerate(employees):
            # Update progress
            progress = int((i + 1) / total_employees * 100)
            self.update_state(state='PROGRESS', meta={'current': i + 1, 'total': total_employees, 'progress': progress})
            
            # Calculate net pay
            net_pay = calculate_net_pay(employee.salary)
            
            # Generate PDF pay stub
            pdf_filename = f"{employee.id}_{employee.name.replace(' ', '_')}_paystub.pdf"
            pdf_path = os.path.join(pdf_dir, pdf_filename)
            generate_pay_stub_pdf(employee, net_pay, pdf_path)
            pay_stubs.append(pdf_path)
            
            # Simulate processing time
            time.sleep(2)
        
        # Create combined PDF path (in real app, would combine all PDFs)
        combined_pdf_path = os.path.join(pdf_dir, "all_pay_stubs.pdf")
        # For now, just copy the first pay stub as the combined one
        if pay_stubs:
            import shutil
            shutil.copy(pay_stubs[0], combined_pdf_path)
        
        # Update payroll run as completed
        payroll_run.status = PayrollStatus.COMPLETED
        payroll_run.completed_at = datetime.utcnow()
        payroll_run.pdf_path = combined_pdf_path
        db.commit()
        
        return {
            'status': 'completed',
            'employees_processed': total_employees,
            'pdf_path': combined_pdf_path
        }
        
    except Exception as e:
        # Update status to failed
        if payroll_run:
            payroll_run.status = PayrollStatus.FAILED
            db.commit()
        raise e
        
    finally:
        db.close()