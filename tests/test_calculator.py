# -*- coding: utf-8 -*-
"""Tests for ROI Calculator"""
import pytest
from src.calculator import ROICalculator, ROIInput


@pytest.fixture
def calculator():
    return ROICalculator()


@pytest.fixture
def sample_input():
    return ROIInput(
        process_name="Invoice Processing",
        current_time_per_month=160,
        people_involved=2,
        hourly_rate=50,
        rpa_implementation_cost=5000,
        rpa_monthly_cost=200,
        expected_automation_percentage=80
    )


def test_calculate_basic(calculator, sample_input):
    """Test basic ROI calculation"""
    result = calculator.calculate(sample_input)
    
    assert result.monthly_savings > 0
    assert result.annual_savings > 0
    assert result.payback_period_months > 0
    assert result.roi_percentage_first_year > 0


def test_calculate_no_savings(calculator):
    """Test calculation when no savings occur"""
    input_data = ROIInput(
        process_name="Test",
        current_time_per_month=10,
        people_involved=1,
        hourly_rate=50,
        rpa_implementation_cost=10000,
        rpa_monthly_cost=600,  # High monthly cost
        expected_automation_percentage=50
    )
    result = calculator.calculate(input_data)
    assert result.monthly_savings <= 0


def test_calculate_extended_roi(calculator, sample_input):
    """Test extended ROI calculation with additional benefits"""
    # First calculate base result
    base_result = calculator.calculate(sample_input)
    
    # Calculate extended ROI with additional benefits
    fines_avoided = 500.0
    sql_savings = 300.0
    
    extended_metrics = calculator.calculate_extended_roi(
        base_result=base_result,
        implementation_cost=sample_input.rpa_implementation_cost,
        fines_avoided=fines_avoided,
        sql_savings=sql_savings
    )
    
    # Verify structure
    assert "total_monthly_savings" in extended_metrics
    assert "total_annual_savings" in extended_metrics
    assert "payback_period_months" in extended_metrics
    assert "roi_1year_percentage" in extended_metrics
    assert "roi_2years_percentage" in extended_metrics
    assert "roi_5years_percentage" in extended_metrics
    assert "economia_1year" in extended_metrics
    assert "economia_2years" in extended_metrics
    assert "economia_5years" in extended_metrics
    
    # Verify additional benefits are included
    assert extended_metrics["fines_avoided"] == fines_avoided
    assert extended_metrics["sql_savings"] == sql_savings
    assert extended_metrics["total_monthly_savings"] == base_result.monthly_savings + fines_avoided + sql_savings
    
    # Verify calculations are correct
    total_monthly = extended_metrics["total_monthly_savings"]
    assert extended_metrics["total_annual_savings"] == total_monthly * 12
    assert extended_metrics["economia_1year"] == (total_monthly * 12) - sample_input.rpa_implementation_cost
    assert extended_metrics["economia_2years"] == (total_monthly * 24) - sample_input.rpa_implementation_cost
    assert extended_metrics["economia_5years"] == (total_monthly * 60) - sample_input.rpa_implementation_cost
    
    # Verify ROI percentages increase with time
    assert extended_metrics["roi_2years_percentage"] > extended_metrics["roi_1year_percentage"]
    assert extended_metrics["roi_5years_percentage"] > extended_metrics["roi_2years_percentage"]


def test_calculate_extended_roi_no_additional_benefits(calculator, sample_input):
    """Test extended ROI calculation without additional benefits"""
    base_result = calculator.calculate(sample_input)
    
    extended_metrics = calculator.calculate_extended_roi(
        base_result=base_result,
        implementation_cost=sample_input.rpa_implementation_cost
    )
    
    # Should be equal to base savings when no additional benefits
    assert extended_metrics["total_monthly_savings"] == base_result.monthly_savings
    assert extended_metrics["fines_avoided"] == 0.0
    assert extended_metrics["sql_savings"] == 0.0

