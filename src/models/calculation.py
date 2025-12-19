# -*- coding: utf-8 -*-
"""Database models for calculations"""
from datetime import datetime
from sqlmodel import Field, SQLModel
from typing import Optional


class Calculation(SQLModel, table=True):
    """Model for storing calculation history"""
    id: Optional[int] = Field(default=None, primary_key=True)
    process_name: str
    current_time_per_month: float
    people_involved: int
    hourly_rate: float
    rpa_implementation_cost: float
    rpa_monthly_cost: float
    expected_automation_percentage: float
    monthly_savings: float
    annual_savings: float
    payback_period_months: float
    roi_first_year: float
    roi_percentage_first_year: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def __repr__(self):
        return f"Calculation(id={self.id}, process_name='{self.process_name}', roi={self.roi_percentage_first_year:.2f}%)"
