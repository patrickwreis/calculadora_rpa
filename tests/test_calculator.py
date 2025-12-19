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
