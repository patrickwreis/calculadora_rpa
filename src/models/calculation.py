# -*- coding: utf-8 -*-
"""Database models for calculations"""
from datetime import datetime
from sqlmodel import Field
from typing import Optional
from src.database.base import SQLModel


def classify_process(roi_percentage: float, payback_months: float) -> str:
    """
    Classify process based on ROI and payback period.
    
    - QUICK WIN: ROI > 50% AND Payback < 12 months
    - MÉDIO PRAZO: ROI > 0% AND Payback < 24 months
    - BAIXA PRIORIDADE: ROI <= 0% OR Payback >= 24 months
    
    Args:
        roi_percentage: ROI percentage (e.g., 120 for 120%)
        payback_months: Payback period in months
        
    Returns:
        Classification string: "QUICK WIN", "MÉDIO PRAZO", or "BAIXA PRIORIDADE"
    """
    if roi_percentage > 50 and payback_months < 12:
        return "QUICK WIN"
    elif roi_percentage > 0 and payback_months < 24:
        return "MÉDIO PRAZO"
    else:
        return "BAIXA PRIORIDADE"


class Calculation(SQLModel, table=True):
    """Model for storing calculation history"""
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # User ownership (multi-tenant)
    user_id: int = Field(default=1, index=True)  # Default to 1 for now (will be linked to User model later)
    
    # Basic Information
    process_name: str
    department: str = ""
    
    # Process Characteristics
    people_involved: int
    current_time_per_month: float
    hourly_rate: float
    complexity: str = "Média"  # Baixa, Média, Alta
    systems_quantity: int = 1
    daily_transactions: int = 100
    error_rate: float = 0.0  # percentage
    exception_rate: float = 0.0  # percentage
    
    # Input fields for edit form (to match add form exactly)
    days_per_month: int = Field(default=22)  # working days per month
    monthly_salary: float = Field(default=0.0)  # salary + benefits per employee
    minutes_per_day: int = Field(default=0)  # time spent per day in minutes
    dev_hours: float = Field(default=0.0)  # development hours
    dev_hourly_rate: float = Field(default=150.0)  # development hourly rate
    
    # Automation Settings
    expected_automation_percentage: float
    
    # Implementation Costs
    rpa_implementation_cost: float
    maintenance_percentage: float = 10.0  # annual % of dev cost
    infra_license_cost: float = 0.0  # monthly
    other_costs: float = 0.0  # one-time
    rpa_monthly_cost: float
    
    # Additional Benefits
    fines_avoided: float = 0.0  # monthly
    sql_savings: float = 0.0  # monthly
    
    # Calculated Results
    monthly_savings: float
    annual_savings: float
    payback_period_months: float
    roi_first_year: float
    roi_percentage_first_year: float
    
    # Process Classification (auto-calculated by classify_process())
    classification: str = Field(default="BAIXA PRIORIDADE")  # QUICK WIN | MÉDIO PRAZO | BAIXA PRIORIDADE
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def __repr__(self):
        return f"Calculation(id={self.id}, user_id={self.user_id}, process_name='{self.process_name}', roi={self.roi_percentage_first_year:.2f}%, classification='{self.classification}')"
