# -*- coding: utf-8 -*-
"""Database models for calculations"""
from datetime import datetime
from sqlmodel import Field
from typing import Optional
from src.database.base import SQLModel


class Calculation(SQLModel, table=True):
    """Model for storing calculation history"""
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    
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
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def __repr__(self):
        return f"Calculation(id={self.id}, process_name='{self.process_name}', roi={self.roi_percentage_first_year:.2f}%)"
