# -*- coding: utf-8 -*-
"""ROI Calculator - Core calculation logic"""
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class ROIInput:
    """Input data for ROI calculation"""
    process_name: str
    current_time_per_month: float  # hours
    people_involved: int
    hourly_rate: float  # currency per hour
    rpa_implementation_cost: float
    rpa_monthly_cost: float
    expected_automation_percentage: float  # 0-100
    

@dataclass
class ROIResult:
    """Result of ROI calculation"""
    monthly_savings: float
    annual_savings: float
    payback_period_months: float
    roi_first_year: float
    roi_percentage_first_year: float
    automation_capacity: float


class ROICalculator:
    """Calculate ROI for RPA implementations"""
    
    def __init__(self):
        pass
    
    def calculate(self, input_data: ROIInput) -> ROIResult:
        """
        Calculate ROI metrics based on input data
        
        Args:
            input_data: ROIInput object with calculation parameters
            
        Returns:
            ROIResult object with calculated metrics
        """
        # Current monthly cost
        current_monthly_cost = (
            input_data.current_time_per_month * 
            input_data.people_involved * 
            input_data.hourly_rate
        )
        
        # Expected monthly cost after automation
        automation_factor = input_data.expected_automation_percentage / 100
        automated_cost = current_monthly_cost * (1 - automation_factor)
        
        # Monthly savings
        monthly_savings = current_monthly_cost - automated_cost
        monthly_savings -= input_data.rpa_monthly_cost  # Subtract RPA cost
        
        # Annual metrics
        annual_savings = monthly_savings * 12
        
        # Payback period (months)
        if monthly_savings > 0:
            payback_period = input_data.rpa_implementation_cost / monthly_savings
        else:
            payback_period = float('inf')
        
        # ROI first year
        roi_first_year = annual_savings - input_data.rpa_implementation_cost
        roi_percentage = (roi_first_year / input_data.rpa_implementation_cost) * 100 if input_data.rpa_implementation_cost > 0 else 0
        
        # Automation capacity (hours per month freed up)
        # Total hours per month = current_time_per_month * people_involved
        # Hours freed = total_hours * automation_percentage / 100
        total_hours_per_month = input_data.current_time_per_month * input_data.people_involved
        automation_capacity = total_hours_per_month * (input_data.expected_automation_percentage / 100)
        
        return ROIResult(
            monthly_savings=monthly_savings,
            annual_savings=annual_savings,
            payback_period_months=payback_period,
            roi_first_year=roi_first_year,
            roi_percentage_first_year=roi_percentage,
            automation_capacity=automation_capacity
        )
    
    def calculate_multiple(self, inputs: list) -> list:
        """Calculate ROI for multiple processes"""
        return [self.calculate(input_data) for input_data in inputs]
