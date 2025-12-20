# -*- coding: utf-8 -*-
"""Tests for edge cases and special scenarios"""
import pytest
from datetime import datetime
from src.analysis.ranking import _safe_payback
from src.models.calculation import Calculation


class TestSafePayback:
    """Test the _safe_payback helper function"""
    
    def test_safe_payback_with_valid_float(self):
        """Test _safe_payback with valid float"""
        calc = Calculation(
            id=1,
            process_name="Test",
            people_involved=1,
            current_time_per_month=20,
            hourly_rate=50,
            expected_automation_percentage=50,
            rpa_implementation_cost=5000,
            rpa_monthly_cost=200,
            monthly_savings=1000,
            annual_savings=12000,
            payback_period_months=5.5,
            roi_first_year=7000,
            roi_percentage_first_year=140,
        )
        
        result = _safe_payback(calc)
        assert result == 5.5
    
    def test_safe_payback_with_infinity(self):
        """Test _safe_payback with infinity"""
        calc = Calculation(
            id=1,
            process_name="Test",
            people_involved=1,
            current_time_per_month=20,
            hourly_rate=50,
            expected_automation_percentage=50,
            rpa_implementation_cost=5000,
            rpa_monthly_cost=200,
            monthly_savings=-100,  # Negative savings
            annual_savings=-1200,
            payback_period_months=float('inf'),
            roi_first_year=-7000,
            roi_percentage_first_year=-140,
        )
        
        result = _safe_payback(calc)
        assert result == float('inf')
    
    def test_safe_payback_with_none(self):
        """Test _safe_payback when payback_period_months is very small (edge case)"""
        # Create a minimal calculation object
        calc = Calculation(
            id=1,
            process_name="Test",
            people_involved=1,
            current_time_per_month=20,
            hourly_rate=50,
            expected_automation_percentage=50,
            rpa_implementation_cost=5000,
            rpa_monthly_cost=200,
            monthly_savings=1000,
            annual_savings=12000,
            payback_period_months=None,
            roi_first_year=7000,
            roi_percentage_first_year=140,
        )
        
        result = _safe_payback(calc)
        assert result == float('inf')
    
    def test_safe_payback_with_zero(self):
        """Test _safe_payback with zero payback"""
        calc = Calculation(
            id=1,
            process_name="Test",
            people_involved=1,
            current_time_per_month=20,
            hourly_rate=50,
            expected_automation_percentage=50,
            rpa_implementation_cost=0,  # No cost, immediate payback
            rpa_monthly_cost=200,
            monthly_savings=1000,
            annual_savings=12000,
            payback_period_months=0,
            roi_first_year=7000,
            roi_percentage_first_year=140,
        )
        
        result = _safe_payback(calc)
        assert result == 0
