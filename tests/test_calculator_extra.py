# -*- coding: utf-8 -*-
"""Additional tests for ROI Calculator"""
import pytest
from src.calculator import ROICalculator, ROIInput


@pytest.fixture
def calculator():
    return ROICalculator()


def test_automation_capacity_hours(calculator):
    """Automation capacity should be hours freed per month"""
    input_data = ROIInput(
        process_name="Capacity Test",
        current_time_per_month=880,  # total hours for all 5 people (176h * 5)
        people_involved=5,
        hourly_rate=23.86,
        rpa_implementation_cost=10000,
        rpa_monthly_cost=500,
        expected_automation_percentage=100,
    )
    result = calculator.calculate(input_data)
    # total hours = 880; with 100% automation -> 880 hours freed
    assert abs(result.automation_capacity - 880) < 1e-6


def test_payback_infinite_when_no_positive_savings(calculator):
    """If monthly savings are zero or negative, payback should be infinite"""
    input_data = ROIInput(
        process_name="No Save",
        current_time_per_month=10,
        people_involved=1,
        hourly_rate=0,
        rpa_implementation_cost=5000,
        rpa_monthly_cost=0,
        expected_automation_percentage=0,
    )
    result = calculator.calculate(input_data)
    assert result.payback_period_months == float('inf')
