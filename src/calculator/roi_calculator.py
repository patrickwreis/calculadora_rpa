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
    expected_automation_percentage: float  # 0-100: % of process that will be automated
    exception_rate: float = 0.0  # 0-100: % of automated work that still needs manual review
    

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
        Calculate ROI metrics based on input data using correct automation formula.
        
        Formula breakdown:
        - fully_automated_pct = expected_automation_percentage × (1 - exception_rate/100)
        - partial_review_pct = expected_automation_percentage × exception_rate/100
        - still_manual_pct = 100 - expected_automation_percentage
        - total_manual_effort = partial_review_pct + still_manual_pct
        
        Cost after automation = current_monthly_cost × (total_manual_effort_pct / 100)
        
        Args:
            input_data: ROIInput object with calculation parameters
            
        Returns:
            ROIResult object with calculated metrics
        """
        # Current monthly cost
        # Note: current_time_per_month already includes all people (total team hours)
        current_monthly_cost = input_data.current_time_per_month * input_data.hourly_rate
        
        # Calculate actual automation metrics
        from src.calculator.utils import calculate_automation_metrics
        
        metrics = calculate_automation_metrics(
            expected_automation_percentage=input_data.expected_automation_percentage,
            exception_rate=input_data.exception_rate
        )
        
        # Cost after automation = current cost × (total manual effort % / 100)
        manual_effort_ratio = metrics["total_manual_effort_pct"] / 100.0
        automated_cost = current_monthly_cost * manual_effort_ratio
        
        # Monthly savings (gross - before RPA costs)
        gross_monthly_savings = current_monthly_cost - automated_cost
        
        # Net monthly savings (after RPA costs)
        monthly_savings = gross_monthly_savings - input_data.rpa_monthly_cost
        
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
        
        # Automation capacity (hours per month freed up - ONLY fully automated portion)
        automation_capacity = input_data.current_time_per_month * (metrics["fully_automated_pct"] / 100.0)
        
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
    
    def calculate_extended_roi(
        self, 
        base_result: ROIResult, 
        implementation_cost: float,
        fines_avoided: float = 0.0,
        sql_savings: float = 0.0
    ) -> Dict[str, float]:
        """
        Calculate extended ROI metrics including additional benefits
        
        Args:
            base_result: Base ROI calculation result
            implementation_cost: Implementation cost
            fines_avoided: Monthly fines avoided (default: 0.0)
            sql_savings: Monthly SLA savings (default: 0.0)
            
        Returns:
            Dictionary with extended metrics including ROI for 1, 2, and 5 years
        """
        # Total monthly savings including additional benefits
        total_monthly_savings = base_result.monthly_savings + fines_avoided + sql_savings
        
        # Calculate annual savings
        total_annual_savings = total_monthly_savings * 12
        
        # Calculate payback period with additional benefits
        if total_monthly_savings > 0:
            payback_period = implementation_cost / total_monthly_savings
        else:
            payback_period = float('inf')
        
        # Calculate ROI for different time periods
        def calculate_roi_for_period(months: int) -> Tuple[float, float]:
            """Calculate ROI percentage and total savings for a given period"""
            total_savings = total_monthly_savings * months
            roi_value = total_savings - implementation_cost
            roi_percentage = (roi_value / implementation_cost * 100) if implementation_cost > 0 else 0
            return roi_percentage, roi_value
        
        roi_1year_pct, economia_1year = calculate_roi_for_period(12)
        roi_2years_pct, economia_2years = calculate_roi_for_period(24)
        roi_5years_pct, economia_5years = calculate_roi_for_period(60)
        
        return {
            # Monthly and annual savings
            "total_monthly_savings": total_monthly_savings,
            "total_annual_savings": total_annual_savings,
            
            # Payback
            "payback_period_months": payback_period,
            
            # ROI percentages for different periods
            "roi_1year_percentage": roi_1year_pct,
            "roi_2years_percentage": roi_2years_pct,
            "roi_5years_percentage": roi_5years_pct,
            
            # Total savings (economia) for different periods
            "economia_1year": economia_1year,
            "economia_2years": economia_2years,
            "economia_5years": economia_5years,
            
            # Additional benefits breakdown
            "fines_avoided": fines_avoided,
            "sql_savings": sql_savings,
            "base_savings": base_result.monthly_savings,
        }
