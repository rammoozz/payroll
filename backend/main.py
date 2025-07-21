from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
import os

from database import get_db, init_db
from models import Employee, PayrollRun, PayrollStatus
from auth import create_access_token, verify_token, authenticate_user, TokenData
from tasks import process_payroll, celery_app

app = FastAPI(title="Family Office Payroll POC")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API
class Token(BaseModel):
    access_token: str
    token_type: str
    family_office_name: str


class EmployeeResponse(BaseModel):
    id: int
    name: str
    salary: float
    
    class Config:
        from_attributes = True


class PayrollRunResponse(BaseModel):
    id: int
    status: PayrollStatus
    created_at: datetime
    completed_at: datetime | None
    
    class Config:
        from_attributes = True


class PayrollRunRequest(BaseModel):
    employee_ids: List[int]


@app.on_event("startup")
async def startup_event():
    init_db()
    # Initialize demo data
    from init_db import seed_demo_data
    seed_demo_data()


@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"email": form_data.username, "family_office_id": user["family_office_id"]}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "family_office_name": user["name"]
    }


@app.get("/employees", response_model=List[EmployeeResponse])
async def get_employees(
    token_data: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
):
    employees = db.query(Employee).filter(
        Employee.family_office_id == token_data.family_office_id
    ).all()
    return employees


@app.post("/payroll/run", response_model=PayrollRunResponse)
async def run_payroll(
    request: PayrollRunRequest,
    token_data: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
):
    # Verify all employees belong to the user's family office
    employees = db.query(Employee).filter(
        Employee.id.in_(request.employee_ids),
        Employee.family_office_id == token_data.family_office_id
    ).all()
    
    if len(employees) != len(request.employee_ids):
        raise HTTPException(status_code=400, detail="Invalid employee IDs")
    
    # Create payroll run
    payroll_run = PayrollRun(
        family_office_id=token_data.family_office_id,
        status=PayrollStatus.PENDING
    )
    db.add(payroll_run)
    db.commit()
    db.refresh(payroll_run)
    
    # Queue async task
    process_payroll.delay(payroll_run.id)
    
    return payroll_run


@app.get("/payroll/{run_id}", response_model=PayrollRunResponse)
async def get_payroll_status(
    run_id: int,
    token_data: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
):
    payroll_run = db.query(PayrollRun).filter(
        PayrollRun.id == run_id,
        PayrollRun.family_office_id == token_data.family_office_id
    ).first()
    
    if not payroll_run:
        raise HTTPException(status_code=404, detail="Payroll run not found")
    
    return payroll_run


@app.get("/payroll/{run_id}/pdf")
async def download_payroll_pdf(
    run_id: int,
    token_data: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
):
    payroll_run = db.query(PayrollRun).filter(
        PayrollRun.id == run_id,
        PayrollRun.family_office_id == token_data.family_office_id,
        PayrollRun.status == PayrollStatus.COMPLETED
    ).first()
    
    if not payroll_run:
        raise HTTPException(status_code=404, detail="Payroll run not found or not completed")
    
    if not payroll_run.pdf_path or not os.path.exists(payroll_run.pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    return FileResponse(
        payroll_run.pdf_path,
        media_type="application/pdf",
        filename=f"payroll_run_{run_id}.pdf"
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy"}